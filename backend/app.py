import logging
import os

import click
import bcrypt
from werkzeug.exceptions import HTTPException

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from config import Config
from database import check_database_connection, db, init_db, register_db_observability
from db_connection import get_database_diagnostics
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
from routes.badge_routes import badge_bp
from socketio_service import init_socketio, socketio
from seed_data import reseed_demo_data, seed_quiz_data
from models import User


def create_app() -> Flask:
    frontend_build = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
    )
    app = Flask(__name__, static_folder=frontend_build, static_url_path="/")
    # Load configuration from environment variables.
    app.config.from_object(Config)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    diagnostics = get_database_diagnostics()
    app.logger.info("Environment precedence: process env > .env (dotenv override=False)")
    app.logger.info(
        "Database config source=%s scheme=%s host=%s database=%s",
        diagnostics["source"],
        diagnostics["scheme"],
        diagnostics["host"],
        diagnostics["database"],
    )
    app.logger.info("Database URL (masked): %s", diagnostics["masked_url"])

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Authorization", "Content-Type", "X-User-Timezone"],
                "expose_headers": ["Content-Type", "Authorization"],
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
    register_db_observability(app)
    if app.config.get("DB_CHECK_ON_STARTUP"):
        check_database_connection(
            app,
            attempts=app.config.get("DB_STARTUP_CHECK_ATTEMPTS", 3),
            delay_seconds=app.config.get("DB_STARTUP_CHECK_DELAY_SECONDS", 2.0),
        )
    init_socketio(app)
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
            401,
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
            try:
                db.create_all()
                seed_quiz_data()
            except SQLAlchemyError as exc:
                app.logger.warning("Skipping startup tasks because database is unavailable: %s", exc)

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
    app.register_blueprint(badge_bp)

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
            password_hash=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            role="admin",
            is_approved=True,
        )
        db.session.add(user)
        db.session.commit()
        click.echo(f"Admin user created: {user.email}")

    @app.cli.command("reseed-demo")
    @click.option("--yes", is_flag=True, help="Skip confirmation prompt")
    def reseed_demo(yes):
        """Reset known demo records and re-seed fresh demo data."""
        if not yes:
            confirmed = click.confirm(
                "This will remove existing demo records and regenerate demo data. Continue?",
                default=False,
            )
            if not confirmed:
                click.echo("Cancelled.")
                return

        summary = reseed_demo_data()
        click.echo("Demo reseed completed.")
        for key, value in summary.items():
            click.echo(f"- {key}: {value}")

    return app


app = create_app()


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
