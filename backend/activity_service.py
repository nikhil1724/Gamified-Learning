from datetime import date, datetime

from database import db
from models import LearningActivity, User


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


def record_learning_activity(user_id: int, activity_dt: datetime | None = None) -> dict:
    now = activity_dt or datetime.utcnow()
    activity_day = now.date()

    existing = LearningActivity.query.filter_by(
        user_id=user_id,
        activity_date=activity_day,
    ).first()

    inserted = False
    if not existing:
        db.session.add(LearningActivity(user_id=user_id, activity_date=activity_day))
        db.session.flush()
        inserted = True

    streak = calculate_learning_streak(user_id)

    user = User.query.get(user_id)
    if user:
        user.daily_streak = streak
        user.last_daily_completed_at = now

    db.session.commit()

    return {
        "activity_recorded": inserted,
        "activity_date": activity_day.isoformat(),
        "streak_days": streak,
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
