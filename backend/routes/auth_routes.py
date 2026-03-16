from datetime import datetime, timedelta
import secrets

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from models import User
from email_service import EmailService


auth_bp = Blueprint("auth", __name__, url_prefix="/api")


def _missing_fields(payload, required_fields):
    return [field for field in required_fields if not payload.get(field)]


def _mail_is_configured():
    return bool(current_app.config.get("MAIL_USERNAME") and current_app.config.get("MAIL_PASSWORD"))


def _verification_link(token):
    app_url = current_app.config.get("APP_URL", "http://localhost:3000")
    return f"{app_url}/verify-email/{token}"


def _include_dev_verification_otp(payload, otp):
    # Never expose OTP in real production responses.
    env = (current_app.config.get("ENV", "production") or "production").lower()
    app_url = (current_app.config.get("APP_URL", "") or "").lower()
    is_localhost_url = "localhost" in app_url or "127.0.0.1" in app_url
    if env != "production" or is_localhost_url:
        payload["verification_otp"] = otp
    return payload


def _generate_verification_otp():
    return f"{secrets.randbelow(1000000):06d}"


def _otp_expiry_datetime():
    return datetime.utcnow() + timedelta(
        minutes=current_app.config.get("OTP_EXPIRY_MINUTES", 5)
    )


def _is_user_verified(user):
    return bool(user.is_verified or user.email_verified)


def _set_user_verified(user, verified):
    user.is_verified = verified
    user.email_verified = verified


def _set_user_otp(user, otp_code, otp_expiry):
    # Keep both old and new fields in sync for compatibility.
    user.otp_code = otp_code
    user.otp_expiry = otp_expiry
    user.verification_token = otp_code
    user.verification_token_expiry = otp_expiry


def _clear_user_otp(user):
    _set_user_otp(user, None, None)


def _get_user_otp(user):
    return user.otp_code or user.verification_token


def _get_user_otp_expiry(user):
    return user.otp_expiry or user.verification_token_expiry


def _enforce_resend_limit(user):
    max_attempts = current_app.config.get("OTP_RESEND_MAX_ATTEMPTS", 3)
    window_minutes = current_app.config.get("OTP_RESEND_WINDOW_MINUTES", 15)
    now = datetime.utcnow()

    if user.otp_resend_window_start is None or (
        now - user.otp_resend_window_start
    ) > timedelta(minutes=window_minutes):
        user.otp_resend_window_start = now
        user.otp_resend_count = 0

    if user.otp_resend_count >= max_attempts:
        retry_after = user.otp_resend_window_start + timedelta(minutes=window_minutes)
        return False, retry_after

    user.otp_resend_count += 1
    return True, None


def send_otp_email(email, otp, user_name="Learner"):
    if not _mail_is_configured():
        return False

    email_service = EmailService(
        smtp_server=current_app.config["MAIL_SERVER"],
        smtp_port=current_app.config["MAIL_PORT"],
        use_tls=current_app.config.get("MAIL_USE_TLS", True),
        smtp_username=current_app.config["MAIL_USERNAME"],
        smtp_password=current_app.config["MAIL_PASSWORD"],
        from_email=current_app.config["MAIL_FROM_EMAIL"],
        from_name=current_app.config["MAIL_FROM_NAME"],
    )

    return email_service.send_verification_otp_email(
        to_email=email,
        user_name=user_name,
        otp_code=otp,
        expiry_minutes=current_app.config.get("OTP_EXPIRY_MINUTES", 5),
    )


