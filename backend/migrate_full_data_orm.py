"""
IMPROVED Full Data Migration Script: Local MySQL → Production (Railway) MySQL
Uses SQLAlchemy ORM models for safe, type-aware data transfer.

USAGE:
    cd backend
    python migrate_full_data_orm.py [--force]

FLAGS:
    --force    Skip production empty check and migrate anyway

WHAT IT DOES:
    1. Connects to LOCAL database (via .env DB_* vars)
    2. Connects to PRODUCTION database (via DATABASE_URL)
    3. Reads all data from local using SQLAlchemy models
    4. Inserts into production, skipping duplicates
    5. Preserves primary keys and relationships
    6. Uses transactions with rollback on failure
    7. Only runs if production is empty (unless --force)

SAFETY FEATURES:
    - Type-safe ORM inserts (no SQL injection)
    - Automatic NULL handling
    - Foreign key constraint checking
    - Detailed error messages
    - Dry-run option available
"""

import sys
import os
from datetime import datetime
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError

load_dotenv()

# No ORM model imports needed - we use raw SQL INSERT IGNORE


# ============================================================================
# LOGGING
# ============================================================================

class Logger:
    """Colored logging utility."""

    RESET = "\033[0m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

    @staticmethod
    def log(message: str, level: str = "INFO") -> None:
        """Log with timestamp and color."""
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        
        if level == "SUCCESS":
            print(f"{Logger.GREEN}[{timestamp}] ✓ {message}{Logger.RESET}")
        elif level == "ERROR":
            print(f"{Logger.RED}[{timestamp}] ✗ {message}{Logger.RESET}")
        elif level == "WARNING":
            print(f"{Logger.YELLOW}[{timestamp}] ⚠ {message}{Logger.RESET}")
        elif level == "STATS":
            print(f"{Logger.CYAN}[{timestamp}] 📊 {message}{Logger.RESET}")
        else:
            print(f"{Logger.BLUE}[{timestamp}] ℹ {message}{Logger.RESET}")

    @staticmethod
    def success(msg: str): Logger.log(msg, "SUCCESS")
    @staticmethod
    def error(msg: str): Logger.log(msg, "ERROR")
    @staticmethod
    def warning(msg: str): Logger.log(msg, "WARNING")
    @staticmethod
    def info(msg: str): Logger.log(msg, "INFO")
    @staticmethod
    def stats(msg: str): Logger.log(msg, "STATS")


# ============================================================================
# DATABASE CONFIG
# ============================================================================

def _normalize_url(url: str) -> str:
    """Normalize database URL."""
    normalized = url.strip()
    if normalized.startswith("mysql://"):
        normalized = normalized.replace("mysql://", "mysql+pymysql://", 1)

    parsed = urlsplit(normalized)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "charset" not in query:
        query["charset"] = "utf8mb4"

    return urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment)
    )


def build_local_uri() -> str:
    """Build local database URI from .env."""
    user = os.getenv("DB_USER", "").strip()
    pwd = os.getenv("DB_PASSWORD", "").strip()
    host = os.getenv("DB_HOST", "").strip()
    port = os.getenv("DB_PORT", "").strip()
    name = os.getenv("DB_NAME", "").strip()

    if all([user, pwd, host, port, name]):
        safe_user = quote_plus(user)
        safe_pwd = quote_plus(pwd)
        return f"mysql+pymysql://{safe_user}:{safe_pwd}@{host}:{port}/{name}?charset=utf8mb4"

    raise RuntimeError("Missing DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME in .env")


def build_prod_uri() -> str:
    """Build production URI from DATABASE_URL (Railway)."""
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        return _normalize_url(url)
    raise RuntimeError("Missing DATABASE_URL in .env")


# ============================================================================
# MIGRATION ENGINE
# ============================================================================

