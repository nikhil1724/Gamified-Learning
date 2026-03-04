import logging
import os

import click
from werkzeug.security import generate_password_hash

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

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
from seed_data import seed_quiz_data
from models import User


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

    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    # Initialize SQLAlchemy with the Flask app.
    init_db(app)
    JWTManager(app)

    with app.app_context():
        # Temporary bootstrap to create tables on first run; remove after migration.
        db.create_all()
        seed_quiz_data()

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
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception("Server error: %s", error)
        return jsonify({"error": "Internal server error"}), 500

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
    app.run(host="0.0.0.0", port=5000)
