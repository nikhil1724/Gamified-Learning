from functools import wraps

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import db
from models import (
    CodeSubmission,
    CodingProblem,
    Course,
    Enrollment,
    LearningActivity,
    LessonProgress,
    Note,
    Notification,
    Problem,
    ProblemProgress,
    Progress,
    Quiz,
    QuizAttempt,
    Submission,
    User,
    UserBadge,
    UserCodingStats,
    UserReward,
    UserSkill,
)


admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def role_required(required_role):
    def decorator(handler):
        @wraps(handler)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id)) if user_id is not None else None
            if not user:
                return jsonify({"success": False, "error": "User not found"}), 404
            if user.role != required_role:
                return (
                    jsonify({"success": False, "error": "Admin access required"}),
                    403,
                )
            return handler(*args, **kwargs)

        return wrapper

    return decorator


@admin_bp.get("/teachers/pending")
@role_required("admin")
def list_pending_teachers():
    teachers = User.query.filter_by(role="teacher", is_approved=False).all()

    data = [
        {
            "id": teacher.id,
            "name": teacher.name,
            "email": teacher.email,
            "created_at": teacher.created_at.isoformat(),
        }
        for teacher in teachers
    ]
    return jsonify({"success": True, "data": data})


@admin_bp.post("/teachers/approve/<int:teacher_id>")
@role_required("admin")
def approve_teacher(teacher_id):
    teacher = User.query.get(teacher_id)
    if not teacher or teacher.role != "teacher":
        return jsonify({"success": False, "error": "Teacher not found"}), 404

    teacher.is_approved = True
    db.session.commit()

    return jsonify(
        {"success": True, "data": {"teacher_id": teacher.id, "is_approved": True}}
    )


@admin_bp.post("/teachers/reject/<int:teacher_id>")
@role_required("admin")
def reject_teacher(teacher_id):
    teacher = User.query.get(teacher_id)
    if not teacher or teacher.role != "teacher":
        return jsonify({"success": False, "error": "Teacher not found"}), 404

    db.session.delete(teacher)
    db.session.commit()

    return jsonify({"success": True, "data": {"teacher_id": teacher_id}})


@admin_bp.get("/users")
@role_required("admin")
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    data = [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_approved": user.is_approved,
            "created_at": user.created_at.isoformat(),
        }
        for user in users
    ]
    return jsonify({"success": True, "data": data})


@admin_bp.delete("/users/<int:user_id>")
@role_required("admin")
def delete_user(user_id):
    current_admin_id = int(get_jwt_identity())
    if user_id == current_admin_id:
        return jsonify({"success": False, "error": "You cannot delete your own account."}), 400

    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"success": False, "error": "User not found"}), 404

    if target_user.role == "admin":
        return jsonify({"success": False, "error": "Deleting admin accounts is not allowed."}), 403

    if target_user.role == "teacher":
        assigned_courses = Course.query.filter_by(teacher_id=target_user.id).count()
        if assigned_courses > 0:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Teacher has assigned courses. Reassign or remove courses before deleting this account.",
                    }
                ),
                409,
            )

    try:
        # Remove dependent records first to avoid foreign key constraint failures.
        UserReward.query.filter_by(user_id=target_user.id).delete(synchronize_session=False)
        UserSkill.query.filter_by(user_id=target_user.id).delete(synchronize_session=False)
        UserBadge.query.filter_by(user_id=target_user.id).delete(synchronize_session=False)
        Progress.query.filter_by(user_id=target_user.id).delete(synchronize_session=False)
        QuizAttempt.query.filter_by(user_id=target_user.id).delete(synchronize_session=False)
        Submission.query.filter_by(student_id=target_user.id).delete(synchronize_session=False)
        Enrollment.query.filter_by(student_id=target_user.id).delete(synchronize_session=False)
        LessonProgress.query.filter_by(user_id=target_user.id).delete(synchronize_session=False)
        Notification.query.filter_by(user_id=target_user.id).delete(synchronize_session=False)
        LearningActivity.query.filter_by(user_id=target_user.id).delete(synchronize_session=False)
        ProblemProgress.query.filter_by(user_id=target_user.id).delete(synchronize_session=False)
        CodeSubmission.query.filter_by(user_id=target_user.id).delete(synchronize_session=False)
        UserCodingStats.query.filter_by(user_id=target_user.id).delete(synchronize_session=False)

        # Keep authored content but detach from deleted account where possible.
        Note.query.filter_by(uploaded_by=target_user.id).delete(synchronize_session=False)
        Problem.query.filter_by(created_by=target_user.id).update(
            {Problem.created_by: current_admin_id},
            synchronize_session=False,
        )
        CodingProblem.query.filter_by(created_by=target_user.id).update(
            {CodingProblem.created_by: current_admin_id},
            synchronize_session=False,
        )

        db.session.delete(target_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "User cannot be deleted because related records still exist.",
                }
            ),
            409,
        )
    except SQLAlchemyError:
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Failed to delete user due to a database error.",
                }
            ),
            500,
        )

    return jsonify({"success": True, "data": {"user_id": user_id}})


@admin_bp.put("/approve-teacher/<int:teacher_id>")
@role_required("admin")
def approve_teacher_v2(teacher_id):
    teacher = User.query.get(teacher_id)
    if not teacher or teacher.role != "teacher":
        return jsonify({"success": False, "error": "Teacher not found"}), 404

    teacher.is_approved = True
    db.session.commit()

    return jsonify(
        {"success": True, "data": {"teacher_id": teacher.id, "is_approved": True}}
    )


@admin_bp.get("/stats")
@role_required("admin")
def admin_stats():
    data = {
        "total_users": User.query.count(),
        "total_students": User.query.filter_by(role="student").count(),
        "total_teachers": User.query.filter_by(role="teacher").count(),
        "total_courses": Course.query.count(),
        "total_quizzes": Quiz.query.count(),
    }
    return jsonify({"success": True, "data": data})
