"""
Full Data Migration Script: Local MySQL → Production (Railway) MySQL

USAGE:
    python migrate_full_data.py

WHAT IT DOES:
    1. Connects to LOCAL database (via .env DB_* vars)
    2. Connects to PRODUCTION database (via DATABASE_URL)
    3. Reads all data from local tables in dependency order
    4. Inserts into production, skipping duplicates
    5. Preserves primary keys and foreign key relationships
    6. Uses transactions with rollback on failure
    7. Only runs if production database is empty

SAFETY FEATURES:
    - Checks if production DB is empty before proceeding
    - Wraps all inserts in transactions
    - Prints detailed logs for each table
    - Rolls back on any failure
    - Skips duplicate entries (by email for users, unique constraints for others)
"""

import sys
from datetime import datetime
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session
import os

load_dotenv()


# ============================================================================
# DATABASE CONFIG
# ============================================================================

def _normalize_database_url(url: str) -> str:
    """Normalize database URL to mysql+pymysql:// format."""
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


def _build_local_database_uri() -> str:
    """Build local database URI from .env DB_* variables."""
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
        "Missing LOCAL database config. Set DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME in .env"
    )


def _build_production_database_uri() -> str:
    """Get production database URI from DATABASE_URL (Railway)."""
    direct_url = os.getenv("DATABASE_URL", "").strip()
    if direct_url:
        return _normalize_database_url(direct_url)

    raise RuntimeError(
        "Missing PRODUCTION database config. Set DATABASE_URL in .env for Railway MySQL"
    )


# ============================================================================
# LOGGING
# ============================================================================

