import os
import time
from typing import Callable, TypeVar
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


T = TypeVar("T")


def normalize_database_url(url: str) -> str:
    normalized = (url or "").strip()
    if normalized.startswith("mysql://"):
        normalized = normalized.replace("mysql://", "mysql+pymysql://", 1)

    parsed = urlsplit(normalized)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "charset" not in query:
        query["charset"] = "utf8mb4"

    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


def get_database_url() -> str:
    direct_url = os.getenv("DATABASE_URL", "").strip()
    if direct_url:
        return normalize_database_url(direct_url)

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


def create_mysql_engine(database_url: str | None = None, *, pool_size: int = 1, max_overflow: int = 0):
    return create_engine(
        database_url or get_database_url(),
        pool_pre_ping=True,
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "280")),
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        pool_size=int(os.getenv("DB_POOL_SIZE", str(pool_size))),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", str(max_overflow))),
        pool_use_lifo=True,
        connect_args={
            "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "15")),
            "read_timeout": int(os.getenv("DB_READ_TIMEOUT", "30")),
            "write_timeout": int(os.getenv("DB_WRITE_TIMEOUT", "30")),
        },
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
