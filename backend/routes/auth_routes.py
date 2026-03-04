from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/api")


def _missing_fields(payload, required_fields):
    return [field for field in required_fields if not payload.get(field)]


def _build_profile_stats(user):
    if user.role == "teacher":
        total_enrollments = sum(len(course.enrollments) for course in user.courses_taught)
        return {
            "courses_created": len(user.courses_taught),
            "problems_created": len(user.created_problems),
            "students_enrolled": total_enrollments,
            "notes_uploaded": len(user.notes_uploaded),
        }

    lessons_completed = sum(1 for entry in user.lesson_progress if entry.completed)
    problems_solved = sum(1 for entry in user.problem_progress if entry.solved)
    return {
        "courses_enrolled": len(user.enrollments),
        "quizzes_completed": len(user.progresses),
        "problems_solved": problems_solved,
        "badges_earned": len(user.user_badges),
        "lessons_completed": lessons_completed,
    }


def _serialize_profile(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_approved": user.is_approved,
        "level": user.level,
        "xp_points": user.xp_points,
        "coins": user.coins,
        "daily_streak": user.daily_streak,
        "created_at": user.created_at.isoformat(),
        "stats": _build_profile_stats(user),
    }


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    missing = _missing_fields(data, ["name", "email", "password"])
    if missing:
        return jsonify({"error": "Missing fields", "fields": missing}), 400

    name = data["name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]
    role = (data.get("role") or "student").strip().lower()

    if role not in {"teacher", "student", "admin"}:
        return jsonify({"error": "Invalid role"}), 400

    if not name or not email or not password:
        return jsonify({"error": "Invalid input"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        is_approved=True,
    )
    db.session.add(user)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Registration successful",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "is_approved": user.is_approved,
                },
            }
        ),
        201,
    )


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    missing = _missing_fields(data, ["email", "password"])
    if missing:
        return jsonify({"error": "Missing fields", "fields": missing}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
    )

    return jsonify(
        {
            "token": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_approved": user.is_approved,
                "level": user.level,
                "xp_points": user.xp_points,
                "coins": user.coins,
            },
        }
    )


@auth_bp.get("/profile")
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(_serialize_profile(user))


@auth_bp.patch("/profile")
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")

    if name is None and email is None:
        return jsonify({"error": "No fields to update"}), 400

    if name is not None:
        name = name.strip()
        if not name:
            return jsonify({"error": "Name cannot be empty"}), 400
        user.name = name

    if email is not None:
        email = email.strip().lower()
        if not email:
            return jsonify({"error": "Email cannot be empty"}), 400
        existing_user = User.query.filter(User.email == email, User.id != user.id).first()
        if existing_user:
            return jsonify({"error": "Email already registered"}), 409
        user.email = email

    db.session.commit()
    return jsonify(_serialize_profile(user))


@auth_bp.post("/auth/logout")
@jwt_required()
def logout():
    return jsonify({"message": "Logged out"})
