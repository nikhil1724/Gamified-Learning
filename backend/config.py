import os
from datetime import timedelta
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv

load_dotenv()


def _normalize_database_url(url: str) -> str:
    normalized = url.strip()
    if normalized.startswith("mysql://"):
        normalized = normalized.replace("mysql://", "mysql+pymysql://", 1)

    parsed = urlsplit(normalized)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "charset" not in query:
        query["charset"] = "utf8mb4"

    normalized = urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment)
    )
    return normalized


def _build_database_uri() -> str:
    """Prefer DATABASE_URL for deployment platforms; fallback to DB_* vars for local use."""
    direct_url = os.getenv("DATABASE_URL", "").strip()
    if direct_url:
        return _normalize_database_url(direct_url)

    db_user = os.getenv("DB_USER", "").strip()
    db_password = os.getenv("DB_PASSWORD", "").strip()
    db_host = os.getenv("DB_HOST", "").strip()
    db_port = os.getenv("DB_PORT", "").strip()
    db_name = os.getenv("DB_NAME", "").strip()

    if all([db_user, db_password, db_host, db_port, db_name]):
        safe_user = quote_plus(db_user)
        safe_password = quote_plus(db_password)
        return (
            "mysql+pymysql://"
            f"{safe_user}:{safe_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
        )

    raise RuntimeError(
        "Missing database config. Set DATABASE_URL or DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME."
    )


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
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
        "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
        "connect_args": {
            "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "15")),
            "read_timeout": int(os.getenv("DB_READ_TIMEOUT", "30")),
            "write_timeout": int(os.getenv("DB_WRITE_TIMEOUT", "30")),
        },
    }
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
