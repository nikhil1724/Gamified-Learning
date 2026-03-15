import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PageTransition from "../components/PageTransition";
import api from "../services/api";
import "./TeacherStudents.css";

const TeacherStudents = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sortBy, setSortBy] = useState("xp"); // xp, name, courses
  const [filterText, setFilterText] = useState("");

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const response = await api.get("/teacher/students/overview");
      setStudents(response.data.students || []);
      setError("");
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to load students");
      console.error("Failed to fetch students:", err);
    } finally {
      setLoading(false);
    }
  };

  const sortedAndFilteredStudents = students
    .filter((student) =>
      student.name.toLowerCase().includes(filterText.toLowerCase()) ||
      student.email.toLowerCase().includes(filterText.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === "name") {
        return a.name.localeCompare(b.name);
      } else if (sortBy === "courses") {
        return b.total_courses - a.total_courses;
      } else {
        return b.xp_points - a.xp_points;
      }
    });

  return (
    <PageTransition>
      <div className="container py-5">
        {/* Header */}
        <div className="teacher-students-header mb-5">
          <div>
            <Link to="/teacher/dashboard" className="back-link mb-3">
              <i className="bi bi-arrow-left me-2"></i>
              Back to Dashboard
            </Link>
            <h1 className="mb-2">Student Analytics</h1>
            <p className="text-muted mb-0">
              Track and monitor your students' performance across all courses
            </p>
          </div>
          <div className="header-stats">
            <div className="stat-card">
              <div className="stat-value">{students.length}</div>
              <div className="stat-label">Total Students</div>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="filters-section mb-4">
          <div className="search-box">
            <i className="bi bi-search"></i>
            <input
              type="text"
              placeholder="Search students by name or email..."
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
              className="form-control"
            />
          </div>
          <div className="sort-controls">
            <label className="sort-label">Sort by:</label>
            <select
              className="form-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="xp">XP Points (High to Low)</option>
              <option value="name">Name (A-Z)</option>
              <option value="courses">Courses Enrolled</option>
            </select>
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="text-center py-5">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <p className="mt-3 text-muted">Loading students...</p>
          </div>
        ) : error ? (
          <div className="alert alert-danger" role="alert">
            <i className="bi bi-exclamation-triangle me-2"></i>
            {error}
          </div>
        ) : sortedAndFilteredStudents.length === 0 ? (
          <div className="empty-state">
            <i className="bi bi-people"></i>
            <h3>No Students Found</h3>
            <p>
              {filterText
                ? "No students match your search criteria"
                : "You don't have any students enrolled in your courses yet"}
            </p>
          </div>
        ) : (
          <>
            <div className="results-info mb-3">
              Showing <strong>{sortedAndFilteredStudents.length}</strong> student(s)
            </div>
            <div className="students-grid">
              {sortedAndFilteredStudents.map((student) => (
                <Link
                  key={student.student_id}
                  to={`/teacher/student/${student.student_id}`}
                  className="student-card"
                >
                  <div className="student-card-header">
                    <div className="student-avatar">
                      <i className="bi bi-person-fill"></i>
                    </div>
                    <div className="student-info">
                      <h4 className="student-name">{student.name}</h4>
                      <p className="student-email">{student.email}</p>
                    </div>
                  </div>

                  <div className="student-card-body">
                    <div className="stat-row">
                      <div className="stat-item">
                        <i className="bi bi-trophy-fill text-warning"></i>
                        <span className="stat-text">
                          <strong>{student.xp_points}</strong> XP
                        </span>
                      </div>
                      <div className="stat-item">
                        <i className="bi bi-star-fill text-primary"></i>
                        <span className="stat-text">
                          Level <strong>{student.level}</strong>
                        </span>
                      </div>
                    </div>

                    <div className="courses-enrolled">
                      <div className="courses-header">
                        <i className="bi bi-book me-2"></i>
                        <span>Enrolled in {student.total_courses} course(s)</span>
                      </div>
                      {student.courses_enrolled.length > 0 && (
                        <div className="course-tags">
                          {student.courses_enrolled.slice(0, 3).map((course) => (
                            <span key={course.course_id} className="course-tag">
                              {course.course_title}
                            </span>
                          ))}
                          {student.courses_enrolled.length > 3 && (
                            <span className="course-tag more">
                              +{student.courses_enrolled.length - 3} more
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="student-card-footer">
                    <span className="view-details">
                      View Performance
                      <i className="bi bi-arrow-right ms-2"></i>
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </>
        )}
      </div>
    </PageTransition>
  );
};

export default TeacherStudents;
