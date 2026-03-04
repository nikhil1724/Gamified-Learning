from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm import joinedload

from database import db
from models import CodingProblem, Course, Enrollment, Lesson, Quiz, User
from routes.notification_routes import create_notification


course_bp = Blueprint("courses", __name__, url_prefix="/api")


def _get_teacher():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id)) if user_id is not None else None
    if not user:
        return None, (jsonify({"error": "User not found"}), 404)
    if user.role not in {"teacher", "admin"}:
        return None, (jsonify({"error": "Teacher access required"}), 403)
    if user.role == "teacher" and not user.is_approved:
        return None, (jsonify({"error": "Teacher approval pending"}), 403)
    return user, None


def _get_student():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id)) if user_id is not None else None
    if not user:
        return None, (jsonify({"error": "User not found"}), 404)
    if user.role != "student":
        return None, (jsonify({"error": "Student access required"}), 403)
    return user, None


def _get_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return None, (jsonify({"error": "Course not found"}), 404)
    return course, None


@course_bp.post("/teacher/courses")
@jwt_required()
def create_course():
    user, error_response = _get_teacher()
    if error_response:
        return error_response

    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    description = (payload.get("description") or "").strip() or None

    if not title:
        return jsonify({"error": "Title is required"}), 400

    course = Course(title=title, description=description, teacher_id=user.id)
    db.session.add(course)
    db.session.commit()

    return (
        jsonify(
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "teacher_id": course.teacher_id,
                "created_at": course.created_at.isoformat(),
            }
        ),
        201,
    )


@course_bp.get("/teacher/courses")
@jwt_required()
def list_teacher_courses():
    user, error_response = _get_teacher()
    if error_response:
        return error_response

    courses = (
        Course.query.filter_by(teacher_id=user.id)
        .order_by(Course.created_at.desc())
        .all()
    )

    return jsonify(
        [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "teacher_id": course.teacher_id,
                "created_at": course.created_at.isoformat(),
            }
            for course in courses
        ]
    )


@course_bp.get("/courses")
@jwt_required()
def list_courses():
    courses = Course.query.options(joinedload(Course.teacher)).all()

    return jsonify(
        [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "teacher_name": course.teacher.name if course.teacher else None,
                "created_at": course.created_at.isoformat(),
            }
            for course in courses
        ]
    )


@course_bp.get("/course/<int:course_id>")
@jwt_required()
def get_course(course_id):
    course, error_response = _get_course(course_id)
    if error_response:
        return error_response

    return jsonify(
        {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "teacher_id": course.teacher_id,
            "teacher_name": course.teacher.name if course.teacher else None,
            "created_at": course.created_at.isoformat(),
        }
    )


@course_bp.get("/course/<int:course_id>/lessons")
@jwt_required()
def list_lessons(course_id):
    course, error_response = _get_course(course_id)
    if error_response:
        return error_response

    lessons = (
        Lesson.query.filter_by(course_id=course.id)
        .order_by(Lesson.order_index.asc(), Lesson.created_at.asc())
        .all()
    )

    return jsonify(
        [
            {
                "id": lesson.id,
                "course_id": lesson.course_id,
                "title": lesson.title,
                "content": lesson.content,
                "video_url": lesson.video_url,
                "audio_url": lesson.audio_url,
                "order_index": lesson.order_index,
                "created_at": lesson.created_at.isoformat(),
            }
            for lesson in lessons
        ]
    )


@course_bp.get("/course/<int:course_id>/quizzes")
@jwt_required()
def list_course_quizzes(course_id):
    course, error_response = _get_course(course_id)
    if error_response:
        return error_response

    quizzes = (
        Quiz.query.filter_by(course_id=course.id)
        .order_by(Quiz.id.desc())
        .all()
    )

    return jsonify(
        [
            {
                "id": quiz.id,
                "title": quiz.title,
                "topic": quiz.topic,
                "difficulty": quiz.difficulty,
                "course_id": quiz.course_id,
            }
            for quiz in quizzes
        ]
    )


@course_bp.get("/course/<int:course_id>/problems")
@jwt_required()
def list_course_problems(course_id):
    course, error_response = _get_course(course_id)
    if error_response:
        return error_response

    problems = (
        CodingProblem.query.filter_by(course_id=course.id)
        .order_by(CodingProblem.created_at.desc())
        .all()
    )

    return jsonify(
        [
            {
                "id": problem.id,
                "title": problem.title,
                "difficulty": problem.difficulty,
                "tags": problem.tags or [],
                "course_id": problem.course_id,
            }
            for problem in problems
        ]
    )


@course_bp.post("/student/enroll")
@jwt_required()
def enroll_in_course():
    user, error_response = _get_student()
    if error_response:
        return error_response

    payload = request.get_json(silent=True) or {}
    course_id = payload.get("course_id")

    if not course_id:
        return jsonify({"error": "Course ID is required"}), 400

    course, error_response = _get_course(course_id)
    if error_response:
        return error_response

    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        student_id=user.id, course_id=course_id
    ).first()
    if existing_enrollment:
        return jsonify({"error": "Already enrolled in this course"}), 400

    # Create enrollment
    enrollment = Enrollment(student_id=user.id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()

    # Create notification for course enrollment
    create_notification(
        user_id=user.id,
        notification_type="COURSE_ADDED",
        title="Course Enrolled!",
        message=f"You've successfully enrolled in '{course.title}'!",
        data={
            "course_id": course.id,
            "course_title": course.title,
            "teacher_name": course.teacher.name if course.teacher else None,
        }
    )

    return (
        jsonify(
            {
                "message": "Enrollment successful",
                "course_id": course.id,
                "course_title": course.title,
                "enrolled_at": enrollment.enrolled_at.isoformat(),
            }
        ),
        201,
    )


@course_bp.get("/student/courses")
@jwt_required()
def list_student_courses():
    user, error_response = _get_student()
    if error_response:
        return error_response

    enrollments = (
        Enrollment.query.options(joinedload(Enrollment.course).joinedload(Course.teacher))
        .filter_by(student_id=user.id)
        .order_by(Enrollment.enrolled_at.desc())
        .all()
    )

    return jsonify(
        [
            {
                "id": enrollment.course.id,
                "title": enrollment.course.title,
                "description": enrollment.course.description,
                "teacher_name": (
                    enrollment.course.teacher.name
                    if enrollment.course.teacher
                    else None
                ),
                "enrollment_date": enrollment.enrolled_at.isoformat(),
            }
            for enrollment in enrollments
            if enrollment.course
        ]
    )
