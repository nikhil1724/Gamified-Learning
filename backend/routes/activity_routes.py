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
