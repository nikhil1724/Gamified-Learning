"""Create database tables during deployment if they do not exist."""

from app import app
from database import db
import models  # noqa: F401  # Register SQLAlchemy models before create_all.


def main() -> None:
    with app.app_context():
        db.create_all()
    print("[bootstrap_db] create_all completed")


if __name__ == "__main__":
    main()
