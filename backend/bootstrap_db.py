"""Create database tables during deployment if they do not exist."""

from flask import Flask

from config import Config
from database import db
import models  # noqa: F401  # Register SQLAlchemy models before create_all.
from models import Quiz
from seed_data import seed_quiz_data

from db_connection import run_with_retry


def _auto_seed_if_empty() -> None:
    quiz_count = Quiz.query.count()
    print(f"[bootstrap_db] existing quizzes: {quiz_count}")

    if quiz_count == 0:
        seed_quiz_data()
        print("[bootstrap_db] demo seed data inserted")
    else:
        print("[bootstrap_db] quizzes already exist; seed skipped")


def _bootstrap_once() -> None:
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        try:
            db.create_all()
            _auto_seed_if_empty()
        except Exception:
            db.session.remove()
            db.engine.dispose()
            raise

    print("[bootstrap_db] create_all completed")


def main() -> None:
    run_with_retry(_bootstrap_once, "bootstrap_db")


if __name__ == "__main__":
    main()
