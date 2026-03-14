import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "parent_chatbot_secret_2024")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "chatbot.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OTP_EXPIRY_SECONDS = 300  # 5 minutes

    # ── Twilio SMS credentials ────────────────────────────
    # Set these as environment variables before running the app:
    #   $env:TWILIO_ACCOUNT_SID  = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    #   $env:TWILIO_AUTH_TOKEN   = "your_auth_token"
    #   $env:TWILIO_FROM_NUMBER  = "+1xxxxxxxxxx"
    
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")