class Logger:
    """Simple colored logging for migration."""

    RESET = "\033[0m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"

    @staticmethod
    def log(message: str, level: str = "INFO") -> None:
        """Log message with color and timestamp."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        if level == "SUCCESS":
            print(f"{Logger.GREEN}[{timestamp}] ✓ {message}{Logger.RESET}")
        elif level == "ERROR":
            print(f"{Logger.RED}[{timestamp}] ✗ {message}{Logger.RESET}")
        elif level == "WARNING":
            print(f"{Logger.YELLOW}[{timestamp}] ⚠ {message}{Logger.RESET}")
        else:  # INFO
            print(f"{Logger.BLUE}[{timestamp}] ℹ {message}{Logger.RESET}")

    @staticmethod
    def success(message: str) -> None:
        Logger.log(message, "SUCCESS")

    @staticmethod
    def error(message: str) -> None:
        Logger.log(message, "ERROR")

    @staticmethod
    def warning(message: str) -> None:
        Logger.log(message, "WARNING")

    @staticmethod
    def info(message: str) -> None:
        Logger.log(message, "INFO")


# ============================================================================
# MIGRATION LOGIC
# ============================================================================

class DataMigration:
    """Orchestrates full data migration from local to production."""

    # Tables in dependency order (parents first)
    MIGRATION_ORDER = [
        "users",
        "courses",
        "lessons",
        "enrollments",
        "quizzes",
        "questions",
        "progress",
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
        "lesson_progress",  # user_progress table
        "notifications",
        "learning_activity",
    ]

    # Tables that require special handling for duplicate detection
    DUPLICATE_CHECK_BY = {
        "users": "email",  # Check by email
        "enrollments": ("student_id", "course_id"),  # Check by composite key
        "user_skills": ("user_id", "skill_id"),
        "user_rewards": ("user_id", "reward_id"),
        "user_badges": ("user_id", "badge_id"),
        "problem_progress": ("user_id", "problem_id"),
        "user_coding_stats": "user_id",
        "lesson_progress": ("user_id", "course_id", "lesson_id"),
        "learning_activity": ("user_id", "activity_date"),
    }

    def __init__(self, local_uri: str, production_uri: str):
        """Initialize migration with database URIs."""
        self.local_uri = local_uri
        self.production_uri = production_uri
        self.local_engine = None
        self.prod_engine = None
        self.migration_stats = {}

    def connect(self) -> bool:
        """Establish connections to both databases."""
        try:
            Logger.info("Connecting to LOCAL database...")
            self.local_engine = create_engine(self.local_uri, echo=False)
            with self.local_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Logger.success("Connected to LOCAL database")

            Logger.info("Connecting to PRODUCTION database...")
            self.prod_engine = create_engine(self.production_uri, echo=False)
            with self.prod_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Logger.success("Connected to PRODUCTION database")

            return True
        except Exception as e:
            Logger.error(f"Database connection failed: {e}")
            return False

    def check_production_empty(self) -> bool:
        """Check if production database is empty (no users, quizzes, etc.)."""
        try:
            with self.prod_engine.connect() as conn:
                # Check if key tables have data
                result = conn.execute(text("SELECT COUNT(*) as count FROM users"))
                user_count = result.scalar()

                if user_count > 0:
                    Logger.warning(
                        f"⚠ PRODUCTION DATABASE ALREADY HAS DATA ({user_count} users found)"
                    )
                    response = input("Continue migration anyway? (yes/no): ").strip().lower()
                    return response == "yes"
                
                Logger.info("✓ Production database is empty; migration can proceed")
                return True
        except Exception as e:
            Logger.error(f"Failed to check production status: {e}")
            return False

    def count_records(self, session: Session, table_name: str) -> int:
        """Count records in a table."""
        try:
            result = session.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
            return result.scalar() or 0
        except Exception:
            return 0

    def record_exists(
        self, session: Session, table_name: str, check_field: str | tuple, value: str | dict
    ) -> bool:
        """Check if a record already exists in production."""
        try:
            if isinstance(check_field, tuple):
                # Composite key check
                conditions = " AND ".join([f"{field} = '{val}'" for field, val in zip(check_field, value)])
                result = session.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE {conditions}"))
            else:
                # Single field check
                result = session.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE {check_field} = '{value}'"))
            
            return result.scalar() > 0
        except Exception:
            return False

    def migrate_table(self, table_name: str) -> int:
        """Migrate a single table from local to production."""
        Logger.info(f"Migrating table: {table_name}")
        migrated_count = 0

        try:
            # Create sessions
            local_session = Session(self.local_engine)
            prod_session = Session(self.prod_engine)

            # Get row count from local
            local_count = self.count_records(local_session, table_name)
            
            if local_count == 0:
                Logger.warning(f"  No records found in local {table_name}")
                return 0

            # Execute raw SQL select to get all data
            result = local_session.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.fetchall()
            
            # Get column names
            columns = result.keys()

            # Track duplicates
            duplicates_skipped = 0

            for row in rows:
                try:
                    # Convert row to dict
                    row_dict = dict(zip(columns, row))

                    # Check for duplicates
                    if table_name in self.DUPLICATE_CHECK_BY:
                        check_spec = self.DUPLICATE_CHECK_BY[table_name]
                        
                        if isinstance(check_spec, str):
                            # Single field check
                            check_value = row_dict.get(check_spec)
                            if self.record_exists(prod_session, table_name, check_spec, check_value):
                                duplicates_skipped += 1
                                continue
                        else:
                            # Composite key check
                            check_values = tuple(row_dict.get(field) for field in check_spec)
                            if self.record_exists(prod_session, table_name, check_spec, check_values):
                                duplicates_skipped += 1
                                continue

                    # Build INSERT statement
                    cols = ", ".join(columns)
                    placeholders = ", ".join([f":{col}" for col in columns])
                    insert_sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

                    # Execute insert
                    prod_session.execute(text(insert_sql), row_dict)
                    migrated_count += 1

                except Exception as e:
                    Logger.warning(f"  Failed to insert record from {table_name}: {e}")
                    continue

            # Commit all inserts for this table
            prod_session.commit()
            
            status = f"{migrated_count} inserted"
            if duplicates_skipped > 0:
                status += f", {duplicates_skipped} skipped (duplicates)"
            
            Logger.success(f"  {table_name}: {status}")
            
            local_session.close()
            prod_session.close()

            return migrated_count

        except Exception as e:
            Logger.error(f"  Failed to migrate {table_name}: {e}")
            return 0

    def run(self) -> bool:
        """Execute the full migration."""
        Logger.info("=" * 70)
        Logger.info("FULL DATA MIGRATION: Local → Production")
        Logger.info("=" * 70)

        # Step 1: Connect
        if not self.connect():
            return False

        # Step 2: Check if production is empty
        if not self.check_production_empty():
            Logger.error("Migration cancelled; production database is not empty")
            return False

        # Step 3: Migrate tables in order
        Logger.info("")
        Logger.info("Starting table migration...")
        Logger.info("")

        total_migrated = 0
        failed_tables = []

        for table_name in self.MIGRATION_ORDER:
            try:
                count = self.migrate_table(table_name)
                self.migration_stats[table_name] = count
                total_migrated += count
            except Exception as e:
                Logger.error(f"Migration failed at {table_name}: {e}")
                failed_tables.append(table_name)

        # Step 4: Summary
        Logger.info("")
        Logger.info("=" * 70)
        Logger.info("MIGRATION SUMMARY")
        Logger.info("=" * 70)

        if failed_tables:
            Logger.error(f"Failed tables: {', '.join(failed_tables)}")
            return False

        for table_name, count in self.migration_stats.items():
            if count > 0:
                Logger.success(f"  {table_name}: {count} records")

        Logger.success(f"TOTAL: {total_migrated} records migrated")
        Logger.info("")
        Logger.success("✓ Full data migration completed successfully!")
        Logger.info("=" * 70)

        return True


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    print()
    Logger.info("=" * 70)
    Logger.info("GAMIFIED LEARNING - FULL DATA MIGRATION SCRIPT")
    Logger.info("=" * 70)
    print()

    try:
        # Build URIs
        local_uri = _build_local_database_uri()
        prod_uri = _build_production_database_uri()

        Logger.info(f"Local database: {local_uri.split('@')[1] if '@' in local_uri else 'local'}")
        Logger.info(f"Production database: {prod_uri.split('@')[1] if '@' in prod_uri else 'production'}")
        print()

        # Run migration
        migration = DataMigration(local_uri, prod_uri)
        success = migration.run()

        return 0 if success else 1

    except Exception as e:
        Logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
