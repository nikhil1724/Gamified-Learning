"""Create database tables during deployment if they do not exist."""

from flask import Flask

from config import Config
from database import db
import models  # noqa: F401  # Register SQLAlchemy models before create_all.
from models import Quiz
from seed_data import seed_quiz_data


def _auto_seed_if_empty() -> None:
    quiz_count = Quiz.query.count()
    print(f"[bootstrap_db] existing quizzes: {quiz_count}")

    if quiz_count == 0:
        seed_quiz_data()
        print("[bootstrap_db] demo seed data inserted")
    else:
        print("[bootstrap_db] quizzes already exist; seed skipped")


def main() -> None:
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()
        _auto_seed_if_empty()

    print("[bootstrap_db] create_all completed")


if __name__ == "__main__":
    main()
