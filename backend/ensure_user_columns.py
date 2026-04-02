"""Ensure required users-table columns exist before app startup.

This script is idempotent and intended to run during deployment.
"""

from sqlalchemy import inspect, text

from db_connection import create_mysql_engine, run_with_retry


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


def _ensure_columns_once() -> None:
    engine = create_mysql_engine()
    try:
        _ensure_columns(engine)
        print("[ensure_user_columns] completed")
    except Exception:
        engine.dispose()
        raise


def main() -> None:
    run_with_retry(_ensure_columns_once, "ensure_user_columns")


if __name__ == "__main__":
    main()
