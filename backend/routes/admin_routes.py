from functools import wraps

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db
from models import Course, Quiz, User


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