def _build_profile_stats(user):
    from models import Course, Problem, Enrollment, Note, Progress, LessonProgress, ProblemProgress, UserBadge
    
    if user.role == "teacher":
        try:
            courses_created = db.session.query(Course).filter_by(teacher_id=user.id).count()
            problems_created = db.session.query(Problem).filter_by(created_by=user.id).count()
            notes_uploaded = db.session.query(Note).filter_by(uploaded_by=user.id).count()
            
            # Count students enrolled across all teacher's courses
            students_enrolled = db.session.query(Enrollment.student_id).join(
                Course, Course.id == Enrollment.course_id
            ).filter(Course.teacher_id == user.id).distinct().count()
            
            return {
                "courses_created": courses_created,
                "problems_created": problems_created,
                "students_enrolled": students_enrolled,
                "notes_uploaded": notes_uploaded,
            }
        except Exception as e:
            print(f"Error building teacher stats: {e}")
            return {
                "courses_created": 0,
                "problems_created": 0,
                "students_enrolled": 0,
                "notes_uploaded": 0,
            }
    
    if user.role == "admin":
        # Admin stats - overview of entire platform
        try:
            from models import User
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
        except Exception as e:
            print(f"Error building admin stats: {e}")
            return {
                "total_users": 0,
                "total_courses": 0,
                "total_problems": 0,
                "total_enrollments": 0,
            }
    
    # Student stats
    try:
        courses_enrolled = db.session.query(Enrollment).filter_by(student_id=user.id).count()
        quizzes_completed = db.session.query(Progress).filter_by(user_id=user.id).count()
        problems_solved = db.session.query(ProblemProgress).filter_by(
            user_id=user.id, solved=True
        ).count()
        badges_earned = db.session.query(UserBadge).filter_by(user_id=user.id).count()
        lessons_completed = db.session.query(LessonProgress).filter_by(
            user_id=user.id, completed=True
        ).count()
        
        return {
            "courses_enrolled": courses_enrolled,
            "quizzes_completed": quizzes_completed,
            "problems_solved": problems_solved,
            "badges_earned": badges_earned,
            "lessons_completed": lessons_completed,
        }
    except Exception as e:
        print(f"Error building student stats: {e}")
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

        # Generate 6-digit OTP for email verification
        verification_token = _generate_verification_otp()
        token_expiry = _otp_expiry_datetime()

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            is_approved=True,
            is_verified=False,
            email_verified=False,
            otp_code=verification_token,
            otp_expiry=token_expiry,
            verification_token=verification_token,
            verification_token_expiry=token_expiry,
            otp_resend_count=0,
            otp_resend_window_start=datetime.utcnow(),
        )
        db.session.add(user)
        db.session.commit()
    except OperationalError as exc:
        db.session.rollback()
        current_app.logger.exception("Database unavailable during register: %s", exc)
        return jsonify({"error": "Database unavailable", "message": "Please try again shortly."}), 503
    except SQLAlchemyError as exc:
        db.session.rollback()
        current_app.logger.exception("Database error during register: %s", exc)
        return jsonify({"error": "Database error", "message": "Registration failed."}), 500

    # Send verification OTP email if enabled
    email_verification_required = current_app.config.get("EMAIL_VERIFICATION_REQUIRED", True)
    email_sent = False
    if email_verification_required and _mail_is_configured():
        try:
            email_sent = send_otp_email(user.email, verification_token, user.name)
        except Exception as e:
            current_app.logger.error(f"Failed to send verification OTP email: {e}")
    elif email_verification_required:
        current_app.logger.warning(
            "Email verification is enabled but MAIL_USERNAME/MAIL_PASSWORD are not configured. "
            "Falling back to manual OTP in non-production environments."
        )

    response_payload = {
        "message": "Registration successful. Please check your email for the OTP to verify your account.",
        "email_verification_required": email_verification_required,
        "email_sent": email_sent,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_approved": user.is_approved,
            "is_verified": user.is_verified,
            "email_verified": user.email_verified,
        },
    }

    if email_verification_required and not email_sent:
        response_payload["message"] = (
            "Registration successful, but email delivery is not configured on the server. "
            "Use the OTP below."
        )
        _include_dev_verification_otp(response_payload, verification_token)

    return (
        jsonify(response_payload),
        201,
    )


@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200

    try:
        data = request.get_json(silent=True) or {}
        missing = _missing_fields(data, ["email", "password"])
        if missing:
            return jsonify({
                "success": False,
                "error": "Missing fields",
                "message": "Email and password are required.",
                "fields": missing,
            }), 400

        email = data["email"].strip().lower()
        password = data["password"]

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({
                "success": False,
                "error": "Invalid credentials",
                "message": "Invalid email or password",
            }), 401

        # Check email verification if enabled
        email_verification_required = current_app.config.get("EMAIL_VERIFICATION_REQUIRED", True)
        if email_verification_required and not _is_user_verified(user):
            return jsonify({
                "success": False,
                "error": "Email not verified",
                "message": "Please verify your email before logging in. Check your inbox for the OTP.",
                "is_verified": False,
                "email_verified": False,
                "user_id": user.id,
            }), 403

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
                    "is_verified": user.is_verified,
                    "email_verified": user.email_verified,
                },
            }
        )
    except OperationalError as exc:
        current_app.logger.exception("Database unavailable during login: %s", exc)
        return jsonify({
            "success": False,
            "error": "Database unavailable",
            "message": "Please try again shortly.",
        }), 503
    except SQLAlchemyError as exc:
        current_app.logger.exception("Database error during login: %s", exc)
        return jsonify({
            "success": False,
            "error": "Database error",
            "message": "Login failed. Please retry.",
        }), 500


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


