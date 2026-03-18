"""
BONUS: Leaderboard Seeding Script
Seeds leaderboard-style data (user stats, XP, level progression) into existing users.

USAGE:
    python seed_leaderboard_data.py

DESCRIPTION:
    - Assigns random XP points to existing users (500-5000)
    - Assigns random levels (1-10)
    - Assigns random coins (100-1000)
    - Creates random daily streaks
    - Assigns random UserCodingStats
    - Ensures demo users have higher scores

REQUIREMENTS:
    - Database must have USERS already populated
    - Run AFTER full data migration
"""

import sys
import os
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))
from models import db, User, UserCodingStats


# ============================================================================
# DATABASE CONFIG (shared with migration script)
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


def build_db_uri() -> str:
    """Build database URI (prefers DATABASE_URL, falls back to local)."""
    direct = os.getenv("DATABASE_URL", "").strip()
    if direct:
        return _normalize_url(direct)

    # Fall back to local
    user = os.getenv("DB_USER", "").strip()
    pwd = os.getenv("DB_PASSWORD", "").strip()
    host = os.getenv("DB_HOST", "").strip()
    port = os.getenv("DB_PORT", "").strip()
    name = os.getenv("DB_NAME", "").strip()

    if all([user, pwd, host, port, name]):
        safe_user = quote_plus(user)
        safe_pwd = quote_plus(pwd)
        return f"mysql+pymysql://{safe_user}:{safe_pwd}@{host}:{port}/{name}?charset=utf8mb4"

    raise RuntimeError("Missing database config")


# ============================================================================
# SEEDING LOGIC
# ============================================================================

DEMO_USERS = {
    "admin@lms.com": {"xp": 8000, "level": 8, "coins": 2000, "streak": 15},
    "john@lms.com": {"xp": 6500, "level": 7, "coins": 1500, "streak": 12},
    "priya@lms.com": {"xp": 7200, "level": 7, "coins": 1800, "streak": 14},
    "rahul@student.com": {"xp": 5000, "level": 6, "coins": 1000, "streak": 10},
    "anita@student.com": {"xp": 4800, "level": 5, "coins": 950, "streak": 8},
}


def seed_user_stats(engine):
    """Seed leaderboard-style data into users."""
    print("\n[LEADERBOARD SEEDING]")
    print("=" * 60)

    session = Session(engine)

    try:
        users = session.query(User).all()
        
        if not users:
            print("✗ No users found in database")
            return False

        print(f"✓ Found {len(users)} users")
        print()

        seeded_count = 0

        for user in users:
            # Check if user has existing stats
            if user.xp_points and user.xp_points > 0:
                print(f"  ⊘ {user.email}: already has stats (xp={user.xp_points}), skipping")
                continue

            # Check if demo user (assign fixed values)
            if user.email in DEMO_USERS:
                stats = DEMO_USERS[user.email]
                user.xp_points = stats["xp"]
                user.level = stats["level"]
                user.coins = stats["coins"]
                user.daily_streak = stats["streak"]
                user.last_daily_completed_at = datetime.utcnow() - timedelta(days=1)
                print(f"  ✓ {user.email}: DEMO USER (xp={stats['xp']}, level={stats['level']}, coins={stats['coins']})")
            else:
                # Random stats for regular users
                user.xp_points = random.randint(500, 5000)
                user.level = random.randint(1, 10)
                user.coins = random.randint(100, 1000)
                user.daily_streak = random.randint(0, 20)
                if user.daily_streak > 0:
                    user.last_daily_completed_at = datetime.utcnow() - timedelta(days=1)
                print(f"  ✓ {user.email}: xp={user.xp_points}, level={user.level}, coins={user.coins}, streak={user.daily_streak}")

            session.add(user)
            seeded_count += 1

        session.commit()
        print()
        print(f"✓ Seeded {seeded_count} users with leaderboard stats")
        print()

        # Also seed UserCodingStats if not exists
        print("Seeding UserCodingStats...")
        
        coding_stats_count = 0
        for user in users:
            # Check if already has stats
            if session.query(UserCodingStats).filter_by(user_id=user.id).first():
                continue

            # Create stats
            stats = UserCodingStats(
                user_id=user.id,
                solved_count=random.randint(0, 50),
                streak_days=random.randint(0, 30),
                last_solved_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)) if random.random() > 0.5 else None
            )
            session.add(stats)
            coding_stats_count += 1

        session.commit()
        print(f"✓ Seeded {coding_stats_count} UserCodingStats records")
        print()

        session.close()
        return True

    except Exception as e:
        session.rollback()
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    print()
    print("=" * 60)
    print("GAMIFIED LEARNING - LEADERBOARD SEEDING")
    print("=" * 60)
    print()

    try:
        uri = build_db_uri()
        engine = create_engine(uri, echo=False)

        # Test connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")

        success = seed_user_stats(engine)

        if success:
            print("=" * 60)
            print("✓ LEADERBOARD SEEDING COMPLETED")
            print("=" * 60)
            print()
            return 0
        else:
            return 1

    except Exception as e:
        print(f"✗ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
