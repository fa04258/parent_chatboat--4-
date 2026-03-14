from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from chatbot.handler import handle_message
from chatbot.translator import translate_html, LANG_MAP, SPEECH_LANG_MAP

chat_bp = Blueprint("chat", __name__)


def _require_auth():
    """Return student_id if authenticated, else None."""
    return session.get("student_id")


@chat_bp.route("/chat", methods=["GET"])
def chat_page():
    student_id = _require_auth()
    if not student_id:
        return redirect(url_for("auth.index"))
    return render_template("chat.html", student_name=session.get("student_name", "Parent"))


@chat_bp.route("/chat", methods=["POST"])
def chat_api():
    student_id = _require_auth()
    if not student_id:
        return jsonify({"success": False, "message": "Unauthorized. Please log in."}), 401

    data = request.get_json(force=True)
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"success": False, "message": "Empty message."}), 400

    # Handle logout via chat
    if message.lower() in ("logout", "exit", "bye", "quit"):
        session.clear()
        return jsonify({
            "success": True,
            "reply": "You have been securely logged out. Stay connected! 👋",
            "logout": True,
        })

    result = handle_message(message, student_id)

    # Translate reply if a non-English language is selected
    lang_label = session.get("language", "english")
    if lang_label != "english":
        result["reply"] = translate_html(result["reply"], lang_label)

    return jsonify({"success": True, **result})


@chat_bp.route("/set-language", methods=["POST"])
def set_language():
    """Save the parent's preferred language in the session."""
    student_id = _require_auth()
    if not student_id:
        return jsonify({"success": False, "message": "Unauthorized."}), 401

    data = request.get_json(force=True)
    lang = (data.get("language") or "english").lower().strip()
    if lang not in LANG_MAP:
        return jsonify({"success": False, "message": "Unsupported language."}), 400

    session["language"] = lang
    lang_code = LANG_MAP[lang]
    speech_locale = SPEECH_LANG_MAP.get(lang_code, "en-US")
    return jsonify({"success": True, "language": lang, "speech_locale": speech_locale})
