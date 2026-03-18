from flask import Blueprint, jsonify

from leaderboard_service import get_cached_leaderboard


leaderboard_bp = Blueprint("leaderboard", __name__, url_prefix="/api")


@leaderboard_bp.get("/leaderboard")
def get_leaderboard():
    return jsonify(get_cached_leaderboard())
