from datetime import datetime, timedelta
import hashlib
import hmac
import json
import secrets
from collections import defaultdict

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy import or_
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from activity_service import update_user_streak
from badge_service import assign_eligible_badges
from models import User
from email_service import EmailService


auth_bp = Blueprint("auth", __name__, url_prefix="/api")

_OTP_SECURITY_EVENTS = defaultdict(list)


def _missing_fields(payload, required_fields):
    return [field for field in required_fields if not payload.get(field)]


def _mail_is_configured():
    return bool(current_app.config.get("RESEND_API_KEY") and current_app.config.get("RESEND_FROM_EMAIL"))


def _client_ip():
    forwarded_for = (request.headers.get("X-Forwarded-For") or "").split(",")[0].strip()
    real_ip = (request.headers.get("X-Real-IP") or "").strip()
    return forwarded_for or real_ip or (request.remote_addr or "unknown")


def _anonymize_email(email: str) -> str:
    normalized = (email or "").strip().lower()
    return hashlib.sha256(f"{_otp_hash_secret()}:{normalized}".encode("utf-8")).hexdigest()[:16]


def _track_security_signal(event_key: str):
    now = datetime.utcnow()
    threshold = current_app.config.get("OTP_SECURITY_ALERT_THRESHOLD", 3)
    window_minutes = current_app.config.get("OTP_SECURITY_ALERT_WINDOW_MINUTES", 30)
    window_start = now - timedelta(minutes=window_minutes)

    bucket = _OTP_SECURITY_EVENTS[event_key]
    bucket[:] = [ts for ts in bucket if ts >= window_start]
    bucket.append(now)

    return len(bucket) >= threshold, len(bucket), window_minutes


