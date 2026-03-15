import hashlib
from datetime import datetime
from io import BytesIO

from flask import Blueprint, current_app, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from database import db
from activity_service import calculate_learning_streak, get_recent_learning_activity, record_learning_activity
from models import Course, Enrollment, Lesson, LessonProgress, Progress, Quiz, QuizAttempt, User

lesson_progress_bp = Blueprint('lesson_progress', __name__)


def _get_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id)) if user_id is not None else None


def _resolve_course_id(course_key):
    """Resolve legacy slug or numeric course identifier to a course id."""
    raw = (course_key or "").strip()
    if not raw:
        return None

    if raw.isdigit():
        course = Course.query.get(int(raw))
        return course.id if course else None

    course = Course.query.filter(Course.title.ilike(f"%{raw}%")).first()
    return course.id if course else None


def _is_instructor(user):
    return bool(user and user.role in {"teacher", "admin"} and (user.role == "admin" or user.is_approved))


def _draw_centered_fitted_text(c, text: str, y: float, max_width: float, font_name: str, start_size: int, min_size: int = 14):
    size = start_size
    clean = (text or "").strip() or "-"

    while size > min_size and c.stringWidth(clean, font_name, size) > max_width:
        size -= 1

    c.setFont(font_name, size)
    c.drawCentredString(A4[0] / 2, y, clean)


def _build_certificate_pdf(
    student_name: str,
    course_name: str,
    completed_on: datetime,
    platform_name: str,
    certificate_id: str,
) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    border_color = colors.HexColor("#1e40af")
    accent_color = colors.HexColor("#1d4ed8")
    dark_text = colors.HexColor("#0f172a")
    muted_text = colors.HexColor("#475569")

    c.setLineWidth(3)
    c.setStrokeColor(border_color)
    c.rect(0.6 * inch, 0.6 * inch, width - 1.2 * inch, height - 1.2 * inch, stroke=1, fill=0)

    c.setLineWidth(1)
    c.setStrokeColor(colors.HexColor("#bfdbfe"))
    c.rect(0.8 * inch, 0.8 * inch, width - 1.6 * inch, height - 1.6 * inch, stroke=1, fill=0)

    c.setFillColor(accent_color)
    c.roundRect((width / 2) - 95, height - 1.8 * inch, 190, 28, 14, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, height - 1.62 * inch, "CERTIFICATE")

    c.setFillColor(dark_text)
    c.setFont("Helvetica-Bold", 33)
    c.drawCentredString(width / 2, height - 2.35 * inch, "Certificate of Completion")

    c.setFillColor(muted_text)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 3.0 * inch, "This is proudly awarded to")

    c.setFillColor(accent_color)
    _draw_centered_fitted_text(
        c,
        student_name,
        height - 3.65 * inch,
        max_width=width - 2.2 * inch,
        font_name="Helvetica-Bold",
        start_size=30,
        min_size=18,
    )

    c.setFillColor(muted_text)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 4.25 * inch, "for successfully completing")

    c.setFillColor(dark_text)
    _draw_centered_fitted_text(
        c,
        course_name,
        height - 4.85 * inch,
        max_width=width - 2.0 * inch,
        font_name="Helvetica-Bold",
        start_size=24,
        min_size=16,
    )

    completion_text = f"Completion Date: {completed_on.strftime('%d %B %Y')}"
    issued_text = f"Issued by: {platform_name}"
    certificate_text = f"Certificate ID: {certificate_id}"

    c.setFillColor(muted_text)
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 5.65 * inch, completion_text)
    c.drawCentredString(width / 2, height - 5.98 * inch, issued_text)
    c.drawCentredString(width / 2, height - 6.31 * inch, certificate_text)

    sig_y = 1.85 * inch
    line_w = 2.0 * inch
    left_x = 2.0 * inch
    right_x = width - 2.0 * inch - line_w

    c.setStrokeColor(colors.HexColor("#94a3b8"))
    c.setLineWidth(1)
    c.line(left_x, sig_y, left_x + line_w, sig_y)
    c.line(right_x, sig_y, right_x + line_w, sig_y)

    c.setFillColor(muted_text)
    c.setFont("Helvetica", 10)
    c.drawCentredString(left_x + line_w / 2, sig_y - 0.2 * inch, "Academic Coordinator")
    c.drawCentredString(right_x + line_w / 2, sig_y - 0.2 * inch, "Platform Director")

    # Seal-style marker
    seal_x = width / 2
    seal_y = sig_y + 0.3 * inch
    c.setFillColor(colors.HexColor("#e0ecff"))
    c.setStrokeColor(border_color)
    c.circle(seal_x, seal_y, 28, stroke=1, fill=1)
    c.setFillColor(border_color)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(seal_x, seal_y + 2, "VERIFIED")
    c.setFont("Helvetica", 7)
    c.drawCentredString(seal_x, seal_y - 9, "LMS")

    c.setFillColor(colors.HexColor("#64748b"))
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width / 2, 1.05 * inch, "Generated digitally by the LMS platform")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

