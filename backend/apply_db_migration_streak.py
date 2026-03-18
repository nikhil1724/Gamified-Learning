from sqlalchemy import text

from app import create_app
from database import db


def _column_exists(table_name: str, column_name: str) -> bool:
    result = db.session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :table_name
              AND COLUMN_NAME = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).scalar()
    return bool(result)


def migrate_streak_schema() -> None:
    if not _column_exists("users", "streak_count"):
        db.session.execute(
            text("ALTER TABLE users ADD COLUMN streak_count INT NOT NULL DEFAULT 0")
        )

    if not _column_exists("users", "longest_streak"):
        db.session.execute(
            text("ALTER TABLE users ADD COLUMN longest_streak INT NOT NULL DEFAULT 0")
        )

    if not _column_exists("users", "last_active_date"):
        db.session.execute(
            text("ALTER TABLE users ADD COLUMN last_active_date DATE NULL")
        )

    db.session.execute(
        text(
            """
            UPDATE users
            SET streak_count = COALESCE(streak_count, daily_streak, 0),
                longest_streak = GREATEST(COALESCE(longest_streak, 0), COALESCE(daily_streak, 0))
            """
        )
    )

    db.session.commit()
    print("Streak schema migration complete.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        migrate_streak_schema()
