from flask import Blueprint, jsonify

from models import User


leaderboard_bp = Blueprint("leaderboard", __name__, url_prefix="/api")


@leaderboard_bp.get("/leaderboard")
def get_leaderboard():
    users = (
        User.query.filter_by(role="student")
        .order_by(User.xp_points.desc(), User.coins.desc())
        .limit(10)
        .all()
    )

    if not users:
        return jsonify([])

    leaderboard = [
        {
            "rank": index + 1,
            "id": user.id,
            "name": user.name,
            "level": user.level,
            "xp_points": user.xp_points,
            "coins": user.coins,
        }
        for index, user in enumerate(users)
    ]

    return jsonify(leaderboard)