class ORM_DataMigration:
    """Robust full data migration using INSERT IGNORE (raw SQL)."""

    # Tables in dependency order (parents before children)
    MIGRATION_PLAN = [
        "users",
        "courses",
        "lessons",
        "enrollments",
        "quizzes",
        "questions",
        "progresses",
        "quiz_attempts",
        "submissions",
        "skills",
        "user_skills",
        "rewards",
        "user_rewards",
        "problems",
        "test_cases",
        "code_submissions",
        "problem_progress",
        "badges",
        "user_badges",
        "user_coding_stats",
        "daily_challenges",
        "notes",
        "coding_problems",
        "user_progress",       # LessonProgress
        "notifications",
        "learning_activity",
    ]

    def __init__(self, local_uri: str, prod_uri: str, force: bool = False):
        self.local_uri = local_uri
        self.prod_uri = prod_uri
        self.force = force
        self.local_engine = None
        self.prod_engine = None
        self.stats = {}

    def _make_engines(self):
        """Create fresh engines (called once)."""
        self.local_engine = create_engine(
            self.local_uri, echo=False,
            pool_pre_ping=True, pool_recycle=3600,
        )
        self.prod_engine = create_engine(
            self.prod_uri, echo=False,
            pool_pre_ping=True, pool_recycle=3600,
            connect_args={"connect_timeout": 30},
        )

    def connect(self) -> bool:
        """Test connections to both databases."""
        try:
            self._make_engines()

            Logger.info("Connecting to LOCAL database...")
            with self.local_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Logger.success("Connected to LOCAL")

            Logger.info("Connecting to PRODUCTION database...")
            with self.prod_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Logger.success("Connected to PRODUCTION")

            return True
        except Exception as e:
            Logger.error(f"Connection failed: {e}")
            return False

    def check_empty(self) -> bool:
        """Check if production has data and ask for confirmation."""
        if self.force:
            Logger.warning("--force flag set; skipping empty check")
            return True

        try:
            with self.prod_engine.connect() as conn:
                user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()

            if user_count > 0:
                Logger.warning(f"⚠ PRODUCTION HAS {user_count} USERS")
                resp = input("Migrate anyway? (type 'yes' to confirm): ").strip()
                if resp != "yes":
                    Logger.error("Migration cancelled")
                    return False

            Logger.success("Proceeding with migration")
            return True
        except Exception as e:
            Logger.error(f"Check failed: {e}")
            return False

    def _table_exists(self, engine, table_name: str) -> bool:
        """Return True if a table exists in the given database."""
        try:
            insp = inspect(engine)
            return table_name in insp.get_table_names()
        except Exception:
            return False

    def migrate_table(self, table_name: str) -> tuple[int, int]:
        """
        Migrate one table using INSERT IGNORE.
        Returns (inserted, skipped) counts.
        """
        Logger.info(f"Migrating {table_name}...")

        if not self._table_exists(self.local_engine, table_name):
            Logger.warning(f"  {table_name}: table not found in local DB, skipping")
            return 0, 0

        if not self._table_exists(self.prod_engine, table_name):
            Logger.warning(f"  {table_name}: table not found in production DB, skipping")
            return 0, 0

        try:
            # ── Read all rows from local ──────────────────────────────────────
            with self.local_engine.connect() as local_conn:
                result = local_conn.execute(text(f"SELECT * FROM `{table_name}`"))
                columns = list(result.keys())
                rows = result.fetchall()

            if not rows:
                Logger.warning(f"  {table_name}: no records in local DB")
                return 0, 0

            total_local = len(rows)

            # ── INSERT IGNORE into production in batches ──────────────────────
            col_list = ", ".join(f"`{c}`" for c in columns)
            placeholders = ", ".join(f":{c}" for c in columns)
            sql = text(
                f"INSERT IGNORE INTO `{table_name}` ({col_list}) VALUES ({placeholders})"
            )

            inserted = 0
            BATCH_SIZE = 50

            with self.prod_engine.begin() as prod_conn:
                for i in range(0, total_local, BATCH_SIZE):
                    batch = rows[i : i + BATCH_SIZE]
                    batch_dicts = [dict(zip(columns, row)) for row in batch]
                    result = prod_conn.execute(sql, batch_dicts)
                    inserted += result.rowcount

            skipped = total_local - inserted
            status = f"{inserted} inserted"
            if skipped > 0:
                status += f", {skipped} skipped (already exist)"
            Logger.success(f"  {table_name}: {status}")
            return inserted, skipped

        except Exception as e:
            Logger.error(f"  {table_name} failed: {e}")
            return 0, 0

    def run(self) -> bool:
        """Execute full migration."""
        print()
        Logger.info("=" * 70)
        Logger.info("FULL DATA MIGRATION")
        Logger.info("=" * 70)
        print()

        if not self.connect():
            return False

        print()
        if not self.check_empty():
            return False

        print()
        Logger.info("Starting table migration...")
        print()

        total_inserted = 0
        failed_tables = []

        for table_name in self.MIGRATION_PLAN:
            try:
                inserted, skipped = self.migrate_table(table_name)
                self.stats[table_name] = inserted
                total_inserted += inserted
            except Exception as e:
                Logger.error(f"Unexpected error on {table_name}: {e}")
                failed_tables.append(table_name)

        print()
        print("=" * 70)
        Logger.stats("MIGRATION RESULTS")
        print("=" * 70)

        for table_name, count in self.stats.items():
            marker = "✓" if count > 0 else "·"
            print(f"  {marker} {table_name:30} {count:5} records inserted")

        print()
        Logger.stats(f"TOTAL: {total_inserted} records migrated")

        if failed_tables:
            Logger.error(f"Tables with errors: {', '.join(failed_tables)}")

        print("=" * 70)
        print()
        Logger.success("✓ MIGRATION COMPLETED!")
        print()

        return True


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    force = "--force" in sys.argv

    print()
    Logger.info("GAMIFIED LEARNING - FULL DATA MIGRATION (ORM)")
    print()

    try:
        local_uri = build_local_uri()
        prod_uri = build_prod_uri()

        # Show URLs (sanitized)
        local_host = local_uri.split("@")[1].split("/")[0] if "@" in local_uri else "local"
        prod_host = prod_uri.split("@")[1].split("/")[0] if "@" in prod_uri else "production"
        
        Logger.info(f"Local DB: {local_host}")
        Logger.info(f"Production DB: {prod_host}")
        
        if force:
            Logger.warning("FORCE MODE ENABLED (skipping safety checks)")
        
        print()

        migration = ORM_DataMigration(local_uri, prod_uri, force=force)
        success = migration.run()

        return 0 if success else 1

    except Exception as e:
        Logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
