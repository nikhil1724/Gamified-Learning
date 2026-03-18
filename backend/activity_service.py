from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from database import db
from models import LearningActivity, User


def _resolve_timezone(user_timezone: str | None):
    tz_name = (user_timezone or "").strip()
    if not tz_name:
        return timezone.utc

    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        return timezone.utc


def _normalize_utc_datetime(activity_dt: datetime | None = None) -> datetime:
    if activity_dt is None:
        return datetime.now(timezone.utc)

    if activity_dt.tzinfo is None:
        return activity_dt.replace(tzinfo=timezone.utc)

    return activity_dt.astimezone(timezone.utc)


def update_user_streak(
    user: User,
    activity_dt: datetime | None = None,
    user_timezone: str | None = None,
) -> dict:
    now_utc = _normalize_utc_datetime(activity_dt)
    tz_info = _resolve_timezone(user_timezone)
    activity_day = now_utc.astimezone(tz_info).date()

    previous_day = user.last_active_date
    current_streak = user.streak_count or 0

    if previous_day is None:
        current_streak = 1
    elif previous_day == activity_day:
        current_streak = max(current_streak, 1)
    elif previous_day == (activity_day - timedelta(days=1)):
        current_streak += 1
    else:
        current_streak = 1

    user.streak_count = current_streak
    user.daily_streak = current_streak
    user.last_active_date = activity_day
    user.longest_streak = max(user.longest_streak or 0, current_streak)

    return {
        "current_streak": user.streak_count,
        "longest_streak": user.longest_streak,
        "last_active_date": user.last_active_date.isoformat() if user.last_active_date else None,
    }


def calculate_learning_streak(user_id: int) -> int:
    activity_dates = [
        row.activity_date
        for row in LearningActivity.query.filter_by(user_id=user_id)
        .order_by(LearningActivity.activity_date.desc())
        .all()
    ]

    if not activity_dates:
        return 0

    today = date.today()
    latest = activity_dates[0]

    # If the latest activity is older than yesterday, streak is broken.
    if (today - latest).days > 1:
        return 0

    streak = 1
    previous = latest

    for current in activity_dates[1:]:
        gap = (previous - current).days
        if gap == 0:
            # Defensive skip for duplicates; DB uniqueness should already prevent this.
            continue
        if gap == 1:
            streak += 1
            previous = current
            continue
        break

    return streak


def record_learning_activity(
    user_id: int,
    activity_dt: datetime | None = None,
    user_timezone: str | None = None,
    auto_commit: bool = True,
) -> dict:
    now_utc = _normalize_utc_datetime(activity_dt)
    activity_day = now_utc.date()

    existing = LearningActivity.query.filter_by(
        user_id=user_id,
        activity_date=activity_day,
    ).first()

    inserted = False
    if not existing:
        db.session.add(LearningActivity(user_id=user_id, activity_date=activity_day))
        db.session.flush()
        inserted = True

    user = User.query.get(user_id)
    streak_info = {
        "current_streak": 0,
        "longest_streak": 0,
        "last_active_date": None,
    }
    if user:
        streak_info = update_user_streak(
            user=user,
            activity_dt=now_utc,
            user_timezone=user_timezone,
        )
        user.last_daily_completed_at = now_utc.replace(tzinfo=None)

    if auto_commit:
        db.session.commit()

    return {
        "activity_recorded": inserted,
        "activity_date": activity_day.isoformat(),
        "streak_days": streak_info["current_streak"],
        "longest_streak": streak_info["longest_streak"],
        "last_active_date": streak_info["last_active_date"],
    }


def get_recent_learning_activity(user_id: int, days: int = 7) -> list[dict]:
    end_day = date.today()
    start_day = end_day.fromordinal(end_day.toordinal() - (days - 1))

    rows = LearningActivity.query.filter(
        LearningActivity.user_id == user_id,
        LearningActivity.activity_date >= start_day,
        LearningActivity.activity_date <= end_day,
    ).all()

    active_dates = {row.activity_date for row in rows}

    timeline = []
    for offset in range(days):
        current = start_day.fromordinal(start_day.toordinal() + offset)
        timeline.append(
            {
                "date": current.isoformat(),
                "label": current.strftime("%a"),
                "active": current in active_dates,
            }
        )

    return timeline
