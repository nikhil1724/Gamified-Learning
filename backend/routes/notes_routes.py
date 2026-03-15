import os
import uuid

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from database import db
from models import Course, Enrollment, Note, User


notes_bp = Blueprint("notes", __name__, url_prefix="/api")

ALLOWED_EXTENSIONS = {"pdf"}
MAX_PDF_BYTES = 20 * 1024 * 1024  # 20 MB
VALID_DIFFICULTIES = {"Beginner", "Intermediate", "Advanced"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _uploads_dir() -> str:
    uploads = current_app.config.get("UPLOAD_DIR") or os.path.join(current_app.root_path, "uploads")
    os.makedirs(uploads, exist_ok=True)
    return uploads


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


def _serialize_note(note):
    return {
        "id": note.id,
        "course_id": note.course_id,
        "title": note.title,
        "lesson_number": note.lesson_number,
        "topic": note.topic,
        "objectives": note.objectives,
        "duration": note.duration,
        "difficulty": note.difficulty,
        "video_url": note.video_url,
        "content": note.content,
        "file_url": note.file_url,
        "uploaded_by": note.uploaded_by,
        "created_at": note.created_at.isoformat(),
    }


def _extract_lesson_fields_from_form():
    def _str(key):
        return request.form.get(key, "").strip() or None

    lesson_number_raw = request.form.get("lesson_number", "").strip()
    lesson_number = int(lesson_number_raw) if lesson_number_raw.isdigit() else None

    duration_raw = request.form.get("duration", "").strip()
    duration = int(duration_raw) if duration_raw.isdigit() else None

    difficulty = request.form.get("difficulty", "").strip() or None
    if difficulty and difficulty not in VALID_DIFFICULTIES:
        difficulty = None

    return {
        "lesson_number": lesson_number,
        "topic": _str("topic"),
        "objectives": _str("objectives"),
        "duration": duration,
        "difficulty": difficulty,
        "video_url": _str("video_url"),
        "content": _str("content"),
    }


def _get_owned_note(note_id: int, user):
    note = Note.query.get(note_id)
    if not note:
        return None, (jsonify({"error": "Lesson not found"}), 404)

    course = Course.query.get(note.course_id)
    if not course:
        return None, (jsonify({"error": "Course not found"}), 404)

    is_admin = user.role == "admin"
    if not is_admin and course.teacher_id != user.id:
        return None, (jsonify({"error": "You do not own this lesson"}), 403)

    return note, None


def _delete_uploaded_file(file_url: str | None) -> None:
    if not file_url:
        return
    prefix = "/api/uploads/"
    if not file_url.startswith(prefix):
        return
    filename = secure_filename(file_url[len(prefix):])
    file_path = os.path.join(_uploads_dir(), filename)
    if os.path.exists(file_path):
        os.remove(file_path)


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

    if not course_id or not title:
        return jsonify({"error": "Course and title are required"}), 400

    lesson_number_raw = str(payload.get("lesson_number") or "")
    lesson_number = int(lesson_number_raw) if lesson_number_raw.isdigit() else None

    duration_raw = str(payload.get("duration") or "")
    duration = int(duration_raw) if duration_raw.isdigit() else None

    difficulty = (payload.get("difficulty") or "").strip() or None
    if difficulty and difficulty not in VALID_DIFFICULTIES:
        difficulty = None

    topic = (payload.get("topic") or "").strip() or None
    objectives = (payload.get("objectives") or "").strip() or None
    video_url = (payload.get("video_url") or "").strip() or None
    content = (payload.get("content") or "").strip() or None
    file_url = (payload.get("file_url") or "").strip() or None

    if not any([content, file_url, objectives, video_url]):
        return jsonify({"error": "Provide at least one of: content, PDF, video link, or objectives"}), 400

    course = Course.query.get(int(course_id))
    if not course:
        return jsonify({"error": "Course not found"}), 404
    if user.role != "admin" and course.teacher_id != user.id:
        return jsonify({"error": "You do not own this course"}), 403

    note = Note(
        course_id=course.id,
        title=title,
        lesson_number=lesson_number,
        topic=topic,
        objectives=objectives,
        duration=duration,
        difficulty=difficulty,
        video_url=video_url,
        content=content,
        file_url=file_url,
        uploaded_by=user.id,
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(_serialize_note(note)), 201


@notes_bp.post("/teacher/notes/upload-pdf")
@jwt_required()
def upload_note_pdf():
    user = _get_user()
    error_response = _teacher_required(user)
    if error_response:
        return error_response

    course_id = request.form.get("course_id", "").strip()
    title = request.form.get("title", "").strip()

    if not course_id or not title:
        return jsonify({"error": "Course and title are required"}), 400

    fields = _extract_lesson_fields_from_form()
    file_url = None
    pdf_file = request.files.get("file")

    if pdf_file and pdf_file.filename:
        if not _allowed_file(pdf_file.filename):
            return jsonify({"error": "Only PDF files are allowed"}), 400
        file_bytes = pdf_file.read()
        if len(file_bytes) > MAX_PDF_BYTES:
            return jsonify({"error": "File exceeds the 20 MB limit"}), 413
        safe_name = secure_filename(pdf_file.filename)
        unique_name = f"{uuid.uuid4().hex}_{safe_name}"
        with open(os.path.join(_uploads_dir(), unique_name), "wb") as file_handle:
            file_handle.write(file_bytes)
        file_url = f"/api/uploads/{unique_name}"

    if not any([fields["content"], file_url, fields["objectives"], fields["video_url"]]):
        return jsonify({"error": "Provide at least one of: content, PDF, video link, or objectives"}), 400

    course = Course.query.get(int(course_id))
    if not course:
        return jsonify({"error": "Course not found"}), 404
    if user.role != "admin" and course.teacher_id != user.id:
        return jsonify({"error": "You do not own this course"}), 403

    note = Note(
        course_id=course.id,
        title=title,
        lesson_number=fields["lesson_number"],
        topic=fields["topic"],
        objectives=fields["objectives"],
        duration=fields["duration"],
        difficulty=fields["difficulty"],
        video_url=fields["video_url"],
        content=fields["content"],
        file_url=file_url,
        uploaded_by=user.id,
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(_serialize_note(note)), 201


@notes_bp.delete("/teacher/notes/<int:note_id>/pdf")
@jwt_required()
def delete_note_pdf(note_id):
    user = _get_user()
    error_response = _teacher_required(user)
    if error_response:
        return error_response

    note, note_error = _get_owned_note(note_id, user)
    if note_error:
        return note_error

    if not note.file_url:
        return jsonify({"error": "This lesson does not have a PDF attached"}), 400

    _delete_uploaded_file(note.file_url)
    note.file_url = None

    if not any([note.content, note.objectives, note.video_url]):
        db.session.delete(note)
        db.session.commit()
        return jsonify({"deleted": True, "action": "lesson_deleted"})

    db.session.commit()
    return jsonify({"deleted": True, "action": "pdf_deleted", "note": _serialize_note(note)})


@notes_bp.get("/uploads/<path:filename>")
def serve_upload(filename):
    safe_name = secure_filename(filename)
    return send_from_directory(_uploads_dir(), safe_name)


@notes_bp.get("/courses/<int:course_id>/notes")
@jwt_required()
def list_course_notes(course_id):
    user = _get_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    is_teacher = user.role in {"teacher", "admin"} and (
        user.role == "admin" or course.teacher_id == user.id
    )
    is_enrolled = (
        Enrollment.query.filter_by(student_id=user.id, course_id=course.id).first()
        is not None
    )

    if not (is_teacher or is_enrolled):
        return jsonify({"error": "Access denied"}), 403

    notes = (
        Note.query.filter_by(course_id=course.id)
        .order_by(Note.lesson_number.asc(), Note.created_at.asc())
        .all()
    )
    return jsonify([_serialize_note(note) for note in notes])