from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from activity_service import record_learning_activity
from models import User


activity_bp = Blueprint("activity", __name__, url_prefix="/api")


@activity_bp.post("/activity")
@jwt_required()
def mark_learning_activity():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    result = record_learning_activity(user_id)
    return jsonify(result), 200


@activity_bp.get("/streak")
@jwt_required()
def get_streak_status():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(
        {
            "current_streak": user.streak_count,
            "longest_streak": user.longest_streak,
            "last_active_date": user.last_active_date.isoformat()
            if user.last_active_date
            else None,
        }
    ), 200
