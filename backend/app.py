import logging
import os
from datetime import datetime

import click
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from config import Config
from database import db, init_db
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.quiz_routes import quiz_bp
from routes.leaderboard_routes import leaderboard_bp
from routes.reward_routes import reward_bp
from routes.skill_routes import skill_bp
from routes.recommendation_routes import recommendation_bp
from routes.daily_routes import daily_bp
from routes.course_routes import course_bp
from routes.notes_routes import notes_bp
from routes.admin_routes import admin_bp
from routes.problem_routes import problem_bp
from routes.coding_admin_routes import coding_admin_bp
from routes.lesson_progress_routes import lesson_progress_bp
from routes.notification_routes import notification_bp
from routes.analytics_routes import analytics_bp
from routes.teacher_analytics_routes import teacher_analytics_bp
from routes.activity_routes import activity_bp
from seed_data import seed_quiz_data
from models import User


def _auto_verify_legacy_users(app: Flask) -> None:
    if not app.config.get("AUTO_VERIFY_LEGACY_USERS"):
        return

    cutoff_raw = (app.config.get("LEGACY_VERIFICATION_CUTOFF") or "").strip()
    if not cutoff_raw:
        app.logger.warning(
            "AUTO_VERIFY_LEGACY_USERS is enabled but LEGACY_VERIFICATION_CUTOFF is empty. Skipping migration."
        )
        return

    try:
        cutoff_dt = datetime.strptime(cutoff_raw, "%Y-%m-%d")
    except ValueError:
        app.logger.warning(
            "Invalid LEGACY_VERIFICATION_CUTOFF format '%s'. Use YYYY-MM-DD.",
            cutoff_raw,
        )
        return

    updated = (
        User.query.filter(
            User.email_verified.is_(False),
            User.created_at < cutoff_dt,
        )
        .update(
            {
                User.is_verified: True,
                User.email_verified: True,
                User.otp_code: None,
                User.otp_expiry: None,
                User.verification_token: None,
                User.verification_token_expiry: None,
            },
            synchronize_session=False,
        )
    )
    db.session.commit()

    if updated:
        app.logger.info(
            "Legacy auto-verification applied: %s users created before %s were marked verified.",
            updated,
            cutoff_raw,
        )
    else:
        app.logger.info(
            "Legacy auto-verification checked: no matching users before %s.",
            cutoff_raw,
        )


def create_app() -> Flask:
    frontend_build = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
    )
    app = Flask(__name__, static_folder=frontend_build, static_url_path="/")
    # Load configuration (MySQL credentials from environment variables).
    app.config.from_object(Config)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Authorization", "Content-Type"],
            }
        },
        supports_credentials=False,
        vary_header=True,
    )

    # Ensure uploads directory exists and is writable for notes/document uploads.
    uploads_dir = app.config.get("UPLOAD_DIR")
    if uploads_dir:
        os.makedirs(uploads_dir, exist_ok=True)
        try:
            probe_path = os.path.join(uploads_dir, ".write_test")
            with open(probe_path, "w", encoding="utf-8") as probe:
                probe.write("ok")
            os.remove(probe_path)
        except OSError as exc:
            raise RuntimeError(f"UPLOAD_DIR is not writable: {uploads_dir}") from exc

    # Initialize SQLAlchemy with the Flask app.
    init_db(app)
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def jwt_missing_token(reason):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Authorization required",
                    "message": reason,
                }
            ),
            401,
        )

    @jwt.invalid_token_loader
    def jwt_invalid_token(reason):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Invalid token",
                    "message": reason,
                }
            ),
            422,
        )

    @jwt.expired_token_loader
    def jwt_expired_token(_header, _payload):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Token expired",
                    "message": "Please login again.",
                }
            ),
            401,
        )

    with app.app_context():
        if app.config.get("RUN_STARTUP_TASKS"):
            # Optional bootstrap for local/dev only.
            db.create_all()
            seed_quiz_data()
        _auto_verify_legacy_users(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(reward_bp)
    app.register_blueprint(skill_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(daily_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(problem_bp)
    app.register_blueprint(coding_admin_bp)
    app.register_blueprint(lesson_progress_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(teacher_analytics_bp)
    app.register_blueprint(activity_bp)

    @app.get("/")
    def root_route():
        if os.path.exists(os.path.join(frontend_build, "index.html")):
            return send_from_directory(frontend_build, "index.html")
        return jsonify({"status": "ok", "message": "Gamified Learning API"})

    @app.get("/api/test")
    def test_route():
        return jsonify({"message": "Backend working"})

    @app.errorhandler(404)
    def not_found(error):
        if (os.path.exists(os.path.join(frontend_build, "index.html"))
                and not str(error).startswith("404 Not Found: /api/")):
            return send_from_directory(frontend_build, "index.html")
        return jsonify({"success": False, "message": "Not found"}), 404

    @app.errorhandler(400)
    def bad_request(_error):
        return jsonify({"success": False, "message": "Bad request"}), 400

    @app.errorhandler(401)
    def unauthorized(_error):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(_error):
        return jsonify({"success": False, "message": "Forbidden"}), 403

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception("Server error: %s", error)
        return jsonify({"success": False, "message": "Internal server error"}), 500

    @app.errorhandler(OperationalError)
    def database_operational_error(error):
        app.logger.exception("Database operational error: %s", error)
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Database temporarily unavailable. Please retry.",
                }
            ),
            503,
        )

    @app.errorhandler(SQLAlchemyError)
    def database_query_error(error):
        app.logger.exception("Database query error: %s", error)
        return (
            jsonify(
                {
                    "success": False,
                    "message": "A database error occurred.",
                }
            ),
            500,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        if isinstance(error, HTTPException):
            message = getattr(error, "description", "Request failed")
            return jsonify({"success": False, "message": message}), error.code

        app.logger.exception("Unhandled exception: %s", error)
        return jsonify({"success": False, "message": "Internal server error"}), 500

    @app.cli.command("create-admin")
    @click.option("--name", default="Admin", help="Admin display name")
    @click.option("--email", required=True, help="Admin email address")
    @click.option("--password", default=None, help="Admin password")
    def create_admin(name, email, password):
        """Create the first admin user."""
        if not password:
            password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
        existing = User.query.filter_by(email=email.lower()).first()
        if existing:
            raise click.ClickException("A user with that email already exists.")

        user = User(
            name=name.strip(),
            email=email.strip().lower(),
            password_hash=generate_password_hash(password),
            role="admin",
            is_approved=True,
        )
        db.session.add(user)
        db.session.commit()
        click.echo(f"Admin user created: {user.email}")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
