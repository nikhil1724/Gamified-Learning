import bcrypt

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from werkzeug.security import check_password_hash

from activity_service import update_user_streak
from badge_service import assign_eligible_badges
from database import db
from models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/api")


def _missing_fields(payload, required_fields):
    return [field for field in required_fields if not payload.get(field)]


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _check_password(password: str, hashed_password: str) -> tuple[bool, bool]:
    if not hashed_password:
        return False, False

    # Preferred path for new accounts.
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")), False
    except ValueError:
        pass

    # Backward compatibility for legacy Werkzeug hashes (e.g. scrypt/pbkdf2).
    try:
        if check_password_hash(hashed_password, password):
            return True, True
    except ValueError:
        pass

    return False, False


def _build_profile_stats(user):
    from models import Course, Enrollment, LessonProgress, Note, Problem, ProblemProgress, Progress, UserBadge

    if user.role == "teacher":
        try:
            courses_created = db.session.query(Course).filter_by(teacher_id=user.id).count()
            problems_created = db.session.query(Problem).filter_by(created_by=user.id).count()
            notes_uploaded = db.session.query(Note).filter_by(uploaded_by=user.id).count()
            students_enrolled = (
                db.session.query(Enrollment.student_id)
                .join(Course, Course.id == Enrollment.course_id)
                .filter(Course.teacher_id == user.id)
                .distinct()
                .count()
            )
            return {
                "courses_created": courses_created,
                "problems_created": problems_created,
                "students_enrolled": students_enrolled,
                "notes_uploaded": notes_uploaded,
            }
        except Exception:
            return {
                "courses_created": 0,
                "problems_created": 0,
                "students_enrolled": 0,
                "notes_uploaded": 0,
            }

    if user.role == "admin":
        try:
            total_users = db.session.query(User).count()
            total_courses = db.session.query(Course).count()
            total_problems = db.session.query(Problem).count()
            total_enrollments = db.session.query(Enrollment).count()
            return {
                "total_users": total_users,
                "total_courses": total_courses,
                "total_problems": total_problems,
                "total_enrollments": total_enrollments,
            }
        except Exception:
            return {
                "total_users": 0,
                "total_courses": 0,
                "total_problems": 0,
                "total_enrollments": 0,
            }

    try:
        courses_enrolled = db.session.query(Enrollment).filter_by(student_id=user.id).count()
        quizzes_completed = db.session.query(Progress).filter_by(user_id=user.id).count()
        problems_solved = db.session.query(ProblemProgress).filter_by(user_id=user.id, solved=True).count()
        badges_earned = db.session.query(UserBadge).filter_by(user_id=user.id).count()
        lessons_completed = db.session.query(LessonProgress).filter_by(user_id=user.id, completed=True).count()
        return {
            "courses_enrolled": courses_enrolled,
            "quizzes_completed": quizzes_completed,
            "problems_solved": problems_solved,
            "badges_earned": badges_earned,
            "lessons_completed": lessons_completed,
        }
    except Exception:
        return {
            "courses_enrolled": 0,
            "quizzes_completed": 0,
            "problems_solved": 0,
            "badges_earned": 0,
            "lessons_completed": 0,
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
        "streak_count": user.streak_count,
        "longest_streak": user.longest_streak,
        "last_active_date": user.last_active_date.isoformat() if user.last_active_date else None,
        "daily_streak": user.daily_streak,
        "created_at": user.created_at.isoformat(),
        "stats": _build_profile_stats(user),
    }


@auth_bp.post("/register")
def register():
    try:
        data = request.get_json(silent=True) or {}
        missing = _missing_fields(data, ["name", "email", "password"])
        if missing:
            return jsonify({"success": False, "error": "Missing fields", "fields": missing}), 400

        name = data["name"].strip()
        email = data["email"].strip().lower()
        password = data["password"]

        if not name or not email or not password:
            return jsonify({"success": False, "error": "Invalid input"}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"success": False, "error": "Email already registered"}), 409

        user = User(
            name=name,
            email=email,
            password_hash=_hash_password(password),
            role="student",
            is_approved=True,
        )
        db.session.add(user)
        db.session.commit()
    except OperationalError as exc:
        db.session.rollback()
        current_app.logger.exception("Database unavailable during register: %s", exc)
        return jsonify({"success": False, "error": "Database unavailable", "message": "Please try again shortly."}), 503
    except SQLAlchemyError as exc:
        db.session.rollback()
        current_app.logger.exception("Database error during register: %s", exc)
        return jsonify({"success": False, "error": "Database error", "message": "Registration failed."}), 500

    return jsonify(
        {
            "success": True,
            "message": "Registration successful.",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_approved": user.is_approved,
            },
        }
    ), 201


@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200

    try:
        data = request.get_json(silent=True) or {}
        missing = _missing_fields(data, ["email", "password"])
        if missing:
            return jsonify(
                {
                    "success": False,
                    "error": "Missing fields",
                    "message": "Email and password are required.",
                    "fields": missing,
                }
            ), 400

        email = data["email"].strip().lower()
        password = data["password"]

        user = User.query.filter_by(email=email).first()
        password_ok, needs_rehash = _check_password(password, user.password_hash if user else "")
        if not user or not password_ok:
            return jsonify(
                {
                    "success": False,
                    "error": "Invalid credentials",
                    "message": "Invalid email or password",
                }
            ), 401

        if needs_rehash:
            user.password_hash = _hash_password(password)

        client_timezone = request.headers.get("X-User-Timezone")
        update_user_streak(user=user, user_timezone=client_timezone)
        newly_unlocked_badges = assign_eligible_badges(user=user, trigger="login")
        db.session.commit()

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role},
        )

        return jsonify(
            {
                "success": True,
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
                    "streak_count": user.streak_count,
                    "longest_streak": user.longest_streak,
                    "last_active_date": user.last_active_date.isoformat() if user.last_active_date else None,
                    "daily_streak": user.daily_streak,
                },
                "unlocked_badges": newly_unlocked_badges,
            }
        )
    except OperationalError as exc:
        current_app.logger.exception("Database unavailable during login: %s", exc)
        return jsonify(
            {
                "success": False,
                "error": "Database unavailable",
                "message": "Please try again shortly.",
            }
        ), 503
    except SQLAlchemyError as exc:
        current_app.logger.exception("Database error during login: %s", exc)
        return jsonify(
            {
                "success": False,
                "error": "Database error",
                "message": "Login failed. Please retry.",
            }
        ), 500


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