def _emit_security_event(event_type: str, email: str = "", level: str = "warning", **extra):
    payload = {
        "event": event_type,
        "email_hash": _anonymize_email(email),
        "ip": _client_ip(),
        "user_agent": request.headers.get("User-Agent", "unknown")[:240],
        "timestamp": datetime.utcnow().isoformat(),
        **extra,
    }

    log_message = f"OTP_SECURITY {json.dumps(payload, sort_keys=True)}"
    logger = current_app.logger
    log_level = getattr(logger, level, logger.warning)
    log_level(log_message)

    key = f"{payload['event']}:{payload['email_hash']}:{payload['ip']}"
    suspicious, count, window_minutes = _track_security_signal(key)
    if suspicious:
        logger.error(
            "OTP_SECURITY_ALERT %s",
            json.dumps(
                {
                    "alert": "repeated-security-events",
                    "event": payload["event"],
                    "email_hash": payload["email_hash"],
                    "ip": payload["ip"],
                    "count": count,
                    "window_minutes": window_minutes,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                sort_keys=True,
            ),
        )


def _verification_link(token):
    app_url = current_app.config.get("APP_URL", "http://localhost:3000")
    return f"{app_url}/verify-email/{token}"


def _generate_verification_otp():
    return f"{secrets.randbelow(1000000):06d}"


def _otp_hash_secret():
    return (
        current_app.config.get("JWT_SECRET_KEY")
        or current_app.config.get("SECRET_KEY")
        or "otp-fallback-secret"
    )


def _hash_otp(otp_code: str) -> str:
    return hashlib.sha256(f"{_otp_hash_secret()}:{otp_code}".encode("utf-8")).hexdigest()


def _otp_matches(user, otp_code: str) -> bool:
    stored = user.otp_code
    if not stored:
        return False

    hashed_input = _hash_otp(otp_code)
    if hmac.compare_digest(stored, hashed_input):
        return True

    # Backward compatibility for any pre-hash OTP records.
    return hmac.compare_digest(stored, otp_code)


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
    hashed_otp = _hash_otp(otp_code) if otp_code else None
    user.otp_code = hashed_otp
    user.otp_expiry = otp_expiry
    # Store verification token as hash only; never persist raw OTP.
    user.verification_token = hashed_otp
    user.verification_token_expiry = otp_expiry


def _clear_user_otp(user):
    _set_user_otp(user, None, None)


def _get_user_otp_expiry(user):
    return user.otp_expiry or user.verification_token_expiry


def _enforce_resend_limit(user):
    max_attempts = current_app.config.get("OTP_RESEND_MAX_ATTEMPTS", 3)
    window_minutes = current_app.config.get("OTP_RESEND_WINDOW_MINUTES", 15)
    cooldown_seconds = current_app.config.get("OTP_RESEND_COOLDOWN_SECONDS", 60)
    now = datetime.utcnow()

    if user.otp_last_sent_at:
        retry_after = user.otp_last_sent_at + timedelta(seconds=cooldown_seconds)
        if now < retry_after:
            return False, retry_after, "cooldown"

    if user.otp_resend_window_start is None or (
        now - user.otp_resend_window_start
    ) > timedelta(minutes=window_minutes):
        user.otp_resend_window_start = now
        user.otp_resend_count = 0

    if user.otp_resend_count >= max_attempts:
        retry_after = user.otp_resend_window_start + timedelta(minutes=window_minutes)
        return False, retry_after, "window-limit"

    user.otp_resend_count += 1
    return True, None, None


def _is_otp_verification_locked(user):
    now = datetime.utcnow()
    return bool(user.otp_verify_locked_until and now < user.otp_verify_locked_until)


def _remaining_lock_seconds(user):
    if not user.otp_verify_locked_until:
        return 0
    return max(1, int((user.otp_verify_locked_until - datetime.utcnow()).total_seconds()))


def _register_otp_failure(user):
    max_attempts = current_app.config.get("OTP_VERIFY_MAX_ATTEMPTS", 5)
    lock_minutes = current_app.config.get("OTP_VERIFY_LOCK_MINUTES", 10)

    user.otp_verify_fail_count = (user.otp_verify_fail_count or 0) + 1
    if user.otp_verify_fail_count >= max_attempts:
        user.otp_verify_locked_until = datetime.utcnow() + timedelta(minutes=lock_minutes)
    return user.otp_verify_fail_count


def _reset_otp_failure_state(user):
    user.otp_verify_fail_count = 0
    user.otp_verify_locked_until = None


def send_otp_email(email, otp, user_name="Learner"):
    if not _mail_is_configured():
        return False

    email_service = EmailService(
        api_key=current_app.config["RESEND_API_KEY"],
        from_email=current_app.config["RESEND_FROM_EMAIL"],
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
        "streak_count": user.streak_count,
        "longest_streak": user.longest_streak,
        "last_active_date": user.last_active_date.isoformat() if user.last_active_date else None,
        "daily_streak": user.daily_streak,
        "created_at": user.created_at.isoformat(),
        "stats": _build_profile_stats(user),
    }


@auth_bp.post("/register")
def register():
    email_verification_required = current_app.config.get("EMAIL_VERIFICATION_REQUIRED", True)
    if email_verification_required and not _mail_is_configured():
        email_hint = ((request.get_json(silent=True) or {}).get("email") or "").strip().lower()
        _emit_security_event("smtp_unavailable_register", email=email_hint, level="error")
        return jsonify({
            "success": False,
            "error": "Email service unavailable",
            "message": "Registration requires email verification, but SMTP is not configured.",
        }), 503

    try:
        data = request.get_json(silent=True) or {}
        missing = _missing_fields(data, ["name", "email", "password"])
        if missing:
            return jsonify({"success": False, "error": "Missing fields", "fields": missing}), 400

        name = data["name"].strip()
        email = data["email"].strip().lower()
        password = data["password"]
        role = (data.get("role") or "student").strip().lower()

        if role not in {"teacher", "student", "admin"}:
            return jsonify({"success": False, "error": "Invalid role"}), 400

        if not name or not email or not password:
            return jsonify({"success": False, "error": "Invalid input"}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"success": False, "error": "Email already registered"}), 409

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
            otp_resend_count=0,
            otp_resend_window_start=datetime.utcnow(),
            otp_last_sent_at=datetime.utcnow(),
            otp_verify_fail_count=0,
            otp_verify_locked_until=None,
        )
        _set_user_otp(user, verification_token, token_expiry)
        db.session.add(user)

        email_sent = True
        if email_verification_required:
            email_sent = send_otp_email(user.email, verification_token, user.name)
            if not email_sent:
                _emit_security_event("otp_delivery_failed_register", email=user.email, level="error")
                db.session.rollback()
                return jsonify({
                    "success": False,
                    "error": "OTP delivery failed",
                    "message": "Unable to send OTP email right now. Please try again.",
                }), 502

        db.session.commit()
    except OperationalError as exc:
        db.session.rollback()
        current_app.logger.exception("Database unavailable during register: %s", exc)
        return jsonify({"success": False, "error": "Database unavailable", "message": "Please try again shortly."}), 503
    except SQLAlchemyError as exc:
        db.session.rollback()
        current_app.logger.exception("Database error during register: %s", exc)
        return jsonify({"success": False, "error": "Database error", "message": "Registration failed."}), 500

    response_payload = {
        "success": True,
        "message": "Registration successful. OTP sent to your email.",
        "email_verification_required": email_verification_required,
        "email_sent": True,
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
            _emit_security_event("login_blocked_unverified", email=email, level="info")
            return jsonify({
                "success": False,
                "error": "EMAIL_NOT_VERIFIED",
                "message": "Please verify your email before logging in. Check your inbox for the OTP.",
                "is_verified": False,
                "email_verified": False,
                "user_id": user.id,
            }), 401

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
                    "is_verified": user.is_verified,
                    "email_verified": user.email_verified,
                },
                "unlocked_badges": newly_unlocked_badges,
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
    token_hash = _hash_otp(token)
    user = User.query.filter(
        or_(User.verification_token == token_hash, User.verification_token == token)
    ).first()
    
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
        return jsonify({"success": False, "error": "Email and OTP are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"success": False, "error": "Invalid email or OTP"}), 400

    if _is_user_verified(user):
        return jsonify({"success": True, "message": "Email already verified"}), 200

    if _is_otp_verification_locked(user):
        _emit_security_event(
            "otp_verify_locked_attempt",
            email=email,
            retry_after_seconds=_remaining_lock_seconds(user),
        )
        return jsonify({
            "success": False,
            "error": "Too many invalid OTP attempts",
            "message": "OTP verification is temporarily locked. Try again later.",
            "retry_after_seconds": _remaining_lock_seconds(user),
        }), 429

    if not _otp_matches(user, otp):
        fail_count = _register_otp_failure(user)
        db.session.commit()

        _emit_security_event(
            "otp_verify_invalid",
            email=email,
            fail_count=fail_count,
        )

        max_attempts = current_app.config.get("OTP_VERIFY_MAX_ATTEMPTS", 5)
        if _is_otp_verification_locked(user):
            _emit_security_event(
                "otp_verify_lock_triggered",
                email=email,
                fail_count=fail_count,
                retry_after_seconds=_remaining_lock_seconds(user),
                level="error",
            )
            return jsonify({
                "success": False,
                "error": "Too many invalid OTP attempts",
                "message": "OTP verification is temporarily locked. Try again later.",
                "retry_after_seconds": _remaining_lock_seconds(user),
            }), 429

        attempts_remaining = max(0, max_attempts - fail_count)
        return jsonify({
            "success": False,
            "error": "Invalid OTP",
            "message": "The OTP you entered is invalid.",
            "attempts_remaining": attempts_remaining,
        }), 400

    otp_expiry = _get_user_otp_expiry(user)
    if otp_expiry and datetime.utcnow() > otp_expiry:
        _emit_security_event("otp_verify_expired", email=email, level="info")
        return jsonify({
            "success": False,
            "error": "OTP has expired",
            "message": "Please request a new OTP.",
        }), 400

    _set_user_verified(user, True)
    _clear_user_otp(user)
    user.otp_resend_count = 0
    user.otp_resend_window_start = None
    user.otp_last_sent_at = None
    _reset_otp_failure_state(user)
    db.session.commit()

    _emit_security_event("otp_verify_success", email=email, level="info")

    return jsonify({
        "success": True,
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
        return jsonify({"success": False, "error": "Email is required"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Don't reveal if email exists for security
        _emit_security_event("otp_resend_unknown_email", email=email, level="info")
        return jsonify({
            "success": True,
            "message": "If an account exists with this email, a verification OTP has been sent."
        }), 200
    
    if _is_user_verified(user):
        return jsonify({"success": True, "message": "Email is already verified"}), 200

    if not _mail_is_configured():
        _emit_security_event("smtp_unavailable_resend", email=email, level="error")
        return jsonify({
            "success": False,
            "error": "Email service unavailable",
            "message": "SMTP is not configured. Please contact support.",
        }), 503

    can_resend, retry_after, limit_reason = _enforce_resend_limit(user)
    if not can_resend:
        wait_seconds = max(1, int((retry_after - datetime.utcnow()).total_seconds()))
        db.session.commit()
        if limit_reason == "cooldown":
            _emit_security_event(
                "otp_resend_cooldown",
                email=email,
                retry_after_seconds=wait_seconds,
            )
            return jsonify({
                "success": False,
                "error": "Resend cooldown active",
                "message": "Please wait before requesting another OTP.",
                "retry_after_seconds": wait_seconds,
            }), 429

        minutes = current_app.config.get("OTP_RESEND_WINDOW_MINUTES", 15)
        _emit_security_event(
            "otp_resend_window_limit",
            email=email,
            retry_after_seconds=wait_seconds,
            level="error",
        )
        return jsonify({
            "success": False,
            "error": "Resend limit exceeded",
            "message": f"Too many OTP requests. Try again in about {minutes} minutes.",
            "retry_after_seconds": wait_seconds,
        }), 429
    
    # Generate new OTP
    verification_token = _generate_verification_otp()
    token_expiry = _otp_expiry_datetime()

    _set_user_otp(user, verification_token, token_expiry)
    _reset_otp_failure_state(user)
    user.otp_last_sent_at = datetime.utcnow()

    email_sent = send_otp_email(user.email, verification_token, user.name)
    if not email_sent:
        _emit_security_event("otp_delivery_failed_resend", email=email, level="error")
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "OTP delivery failed",
            "message": "Unable to send OTP email right now. Please try again.",
        }), 502

    db.session.commit()

    _emit_security_event("otp_resend_success", email=email, level="info")

    return jsonify({
        "success": True,
        "message": "Verification OTP sent. Please check your inbox.",
        "email_sent": True,
    }), 200


@auth_bp.post("/auth/logout")
@jwt_required()
def logout():
    return jsonify({"message": "Logged out"})
