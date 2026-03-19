"""Ensure required users-table columns exist before app startup.

This script is idempotent and intended to run during deployment.
"""

import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import create_engine, inspect, text


def _normalize_database_url(url: str) -> str:
    normalized = (url or "").strip()
    if normalized.startswith("mysql://"):
        normalized = normalized.replace("mysql://", "mysql+pymysql://", 1)

    parsed = urlsplit(normalized)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "charset" not in query:
        query["charset"] = "utf8mb4"

    return urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment)
    )


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
        return (
            f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            "?charset=utf8mb4"
        )

    raise RuntimeError(
        "Missing database config. Set DATABASE_URL or DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME."
    )


def _ensure_columns(engine) -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        print("[ensure_user_columns] users table not found; skipping.")
        return

    existing = {col["name"] for col in inspector.get_columns("users")}
    required = {
        "streak_count": "ALTER TABLE users ADD COLUMN streak_count INT NOT NULL DEFAULT 0",
        "longest_streak": "ALTER TABLE users ADD COLUMN longest_streak INT NOT NULL DEFAULT 0",
        "last_active_date": "ALTER TABLE users ADD COLUMN last_active_date DATE NULL",
    }

    with engine.begin() as conn:
        for column_name, ddl in required.items():
            if column_name in existing:
                continue
            print(f"[ensure_user_columns] adding missing column: {column_name}")
            conn.execute(text(ddl))

        if "streak_count" in required and "longest_streak" in required:
            conn.execute(
                text(
                    "UPDATE users "
                    "SET streak_count = COALESCE(streak_count, daily_streak, 0), "
                    "longest_streak = GREATEST(COALESCE(longest_streak, 0), COALESCE(daily_streak, 0))"
                )
            )


def main() -> None:
    database_url = _get_database_url()
    engine = create_engine(database_url, pool_pre_ping=True)
    _ensure_columns(engine)
    print("[ensure_user_columns] completed")


if __name__ == "__main__":
    main()
