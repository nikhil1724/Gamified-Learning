import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import PageTransition from "../components/PageTransition";
import api from "../services/api";
import "./CourseAnalytics.css";

const CourseAnalytics = () => {
  const { courseId } = useParams();
  const [analytics, setAnalytics] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("overview"); // overview, students, lessons, quizzes, problems

  useEffect(() => {
    fetchAnalytics();
    fetchStudents();
  }, [courseId]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/teacher/course/${courseId}/analytics`);
      setAnalytics(response.data);
      setError("");
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to load analytics");
      console.error("Failed to fetch analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStudents = async () => {
    try {
      const response = await api.get(`/teacher/course/${courseId}/students`);
      setStudents(response.data.students || []);
    } catch (err) {
      console.error("Failed to fetch students:", err);
    }
  };

  if (loading) {
    return (
      <PageTransition>
        <div className="container py-5">
          <div className="text-center py-5">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <p className="mt-3 text-muted">Loading course analytics...</p>
          </div>
        </div>
      </PageTransition>
    );
  }

  if (error) {
    return (
      <PageTransition>
        <div className="container py-5">
          <div className="alert alert-danger" role="alert">
            <i className="bi bi-exclamation-triangle me-2"></i>
            {error}
          </div>
          <Link to="/teacher/courses" className="btn btn-primary">
            <i className="bi bi-arrow-left me-2"></i>
            Back to Courses
          </Link>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="container py-5">
        {/* Header */}
        <Link to="/teacher/courses" className="back-link mb-4">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Courses
        </Link>

        <div className="course-analytics-header mb-5">
          <div>
            <h1 className="mb-2">{analytics.course_title}</h1>
            {analytics.course_description && (
              <p className="text-muted mb-0">{analytics.course_description}</p>
            )}
          </div>
          <div className="d-flex align-items-center gap-2 flex-wrap justify-content-end">
            <Link to={`/instructor/analytics/${courseId}`} className="btn btn-sm btn-primary">
              <i className="bi bi-bar-chart-line me-2"></i>
              Instructor Dashboard
            </Link>
            <div className="header-badge">
              <i className="bi bi-graph-up-arrow me-2"></i>
              Course Analytics
            </div>
          </div>
        </div>

        {/* Overview Stats */}
        <div className="stats-grid mb-5">
          <div className="stat-card blue">
            <div className="stat-icon">
              <i className="bi bi-people-fill"></i>
            </div>
            <div className="stat-content">
              <div className="stat-value">{analytics.overview.total_students}</div>
              <div className="stat-label">Enrolled Students</div>
            </div>
          </div>
          <div className="stat-card purple">
            <div className="stat-icon">
              <i className="bi bi-book-fill"></i>
            </div>
            <div className="stat-content">
              <div className="stat-value">{analytics.overview.total_lessons}</div>
              <div className="stat-label">Total Lessons</div>
            </div>
          </div>
          <div className="stat-card green">
            <div className="stat-icon">
              <i className="bi bi-clipboard-check-fill"></i>
            </div>
            <div className="stat-content">
              <div className="stat-value">{analytics.overview.total_quizzes}</div>
              <div className="stat-label">Total Quizzes</div>
            </div>
          </div>
          <div className="stat-card orange">
            <div className="stat-icon">
              <i className="bi bi-code-square"></i>
            </div>
            <div className="stat-content">
              <div className="stat-value">{analytics.overview.total_problems}</div>
              <div className="stat-label">Coding Problems</div>
            </div>
          </div>
          <div className="stat-card teal">
            <div className="stat-icon">
              <i className="bi bi-person-plus-fill"></i>
            </div>
            <div className="stat-content">
              <div className="stat-value">{analytics.overview.recent_enrollments}</div>
              <div className="stat-label">New (30 days)</div>
            </div>
          </div>
          <div className="stat-card pink">
            <div className="stat-icon">
              <i className="bi bi-activity"></i>
            </div>
            <div className="stat-content">
              <div className="stat-value">{analytics.overview.recent_activity}</div>
              <div className="stat-label">Recent Activity</div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="analytics-tabs mb-4">
          <button
            className={`tab-btn ${activeTab === "overview" ? "active" : ""}`}
            onClick={() => setActiveTab("overview")}
          >
            <i className="bi bi-bar-chart me-2"></i>
            Overview
          </button>
          <button
            className={`tab-btn ${activeTab === "students" ? "active" : ""}`}
            onClick={() => setActiveTab("students")}
          >
            <i className="bi bi-people me-2"></i>
            Students ({students.length})
          </button>
          <button
            className={`tab-btn ${activeTab === "lessons" ? "active" : ""}`}
            onClick={() => setActiveTab("lessons")}
          >
            <i className="bi bi-book me-2"></i>
            Lessons
          </button>
          <button
            className={`tab-btn ${activeTab === "quizzes" ? "active" : ""}`}
            onClick={() => setActiveTab("quizzes")}
          >
            <i className="bi bi-clipboard-check me-2"></i>
            Quizzes
          </button>
          <button
            className={`tab-btn ${activeTab === "problems" ? "active" : ""}`}
            onClick={() => setActiveTab("problems")}
          >
            <i className="bi bi-code me-2"></i>
            Problems
          </button>
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {/* Overview Tab */}
          {activeTab === "overview" && (
            <div className="overview-content">
              <div className="row g-4">
                <div className="col-lg-6">
                  <div className="content-card">
                    <h3 className="card-title">
                      <i className="bi bi-pie-chart me-2"></i>
                      Course Completion Overview
                    </h3>
                    <div className="completion-summary">
                      <div className="summary-item">
                        <span className="label">Avg. Lesson Completion:</span>
                        <span className="value">
                          {analytics.lesson_analytics.length > 0
                            ? Math.round(
                                analytics.lesson_analytics.reduce((acc, l) => acc + l.completion_rate, 0) /
                                  analytics.lesson_analytics.length
                              )
                            : 0}
                          %
                        </span>
                      </div>
                      <div className="summary-item">
                        <span className="label">Total Quiz Attempts:</span>
                        <span className="value">
                          {analytics.quiz_analytics.reduce((acc, q) => acc + q.total_attempts, 0)}
                        </span>
                      </div>
                      <div className="summary-item">
                        <span className="label">Problems Solved:</span>
                        <span className="value">
                          {analytics.problem_analytics.reduce((acc, p) => acc + p.solved_by, 0)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-lg-6">
                  <div className="content-card">
                    <h3 className="card-title">
                      <i className="bi bi-trophy me-2"></i>
                      Top Performers
                    </h3>
                    {students.length > 0 ? (
                      <div className="top-performers">
                        {students
                          .sort((a, b) => b.progress_percentage - a.progress_percentage)
                          .slice(0, 5)
                          .map((student, idx) => (
                            <div key={student.student_id} className="performer-item">
                              <div className="rank">#{idx + 1}</div>
                              <div className="performer-info">
                                <div className="name">{student.name}</div>
                                <div className="progress-mini">
                                  <div
                                    className="progress-fill"
                                    style={{ width: `${student.progress_percentage}%` }}
                                  ></div>
                                </div>
                              </div>
                              <div className="percentage">{student.progress_percentage}%</div>
                            </div>
                          ))}
                      </div>
                    ) : (
                      <p className="text-muted">No students enrolled yet</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Students Tab */}
          {activeTab === "students" && (
            <div className="students-content">
              <div className="content-card">
                <h3 className="card-title">
                  <i className="bi bi-people me-2"></i>
                  Enrolled Students
                </h3>
                {students.length === 0 ? (
                  <p className="text-muted">No students enrolled in this course yet</p>
                ) : (
                  <div className="students-table-wrapper">
                    <table className="students-table">
                      <thead>
                        <tr>
                          <th>Student</th>
                          <th>Progress</th>
                          <th>Lessons</th>
                          <th>Quizzes</th>
                          <th>Problems</th>
                          <th>Avg Score</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {students.map((student) => (
                          <tr key={student.student_id}>
                            <td>
                              <div className="student-cell">
                                <div className="student-name">{student.name}</div>
                                <div className="student-email-small">{student.email}</div>
                              </div>
                            </td>
                            <td>
                              <div className="progress-cell">
                                <span className="progress-percent">{student.progress_percentage}%</span>
                                <div className="progress-bar-mini">
                                  <div
                                    className="progress-fill"
                                    style={{ width: `${student.progress_percentage}%` }}
                                  ></div>
                                </div>
                              </div>
                            </td>
                            <td>
                              <span className="fraction">
                                {student.completed_lessons} / {student.total_lessons}
                              </span>
                            </td>
                            <td>
                              <span className="fraction">
                                {student.completed_quizzes} / {student.total_quizzes}
                              </span>
                            </td>
                            <td>
                              <span className="fraction">
                                {student.problems_solved} / {student.total_problems}
                              </span>
                            </td>
                            <td>
                              <span className={`score-badge ${student.avg_quiz_score >= 7 ? 'good' : student.avg_quiz_score >= 5 ? 'ok' : 'poor'}`}>
                                {student.avg_quiz_score.toFixed(1)}
                              </span>
                            </td>
                            <td>
                              <Link
                                to={`/teacher/student/${student.student_id}`}
                                className="btn-view-details"
                              >
                                View Details
                              </Link>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Lessons Tab */}
          {activeTab === "lessons" && (
            <div className="lessons-content">
              <div className="content-card">
                <h3 className="card-title">
                  <i className="bi bi-book me-2"></i>
                  Lesson Completion Rates
                </h3>
                {analytics.lesson_analytics.length === 0 ? (
                  <p className="text-muted">No lessons in this course yet</p>
                ) : (
                  <div className="lessons-list">
                    {analytics.lesson_analytics.map((lesson) => (
                      <div key={lesson.lesson_id} className="lesson-item">
                        <div className="lesson-info">
                          <h4 className="lesson-title">{lesson.lesson_title}</h4>
                          <span className="lesson-stats">
                            {lesson.completed_by} / {analytics.overview.total_students} students completed
                          </span>
                        </div>
                        <div className="lesson-completion">
                          <div className="completion-bar">
                            <div
                              className="completion-fill"
                              style={{ width: `${lesson.completion_rate}%` }}
                            ></div>
                          </div>
                          <span className="completion-percentage">{lesson.completion_rate}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Quizzes Tab */}
          {activeTab === "quizzes" && (
            <div className="quizzes-content">
              <div className="content-card">
                <h3 className="card-title">
                  <i className="bi bi-clipboard-check me-2"></i>
                  Quiz Performance
                </h3>
                {analytics.quiz_analytics.length === 0 ? (
                  <p className="text-muted">No quizzes in this course yet</p>
                ) : (
                  <div className="quizzes-grid">
                    {analytics.quiz_analytics.map((quiz) => (
                      <div key={quiz.quiz_id} className="quiz-card">
                        <div className="quiz-header">
                          <h4 className="quiz-title">{quiz.quiz_title}</h4>
                          <span className={`difficulty-badge ${quiz.difficulty.toLowerCase()}`}>
                            {quiz.difficulty}
                          </span>
                        </div>
                        <div className="quiz-stats">
                          <div className="stat-item">
                            <span className="stat-label">Total Attempts</span>
                            <span className="stat-value-small">{quiz.total_attempts}</span>
                          </div>
                          <div className="stat-item">
                            <span className="stat-label">Unique Students</span>
                            <span className="stat-value-small">{quiz.unique_students}</span>
                          </div>
                          <div className="stat-item">
                            <span className="stat-label">Avg Score</span>
                            <span className="stat-value-small">{quiz.avg_score.toFixed(1)}</span>
                          </div>
                          <div className="stat-item">
                            <span className="stat-label">Avg %</span>
                            <span className={`stat-value-small ${quiz.avg_percentage >= 70 ? 'text-success' : quiz.avg_percentage >= 50 ? 'text-warning' : 'text-danger'}`}>
                              {quiz.avg_percentage.toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Problems Tab */}
          {activeTab === "problems" && (
            <div className="problems-content">
              <div className="content-card">
                <h3 className="card-title">
                  <i className="bi bi-code-square me-2"></i>
                  Coding Problem Statistics
                </h3>
                {analytics.problem_analytics.length === 0 ? (
                  <p className="text-muted">No coding problems in this course yet</p>
                ) : (
                  <div className="problems-list">
                    {analytics.problem_analytics.map((problem) => (
                      <div key={problem.problem_id} className="problem-item">
                        <div className="problem-info">
                          <div className="problem-header">
                            <h4 className="problem-title">{problem.problem_title}</h4>
                            <span className={`difficulty-badge ${problem.difficulty.toLowerCase()}`}>
                              {problem.difficulty}
                            </span>
                          </div>
                          <div className="problem-stats-row">
                            <span className="stat">
                              <i className="bi bi-check-circle me-1"></i>
                              Solved by {problem.solved_by} students
                            </span>
                            <span className="stat">
                              <i className="bi bi-arrow-repeat me-1"></i>
                              {problem.total_attempts} attempts
                            </span>
                            <span className={`success-rate ${problem.success_rate >= 50 ? 'good' : problem.success_rate >= 25 ? 'ok' : 'low'}`}>
                              <i className="bi bi-graph-up me-1"></i>
                              {problem.success_rate}% success rate
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </PageTransition>
  );
};

export default CourseAnalytics;
