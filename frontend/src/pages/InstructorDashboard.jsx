import { Link } from "react-router-dom";
import PageTransition from "../components/PageTransition";
import "./InstructorDashboard.css";

const InstructorDashboard = () => {
  return (
    <PageTransition>
      <div className="container py-5">
        {/* Header */}
        <div className="instructor-hero mb-5">
          <div>
            <span className="instructor-badge">Instructor Console</span>
            <h1 className="mb-2">Dashboard</h1>
            <p className="text-muted mb-0">Manage your courses, problems, and content.</p>
          </div>
        </div>

        {/* Quick Actions Grid */}
        <div className="row g-4">
          {/* Courses Card */}
          <div className="col-md-6 col-lg-4">
            <Link to="/teacher/courses" className="instructor-card instructor-card--courses">
              <div className="instructor-card__icon">
                <i className="bi bi-book-half"></i>
              </div>
              <div className="instructor-card__content">
                <h3>Manage Courses</h3>
                <p>Create and edit your courses</p>
              </div>
              <div className="instructor-card__arrow">
                <i className="bi bi-arrow-right"></i>
              </div>
            </Link>
          </div>

          {/* Problems Card */}
          <div className="col-md-6 col-lg-4">
            <Link to="/teacher/problems" className="instructor-card instructor-card--problems">
              <div className="instructor-card__icon">
                <i className="bi bi-code-square"></i>
              </div>
              <div className="instructor-card__content">
                <h3>Manage Problems</h3>
                <p>Create coding problems for students</p>
              </div>
              <div className="instructor-card__arrow">
                <i className="bi bi-arrow-right"></i>
              </div>
            </Link>
          </div>

          {/* Content Manager Card */}
          <div className="col-md-6 col-lg-4">
            <Link to="/teacher/course-content" className="instructor-card instructor-card--content">
              <div className="instructor-card__icon">
                <i className="bi bi-file-text"></i>
              </div>
              <div className="instructor-card__content">
                <h3>Content Manager</h3>
                <p>Manage lessons and course content</p>
              </div>
              <div className="instructor-card__arrow">
                <i className="bi bi-arrow-right"></i>
              </div>
            </Link>
          </div>
        </div>

        {/* Info Section */}
        <div className="instructor-info mt-5 p-4 rounded-3 bg-light">
          <div className="row g-4">
            <div className="col-md-6">
              <h4 className="mb-3">Your Dashboard</h4>
              <p className="text-muted mb-0">
                Use the cards above to manage your courses, create problems, and organize your course content. 
                All content you create is visible only to your students, and you have full control over editing and deletion.
              </p>
            </div>
            <div className="col-md-6">
              <h4 className="mb-3">Quick Stats</h4>
              <div className="row g-3">
                <div className="col-6">
                  <div className="stat-box">
                    <div className="stat-number">0</div>
                    <div className="stat-label">Courses Created</div>
                  </div>
                </div>
                <div className="col-6">
                  <div className="stat-box">
                    <div className="stat-number">0</div>
                    <div className="stat-label">Problems Created</div>
                  </div>
                </div>
                <div className="col-6">
                  <div className="stat-box">
                    <div className="stat-number">0</div>
                    <div className="stat-label">Active Students</div>
                  </div>
                </div>
                <div className="col-6">
                  <div className="stat-box">
                    <div className="stat-number">0</div>
                    <div className="stat-label">Total Enrolments</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default InstructorDashboard;
