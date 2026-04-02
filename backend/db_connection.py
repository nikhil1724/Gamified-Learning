import os
import time
from typing import Callable, TypeVar
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


T = TypeVar("T")


def normalize_database_url(url: str) -> str:
    normalized = (url or "").strip()
    if normalized.startswith("mysql://") or normalized.startswith("mysql+pymysql://"):
        raise RuntimeError(
            "Invalid DATABASE_URL for PostgreSQL deployment: MySQL URL detected. "
            "Set DATABASE_URL to postgresql+psycopg2://..."
        )

    if normalized.startswith("postgres://"):
        normalized = normalized.replace("postgres://", "postgresql+psycopg2://", 1)
    elif normalized.startswith("postgresql://"):
        normalized = normalized.replace("postgresql://", "postgresql+psycopg2://", 1)
    elif normalized.startswith("postgresql+psycopg://"):
        normalized = normalized.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)

    parsed = urlsplit(normalized)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "sslmode" not in query and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        query["sslmode"] = "require"

    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


def mask_database_url(url: str) -> str:
    parsed = urlsplit(url)
    hostname = parsed.hostname or "unknown"
    port = f":{parsed.port}" if parsed.port else ""
    username = parsed.username or "user"
    netloc = f"{username}:***@{hostname}{port}"
    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))


def get_database_config() -> tuple[str, str]:
    direct_url = os.getenv("DATABASE_URL", "").strip()
    if direct_url:
        return normalize_database_url(direct_url), "DATABASE_URL"

    env_name = os.getenv("FLASK_ENV", "production").strip().lower()
    allow_fallback_in_prod = os.getenv("ALLOW_DB_FALLBACK_IN_PROD", "false").strip().lower() == "true"
    if env_name == "production" and not allow_fallback_in_prod:
        raise RuntimeError(
            "DATABASE_URL is required in production. Set it in Render environment variables."
        )

    db_user = os.getenv("DB_USER", "").strip()
    db_password = os.getenv("DB_PASSWORD", "").strip()
    db_host = os.getenv("DB_HOST", "").strip()
    db_port = os.getenv("DB_PORT", "").strip()
    db_name = os.getenv("DB_NAME", "").strip()

    if all([db_user, db_password, db_host, db_port, db_name]):
        safe_user = quote_plus(db_user)
        safe_password = quote_plus(db_password)
        fallback_url = (
            "postgresql+psycopg2://"
            f"{safe_user}:{safe_password}@{db_host}:{db_port}/{db_name}"
        )
        return normalize_database_url(fallback_url), "DB_* fallback"

    raise RuntimeError(
        "Missing database config. Set DATABASE_URL or DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME."
    )


def get_database_diagnostics() -> dict[str, str]:
    url, source = get_database_config()
    parsed = urlsplit(url)
    database_name = (parsed.path or "/").lstrip("/") or "unknown"
    return {
        "source": source,
        "scheme": parsed.scheme or "unknown",
        "host": parsed.hostname or "unknown",
        "database": database_name,
        "masked_url": mask_database_url(url),
    }


def get_database_url() -> str:
    return get_database_config()[0]


def create_database_engine(database_url: str | None = None):
    return create_engine(
        database_url or get_database_url(),
        pool_pre_ping=True,
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "280")),
    )


def run_with_retry(
    action: Callable[[], T],
    label: str,
    attempts: int = 7,
    initial_delay: float = 3.0,
    max_delay: float = 30.0,
    cleanup: Callable[[], None] | None = None,
) -> T:
    delay = initial_delay
    last_error: OperationalError | None = None

    for attempt in range(1, attempts + 1):
        try:
            return action()
        except OperationalError as exc:
            last_error = exc
            if attempt == attempts:
                break

            print(f"[{label}] transient database error on attempt {attempt}/{attempts}: {exc}")
            if cleanup is not None:
                try:
                    cleanup()
                except Exception:
                    pass
            time.sleep(delay)
            delay = min(delay * 2, max_delay)

    raise RuntimeError(f"[{label}] database remained unavailable after {attempts} attempts") from last_error
