from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from adaptive_engine import analyze_user_performance
from models import User


recommendation_bp = Blueprint("recommendations", __name__, url_prefix="/api")


@recommendation_bp.get("/recommendations")
@jwt_required()
def get_recommendations():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = analyze_user_performance(user_id)
    return jsonify(data)
