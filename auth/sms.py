"""
SMS helper – sends OTP via Twilio.
Credentials are loaded from environment variables (see config.py).
"""

import logging
from twilio.rest import Client
from config import Config

logger = logging.getLogger(__name__)


def _format_indian_number(phone: str) -> str:
    """
    Convert a 10-digit Indian mobile number to E.164 format (+91XXXXXXXXXX).
    If the number already starts with '+', return it as-is.
    """
    phone = phone.strip()
    if phone.startswith("+"):
        return phone
    # Strip leading 0 or 91 if present
    if phone.startswith("91") and len(phone) == 12:
        return "+" + phone
    if phone.startswith("0"):
        phone = phone[1:]
    return "+91" + phone


def send_otp_sms(phone: str, otp: str) -> bool:
    """
    Send the OTP to *phone* via Twilio SMS.
    Returns True on success, False on failure.
    """
    sid   = Config.TWILIO_ACCOUNT_SID
    token = Config.TWILIO_AUTH_TOKEN
    from_ = Config.TWILIO_FROM_NUMBER

    if not all([sid, token, from_]):
        logger.error("Twilio credentials are not configured. Set TWILIO_ACCOUNT_SID, "
                     "TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER environment variables.")
        return False

    try:
        client = Client(sid, token)
        to_number = _format_indian_number(phone)
        client.messages.create(
            body=f"Your Academic Portal OTP is: {otp}\nValid for 5 minutes. Do not share this with anyone.",
            from_=from_,
            to=to_number,
        )
        logger.info(f"OTP SMS sent successfully to {to_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP SMS to {phone}: {type(e).__name__}: {e}")
        return False
