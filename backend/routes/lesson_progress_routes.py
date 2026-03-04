from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db
from models import Course, Enrollment, Lesson, LessonProgress, Progress, User

lesson_progress_bp = Blueprint('lesson_progress', __name__)


def _get_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id)) if user_id is not None else None

@lesson_progress_bp.route('/api/lesson-progress/<course>/<int:lesson_id>', methods=['POST'])
@jwt_required()
def mark_lesson_complete(course, lesson_id):
    """Mark a lesson as completed"""
    try:
        user_id = get_jwt_identity()
        
        # Check if already completed
        progress = LessonProgress.query.filter_by(
            user_id=user_id,
            course=course,
            lesson_id=lesson_id
        ).first()
        
        if progress:
            progress.completed = True
            progress.completed_at = datetime.utcnow()
        else:
            progress = LessonProgress(
                user_id=user_id,
                course=course,
                lesson_id=lesson_id,
                completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(progress)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Lesson marked as complete',
            'course': course,
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
        user_id = get_jwt_identity()
        
        completed_lessons = LessonProgress.query.filter_by(
            user_id=user_id,
            course=course,
            completed=True
        ).all()
        
        lesson_ids = [p.lesson_id for p in completed_lessons]
        
        return jsonify({
            'course': course,
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
        user_id = get_jwt_identity()
        
        all_progress = LessonProgress.query.filter_by(
            user_id=user_id,
            completed=True
        ).all()
        
        # Group by course
        progress_by_course = {}
        for p in all_progress:
            if p.course not in progress_by_course:
                progress_by_course[p.course] = []
            progress_by_course[p.course].append(p.lesson_id)
        
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
        user_id = get_jwt_identity()
        
        progress = LessonProgress.query.filter_by(
            user_id=user_id,
            course=course,
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
            course=str(course_id),
            lesson_id=lesson_id,
        ).first()

        if progress:
            progress.completed = True
            progress.completed_at = datetime.utcnow()
        else:
            progress = LessonProgress(
                user_id=user.id,
                course=str(course_id),
                lesson_id=lesson_id,
                completed=True,
                completed_at=datetime.utcnow(),
            )
            db.session.add(progress)

        db.session.commit()

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
            course=str(course.id),
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
                course=str(course.id),
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
