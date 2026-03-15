from sqlalchemy import text

from app import create_app
from database import db



def _table_exists(table_name: str) -> bool:
    result = db.session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table_name
            """
        ),
        {"table_name": table_name},
    ).scalar()
    return bool(result)



def _column_exists(table_name: str, column_name: str) -> bool:
    result = db.session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :table_name
              AND COLUMN_NAME = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).scalar()
    return bool(result)



def migrate_student_progress_schema():
    renamed_problem_table = False
    created_user_progress = False
    altered_user_progress = False
    migrated_rows = 0
    created_quiz_attempts = False
    migrated_quiz_attempts = 0

    # Reconcile existing user_progress table shape, if present.
    if _table_exists("user_progress"):
        has_problem_id = _column_exists("user_progress", "problem_id")
        has_course = _column_exists("user_progress", "course")
        has_course_id = _column_exists("user_progress", "course_id")

        # Case 1: user_progress is the old coding-problem table.
        if has_problem_id and not has_course_id and not has_course:
            if not _table_exists("problem_progress"):
                db.session.execute(text("RENAME TABLE user_progress TO problem_progress"))
                renamed_problem_table = True
            else:
                # A conflicting legacy table exists under user_progress; remove it
                # so lesson-progress table can be created with the required schema.
                db.session.execute(text("DROP TABLE user_progress"))
                print("Dropped conflicting legacy user_progress table because problem_progress already exists.")

        # Case 2: user_progress is old lesson-progress table with string course column.
        elif has_course and not has_course_id:
            db.session.execute(text("ALTER TABLE user_progress ADD COLUMN course_id INT NULL"))
            db.session.execute(
                text(
                    """
                    UPDATE user_progress
                    SET course_id = CAST(course AS UNSIGNED)
                    WHERE course REGEXP '^[0-9]+$'
                    """
                )
            )
            db.session.execute(
                text(
                    """
                    UPDATE user_progress
                    SET completed_at = CURRENT_TIMESTAMP
                    WHERE completed_at IS NULL
                    """
                )
            )
            altered_user_progress = True

    # Ensure lesson progress table exists in the required shape.
    if not _table_exists("user_progress"):
        db.session.execute(
            text(
                """
                CREATE TABLE user_progress (
                  id INT AUTO_INCREMENT PRIMARY KEY,
                  user_id INT NOT NULL,
                  course_id INT NOT NULL,
                  lesson_id INT NOT NULL,
                  completed BOOLEAN NOT NULL DEFAULT TRUE,
                  completed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  CONSTRAINT fk_user_progress_user
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                  CONSTRAINT fk_user_progress_course
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                  CONSTRAINT fk_user_progress_lesson
                    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
                  UNIQUE KEY uq_user_course_lesson (user_id, course_id, lesson_id)
                )
                """
            )
        )
        created_user_progress = True

    # Optional migration from old lesson_progress(course string) into new user_progress.
    if (
        _table_exists("lesson_progress")
        and _column_exists("lesson_progress", "course")
        and _column_exists("user_progress", "course_id")
    ):
        result = db.session.execute(
            text(
                """
                INSERT INTO user_progress (user_id, course_id, lesson_id, completed, completed_at)
                SELECT lp.user_id,
                       CAST(lp.course AS UNSIGNED),
                       lp.lesson_id,
                       lp.completed,
                       COALESCE(lp.completed_at, CURRENT_TIMESTAMP)
                FROM lesson_progress lp
                WHERE lp.completed = TRUE
                  AND lp.course REGEXP '^[0-9]+$'
                ON DUPLICATE KEY UPDATE
                  completed = VALUES(completed),
                  completed_at = VALUES(completed_at)
                """
            )
        )
        migrated_rows = result.rowcount or 0

    # Ensure quiz_attempts table exists.
    if not _table_exists("quiz_attempts"):
        db.session.execute(
            text(
                """
                CREATE TABLE quiz_attempts (
                  id INT AUTO_INCREMENT PRIMARY KEY,
                  user_id INT NOT NULL,
                  quiz_id INT NOT NULL,
                  score INT NOT NULL,
                  total_questions INT NOT NULL,
                  attempted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  CONSTRAINT fk_quiz_attempts_user
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                  CONSTRAINT fk_quiz_attempts_quiz
                    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
                )
                """
            )
        )
        created_quiz_attempts = True

    # Optional backfill from existing progresses table.
    if _table_exists("progresses") and _table_exists("quiz_attempts"):
        result = db.session.execute(
            text(
                """
                INSERT INTO quiz_attempts (user_id, quiz_id, score, total_questions, attempted_at)
                SELECT p.user_id,
                       p.quiz_id,
                       p.score,
                       GREATEST(1, CAST(ROUND((p.score * 100) / NULLIF(p.completion_percentage, 0), 0) AS SIGNED)),
                       p.attempted_at
                FROM progresses p
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM quiz_attempts qa
                    WHERE qa.user_id = p.user_id
                      AND qa.quiz_id = p.quiz_id
                      AND qa.attempted_at = p.attempted_at
                )
                """
            )
        )
        migrated_quiz_attempts = result.rowcount or 0

    db.session.commit()

    print("Student progress migration complete.")
    print(f"Renamed user_progress -> problem_progress: {renamed_problem_table}")
    print(f"Created new user_progress table: {created_user_progress}")
    print(f"Altered legacy user_progress table: {altered_user_progress}")
    print(f"Migrated rows from lesson_progress: {migrated_rows}")
    print(f"Created quiz_attempts table: {created_quiz_attempts}")
    print(f"Migrated rows into quiz_attempts: {migrated_quiz_attempts}")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        migrate_student_progress_schema()
