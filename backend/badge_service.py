from datetime import datetime

from sqlalchemy import and_, func, or_
from sqlalchemy.exc import IntegrityError

from database import db
from models import Badge, Progress, User, UserBadge


BADGE_DEFINITIONS = [
    {
        "name": "First Login",
        "description": "Logged in for the first time.",
        "icon": "👋",
        "rule_type": "first_login",
        "rule_value": 1,
    },
    {
        "name": "First Quiz Completed",
        "description": "Completed your first quiz.",
        "icon": "📝",
        "rule_type": "first_quiz_completed",
        "rule_value": 1,
    },
    {
        "name": "Century XP",
        "description": "Reached 100 XP.",
        "icon": "💯",
        "rule_type": "xp_earned",
        "rule_value": 100,
    },
    {
        "name": "7-Day Streak",
        "description": "Maintained a 7-day streak.",
        "icon": "🔥",
        "rule_type": "streak_days",
        "rule_value": 7,
    },
    {
        "name": "Top 10 Leaderboard",
        "description": "Reached the top 10 on the leaderboard.",
        "icon": "🏆",
        "rule_type": "leaderboard_rank",
        "rule_value": 10,
    },
]


def ensure_badges() -> None:
    names = [definition["name"] for definition in BADGE_DEFINITIONS]
    existing = {badge.name: badge for badge in Badge.query.filter(Badge.name.in_(names)).all()}

    for definition in BADGE_DEFINITIONS:
        badge = existing.get(definition["name"])
        if not badge:
            db.session.add(Badge(**definition))
            continue

        # Keep descriptions/icons current as catalog evolves.
        badge.description = definition["description"]
        badge.icon = definition["icon"]
        badge.rule_type = definition["rule_type"]
        badge.rule_value = definition["rule_value"]


def _is_top_10(user: User) -> bool:
    if user.role != "student":
        return False

    higher_ranked = (
        db.session.query(func.count(User.id))
        .filter(User.role == "student")
        .filter(
            or_(
                User.xp_points > user.xp_points,
                and_(User.xp_points == user.xp_points, User.coins > user.coins),
            )
        )
        .scalar()
        or 0
    )

    return higher_ranked < 10


def _get_badge_catalog() -> dict[str, Badge]:
    names = [definition["name"] for definition in BADGE_DEFINITIONS]
    return {badge.name: badge for badge in Badge.query.filter(Badge.name.in_(names)).all()}


def _serialize_user_badge(user_badge: UserBadge) -> dict:
    badge = user_badge.badge
    return {
        "id": badge.id,
        "name": badge.name,
        "description": badge.description,
        "icon": badge.icon,
        "earned_at": user_badge.earned_at.isoformat(),
    }


def assign_eligible_badges(user: User, trigger: str | None = None) -> list[dict]:
    ensure_badges()

    badge_catalog = _get_badge_catalog()
    existing_badge_ids = {
        row.badge_id
        for row in db.session.query(UserBadge.badge_id).filter_by(user_id=user.id).all()
    }

    quiz_completed = (
        db.session.query(Progress.id)
        .filter(Progress.user_id == user.id)
        .limit(1)
        .scalar()
        is not None
    )

    conditions = {
        "First Login": trigger == "login",
        "First Quiz Completed": quiz_completed,
        "Century XP": (user.xp_points or 0) >= 100,
        "7-Day Streak": max(user.streak_count or 0, user.daily_streak or 0) >= 7,
        "Top 10 Leaderboard": _is_top_10(user),
    }

    unlocked: list[UserBadge] = []
    now = datetime.utcnow()

    for badge_name, is_eligible in conditions.items():
        if not is_eligible:
            continue

        badge = badge_catalog.get(badge_name)
        if not badge or badge.id in existing_badge_ids:
            continue

        assignment = UserBadge(user_id=user.id, badge_id=badge.id, earned_at=now)
        try:
            with db.session.begin_nested():
                db.session.add(assignment)
                db.session.flush()
            unlocked.append(assignment)
            existing_badge_ids.add(badge.id)
        except IntegrityError:
            # Another concurrent request may have inserted the same badge.
            continue

    return [_serialize_user_badge(user_badge) for user_badge in unlocked]


def get_user_badges(user_id: int) -> list[dict]:
    rows = (
        db.session.query(UserBadge)
        .filter(UserBadge.user_id == user_id)
        .join(Badge, Badge.id == UserBadge.badge_id)
        .order_by(UserBadge.earned_at.desc())
        .all()
    )
    return [_serialize_user_badge(row) for row in rows]
