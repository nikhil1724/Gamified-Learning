import os

from dotenv import load_dotenv

load_dotenv()


def _build_database_uri() -> str:
    """Prefer DATABASE_URL for deployment platforms; fallback to DB_* vars for local use."""
    direct_url = os.getenv("DATABASE_URL", "").strip()
    if direct_url:
        return direct_url

    db_user = os.getenv("DB_USER", "").strip()
    db_password = os.getenv("DB_PASSWORD", "").strip()
    db_host = os.getenv("DB_HOST", "").strip()
    db_port = os.getenv("DB_PORT", "").strip()
    db_name = os.getenv("DB_NAME", "").strip()

    if all([db_user, db_password, db_host, db_port, db_name]):
        return (
            "mysql+pymysql://"
            f"{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )

    raise RuntimeError(
        "Missing database config. Set DATABASE_URL or DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME."
    )


def _parse_cors_origins(value: str):
    raw = (value or "").strip()
    if not raw:
        return ["http://localhost:3000"]
    if raw == "*":
        return "*"
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class Config:
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    CORS_ORIGINS = _parse_cors_origins(os.getenv("CORS_ORIGINS", "http://localhost:3000"))
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET",
        os.getenv(
        "JWT_SECRET_KEY",
        "change-this-secret-to-a-long-random-string-at-least-32-bytes",
        ),
    )

    # Uploads configuration
    UPLOAD_DIR = os.getenv(
        "UPLOAD_DIR",
        os.path.join(os.path.dirname(__file__), "uploads"),
    )
    
    # Email configuration
    APP_URL = os.getenv("APP_URL", "http://localhost:3000")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", os.getenv("MAIL_FROM_EMAIL", "noreply@gamifiedlearning.com"))
    MAIL_FROM_EMAIL = os.getenv("MAIL_FROM_EMAIL", MAIL_DEFAULT_SENDER)
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Gamified Learning Platform")
    
    # Email verification settings
    EMAIL_VERIFICATION_REQUIRED = os.getenv("EMAIL_VERIFICATION_REQUIRED", "true").lower() == "true"
    OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "5"))
    OTP_RESEND_MAX_ATTEMPTS = int(os.getenv("OTP_RESEND_MAX_ATTEMPTS", "3"))
    OTP_RESEND_WINDOW_MINUTES = int(os.getenv("OTP_RESEND_WINDOW_MINUTES", "15"))
    VERIFICATION_TOKEN_EXPIRY_HOURS = int(os.getenv("VERIFICATION_TOKEN_EXPIRY_HOURS", "24"))

    # Legacy user migration settings
    AUTO_VERIFY_LEGACY_USERS = os.getenv("AUTO_VERIFY_LEGACY_USERS", "false").lower() == "true"
    LEGACY_VERIFICATION_CUTOFF = os.getenv("LEGACY_VERIFICATION_CUTOFF", "")
