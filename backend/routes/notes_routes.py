from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db
from models import Course, Enrollment, Note, User


notes_bp = Blueprint("notes", __name__, url_prefix="/api")


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


@notes_bp.post("/teacher/notes")
@jwt_required()
def create_note():
    user = _get_user()
    error_response = _teacher_required(user)
    if error_response:
        return error_response

    payload = request.get_json(silent=True) or {}
    course_id = payload.get("course_id")
    title = (payload.get("title") or "").strip()
    content = (payload.get("content") or "").strip() or None
    file_url = (payload.get("file_url") or "").strip() or None

    if not course_id or not title:
        return jsonify({"error": "Course and title are required"}), 400

    if not content and not file_url:
        return jsonify({"error": "Content or file_url is required"}), 400

    course = Course.query.get(int(course_id))
    if not course:
        return jsonify({"error": "Course not found"}), 404

    if course.teacher_id != user.id:
        return jsonify({"error": "You do not own this course"}), 403

    note = Note(
        course_id=course.id,
        title=title,
        content=content,
        file_url=file_url,
        uploaded_by=user.id,
    )
    db.session.add(note)
    db.session.commit()

    return (
        jsonify(
            {
                "id": note.id,
                "course_id": note.course_id,
                "title": note.title,
                "content": note.content,
                "file_url": note.file_url,
                "uploaded_by": note.uploaded_by,
                "created_at": note.created_at.isoformat(),
            }
        ),
        201,
    )


@notes_bp.get("/courses/<int:course_id>/notes")
@jwt_required()
def list_course_notes(course_id):
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

    notes = Note.query.filter_by(course_id=course.id).order_by(Note.created_at.desc()).all()

    return jsonify(
        [
            {
                "id": note.id,
                "course_id": note.course_id,
                "title": note.title,
                "content": note.content,
                "file_url": note.file_url,
                "uploaded_by": note.uploaded_by,
                "created_at": note.created_at.isoformat(),
            }
            for note in notes
        ]
    )
