from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db
from models import Course, Enrollment, Progress, Question, Quiz, User
from routes.reward_routes import check_and_unlock_rewards
from routes.skill_routes import unlock_skills_for_quiz
from routes.notification_routes import create_notification


quiz_bp = Blueprint("quizzes", __name__, url_prefix="/api")


def _serialize_quiz(quiz: Quiz) -> dict:
    return {
        "id": quiz.id,
        "title": quiz.title,
        "topic": quiz.topic,
        "difficulty": quiz.difficulty,
        "course_id": quiz.course_id,
    }


def _serialize_question(question: Question) -> dict:
    return {
        "id": question.id,
        "question_text": question.question_text,
        "option_a": question.option_a,
        "option_b": question.option_b,
        "option_c": question.option_c,
        "option_d": question.option_d,
    }


def _get_user():
    user_id = get_jwt_identity()
    if user_id is None:
        return None
    return User.query.get(int(user_id))


def _teacher_required(user):
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.role not in {"teacher", "admin"}:
        return jsonify({"error": "Teacher access required"}), 403
    if user.role == "teacher" and not user.is_approved:
        return jsonify({"error": "Teacher approval pending"}), 403
    return None


@quiz_bp.get("/quizzes")
def list_quizzes():
    quizzes = Quiz.query.all()
    return jsonify([_serialize_quiz(quiz) for quiz in quizzes])


@quiz_bp.get("/quiz/<int:quiz_id>")
def quiz_details(quiz_id: int):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    return jsonify(
        {
            **_serialize_quiz(quiz),
            "questions": [_serialize_question(q) for q in quiz.questions],
        }
    )


@quiz_bp.post("/teacher/quizzes")
@jwt_required()
def create_quiz():
    user = _get_user()
    error_response = _teacher_required(user)
    if error_response:
        return error_response

    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    topic = (payload.get("topic") or "").strip()
    difficulty = (payload.get("difficulty") or "").strip()
    course_id = payload.get("course_id")
    skill_id = payload.get("skill_id")

    if not title or not topic or not difficulty or not course_id:
        return jsonify({"error": "Title, topic, difficulty, and course are required"}), 400

    if difficulty not in {"Easy", "Medium", "Hard"}:
        return jsonify({"error": "Invalid difficulty"}), 400

    course = Course.query.get(int(course_id))
    if not course:
        return jsonify({"error": "Course not found"}), 404

    if user.role == "teacher" and course.teacher_id != user.id:
        return jsonify({"error": "You do not own this course"}), 403

    quiz = Quiz(
        title=title,
        topic=topic,
        difficulty=difficulty,
        course_id=course.id,
        skill_id=skill_id,
    )
    db.session.add(quiz)
    db.session.commit()

    return jsonify(_serialize_quiz(quiz)), 201


@quiz_bp.post("/quiz/submit")
@jwt_required()
def submit_quiz():
    data = request.get_json(silent=True) or {}
    quiz_id = data.get("quiz_id")
    answers = data.get("answers")

    if not quiz_id or not isinstance(answers, dict):
        return jsonify({"error": "Missing or invalid fields"}), 400

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    total_questions = len(quiz.questions)
    if total_questions == 0:
        return jsonify({"error": "Quiz has no questions"}), 400

    score = 0
    answered_count = 0

    for question in quiz.questions:
        answer = answers.get(str(question.id)) or answers.get(question.id)
        if answer is None:
            continue
        answered_count += 1
        if str(answer).strip().lower() == question.correct_option.lower():
            score += 1

    completion_percentage = (answered_count / total_questions) * 100
    xp_earned = score * 10
    coins_earned = score

    existing_progress_count = Progress.query.filter_by(user_id=user.id).count()

    user.xp_points += xp_earned
    user.coins += coins_earned

    progress = Progress(
        user_id=user.id,
        quiz_id=quiz.id,
        score=score,
        completion_percentage=completion_percentage,
    )
    db.session.add(progress)
    db.session.commit()

    # Create notification for quiz completion and XP earned
    create_notification(
        user_id=user.id,
        notification_type="QUIZ_COMPLETED",
        title="Quiz Completed!",
        message=f"You completed '{quiz.title}' and earned {xp_earned} XP!",
        data={
            "quiz_id": quiz.id,
            "quiz_title": quiz.title,
            "score": score,
            "total_questions": total_questions,
            "xp_earned": xp_earned,
            "coins_earned": coins_earned,
        }
    )

    unlocked_badges = check_and_unlock_rewards(
        user=user,
        first_quiz_completed=existing_progress_count == 0,
    )
    
    # Create notifications for unlocked badges
    for badge in unlocked_badges:
        create_notification(
            user_id=user.id,
            notification_type="BADGE_EARNED",
            title="Badge Earned! 🏆",
            message=f"You earned the '{badge['badge_name']}' badge!",
            data={
                "badge_id": badge["id"],
                "badge_name": badge["badge_name"],
                "badge_description": badge["description"],
            }
        )
    
    unlocked_skills = unlock_skills_for_quiz(user=user, quiz=quiz)

    return jsonify(
        {
            "score": score,
            "total_questions": total_questions,
            "xp_earned": xp_earned,
            "coins_earned": coins_earned,
            "unlocked_badges": unlocked_badges,
            "unlocked_skills": unlocked_skills,
        }
    )


@quiz_bp.get("/courses/<int:course_id>/quizzes")
@jwt_required()
def list_course_quizzes(course_id: int):
    user = _get_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    is_teacher = user.role == "teacher" and course.teacher_id == user.id
    is_enrolled = (
        Enrollment.query.filter_by(student_id=user.id, course_id=course.id).first()
        is not None
    )

    if not (is_teacher or is_enrolled):
        return jsonify({"error": "Access denied"}), 403

    quizzes = Quiz.query.filter_by(course_id=course.id).all()
    return jsonify([_serialize_quiz(quiz) for quiz in quizzes])
