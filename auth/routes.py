import random
import logging
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from database.models import db, Student, OTPStore, StudentContact
from config import Config
from auth.sms import send_otp_sms

auth_bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


# ── Helper ────────────────────────────────────────────────────────────────────

def _generate_otp():
    return str(random.randint(100000, 999999))


# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.route("/", methods=["GET"])
def index():
    if session.get("student_id"):
        return redirect(url_for("chat.chat_page"))
    return render_template("index.html")


@auth_bp.route("/verify-registration", methods=["POST"])
def verify_registration():
    """Step 1 – Validate student registration number."""
    data = request.get_json(force=True)
    reg_number = (data.get("reg_number") or "").strip().upper()

    if not reg_number:
        return jsonify({"success": False, "message": "Registration number is required."}), 400

    student = Student.query.filter_by(reg_number=reg_number).first()
    if not student:
        return jsonify({"success": False, "message": "Invalid registration number. Please try again."}), 404

    # Store reg_number temporarily in session (not fully authenticated yet)
    session["pending_reg"] = reg_number
    return jsonify({
        "success": True,
        "message": f"Registration number verified. Welcome, {student.name}'s parent! Please enter the registered phone number.",
    })


def _mask_phone(phone: str) -> str:
    """Return a masked version like ******3210 for display."""
    phone = phone.strip()
    return "*" * (len(phone) - 4) + phone[-4:]


@auth_bp.route("/get-contacts", methods=["GET"])
def get_contacts():
    """Return masked phone numbers registered for the pending student."""
    pending_reg = session.get("pending_reg")
    if not pending_reg:
        return jsonify({"success": False, "message": "Session expired."}), 403

    student = Student.query.filter_by(reg_number=pending_reg).first()
    if not student:
        return jsonify({"success": False, "message": "Student not found."}), 404

    # Collect all registered phones (primary + extra contacts)
    phones = []
    if student.parent_phone:
        phones.append({"masked": _mask_phone(student.parent_phone), "type": "Parent"})

    for c in student.contacts:
        phones.append({"masked": _mask_phone(c.phone), "type": c.contact_type.capitalize()})

    return jsonify({"success": True, "contacts": phones})


@auth_bp.route("/verify-phone", methods=["POST"])
def verify_phone():
    """Step 2 – Validate parent phone number."""
    pending_reg = session.get("pending_reg")
    if not pending_reg:
        return jsonify({"success": False, "message": "Session expired. Please start again."}), 403

    data = request.get_json(force=True)
    student = Student.query.filter_by(reg_number=pending_reg).first()
    if not student:
        return jsonify({"success": False, "message": "Student not found."}), 404

    # Build ordered list of registered phones (same order as /get-contacts)
    registered_phones = []
    if student.parent_phone:
        registered_phones.append(student.parent_phone)
    registered_phones += [c.phone for c in student.contacts]

    # Accept either contact_index (button click) or phone (manual entry)
    contact_index = data.get("contact_index")
    if contact_index is not None:
        try:
            phone = registered_phones[int(contact_index)]
        except (IndexError, ValueError, TypeError):
            return jsonify({"success": False, "message": "Invalid selection. Please try again."}), 400
    else:
        phone = (data.get("phone") or "").strip()
        if not phone:
            return jsonify({"success": False, "message": "Phone number is required."}), 400
        if phone not in registered_phones:
            return jsonify({"success": False, "message": "Phone number does not match our records."}), 401

    # Generate and store OTP
    otp_code = _generate_otp()
    expires_at = datetime.utcnow() + timedelta(seconds=Config.OTP_EXPIRY_SECONDS)

    # Invalidate previous OTPs for this phone
    OTPStore.query.filter_by(phone=phone, used=False).update({"used": True})
    db.session.add(OTPStore(phone=phone, otp_code=otp_code, expires_at=expires_at))
    db.session.commit()

    # Send OTP via Twilio SMS
    sms_sent = send_otp_sms(phone, otp_code)
    if not sms_sent:
        # Fallback: log to console so development still works without Twilio
        logger.warning("=" * 45)
        logger.warning(f"  [SMS FALLBACK] OTP for {phone}: {otp_code}  (valid 5 min)")
        logger.warning("=" * 45)

    session["pending_phone"] = phone
    return jsonify({
        "success": True,
        "message": "OTP sent to your registered mobile number. Please enter it below.",
    })


@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    """Step 3 – Validate OTP and create authenticated session."""
    pending_reg = session.get("pending_reg")
    pending_phone = session.get("pending_phone")

    if not pending_reg or not pending_phone:
        return jsonify({"success": False, "message": "Session expired. Please start again."}), 403

    data = request.get_json(force=True)
    entered_otp = (data.get("otp") or "").strip()

    if not entered_otp:
        return jsonify({"success": False, "message": "OTP is required."}), 400

    otp_record = (
        OTPStore.query
        .filter_by(phone=pending_phone, otp_code=entered_otp, used=False)
        .order_by(OTPStore.created_at.desc())
        .first()
    )

    if not otp_record:
        return jsonify({"success": False, "message": "Invalid OTP. Please try again."}), 401

    if datetime.utcnow() > otp_record.expires_at:
        otp_record.used = True
        db.session.commit()
        return jsonify({"success": False, "message": "OTP has expired. Please request a new one."}), 401

    # Mark OTP as used
    otp_record.used = True
    db.session.commit()

    # Fully authenticate
    student = Student.query.filter_by(reg_number=pending_reg).first()
    session.clear()
    session["student_id"] = student.id
    session["student_name"] = student.name
    session.permanent = True

    return jsonify({
        "success": True,
        "message": "Authentication successful! Redirecting to chatbot...",
        "redirect": url_for("chat.chat_page"),
    })


@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect(url_for("auth.index"))
