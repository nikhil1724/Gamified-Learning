import { useEffect, useState, useRef } from "react";
import api from "../services/api";
import "./NotificationBell.css";

const NotificationBell = () => {
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const dropdownRef = useRef(null);

  // Fetch unread count
  const fetchUnreadCount = async () => {
    try {
      const response = await api.get("/notifications/unread-count");
      setUnreadCount(response.data.unread_count);
    } catch (error) {
      console.error("Failed to fetch unread count:", error);
    }
  };

  // Fetch notifications
  const fetchNotifications = async () => {
    setIsLoading(true);
    try {
      const response = await api.get("/notifications", {
        params: {
          limit: 10,
          offset: 0,
        },
      });
      
      // Safely access the notifications array
      const notificationsData = response.data?.notifications || [];
      setNotifications(Array.isArray(notificationsData) ? notificationsData : []);
    } catch (error) {
      console.error("Failed to fetch notifications:", error);
      setNotifications([]); // Ensure notifications is an array on error
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch unread count on mount and set up polling
  useEffect(() => {
    fetchUnreadCount();

    // Poll for new notifications every 10 seconds
    const interval = setInterval(fetchUnreadCount, 10000);

    return () => clearInterval(interval);
  }, []);

  // Fetch notifications when dropdown opens
  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const handleMarkAsRead = async (notificationId) => {
    try {
      await api.put(`/notifications/${notificationId}/read`);
      // Update local state
      setNotifications(
        notifications.map((n) =>
          n.id === notificationId ? { ...n, is_read: true } : n
        )
      );
      // Update unread count
      setUnreadCount(Math.max(0, unreadCount - 1));
    } catch (error) {
      console.error("Failed to mark notification as read:", error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await api.put("/notifications/read-all");
      setNotifications(notifications.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error("Failed to mark all as read:", error);
    }
  };

  const handleDeleteNotification = async (notificationId) => {
    try {
      await api.delete(`/notifications/${notificationId}`);
      setNotifications(notifications.filter((n) => n.id !== notificationId));
    } catch (error) {
      console.error("Failed to delete notification:", error);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case "XP_EARNED":
        return "⭐";
      case "QUIZ_COMPLETED":
        return "✅";
      case "BADGE_EARNED":
        return "🏆";
      case "COURSE_ADDED":
        return "📚";
      default:
        return "🔔";
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
  };

  return (
    <div className="notification-bell-container" ref={dropdownRef}>
      <button
        className="notification-bell-button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Notifications"
        title={`${unreadCount} unread notifications`}
      >
        <span className="bell-icon">🔔</span>
        {unreadCount > 0 && (
          <span className="notification-badge">{unreadCount > 9 ? "9+" : unreadCount}</span>
        )}
      </button>

      {isOpen && (
        <div className="notification-dropdown">
          <div className="notification-header">
            <h3>Notifications</h3>
            {unreadCount > 0 && (
              <button className="mark-all-read-btn" onClick={handleMarkAllAsRead}>
                Mark all as read
              </button>
            )}
          </div>

          <div className="notification-list">
            {isLoading ? (
              <div className="notification-loading">Loading...</div>
            ) : !notifications || notifications.length === 0 ? (
              <div className="notification-empty">No notifications yet</div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`notification-item ${notification.is_read ? "read" : "unread"}`}
                >
                  <div className="notification-content">
                    <div className="notification-header-row">
                      <span className="notification-icon">
                        {getNotificationIcon(notification.type)}
                      </span>
                      <h4 className="notification-title">{notification.title}</h4>
                      {!notification.is_read && (
                        <button
                          className="notification-action-btn"
                          onClick={() => handleMarkAsRead(notification.id)}
                          title="Mark as read"
                        >
                          ●
                        </button>
                      )}
                      <button
                        className="notification-delete-btn"
                        onClick={() => handleDeleteNotification(notification.id)}
                        title="Delete"
                      >
                        ✕
                      </button>
                    </div>
                    <p className="notification-message">{notification.message}</p>
                    <span className="notification-time">
                      {formatTime(notification.created_at)}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>

          {notifications && notifications.length > 0 && (
            <div className="notification-footer">
              <a href="/notifications" className="view-all-link">
                View all notifications
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
