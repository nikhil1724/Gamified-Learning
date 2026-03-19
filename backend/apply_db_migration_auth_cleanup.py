"""Drop legacy verification columns from users table.

Run this once after deploying the simplified auth model.
"""

import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv


load_dotenv()


def _normalize_database_url(url: str) -> str:
    normalized = (url or "").strip()
    if normalized.startswith("mysql://"):
        normalized = normalized.replace("mysql://", "mysql+pymysql://", 1)

    parsed = urlsplit(normalized)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "charset" not in query:
        query["charset"] = "utf8mb4"

    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


def _get_database_url() -> str:
    direct_url = os.getenv("DATABASE_URL", "").strip()
    if direct_url:
        return _normalize_database_url(direct_url)

    db_user = os.getenv("DB_USER", "").strip()
    db_password = os.getenv("DB_PASSWORD", "").strip()
    db_host = os.getenv("DB_HOST", "").strip()
    db_port = os.getenv("DB_PORT", "").strip()
    db_name = os.getenv("DB_NAME", "").strip()

    if all([db_user, db_password, db_host, db_port, db_name]):
        return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"

    raise RuntimeError(
        "Missing database config. Set DATABASE_URL or DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME."
    )


def _drop_column_if_exists(conn, column_name: str):
    exists_query = text(
        """
        SELECT COUNT(*)
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'users'
          AND COLUMN_NAME = :column_name
        """
    )
    exists = conn.execute(exists_query, {"column_name": column_name}).scalar() > 0
    if not exists:
        print(f"[auth-cleanup] column not present, skipping: {column_name}")
        return

    conn.execute(text(f"ALTER TABLE users DROP COLUMN {column_name}"))
    print(f"[auth-cleanup] dropped column: {column_name}")


def main() -> None:
    database_url = _get_database_url()
    engine = create_engine(database_url, pool_pre_ping=True)

    legacy_columns = [
        "is_verified",
        "email_verified",
        "verification_token",
        "verification_token_expiry",
        "otp_code",
        "otp_expiry",
        "otp_resend_count",
        "otp_resend_window_start",
        "otp_last_sent_at",
        "otp_verify_fail_count",
        "otp_verify_locked_until",
    ]

    try:
        with engine.begin() as conn:
            for column in legacy_columns:
                _drop_column_if_exists(conn, column)
        print("[auth-cleanup] completed")
    except SQLAlchemyError as exc:
        raise RuntimeError(f"Failed to apply auth cleanup migration: {exc}") from exc


if __name__ == "__main__":
    main()