@lesson_progress_bp.route('/api/lesson-progress/<course>/<int:lesson_id>', methods=['POST'])
@jwt_required()
def mark_lesson_complete(course, lesson_id):
    """Mark a lesson as completed"""
    try:
        user = _get_user()
        if not user:
            return jsonify({"error": "User not found"}), 404

        course_id = _resolve_course_id(course)
        if not course_id:
            return jsonify({"error": "Course not found"}), 404

        lesson = Lesson.query.filter_by(id=lesson_id, course_id=course_id).first()
        if not lesson:
            return jsonify({"error": "Lesson not found"}), 404
        
        # Check if already completed
        progress = LessonProgress.query.filter_by(
            user_id=user.id,
            course_id=course_id,
            lesson_id=lesson_id
        ).first()
        
        if progress:
            progress.completed = True
            progress.completed_at = datetime.utcnow()
        else:
            progress = LessonProgress(
                user_id=user.id,
                course_id=course_id,
                lesson_id=lesson_id,
                completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(progress)
        
        db.session.commit()

        try:
            record_learning_activity(user.id)
        except Exception:
            db.session.rollback()
        
        return jsonify({
            'message': 'Lesson marked as complete',
            'course_id': course_id,
            'lesson_id': lesson_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@lesson_progress_bp.route('/api/lesson-progress/<course>', methods=['GET'])
@jwt_required()
def get_course_progress(course):
    """Get all completed lessons for a course"""
    try:
        user = _get_user()
        if not user:
            return jsonify({"error": "User not found"}), 404

        course_id = _resolve_course_id(course)
        if not course_id:
            return jsonify({"error": "Course not found"}), 404
        
        completed_lessons = LessonProgress.query.filter_by(
            user_id=user.id,
            course_id=course_id,
            completed=True
        ).all()
        
        lesson_ids = [p.lesson_id for p in completed_lessons]
        
        return jsonify({
            'course_id': course_id,
            'completed_lessons': lesson_ids,
            'total_completed': len(lesson_ids)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lesson_progress_bp.route('/api/lesson-progress', methods=['GET'])
@jwt_required()
def get_all_progress():
    """Get progress for all courses"""
    try:
        user = _get_user()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        all_progress = LessonProgress.query.filter_by(
            user_id=user.id,
            completed=True
        ).all()
        
        # Group by course
        progress_by_course = {}
        for p in all_progress:
            key = str(p.course_id)
            if key not in progress_by_course:
                progress_by_course[key] = []
            progress_by_course[key].append(p.lesson_id)
        
        return jsonify({
            'progress': progress_by_course
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lesson_progress_bp.route('/api/lesson-progress/<course>/<int:lesson_id>', methods=['DELETE'])
@jwt_required()
def unmark_lesson(course, lesson_id):
    """Unmark a lesson (for testing)"""
    try:
        user = _get_user()
        if not user:
            return jsonify({"error": "User not found"}), 404

        course_id = _resolve_course_id(course)
        if not course_id:
            return jsonify({"error": "Course not found"}), 404
        
        progress = LessonProgress.query.filter_by(
            user_id=user.id,
            course_id=course_id,
            lesson_id=lesson_id
        ).first()
        
        if progress:
            db.session.delete(progress)
            db.session.commit()
            return jsonify({'message': 'Lesson unmarked'}), 200
        
        return jsonify({'message': 'No progress found'}), 404
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@lesson_progress_bp.route('/api/courses/<int:course_id>/lessons/<int:lesson_id>/complete', methods=['POST'])
@jwt_required()
def mark_lesson_complete_by_course_id(course_id, lesson_id):
    """Mark a lesson as completed for a numeric course id."""
    try:
        user = _get_user()
        if not user:
            return jsonify({"error": "User not found"}), 404

        lesson = Lesson.query.filter_by(id=lesson_id, course_id=course_id).first()
        if not lesson:
            return jsonify({"error": "Lesson not found"}), 404

        progress = LessonProgress.query.filter_by(
            user_id=user.id,
            course_id=course_id,
            lesson_id=lesson_id,
        ).first()

        if progress:
            progress.completed = True
            progress.completed_at = datetime.utcnow()
        else:
            progress = LessonProgress(
                user_id=user.id,
                course_id=course_id,
                lesson_id=lesson_id,
                completed=True,
                completed_at=datetime.utcnow(),
            )
            db.session.add(progress)

        db.session.commit()

        try:
            record_learning_activity(user.id)
        except Exception:
            db.session.rollback()

        return jsonify(
            {
                "message": "Lesson marked as complete",
                "course_id": course_id,
                "lesson_id": lesson_id,
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@lesson_progress_bp.route('/api/courses/<int:course_id>/progress', methods=['GET'])
@jwt_required()
def get_course_progress_by_id(course_id):
    """Get completion details for a course using its numeric id."""
    try:
        user = _get_user()
        if not user:
            return jsonify({"error": "User not found"}), 404

        course = Course.query.get(course_id)
        if not course:
            return jsonify({"error": "Course not found"}), 404

        total_lessons = Lesson.query.filter_by(course_id=course.id).count()
        completed = LessonProgress.query.filter_by(
            user_id=user.id,
            course_id=course.id,
            completed=True,
        ).all()

        completed_ids = [entry.lesson_id for entry in completed]
        percent = int((len(completed_ids) / total_lessons) * 100) if total_lessons else 0

        return jsonify(
            {
                "course_id": course.id,
                "course_title": course.title,
                "total_lessons": total_lessons,
                "completed_lessons": completed_ids,
                "completed_count": len(completed_ids),
                "percent_complete": percent,
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@lesson_progress_bp.route('/api/learning-dashboard', methods=['GET'])
@jwt_required()
def get_learning_dashboard():
    """Return summary stats and recent activity for the student dashboard."""
    try:
        user = _get_user()
        if not user:
            return jsonify({"error": "User not found"}), 404

        quiz_attempts = Progress.query.filter_by(user_id=user.id).all()
        total_quizzes = len(quiz_attempts)
        avg_score = round(
            sum(entry.score for entry in quiz_attempts) / total_quizzes, 2
        ) if total_quizzes else 0
        avg_completion = round(
            sum(entry.completion_percentage for entry in quiz_attempts) / total_quizzes, 2
        ) if total_quizzes else 0

        enrollments = (
            Enrollment.query.filter_by(student_id=user.id)
            .order_by(Enrollment.enrolled_at.desc())
            .all()
        )

        course_progress = []
        for enrollment in enrollments:
            course = enrollment.course
            if not course:
                continue
            total_lessons = Lesson.query.filter_by(course_id=course.id).count()
            completed_count = LessonProgress.query.filter_by(
                user_id=user.id,
                course_id=course.id,
                completed=True,
            ).count()
            percent = int((completed_count / total_lessons) * 100) if total_lessons else 0
            course_progress.append(
                {
                    "course_id": course.id,
                    "title": course.title,
                    "teacher_name": course.teacher.name if course.teacher else None,
                    "total_lessons": total_lessons,
                    "completed_lessons": completed_count,
                    "percent_complete": percent,
                }
            )

        recent_quizzes = (
            Progress.query.filter_by(user_id=user.id)
            .order_by(Progress.attempted_at.desc())
            .limit(5)
            .all()
        )
        recent_lessons = (
            LessonProgress.query.filter_by(user_id=user.id, completed=True)
            .order_by(LessonProgress.completed_at.desc())
            .limit(5)
            .all()
        )

        activity = []
        for entry in recent_quizzes:
            activity.append(
                {
                    "type": "quiz",
                    "title": f"Quiz attempt (score {entry.score})",
                    "timestamp": entry.attempted_at.isoformat(),
                }
            )
        for entry in recent_lessons:
            lesson = Lesson.query.get(entry.lesson_id)
            activity.append(
                {
                    "type": "lesson",
                    "title": f"Completed lesson: {lesson.title if lesson else 'Lesson'}",
                    "timestamp": entry.completed_at.isoformat() if entry.completed_at else None,
                }
            )

        activity = sorted(
            [item for item in activity if item.get("timestamp")],
            key=lambda x: x["timestamp"],
            reverse=True,
        )[:8]

        return jsonify(
            {
                "total_xp": user.xp_points,
                "total_quizzes_attempted": total_quizzes,
                "average_quiz_score": avg_score,
                "average_quiz_completion": avg_completion,
                "course_progress": course_progress,
                "recent_activity": activity,
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@lesson_progress_bp.route('/api/lesson/complete', methods=['POST'])
@jwt_required()
def mark_lesson_complete_body():
    """Mark a lesson complete via JSON body: {user_id, course_id, lesson_id}."""
    user = _get_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    body_user_id = data.get("user_id")
    course_id = data.get("course_id")
    lesson_id = data.get("lesson_id")

    if body_user_id is None or not course_id or not lesson_id:
        return jsonify({"error": "user_id, course_id and lesson_id are required"}), 400

    try:
        body_user_id = int(body_user_id)
        course_id = int(course_id)
        lesson_id = int(lesson_id)
    except (TypeError, ValueError):
        return jsonify({"error": "user_id, course_id and lesson_id must be integers"}), 400

    if body_user_id != user.id:
        return jsonify({"error": "user_id does not match authenticated user"}), 403

    lesson = Lesson.query.filter_by(id=lesson_id, course_id=course_id).first()
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    progress = LessonProgress.query.filter_by(
        user_id=user.id,
        course_id=course_id,
        lesson_id=lesson_id,
    ).first()

    now = datetime.utcnow()
    if progress:
        progress.completed = True
        progress.completed_at = now
    else:
        progress = LessonProgress(
            user_id=user.id,
            course_id=course_id,
            lesson_id=lesson_id,
            completed=True,
            completed_at=now,
        )
        db.session.add(progress)

    db.session.commit()

    try:
        record_learning_activity(user.id)
    except Exception:
        db.session.rollback()

    return jsonify({
        "message": "Lesson marked as complete",
        "user_id": user.id,
        "course_id": course_id,
        "lesson_id": lesson_id,
        "completed_at": now.isoformat(),
    }), 200


@lesson_progress_bp.route('/api/progress/<int:user_id>/<int:course_id>', methods=['GET'])
@jwt_required()
def get_progress_by_user_and_course(user_id, course_id):
    """Return completed/total lesson counts and completion percentage."""
    user = _get_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user_id != user.id:
        return jsonify({"error": "Unauthorized access to another user's progress"}), 403

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    total_lessons = Lesson.query.filter_by(course_id=course_id).count()
    completed_lessons = LessonProgress.query.filter_by(
        user_id=user_id,
        course_id=course_id,
        completed=True,
    ).count()

    completion_percentage = int((completed_lessons / total_lessons) * 100) if total_lessons else 0

    return jsonify({
        "completed_lessons": completed_lessons,
        "total_lessons": total_lessons,
        "completion_percentage": completion_percentage,
    }), 200


@lesson_progress_bp.route('/api/student/dashboard', methods=['GET'])
@jwt_required()
def get_student_dashboard():
    """Top-level summary stats for the student progress dashboard."""
    user = _get_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    enrollments = Enrollment.query.filter_by(student_id=user.id).all()
    courses_enrolled = len(enrollments)

    lessons_completed = LessonProgress.query.filter_by(
        user_id=user.id,
        completed=True,
    ).count()

    quiz_attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
    if not quiz_attempts:
        # Backward compatibility for older data.
        quiz_attempts = Progress.query.filter_by(user_id=user.id).all()

    quizzes_attempted = len(quiz_attempts)

    if quizzes_attempted:
        # Prefer percentage from quiz_attempts; fallback to raw score average for legacy progresses.
        first_attempt = quiz_attempts[0]
        if isinstance(first_attempt, QuizAttempt):
            average_score = round(
                sum((a.score / max(1, a.total_questions)) * 100 for a in quiz_attempts) / quizzes_attempted,
                1,
            )
        else:
            average_score = round(sum(e.score for e in quiz_attempts) / quizzes_attempted, 1)
    else:
        average_score = 0

    course_progress = []
    for enrollment in enrollments:
        course = enrollment.course
        if not course:
            continue
        total = Lesson.query.filter_by(course_id=course.id).count()
        done = LessonProgress.query.filter_by(
            user_id=user.id,
            course_id=course.id,
            completed=True,
        ).count()
        pct = int((done / total) * 100) if total else 0
        course_progress.append({
            "course_id": course.id,
            "title": course.title,
            "teacher_name": course.teacher.name if course.teacher else None,
            "total_lessons": total,
            "completed_lessons": done,
            "percent_complete": pct,
        })

    return jsonify({
        "total_xp": user.xp_points,
        "courses_enrolled": courses_enrolled,
        "lessons_completed": lessons_completed,
        "quizzes_attempted": quizzes_attempted,
        "average_score": average_score,
        "learning_streak_days": calculate_learning_streak(user.id),
        "learning_activity_last_7_days": get_recent_learning_activity(user.id, days=7),
        "course_progress": course_progress,
    }), 200


@lesson_progress_bp.route('/api/instructor/analytics/<int:course_id>', methods=['GET'])
@jwt_required()
def get_instructor_analytics(course_id):
    """Return instructor analytics summary for a course."""
    user = _get_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not _is_instructor(user):
        return jsonify({"error": "Instructor access required"}), 403

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    if user.role == "teacher" and course.teacher_id != user.id:
        return jsonify({"error": "Unauthorized access to this course"}), 403

    students_enrolled = Enrollment.query.filter_by(course_id=course_id).count()

    quizzes = Quiz.query.filter_by(course_id=course_id).all()
    quiz_ids = [q.id for q in quizzes]

    attempt_rows = []
    if quiz_ids:
        attempt_rows = QuizAttempt.query.filter(QuizAttempt.quiz_id.in_(quiz_ids)).all()
        if not attempt_rows:
            attempt_rows = Progress.query.filter(Progress.quiz_id.in_(quiz_ids)).all()

    if attempt_rows:
        first_row = attempt_rows[0]
        if isinstance(first_row, QuizAttempt):
            average_quiz_score = round(
                sum((a.score / max(1, a.total_questions)) * 100 for a in attempt_rows) / len(attempt_rows),
                1,
            )
        else:
            average_quiz_score = round(sum(a.score for a in attempt_rows) / len(attempt_rows), 1)
    else:
        average_quiz_score = 0

    total_lessons = Lesson.query.filter_by(course_id=course_id).count()
    completed_lesson_rows = (
        LessonProgress.query.filter_by(course_id=course_id, completed=True).count()
        if total_lessons and students_enrolled
        else 0
    )
    completion_rate = round(
        (completed_lesson_rows / (students_enrolled * total_lessons)) * 100,
        1,
    ) if students_enrolled and total_lessons else 0

    return jsonify({
        "students_enrolled": students_enrolled,
        "average_quiz_score": average_quiz_score,
        "completion_rate": completion_rate,
    }), 200


@lesson_progress_bp.route('/api/certificate/<int:user_id>/<int:course_id>', methods=['GET'])
@jwt_required()
def download_course_certificate(user_id, course_id):
    """Generate and download a course completion certificate PDF."""
    requester = _get_user()
    if not requester:
        return jsonify({"error": "User not found"}), 404

    if requester.id != user_id and not _is_instructor(requester):
        return jsonify({"error": "Unauthorized access to certificate"}), 403

    student = User.query.get(user_id)
    if not student:
        return jsonify({"error": "Target user not found"}), 404

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    total_lessons = Lesson.query.filter_by(course_id=course_id).count()
    if total_lessons == 0:
        return jsonify({"error": "No lessons found for this course"}), 400

    completed_rows = LessonProgress.query.filter_by(
        user_id=user_id,
        course_id=course_id,
        completed=True,
    ).all()

    completed_lesson_ids = {row.lesson_id for row in completed_rows}
    if len(completed_lesson_ids) < total_lessons:
        return jsonify({"error": "Course not fully completed yet"}), 400

    completion_date = max(
        (row.completed_at for row in completed_rows if row.completed_at is not None),
        default=datetime.utcnow(),
    )

    certificate_id = hashlib.sha1(
        f"{user_id}:{course_id}:{completion_date.isoformat()}".encode("utf-8")
    ).hexdigest()[:12].upper()

    platform_name = current_app.config.get("PLATFORM_NAME", "Gamified Learning LMS")
    pdf_buffer = _build_certificate_pdf(
        student_name=student.name,
        course_name=course.title,
        completed_on=completion_date,
        platform_name=platform_name,
        certificate_id=certificate_id,
    )

    safe_course = "_".join(course.title.split()) or f"course_{course.id}"
    safe_student = "_".join(student.name.split()) or f"student_{student.id}"
    filename = f"certificate_{safe_student}_{safe_course}.pdf"

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename,
    )
