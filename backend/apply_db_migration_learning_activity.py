"""Create learning_activity table for learning streak tracking."""

from app import app
from database import db


def apply_migration() -> None:
    with app.app_context():
        conn = db.engine.connect()
        trans = conn.begin()
        try:
            conn.execute(
                db.text(
                    """
                    CREATE TABLE IF NOT EXISTS learning_activity (
                      id INT AUTO_INCREMENT PRIMARY KEY,
                      user_id INT NOT NULL,
                      activity_date DATE NOT NULL,
                      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      CONSTRAINT fk_learning_activity_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                      UNIQUE KEY uq_learning_activity_user_date (user_id, activity_date)
                    )
                    """
                )
            )
            trans.commit()
            print("Learning activity migration complete.")
        except Exception:
            trans.rollback()
            raise
        finally:
            conn.close()


if __name__ == "__main__":
    apply_migration()
