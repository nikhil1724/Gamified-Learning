import os

from dotenv import load_dotenv


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

load_dotenv()


class Config:
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    # Build a MySQL connection string from environment variables.
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://"
        f"{_require_env('DB_USER')}:{_require_env('DB_PASSWORD')}"
        f"@{_require_env('DB_HOST')}:{_require_env('DB_PORT')}"
        f"/{_require_env('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "change-this-secret-to-a-long-random-string-at-least-32-bytes",
    )
