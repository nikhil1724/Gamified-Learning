import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import PageTransition from "../components/PageTransition";
import api from "../services/api";
import "./StudentPerformanceDetail.css";

const StudentPerformanceDetail = () => {
  const { studentId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchStudentPerformance();
  }, [studentId]);

  const fetchStudentPerformance = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/teacher/student/${studentId}/performance`);
      setData(response.data);
      setError("");
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to load student performance");
      console.error("Failed to fetch student performance:", err);
    } finally {
      setLoading(false);
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
            <p className="mt-3 text-muted">Loading student performance...</p>
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
          <Link to="/teacher/students" className="btn btn-primary">
            <i className="bi bi-arrow-left me-2"></i>
            Back to Students
          </Link>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="container py-5">
        {/* Back Link */}
        <Link to="/teacher/students" className="back-link mb-4">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Students
        </Link>

        {/* Student Header */}
        <div className="student-performance-header mb-5">
          <div className="student-profile">
            <div className="student-avatar-large">
              <i className="bi bi-person-fill"></i>
            </div>
            <div>
              <h1 className="mb-2">{data.student_name}</h1>
              <p className="text-muted mb-3">{data.student_email}</p>
              <div className="student-badges">
                <span className="badge-item level">
                  <i className="bi bi-star-fill me-1"></i>
                  Level {data.level}
                </span>
                <span className="badge-item xp">
                  <i className="bi bi-trophy-fill me-1"></i>
                  {data.xp_points} XP
                </span>
                <span className="badge-item streak">
                  <i className="bi bi-fire me-1"></i>
                  {data.daily_streak} Day Streak
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Courses Performance */}
        <div className="courses-performance">
          <h2 className="section-title mb-4">
            <i className="bi bi-graph-up me-2"></i>
            Performance by Course
          </h2>

          {data.courses.length === 0 ? (
            <div className="alert alert-info">
              This student is not enrolled in any of your courses.
            </div>
          ) : (
            <div className="courses-grid">
              {data.courses.map((course) => (
                <div key={course.course_id} className="course-performance-card">
                  <div className="course-header">
                    <h3 className="course-title">{course.course_title}</h3>
                    <span className="enrolled-date">
                      Enrolled: {new Date(course.enrolled_at).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Lessons Progress */}
                  <div className="progress-section">
                    <div className="progress-header">
                      <span className="progress-label">
                        <i className="bi bi-book me-2"></i>
                        Lessons
                      </span>
                      <span className="progress-stats">
                        {course.lessons.completed} / {course.lessons.total} 
                        <span className="percentage"> ({course.lessons.percentage}%)</span>
                      </span>
                    </div>
                    <div className="progress-bar-container">
                      <div 
                        className="progress-bar-fill lessons"
                        style={{ width: `${course.lessons.percentage}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Quizzes Performance */}
                  <div className="progress-section">
                    <div className="progress-header">
                      <span className="progress-label">
                        <i className="bi bi-clipboard-check me-2"></i>
                        Quizzes
                      </span>
                      <span className="progress-stats">
                        {course.quizzes.attempts} attempts • Avg Score: {course.quizzes.avg_score}
                      </span>
                    </div>
                    
                    {course.quizzes.details.length > 0 && (
                      <div className="quiz-details">
                        <p className="quiz-details-title">Recent Attempts:</p>
                        {course.quizzes.details.map((quiz, idx) => (
                          <div key={idx} className="quiz-attempt">
                            <div className="quiz-info">
                              <span className="quiz-name">{quiz.quiz_title}</span>
                              <span className={`difficulty-badge ${quiz.difficulty.toLowerCase()}`}>
                                {quiz.difficulty}
                              </span>
                            </div>
                            <div className="quiz-score">
                              <span className="score-text">
                                {quiz.score} / {quiz.total_questions}
                              </span>
                              <span className={`percentage ${quiz.percentage >= 70 ? 'good' : quiz.percentage >= 50 ? 'ok' : 'poor'}`}>
                                {quiz.percentage}%
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Problems Performance */}
                  {course.problems.total > 0 && (
                    <div className="progress-section">
                      <div className="progress-header">
                        <span className="progress-label">
                          <i className="bi bi-code-square me-2"></i>
                          Coding Problems
                        </span>
                        <span className="progress-stats">
                          {course.problems.solved} / {course.problems.total} solved
                        </span>
                      </div>
                      <div className="progress-bar-container">
                        <div 
                          className="progress-bar-fill problems"
                          style={{ 
                            width: `${course.problems.total > 0 ? (course.problems.solved / course.problems.total * 100) : 0}%` 
                          }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </PageTransition>
  );
};

export default StudentPerformanceDetail;
