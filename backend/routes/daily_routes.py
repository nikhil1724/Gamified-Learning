from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db
from models import DailyChallenge, Quiz, User


daily_bp = Blueprint("daily", __name__, url_prefix="/api")

DAILY_BONUS_XP = 50


def _random_quiz():
    dialect = db.session.bind.dialect.name if db.session.bind else ""
    if dialect == "mysql":
        return Quiz.query.order_by(db.func.rand()).first()
    return Quiz.query.order_by(db.func.random()).first()


def _get_or_create_daily() -> DailyChallenge | None:
    today = date.today()
    daily = DailyChallenge.query.filter_by(date=today).first()
    if daily:
        return daily

    quiz = _random_quiz()
    if not quiz:
        return None

    daily = DailyChallenge(date=today, quiz_id=quiz.id)
    db.session.add(daily)
    db.session.commit()
    return daily


@daily_bp.get("/daily-challenge")
def get_daily_challenge():
    daily = _get_or_create_daily()
    if not daily:
        return jsonify({"error": "No quizzes available"}), 404

    quiz = daily.quiz
    return jsonify(
        {
            "date": daily.date.isoformat(),
            "quiz": {
                "id": quiz.id,
                "title": quiz.title,
                "topic": quiz.topic,
                "difficulty": quiz.difficulty,
            },
        }
    )


@daily_bp.get("/daily-challenge/status")
@jwt_required()
def get_daily_status():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    completed_today = False
    if user.last_daily_completed_at:
        completed_today = user.last_daily_completed_at.date() == date.today()

    return jsonify(
        {
            "daily_streak": user.daily_streak,
            "completed_today": completed_today,
            "last_completed_at": user.last_daily_completed_at.isoformat()
            if user.last_daily_completed_at
            else None,
            "bonus_xp": DAILY_BONUS_XP,
        }
    )


@daily_bp.post("/daily-challenge/complete")
@jwt_required()
def complete_daily_challenge():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    now = datetime.utcnow()
    today = date.today()

    if user.last_daily_completed_at and user.last_daily_completed_at.date() == today:
        return jsonify({"message": "Daily challenge already completed"}), 200

    if not user.last_daily_completed_at:
        user.daily_streak = 1
    else:
        yesterday = today - timedelta(days=1)
        if user.last_daily_completed_at.date() == yesterday:
            user.daily_streak += 1
        else:
            user.daily_streak = 1

    user.last_daily_completed_at = now
    user.xp_points += DAILY_BONUS_XP

    db.session.commit()

    return jsonify(
        {
            "message": "Daily challenge completed",
            "daily_streak": user.daily_streak,
            "bonus_xp": DAILY_BONUS_XP,
        }
    )
