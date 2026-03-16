"""Create database tables during deployment if they do not exist."""

from flask import Flask

from config import Config
from database import db
import models  # noqa: F401  # Register SQLAlchemy models before create_all.


def main() -> None:
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    print("[bootstrap_db] create_all completed")


if __name__ == "__main__":
    main()
