from collections import OrderedDict

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func, or_

from adaptive_engine import analyze_user_performance
from database import db
from models import Course, Lesson, LessonProgress, Quiz, QuizAttempt, User


recommendation_bp = Blueprint("recommendations", __name__, url_prefix="/api")


def _is_staff(user: User) -> bool:
    return user.role in {"teacher", "admin"}


def _add_course(rec_map: OrderedDict, course: Course, reason: str, related_topic: str | None = None) -> None:
    if not course or course.id in rec_map:
        return
    rec_map[course.id] = {
        "course_id": course.id,
        "title": course.title,
        "reason": reason,
        "related_topic": related_topic,
    }


def _add_lesson(rec_map: OrderedDict, lesson: Lesson, reason: str, related_topic: str | None = None) -> None:
    if not lesson or lesson.id in rec_map:
        return
    rec_map[lesson.id] = {
        "lesson_id": lesson.id,
        "title": lesson.title,
        "course_id": lesson.course_id,
        "reason": reason,
        "related_topic": related_topic,
    }


def _build_recommendations(user_id: int) -> dict:
    recommended_courses = OrderedDict()
    recommended_lessons = OrderedDict()

    score_pct_expr = (QuizAttempt.score * 100.0) / func.nullif(QuizAttempt.total_questions, 0)

    topic_rows = (
        db.session.query(
            Quiz.topic.label("topic"),
            func.avg(score_pct_expr).label("avg_score"),
        )
        .join(Quiz, Quiz.id == QuizAttempt.quiz_id)
        .filter(QuizAttempt.user_id == user_id)
        .group_by(Quiz.topic)
        .order_by(func.avg(score_pct_expr).asc())
        .all()
    )

    weak_topics = [(row.topic or "General", float(row.avg_score or 0.0)) for row in topic_rows if (row.avg_score or 0) < 50]
    weak_topic_scores = [
        {
            "topic": topic,
            "avg_score_pct": round(avg_score, 1),
        }
        for topic, avg_score in weak_topics
    ]

    # Rule 1: If quiz score is weak (<50%), recommend lessons/courses around that topic.
    for topic, _avg in weak_topics[:3]:
        reason = f"Your quiz scores indicate difficulty with {topic.lower()}."

        topic_courses = (
            Course.query.filter(
                or_(
                    Course.title.ilike(f"%{topic}%"),
                    Course.description.ilike(f"%{topic}%"),
                    Course.id.in_(
                        db.session.query(Quiz.course_id)
                        .filter(Quiz.course_id.isnot(None), Quiz.topic.ilike(f"%{topic}%"))
                        .distinct()
                    ),
                )
            )
            .order_by(Course.created_at.desc())
            .limit(3)
            .all()
        )

        for course in topic_courses:
            _add_course(recommended_courses, course, reason, topic)

        topic_lessons = (
            Lesson.query.join(Course, Course.id == Lesson.course_id)
            .filter(
                or_(
                    Lesson.title.ilike(f"%{topic}%"),
                    Course.title.ilike(f"%{topic}%"),
                    Course.description.ilike(f"%{topic}%"),
                )
            )
            .order_by(Lesson.order_index.asc(), Lesson.id.asc())
            .limit(4)
            .all()
        )

        for lesson in topic_lessons:
            _add_lesson(recommended_lessons, lesson, reason, topic)

    started_course_ids = {
        row.course_id
        for row in db.session.query(LessonProgress.course_id)
        .filter(LessonProgress.user_id == user_id)
        .distinct()
        .all()
    }

    # Rule 2: If a started course isn't complete, recommend the next lesson.
    for course_id in started_course_ids:
        total_lessons = Lesson.query.filter_by(course_id=course_id).count()
        if total_lessons == 0:
            continue

        completed_lesson_ids = {
            row.lesson_id
            for row in db.session.query(LessonProgress.lesson_id)
            .filter_by(user_id=user_id, course_id=course_id, completed=True)
            .all()
        }

        if len(completed_lesson_ids) >= total_lessons:
            continue

        pending_query = Lesson.query.filter(Lesson.course_id == course_id)
        if completed_lesson_ids:
            pending_query = pending_query.filter(~Lesson.id.in_(completed_lesson_ids))

        next_lesson = pending_query.order_by(Lesson.order_index.asc(), Lesson.id.asc()).first()
        course = Course.query.get(course_id)
        if next_lesson and course:
            _add_lesson(
                recommended_lessons,
                next_lesson,
                f"Continue {course.title} with the next lesson.",
            )

    # Rule 3: If user has not started a course, prioritize beginner-style courses.
    not_started_query = Course.query
    if started_course_ids:
        not_started_query = not_started_query.filter(~Course.id.in_(started_course_ids))
    not_started_courses = not_started_query.order_by(Course.created_at.desc()).all()

    beginner_keywords = ("beginner", "basics", "intro", "introduction", "fundamentals")
    beginner_courses = [
        c
        for c in not_started_courses
        if any(
            keyword in (c.title or "").lower() or keyword in (c.description or "").lower()
            for keyword in beginner_keywords
        )
    ]

    if beginner_courses:
        for course in beginner_courses[:3]:
            _add_course(
                recommended_courses,
                course,
                "You have not started this beginner-friendly course yet.",
            )
    else:
        for course in not_started_courses[:3]:
            _add_course(
                recommended_courses,
                course,
                "You have not started this course yet.",
            )

    return {
        "recommended_courses": list(recommended_courses.values())[:5],
        "recommended_lessons": list(recommended_lessons.values())[:6],
        "ai_signals": {
            "weak_topics": weak_topic_scores,
            "rule_notes": [
                "If quiz score is below 50%, recommend lessons/courses from the same topic.",
                "If a course is started but incomplete, recommend the next lesson.",
                "If a course is not started, recommend beginner-friendly courses first.",
            ],
        },
    }


@recommendation_bp.get("/recommendations")
@jwt_required()
def get_recommendations():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = analyze_user_performance(user_id)
    return jsonify(data)


@recommendation_bp.get("/recommendations/<int:user_id>")
@jwt_required()
def get_recommendations_for_user(user_id: int):
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    if current_user.id != user_id and not _is_staff(current_user):
        return jsonify({"error": "Unauthorized access to recommendations"}), 403

    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"error": "Target user not found"}), 404

    return jsonify(_build_recommendations(user_id)), 200
