from flask import Blueprint, jsonify


user_bp = Blueprint("users", __name__, url_prefix="/api/users")


@user_bp.get("/health")
def users_health():
    return jsonify({"status": "ok"})
