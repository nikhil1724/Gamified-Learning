from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db
from models import CodingProblem, Course, Lesson, Problem, ProblemTestCase, User


coding_admin_bp = Blueprint("coding_admin", __name__, url_prefix="/api/admin")


def role_required(required_roles=None):
    """Allow multiple roles. If required_roles is None, only admin is required."""
    if required_roles is None:
        required_roles = ["admin"]
    elif isinstance(required_roles, str):
        required_roles = [required_roles]
    
    def decorator(handler):
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id)) if user_id is not None else None
            if not user:
                return jsonify({"success": False, "error": "User not found"}), 404
            if user.role not in required_roles:
                return (
                    jsonify({"success": False, "error": "Admin or Teacher access required"}),
                    403,
                )
            return handler(*args, **kwargs)

        wrapper.__name__ = handler.__name__
        return wrapper

    return decorator


def _get_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return None, (jsonify({"success": False, "error": "Course not found"}), 404)
    return course, None


@coding_admin_bp.post("/problems")
@role_required(["admin", "teacher"])
def create_problem():
    payload = request.get_json(silent=True) or {}
    required = ["title", "difficulty", "description"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        return jsonify({"success": False, "error": "Missing fields", "fields": missing}), 400

    if payload.get("difficulty") not in {"Easy", "Medium", "Hard"}:
        return jsonify({"success": False, "error": "Invalid difficulty"}), 400

    user_id = get_jwt_identity()
    user = User.query.get(int(user_id)) if user_id is not None else None
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    problem = Problem(
        title=payload["title"].strip(),
        difficulty=payload["difficulty"],
        tags=payload.get("tags") or [],
        description=payload["description"],
        constraints=payload.get("constraints"),
        example_input=payload.get("example_input"),
        example_output=payload.get("example_output"),
        created_by=user.id,
    )
    db.session.add(problem)
    db.session.commit()

    return jsonify({"success": True, "data": {"id": problem.id}}), 201


@coding_admin_bp.post("/course")
@role_required(["admin", "teacher"])
def create_course():
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    description = (payload.get("description") or "").strip() or None

    if not title:
        return jsonify({"success": False, "error": "Title is required"}), 400

    user_id = get_jwt_identity()
    course = Course(title=title, description=description, teacher_id=int(user_id))
    db.session.add(course)
    db.session.commit()

    return jsonify({"success": True, "data": {"id": course.id}}), 201


@coding_admin_bp.put("/problems/<int:problem_id>")
@role_required(["admin", "teacher"])
def update_problem(problem_id):
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({"success": False, "error": "Problem not found"}), 404

    payload = request.get_json(silent=True) or {}
    for field in ["title", "difficulty", "tags", "description", "constraints", "example_input", "example_output"]:
        if field in payload:
            setattr(problem, field, payload[field])

    db.session.commit()
    return jsonify({"success": True, "data": {"id": problem.id}})


@coding_admin_bp.post("/problems/<int:problem_id>/test-cases")
@role_required(["admin", "teacher"])
def create_test_case(problem_id):
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({"success": False, "error": "Problem not found"}), 404

    payload = request.get_json(silent=True) or {}
    required = ["input_data", "expected_output"]
    missing = [field for field in required if payload.get(field) is None]
    if missing:
        return jsonify({"success": False, "error": "Missing fields", "fields": missing}), 400

    test_case = ProblemTestCase(
        problem_id=problem.id,
        input_data=payload["input_data"],
        expected_output=payload["expected_output"],
        is_hidden=bool(payload.get("is_hidden", False)),
    )
    db.session.add(test_case)
    db.session.commit()

    return jsonify({"success": True, "data": {"id": test_case.id}}), 201


@coding_admin_bp.put("/test-cases/<int:test_case_id>")
@role_required(["admin", "teacher"])
def update_test_case(test_case_id):
    test_case = ProblemTestCase.query.get(test_case_id)
    if not test_case:
        return jsonify({"success": False, "error": "Test case not found"}), 404

    payload = request.get_json(silent=True) or {}
    for field in ["input_data", "expected_output", "is_hidden"]:
        if field in payload:
            setattr(test_case, field, payload[field])

    db.session.commit()
    return jsonify({"success": True, "data": {"id": test_case.id}})


@coding_admin_bp.delete("/test-cases/<int:test_case_id>")
@role_required(["admin", "teacher"])
def delete_test_case(test_case_id):
    test_case = ProblemTestCase.query.get(test_case_id)
    if not test_case:
        return jsonify({"success": False, "error": "Test case not found"}), 404

    db.session.delete(test_case)
    db.session.commit()

    return jsonify({"success": True, "data": {"id": test_case_id}})


@coding_admin_bp.post("/lessons")
@role_required(["admin", "teacher"])
def create_lesson():
    payload = request.get_json(silent=True) or {}
    required = ["course_id", "title", "content"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        return jsonify({"success": False, "error": "Missing fields", "fields": missing}), 400

    course, error_response = _get_course(payload.get("course_id"))
    if error_response:
        return error_response

    lesson = Lesson(
        course_id=course.id,
        title=payload["title"].strip(),
        content=payload["content"],
        video_url=payload.get("video_url"),
        audio_url=payload.get("audio_url"),
        order_index=int(payload.get("order_index") or 0),
    )
    db.session.add(lesson)
    db.session.commit()

    return jsonify({"success": True, "data": {"id": lesson.id}}), 201


@coding_admin_bp.post("/course/<int:course_id>/lesson")
@role_required(["admin", "teacher"])
def create_lesson_for_course(course_id):
    payload = request.get_json(silent=True) or {}
    required = ["title", "content"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        return jsonify({"success": False, "error": "Missing fields", "fields": missing}), 400

    course, error_response = _get_course(course_id)
    if error_response:
        return error_response

    lesson = Lesson(
        course_id=course.id,
        title=payload["title"].strip(),
        content=payload["content"],
        video_url=payload.get("video_url"),
        audio_url=payload.get("audio_url"),
        order_index=int(payload.get("order_index") or 0),
    )
    db.session.add(lesson)
    db.session.commit()

    return jsonify({"success": True, "data": {"id": lesson.id}}), 201


@coding_admin_bp.put("/lessons/<int:lesson_id>")
@role_required(["admin", "teacher"])
def update_lesson(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"success": False, "error": "Lesson not found"}), 404

    payload = request.get_json(silent=True) or {}
    for field in ["title", "content", "video_url", "audio_url", "order_index", "course_id"]:
        if field in payload:
            setattr(lesson, field, payload[field])

    db.session.commit()
    return jsonify({"success": True, "data": {"id": lesson.id}})


@coding_admin_bp.delete("/lessons/<int:lesson_id>")
@role_required(["admin", "teacher"])
def delete_lesson(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"success": False, "error": "Lesson not found"}), 404

    db.session.delete(lesson)
    db.session.commit()

    return jsonify({"success": True, "data": {"id": lesson_id}})


@coding_admin_bp.post("/coding-problems")
@role_required(["admin", "teacher"])
def create_coding_problem():
    payload = request.get_json(silent=True) or {}
    required = ["course_id", "title", "difficulty", "description"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        return jsonify({"success": False, "error": "Missing fields", "fields": missing}), 400

    if payload.get("difficulty") not in {"Easy", "Medium", "Hard"}:
        return jsonify({"success": False, "error": "Invalid difficulty"}), 400

    course, error_response = _get_course(payload.get("course_id"))
    if error_response:
        return error_response

    user_id = get_jwt_identity()
    problem = CodingProblem(
        course_id=course.id,
        title=payload["title"].strip(),
        difficulty=payload["difficulty"],
        tags=payload.get("tags") or [],
        description=payload["description"],
        constraints=payload.get("constraints"),
        example_input=payload.get("example_input"),
        example_output=payload.get("example_output"),
        created_by=int(user_id) if user_id is not None else None,
    )
    db.session.add(problem)
    db.session.commit()

    return jsonify({"success": True, "data": {"id": problem.id}}), 201


@coding_admin_bp.put("/coding-problems/<int:problem_id>")
@role_required(["admin", "teacher"])
def update_coding_problem(problem_id):
    problem = CodingProblem.query.get(problem_id)
    if not problem:
        return jsonify({"success": False, "error": "Coding problem not found"}), 404

    payload = request.get_json(silent=True) or {}
    if "difficulty" in payload and payload["difficulty"] not in {"Easy", "Medium", "Hard"}:
        return jsonify({"success": False, "error": "Invalid difficulty"}), 400

    for field in [
        "title",
        "difficulty",
        "tags",
        "description",
        "constraints",
        "example_input",
        "example_output",
        "course_id",
    ]:
        if field in payload:
            setattr(problem, field, payload[field])

    db.session.commit()
    return jsonify({"success": True, "data": {"id": problem.id}})


@coding_admin_bp.delete("/coding-problems/<int:problem_id>")
@role_required(["admin", "teacher"])
def delete_coding_problem(problem_id):
    problem = CodingProblem.query.get(problem_id)
    if not problem:
        return jsonify({"success": False, "error": "Coding problem not found"}), 404

    db.session.delete(problem)
    db.session.commit()

    return jsonify({"success": True, "data": {"id": problem_id}})
