import os
from datetime import timedelta

from dotenv import load_dotenv
from db_connection import get_database_config

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=False)


SENDER_EMAIL = "Gamified Learning <no-reply@gamifiedlearning.quest>"

def _build_database_uri() -> str:
    return get_database_config()[0]


def _parse_cors_origins(value: str):
    def _normalize_origin_pattern(origin: str) -> str:
        if "*" not in origin:
            return origin

        escaped = ""
        for ch in origin:
            if ch == "*":
                escaped += ".*"
            elif ch in ".^$+?{}[]|()":
                escaped += f"\\{ch}"
            else:
                escaped += ch

        return f"^{escaped}$"

    required_origins = {
        "https://gamifiedlearning.quest",
        "https://www.gamifiedlearning.quest",
        "https://gamified-learning-flame.vercel.app",
        "https://gamified-learning.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    }
    raw = (value or "").strip()
    if not raw:
        return sorted(required_origins)
    if raw == "*":
        return sorted(required_origins)

    parsed_origins = []
    for origin in raw.split(","):
        normalized = origin.strip()
        if not normalized:
            continue
        parsed_origins.append(_normalize_origin_pattern(normalized))

    # Allow explicit Vercel preview patterns by preserving wildcard-like entries.
    # Example CORS_ORIGINS: https://my-app.vercel.app,https://*.vercel.app
    parsed_set = set(parsed_origins)
    parsed_set.update(required_origins)

    return sorted(parsed_set)


class Config:
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "280")),
    }
    DB_CHECK_ON_STARTUP = os.getenv("DB_CHECK_ON_STARTUP", "true").lower() == "true"
    DB_STARTUP_CHECK_ATTEMPTS = int(os.getenv("DB_STARTUP_CHECK_ATTEMPTS", "3"))
    DB_STARTUP_CHECK_DELAY_SECONDS = float(os.getenv("DB_STARTUP_CHECK_DELAY_SECONDS", "2"))
    JSON_SORT_KEYS = False
    CORS_ORIGINS = _parse_cors_origins(os.getenv("CORS_ORIGINS", ""))
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET",
        os.getenv(
            "JWT_SECRET_KEY",
            "change-this-secret-to-a-long-random-string-at-least-32-bytes",
        ),
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_ERROR_MESSAGE_KEY = "message"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", "24"))
    )

    # Uploads configuration
    UPLOAD_DIR = os.getenv(
        "UPLOAD_DIR",
        os.path.join(os.path.dirname(__file__), "uploads"),
    )

    # Disable startup DB mutations in production by default.
    RUN_STARTUP_TASKS = os.getenv("RUN_STARTUP_TASKS", "false").lower() == "true"

    # Email configuration (Resend)
    OTP_EMAIL_PROVIDER = os.getenv("OTP_EMAIL_PROVIDER", "resend").strip().lower()
    EMAIL_FROM = os.getenv("EMAIL_FROM", SENDER_EMAIL)
    RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
    RESEND_API_URL = os.getenv("RESEND_API_URL", "https://api.resend.com")

    # Google Sign-In configuration
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
