import PropTypes from "prop-types";
import "./AuthLayout.css";

const AuthLayout = ({
  children,
  title,
  subtitle,
  illustration = null,
  stacked = false,
}) => {
  return (
    <div className={`auth-page ${stacked ? "auth-page--stacked" : ""}`.trim()}>
      {/* Left side: Branding & Info */}
      <div className="auth-sidebar">
        <div className="auth-sidebar__content">
          <div className="auth-logo">
            <div className="auth-logo__icon">📚</div>
            <h1 className="auth-logo__text">Gamified Learning</h1>
          </div>

          <div className="auth-info">
            <h2 className="auth-info__title">Master Skills Through Gamified Learning</h2>
            <p className="auth-info__description">
              Join thousands of learners who are leveling up their skills through interactive quizzes,
              adaptive learning paths, and competitive challenges.
            </p>

            <ul className="auth-features">
              <li className="auth-feature">
                <span className="auth-feature__icon">✓</span>
                <div>
                  <h4>Adaptive Learning</h4>
                  <p>Personalized content based on your pace and performance</p>
                </div>
              </li>
              <li className="auth-feature">
                <span className="auth-feature__icon">✓</span>
                <div>
                  <h4>Gamified Progress</h4>
                  <p>Earn XP, unlock badges, and climb the leaderboard</p>
                </div>
              </li>
              <li className="auth-feature">
                <span className="auth-feature__icon">✓</span>
                <div>
                  <h4>Real-time Analytics</h4>
                  <p>Track your progress with detailed performance insights</p>
                </div>
              </li>
              <li className="auth-feature">
                <span className="auth-feature__icon">✓</span>
                <div>
                  <h4>Expert Content</h4>
                  <p>Learn from curated courses and community-driven problems</p>
                </div>
              </li>
            </ul>
          </div>

          <div className="auth-footer-sidebar">
            <p className="auth-footer-text">
              Trusted by learners worldwide. Start your journey today.
            </p>
          </div>
        </div>
      </div>

      {/* Right side: Form */}
      <div className="auth-form-area">
        <div className="auth-form-container">
          <div className="auth-form-header">
            {title && <h2 className="auth-form-title">{title}</h2>}
            {subtitle && <p className="auth-form-subtitle">{subtitle}</p>}
          </div>

          <div className="auth-form-content">{children}</div>
        </div>
      </div>
    </div>
  );
};

AuthLayout.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string,
  subtitle: PropTypes.string,
  illustration: PropTypes.string,
  stacked: PropTypes.bool,
};

export default AuthLayout;
