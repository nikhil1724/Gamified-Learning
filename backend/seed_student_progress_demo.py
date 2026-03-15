from datetime import datetime, timedelta

from app import create_app
from database import db
from models import Course, Enrollment, Lesson, LessonProgress, Progress, Quiz, QuizAttempt, User


def _ensure_enrollment(student_id, course_id):
    existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing:
        return False
    db.session.add(Enrollment(student_id=student_id, course_id=course_id))
    return True


def _ensure_lesson_completion(student_id, course_id, lesson_id, completed_at):
    existing = LessonProgress.query.filter_by(
        user_id=student_id,
        course_id=course_id,
        lesson_id=lesson_id,
    ).first()

    if existing:
        existing.completed = True
        existing.completed_at = completed_at
        return False

    db.session.add(
        LessonProgress(
            user_id=student_id,
            course_id=course_id,
            lesson_id=lesson_id,
            completed=True,
            completed_at=completed_at,
        )
    )
    return True


def _seed_one_quiz_attempt(student_id, course_id):
    quizzes = Quiz.query.filter_by(course_id=course_id).order_by(Quiz.id.asc()).all()
    if not quizzes:
        return False

    quiz = quizzes[0]
    existing = Progress.query.filter_by(user_id=student_id, quiz_id=quiz.id).first()
    existing_attempt = QuizAttempt.query.filter_by(user_id=student_id, quiz_id=quiz.id).first()
    if existing and existing_attempt:
        return False

    total_questions = max(1, len(quiz.questions))
    score = max(1, total_questions - 1)
    completion_percentage = round((score / total_questions) * 100, 2)

    if not existing:
        db.session.add(
            Progress(
                user_id=student_id,
                quiz_id=quiz.id,
                score=score,
                completion_percentage=completion_percentage,
            )
        )

    if not existing_attempt:
        db.session.add(
            QuizAttempt(
                user_id=student_id,
                quiz_id=quiz.id,
                score=score,
                total_questions=total_questions,
            )
        )

    return True


def seed_demo_progress():
    students = User.query.filter_by(role="student").order_by(User.id.asc()).all()
    courses = Course.query.order_by(Course.id.asc()).all()

    if not students:
        print("No students found. Seed users first.")
        return

    if not courses:
        print("No courses found. Seed courses first.")
        return

    enrolled_count = 0
    progress_count = 0
    quiz_attempt_count = 0

    # Enroll each student in up to first 2 courses and mark a few lessons complete.
    target_courses = courses[:2]

    for student_index, student in enumerate(students):
        for course in target_courses:
            if _ensure_enrollment(student.id, course.id):
                enrolled_count += 1

            lessons = (
                Lesson.query.filter_by(course_id=course.id)
                .order_by(Lesson.order_index.asc(), Lesson.id.asc())
                .all()
            )
            if not lessons:
                continue

            lessons_to_complete = min(len(lessons), 1 + student_index)
            for offset, lesson in enumerate(lessons[:lessons_to_complete]):
                completed_at = datetime.now() - timedelta(days=offset)
                if _ensure_lesson_completion(student.id, course.id, lesson.id, completed_at):
                    progress_count += 1

            if _seed_one_quiz_attempt(student.id, course.id):
                quiz_attempt_count += 1

    db.session.commit()

    print("Demo progress seeding complete.")
    print(f"Enrollments created: {enrolled_count}")
    print(f"Lesson progress rows created: {progress_count}")
    print(f"Quiz attempts created: {quiz_attempt_count}")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_demo_progress()
