from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime

from database import db
from models import Notification, User


notification_bp = Blueprint("notifications", __name__, url_prefix="/api")


def _serialize_notification(notification: Notification) -> dict:
    return {
        "id": notification.id,
        "type": notification.type,
        "title": notification.title,
        "message": notification.message,
        "data": notification.data or {},
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat(),
        "read_at": notification.read_at.isoformat() if notification.read_at else None,
    }


def create_notification(user_id: int, notification_type: str, title: str, message: str, data: dict = None):
    """Helper function to create and store a notification"""
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        data=data or {},
    )
    db.session.add(notification)
    db.session.commit()
    return notification


@notification_bp.get("/notifications")
@jwt_required()
def list_notifications():
    """Fetch all notifications for the current user"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get query parameters for filtering
    unread_only = request.args.get("unread_only", "false").lower() == "true"
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)
    
    query = Notification.query.filter_by(user_id=user.id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    total_count = query.count()
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset).all()
    
    return jsonify({
        "notifications": [_serialize_notification(n) for n in notifications],
        "total_count": total_count,
        "unread_count": Notification.query.filter_by(user_id=user.id, is_read=False).count(),
    })


@notification_bp.get("/notifications/unread-count")
@jwt_required()
def get_unread_count():
    """Get the count of unread notifications"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    unread_count = Notification.query.filter_by(user_id=user.id, is_read=False).count()
    
    return jsonify({"unread_count": unread_count})


@notification_bp.put("/notifications/<int:notification_id>/read")
@jwt_required()
def mark_notification_as_read(notification_id: int):
    """Mark a notification as read"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    notification = Notification.query.get(notification_id)
    
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    
    if notification.user_id != user.id:
        return jsonify({"error": "Access denied"}), 403
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(_serialize_notification(notification))


@notification_bp.put("/notifications/read-all")
@jwt_required()
def mark_all_notifications_as_read():
    """Mark all notifications as read for the current user"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    now = datetime.utcnow()
    Notification.query.filter_by(user_id=user.id, is_read=False).update(
        {"is_read": True, "read_at": now}
    )
    db.session.commit()
    
    return jsonify({"message": "All notifications marked as read"})


@notification_bp.delete("/notifications/<int:notification_id>")
@jwt_required()
def delete_notification(notification_id: int):
    """Delete a notification"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    notification = Notification.query.get(notification_id)
    
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    
    if notification.user_id != user.id:
        return jsonify({"error": "Access denied"}), 403
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({"message": "Notification deleted"}), 204
