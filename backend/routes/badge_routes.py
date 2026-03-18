from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from badge_service import get_user_badges
from models import User


badge_bp = Blueprint("badges", __name__, url_prefix="/api")


@badge_bp.get("/badges")
@jwt_required()
def list_current_user_badges():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(get_user_badges(user_id)), 200
