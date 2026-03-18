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


def _column_exists(inspector, table_name: str, column_name: str) -> bool:
    if table_name not in inspector.get_table_names():
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _index_exists(inspector, table_name: str, index_name: str) -> bool:
    if table_name not in inspector.get_table_names():
        return False
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def migrate_badge_schema() -> None:
    engine = create_engine(_get_database_url(), pool_pre_ping=True)
    inspector = inspect(engine)

    with engine.begin() as conn:
        if not _column_exists(inspector, "badges", "icon"):
            conn.execute(text("ALTER TABLE badges ADD COLUMN icon VARCHAR(32) NULL"))

        if not _index_exists(inspector, "badges", "uq_badges_name"):
            conn.execute(text("ALTER TABLE badges ADD CONSTRAINT uq_badges_name UNIQUE (name)"))

        if not _index_exists(inspector, "user_badges", "uq_user_badges_user_badge"):
            conn.execute(
                text(
                    "ALTER TABLE user_badges ADD CONSTRAINT uq_user_badges_user_badge UNIQUE (user_id, badge_id)"
                )
            )

        if not _index_exists(inspector, "user_badges", "idx_user_badges_user_earned"):
            conn.execute(
                text("CREATE INDEX idx_user_badges_user_earned ON user_badges(user_id, earned_at)")
            )

    print("Badge schema migration complete.")


if __name__ == "__main__":
    migrate_badge_schema()
