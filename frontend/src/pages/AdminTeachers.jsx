import { useEffect, useState } from "react";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import "./AdminTeachers.css";

const AdminTeachers = () => {
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPendingTeachers = async () => {
      try {
        setLoading(true);
        setError("");
        const response = await api.get("/admin/teachers/pending");
        setTeachers(response.data?.data || []);
      } catch (err) {
        setError(
          err?.response?.data?.error || "Failed to load pending teachers."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchPendingTeachers();
  }, []);

  return (
    <PageTransition>
      <div className="admin-teachers-page py-5">
        <div className="container">
          <div className="admin-teachers-hero mb-4">
            <div>
              <span className="admin-badge">Admin Console</span>
              <h1 className="mb-2">Teacher Approvals</h1>
              <p className="text-muted mb-0">
                Review teacher requests and keep the platform trusted.
              </p>
            </div>
            <div className="admin-stat">
              <div className="admin-stat__label">Pending</div>
              <div className="admin-stat__value">{teachers.length}</div>
            </div>
          </div>

          {error ? <div className="alert alert-danger">{error}</div> : null}

          {loading ? (
            <div className="admin-list">Loading teachers...</div>
          ) : teachers.length ? (
            <div className="admin-list">
              {teachers.map((teacher) => (
                <div className="admin-card" key={teacher.id}>
                  <div>
                    <h5 className="mb-1">{teacher.name}</h5>
                    <div className="text-muted small">{teacher.email}</div>
                  </div>
                  <span className="admin-pill">Pending</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="admin-list">No pending teachers right now.</div>
          )}
        </div>
      </div>
    </PageTransition>
  );
};

export default AdminTeachers;
