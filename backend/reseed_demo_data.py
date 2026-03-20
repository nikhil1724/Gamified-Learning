"""One-click demo data reset and reseed utility.

Usage:
    python backend/reseed_demo_data.py
"""

from flask import Flask

from config import Config
from database import db
import models  # noqa: F401  # Ensure models are registered before DB operations.
from seed_data import reseed_demo_data


def main() -> None:
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        summary = reseed_demo_data()

    print("Demo reseed completed.")
    for key, value in summary.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
