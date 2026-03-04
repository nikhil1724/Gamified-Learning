import { useEffect, useState } from "react";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import "./AdminDashboard.css";

const emptyStats = {
  total_users: 0,
  total_students: 0,
  total_teachers: 0,
  total_courses: 0,
  total_quizzes: 0,
};

const AdminDashboard = () => {
  const [stats, setStats] = useState(emptyStats);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [approvingIds, setApprovingIds] = useState([]);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      setError("");
      const [statsResponse, usersResponse] = await Promise.all([
        api.get("/admin/stats"),
        api.get("/admin/users"),
      ]);
      setStats(statsResponse.data?.data || emptyStats);
      setUsers(usersResponse.data?.data || []);
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to load admin data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const handleApprove = async (userId) => {
    if (approvingIds.includes(userId)) {
      return;
    }

    try {
      setApprovingIds((prev) => [...prev, userId]);
      await api.put(`/admin/approve-teacher/${userId}`);
      setUsers((prev) =>
        prev.map((user) =>
          user.id === userId ? { ...user, is_approved: true } : user
        )
      );
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to approve teacher.");
    } finally {
      setApprovingIds((prev) => prev.filter((id) => id !== userId));
    }
  };

  return (
    <PageTransition>
      <div className="admin-dashboard-page py-5">
        <div className="container">
          <div className="admin-dashboard-hero mb-4">
            <div>
              <span className="admin-badge">Admin Console</span>
              <h1 className="mb-2">Admin Dashboard</h1>
              <p className="text-muted mb-0">
                Review users, approve instructors, and monitor platform stats.
              </p>
            </div>
            <button
              type="button"
              className="btn btn-outline-primary"
              onClick={fetchAdminData}
              disabled={loading}
            >
              {loading ? "Refreshing..." : "Refresh"}
            </button>
          </div>

          {error ? <div className="alert alert-danger">{error}</div> : null}

          <div className="admin-stat-grid">
            <div className="admin-stat-card">
              <div className="admin-stat-card__label">Total Users</div>
              <div className="admin-stat-card__value">{stats.total_users}</div>
            </div>
            <div className="admin-stat-card">
              <div className="admin-stat-card__label">Students</div>
              <div className="admin-stat-card__value">{stats.total_students}</div>
            </div>
            <div className="admin-stat-card">
              <div className="admin-stat-card__label">Teachers</div>
              <div className="admin-stat-card__value">{stats.total_teachers}</div>
            </div>
            <div className="admin-stat-card">
              <div className="admin-stat-card__label">Courses</div>
              <div className="admin-stat-card__value">{stats.total_courses}</div>
            </div>
            <div className="admin-stat-card">
              <div className="admin-stat-card__label">Quizzes</div>
              <div className="admin-stat-card__value">{stats.total_quizzes}</div>
            </div>
          </div>

          <div className="admin-table-card mt-4">
            <div className="admin-table-card__header">
              <h5 className="mb-0">All Users</h5>
            </div>
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
                <thead>
                  <tr>
                    <th scope="col">Name</th>
                    <th scope="col">Email</th>
                    <th scope="col">Role</th>
                    <th scope="col">Approved</th>
                    <th scope="col">Joined</th>
                    <th scope="col">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan="6" className="text-center py-4">
                        Loading users...
                      </td>
                    </tr>
                  ) : users.length ? (
                    users.map((user) => (
                      <tr key={user.id}>
                        <td>{user.name}</td>
                        <td>{user.email}</td>
                        <td className="text-capitalize">{user.role}</td>
                        <td>
                          {user.role === "teacher" ? (
                            <span
                              className={`badge ${
                                user.is_approved ? "text-bg-success" : "text-bg-warning"
                              }`}
                            >
                              {user.is_approved ? "Approved" : "Pending"}
                            </span>
                          ) : (
                            <span className="badge text-bg-secondary">N/A</span>
                          )}
                        </td>
                        <td>
                          {user.created_at
                            ? new Date(user.created_at).toLocaleDateString()
                            : "-"}
                        </td>
                        <td>
                          {user.role === "teacher" && !user.is_approved ? (
                            <button
                              type="button"
                              className="btn btn-sm btn-primary"
                              onClick={() => handleApprove(user.id)}
                              disabled={approvingIds.includes(user.id)}
                            >
                              {approvingIds.includes(user.id)
                                ? "Approving..."
                                : "Approve"}
                            </button>
                          ) : (
                            <span className="text-muted small">No action</span>
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="6" className="text-center py-4">
                        No users found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default AdminDashboard;
