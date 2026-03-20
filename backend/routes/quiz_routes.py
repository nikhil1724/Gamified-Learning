from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import re

from database import db
from activity_service import record_learning_activity, update_user_streak
from badge_service import assign_eligible_badges
from leaderboard_service import broadcast_leaderboard_update
from models import Course, Enrollment, Progress, Question, Quiz, QuizAttempt, User
from routes.reward_routes import check_and_unlock_rewards
from routes.skill_routes import unlock_skills_for_quiz
from routes.notification_routes import create_notification


quiz_bp = Blueprint("quizzes", __name__, url_prefix="/api")


def _serialize_quiz(quiz: Quiz) -> dict:
    title = quiz.title or ""
    xp_match = re.search(r"xp\s*(\d+)", title, re.IGNORECASE)
    xp_reward = int(xp_match.group(1)) if xp_match else (10 if quiz.difficulty == "Easy" else 20 if quiz.difficulty == "Medium" else 30)
    return {
        "id": quiz.id,
        "title": quiz.title,
        "topic": quiz.topic,
        "difficulty": quiz.difficulty,
        "course_id": quiz.course_id,
        "xp_reward": xp_reward,
        "question_count": len(quiz.questions),
    }


def _serialize_question(question: Question) -> dict:
    return {
        "id": question.id,
        "question_text": question.question_text,
        "option_a": question.option_a,
        "option_b": question.option_b,
        "option_c": question.option_c,
        "option_d": question.option_d,
        "explanation": getattr(question, "explanation", None),
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
    question_results = []

    for question in quiz.questions:
        answer = answers.get(str(question.id)) or answers.get(question.id)
        normalized_answer = str(answer).strip().upper() if answer is not None else None
        correct_option = str(question.correct_option).strip().upper()
        is_correct = normalized_answer == correct_option if normalized_answer is not None else False

        if answer is None:
            question_results.append(
                {
                    "question_id": question.id,
                    "question_text": question.question_text,
                    "selected_option": None,
                    "correct_option": correct_option,
                    "is_correct": False,
                    "explanation": getattr(question, "explanation", None),
                }
            )
            continue

        answered_count += 1
        if is_correct:
            score += 1

        question_results.append(
            {
                "question_id": question.id,
                "question_text": question.question_text,
                "selected_option": normalized_answer,
                "correct_option": correct_option,
                "is_correct": is_correct,
                "explanation": getattr(question, "explanation", None),
            }
        )

    completion_percentage = (answered_count / total_questions) * 100
    xp_earned = score * 10
    coins_earned = score
    client_timezone = request.headers.get("X-User-Timezone")

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

    quiz_attempt = QuizAttempt(
        user_id=user.id,
        quiz_id=quiz.id,
        score=score,
        total_questions=total_questions,
    )
    db.session.add(quiz_attempt)

    streak_info = update_user_streak(user=user, user_timezone=client_timezone)
    record_learning_activity(
        user_id=user.id,
        user_timezone=client_timezone,
        auto_commit=False,
    )
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

    unlocked_rewards = check_and_unlock_rewards(
        user=user,
        first_quiz_completed=existing_progress_count == 0,
    )
    
    # Create notifications for unlocked badges
    for badge in unlocked_rewards:
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

    unlocked_badges = assign_eligible_badges(user=user, trigger="quiz_complete")
    db.session.commit()

    for badge in unlocked_badges:
        create_notification(
            user_id=user.id,
            notification_type="BADGE_EARNED",
            title="Achievement Unlocked!",
            message=f"You earned '{badge['name']}' {badge['icon'] or '🏅'}",
            data={
                "badge_id": badge["id"],
                "badge_name": badge["name"],
                "badge_description": badge["description"],
                "badge_icon": badge["icon"],
            },
        )
    
    unlocked_skills = unlock_skills_for_quiz(user=user, quiz=quiz)
    broadcast_leaderboard_update()

    return jsonify(
        {
            "score": score,
            "total_questions": total_questions,
            "percentage": round((score / max(total_questions, 1)) * 100, 1),
            "xp_earned": xp_earned,
            "coins_earned": coins_earned,
            "attempted_at": quiz_attempt.attempted_at.isoformat() if quiz_attempt.attempted_at else None,
            "question_results": question_results,
            "streak_count": streak_info["current_streak"],
            "longest_streak": streak_info["longest_streak"],
            "last_active_date": streak_info["last_active_date"],
            "unlocked_rewards": unlocked_rewards,
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


@quiz_bp.get("/quiz/history")
@jwt_required()
def get_quiz_history():
    user = _get_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    attempts = (
        QuizAttempt.query.filter_by(user_id=user.id)
        .order_by(QuizAttempt.attempted_at.desc())
        .limit(30)
        .all()
    )

    if attempts:
        return jsonify(
            [
                {
                    "attempt_id": attempt.id,
                    "quiz_id": attempt.quiz_id,
                    "quiz_title": attempt.quiz.title if attempt.quiz else "Quiz",
                    "topic": attempt.quiz.topic if attempt.quiz else None,
                    "difficulty": attempt.quiz.difficulty if attempt.quiz else None,
                    "score": attempt.score,
                    "total_questions": attempt.total_questions,
                    "percentage": round((attempt.score / max(attempt.total_questions, 1)) * 100, 1),
                    "attempted_at": attempt.attempted_at.isoformat(),
                }
                for attempt in attempts
            ]
        )

    fallback_progress = (
        Progress.query.filter_by(user_id=user.id)
        .order_by(Progress.attempted_at.desc())
        .limit(30)
        .all()
    )

    return jsonify(
        [
            {
                "attempt_id": entry.id,
                "quiz_id": entry.quiz_id,
                "quiz_title": entry.quiz.title if entry.quiz else "Quiz",
                "topic": entry.quiz.topic if entry.quiz else None,
                "difficulty": entry.quiz.difficulty if entry.quiz else None,
                "score": entry.score,
                "total_questions": len(entry.quiz.questions) if entry.quiz and entry.quiz.questions else 1,
                "percentage": round(entry.completion_percentage or 0, 1),
                "attempted_at": entry.attempted_at.isoformat(),
            }
            for entry in fallback_progress
        ]
    )