@auth_bp.get("/verify-email/<token>")
def verify_email(token):
    """Verify user email with token or OTP."""
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        return jsonify({"error": "Invalid verification token"}), 400
    
    if _is_user_verified(user):
        return jsonify({"message": "Email already verified"}), 200
    
    # Check if token has expired
    token_expiry = _get_user_otp_expiry(user)
    if token_expiry and datetime.utcnow() > token_expiry:
        return jsonify({
            "error": "Verification token has expired",
            "message": "Please request a new verification email.",
        }), 400
    
    # Verify the email
    _set_user_verified(user, True)
    _clear_user_otp(user)
    db.session.commit()
    
    return jsonify({
        "message": "Email verified successfully! You can now log in.",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_verified": user.is_verified,
            "email_verified": user.email_verified,
        },
    }), 200


@auth_bp.post("/verify-email-otp")
@auth_bp.post("/verify-otp")
def verify_email_otp():
    """Verify user email with OTP and email."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    otp = (data.get("otp") or "").strip()

    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid email or OTP"}), 400

    if _is_user_verified(user):
        return jsonify({"message": "Email already verified"}), 200

    if _get_user_otp(user) != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    otp_expiry = _get_user_otp_expiry(user)
    if otp_expiry and datetime.utcnow() > otp_expiry:
        return jsonify({
            "error": "OTP has expired",
            "message": "Please request a new OTP.",
        }), 400

    _set_user_verified(user, True)
    _clear_user_otp(user)
    user.otp_resend_count = 0
    user.otp_resend_window_start = None
    db.session.commit()

    return jsonify({
        "message": "Email verified successfully! You can now log in.",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_verified": user.is_verified,
            "email_verified": user.email_verified,
        },
    }), 200


@auth_bp.post("/resend-verification")
@auth_bp.post("/resend-otp")
def resend_verification():
    """Resend verification email to user."""
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Don't reveal if email exists for security
        return jsonify({
            "message": "If an account exists with this email, a verification OTP has been sent."
        }), 200
    
    if _is_user_verified(user):
        return jsonify({"message": "Email is already verified"}), 200

    can_resend, retry_after = _enforce_resend_limit(user)
    if not can_resend:
        minutes = current_app.config.get("OTP_RESEND_WINDOW_MINUTES", 15)
        wait_seconds = max(1, int((retry_after - datetime.utcnow()).total_seconds()))
        db.session.commit()
        return jsonify({
            "error": "Resend limit exceeded",
            "message": f"Too many OTP requests. Try again in about {minutes} minutes.",
            "retry_after_seconds": wait_seconds,
        }), 429
    
    # Generate new OTP
    verification_token = _generate_verification_otp()
    token_expiry = _otp_expiry_datetime()

    _set_user_otp(user, verification_token, token_expiry)
    db.session.commit()
    
    # Send verification OTP email
    email_sent = False
    if _mail_is_configured():
        try:
            email_sent = send_otp_email(user.email, verification_token, user.name)
        except Exception as e:
            current_app.logger.error(f"Failed to send verification OTP email: {e}")
    else:
        current_app.logger.warning(
            "Resend requested, but MAIL_USERNAME/MAIL_PASSWORD are not configured."
        )

    response_payload = {
        "message": "Verification OTP sent. Please check your inbox.",
        "email_sent": email_sent,
    }

    if not email_sent:
        response_payload["message"] = (
            "Email delivery is not configured on the server. Use the OTP below."
        )
        _include_dev_verification_otp(response_payload, verification_token)
    
    return jsonify(response_payload), 200


@auth_bp.post("/auth/logout")
@jwt_required()
def logout():
    return jsonify({"message": "Logged out"})
