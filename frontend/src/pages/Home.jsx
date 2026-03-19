import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import PageTransition from "../components/PageTransition";
import "./Home.css";

const Home = () => {
  const [stats, setStats] = useState({
    courses: 0,
    challenges: 0,
    quizzes: 0,
    learners: 0,
  });

  useEffect(() => {
    // Animate stats
    const animateValue = (key, end, duration) => {
      let start = 0;
      const increment = end / (duration / 16);
      const timer = setInterval(() => {
        start += increment;
        if (start >= end) {
          setStats((prev) => ({ ...prev, [key]: end }));
          clearInterval(timer);
        } else {
          setStats((prev) => ({ ...prev, [key]: Math.ceil(start) }));
        }
      }, 16);
    };

    animateValue("courses", 10, 2000);
    animateValue("challenges", 50, 2000);
    animateValue("quizzes", 100, 2000);
    animateValue("learners", 500, 2000);
  }, []);

  const features = [
    {
      icon: "💻",
      title: "Coding Challenges",
      description: "Practice real-world programming problems with instant feedback and comprehensive test cases to build professional-grade coding skills.",
    },
    {
      icon: "📚",
      title: "Structured Learning Paths",
      description: "Follow expert-designed curriculum from fundamentals to advanced topics with hands-on labs and real-world projects.",
    },
    {
      icon: "🎮",
      title: "Gamified Engagement",
      description: "Earn XP points, unlock achievements, and climb leaderboards while maintaining consistent learning habits with streak tracking.",
    },
    {
      icon: "📝",
      title: "Interactive Assessments",
      description: "Reinforce learning with dynamic quizzes, auto-graded assignments, and detailed performance analytics.",
    },
    {
      icon: "📊",
      title: "Advanced Progress Insights",
      description: "Detailed analytics dashboards showing skill mastery, learning velocity, and personalized recommendations.",
    },
    {
      icon: "🤝",
      title: "Peer Collaboration",
      description: "Learn together with community discussions, code reviews, and collaborative problem-solving.",
    },
  ];

  const roles = [
    {
      icon: "🎓",
      title: "For Learners",
      description: "Accelerate your coding journey",
      features: [
        "Structured learning paths & courses",
        "Hundreds of coding challenges",
        "Real-time feedback & analytics",
        "Earn badges & climb leaderboards",
      ],
      link: "/login/student",
      primary: true,
    },
    {
      icon: "🧑‍🏫",
      title: "For Instructors",
      description: "Create engaging learning experiences",
      features: [
        "Build & publish custom courses",
        "Design coding challenges & quizzes",
        "Monitor student progress in real-time",
        "Access comprehensive analytics",
      ],
      link: "/login/teacher",
    },
    {
      icon: "🛡️",
      title: "For Administrators",
      description: "Manage your learning ecosystem",
      features: [
        "User & instructor management",
        "Platform activity monitoring",
        "System configuration & settings",
        "Comprehensive reporting tools",
      ],
      link: "/login/admin",
    },
  ];

  const gamificationFeatures = [
    { icon: "⭐", title: "XP Points System", description: "Earn points for every completed task, course, and challenge. Watch your skills grow with every achievement." },
    { icon: "🏆", title: "Badges & Achievements", description: "Unlock exclusive badges for milestones. Display your accomplishments in your public learner profile." },
    { icon: "🔥", title: "Daily Streak Tracking", description: "Build consistency and maintain daily learning streaks. Watch your longest streak grow as you commit to learning." },
    { icon: "📈", title: "Global Leaderboards", description: "Compete with learners worldwide. Track your ranking and celebrate your progress on community leaderboards." },
    { icon: "⭐", title: "XP Points System", description: "Earn points for every completed task" },
    { icon: "🏆", title: "Badges & Achievements", description: "Unlock achievements as you progress" },
    { icon: "🔥", title: "Daily Streak Tracking", description: "Build consistent learning habits" },
    { icon: "📈", title: "Leaderboards", description: "Compete with peers and climb rankings" },
  ];

  return (
    <PageTransition>
      <div className="landing-page">
        {/* Hero Section */}
        <section className="hero-section">
          <div className="container">
            <div className="hero-content">
              <motion.div
                className="hero-text"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                <h1 className="hero-title">
                  Master Programming Through <span className="highlight">Gamified Learning</span>
                </h1>
                <p className="hero-subtitle">
                  Transform your coding journey with interactive courses, real-world challenges, and an engaging reward system designed to keep you motivated and consistently progressing.
                </p>
                <div className="hero-buttons">
                  <Link to="/register" className="btn btn-primary btn-lg">
                    Start Learning
                  </Link>
                  <Link to="/role-select" className="btn btn-outline-primary btn-lg">
                    Explore Courses
                  </Link>
                </div>
              </motion.div>
              <motion.div
                className="hero-image"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <div className="hero-graphic">
                  <div className="code-window">
                    <div className="window-header">
                      <span className="dot"></span>
                      <span className="dot"></span>
                      <span className="dot"></span>
                    </div>
                    <div className="window-body">
                      <pre className="code-snippet">
                        <code>{`function learn() {
  const skills = [];
  while (motivated) {
    skills.push(
      practice()
    );
    earnRewards();
  }
  return success;
}`}</code>
                      </pre>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="features-section">
          <div className="container">
            <motion.div
              className="section-header"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              <h2 className="section-title">Platform Features</h2>
              <p className="section-subtitle">Everything you need to master programming</p>
            </motion.div>
            <div className="features-grid">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  className="feature-card"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <div className="feature-icon">{feature.icon}</div>
                  <h3 className="feature-title">{feature.title}</h3>
                  <p className="feature-description">{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Role-Based System Section */}
        <section className="roles-section">
          <div className="container">
            <motion.div
              className="section-header"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              <h2 className="section-title">Choose Your Path</h2>
              <p className="section-subtitle">Different experiences for different users</p>
            </motion.div>
            <div className="roles-grid">
              {roles.map((role, index) => (
                <motion.div
                  key={index}
                  className="role-card"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <div className="role-icon">{role.icon}</div>
                  <h3 className="role-title">{role.title}</h3>
                  {role.description && <p className="role-description">{role.description}</p>}
                  <ul className="role-features">
                    {role.features.map((feat, i) => (
                      <li key={i}>✓ {feat}</li>
                    ))}
                  </ul>
                  <Link to={role.link} className="btn btn-outline-primary w-100">
                    Get Started
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Gamification Section */}
        <section className="gamification-section">
          <div className="container">
            <motion.div
              className="section-header"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              <h2 className="section-title">Stay Motivated with Gamification</h2>
              <p className="section-subtitle">Engaging features to keep you learning</p>
            </motion.div>
            <div className="gamification-grid">
              {gamificationFeatures.map((item, index) => (
                <motion.div
                  key={index}
                  className="gamification-card"
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <div className="gamification-icon">{item.icon}</div>
                  <h4 className="gamification-title">{item.title}</h4>
                  <p className="gamification-description">{item.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Statistics Section */}
        <section className="stats-section">
          <div className="container">
            <div className="stats-grid">
              <motion.div
                className="stat-item"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5 }}
              >
                <div className="stat-value">{stats.courses}+</div>
                <div className="stat-label">Courses</div>
              </motion.div>
              <motion.div
                className="stat-item"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <div className="stat-value">{stats.challenges}+</div>
                <div className="stat-label">Coding Challenges</div>
              </motion.div>
              <motion.div
                className="stat-item"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <div className="stat-value">{stats.quizzes}+</div>
                <div className="stat-label">Quizzes</div>
              </motion.div>
              <motion.div
                className="stat-item"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                <div className="stat-value">{stats.learners}+</div>
                <div className="stat-label">Active Learners</div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="landing-footer">
          <div className="container">
            <div className="footer-content">
              <div className="footer-column">
                <h4 className="footer-title">Platform</h4>
                <ul className="footer-links">
                  <li><Link to="/register">Courses</Link></li>
                  <li><Link to="/register">Problems</Link></li>
                  <li><Link to="/register">Quizzes</Link></li>
                  <li><Link to="/register">Leaderboard</Link></li>
                </ul>
              </div>
              <div className="footer-column">
                <h4 className="footer-title">Resources</h4>
                <ul className="footer-links">
                  <li><Link to="/register">Learning Tracks</Link></li>
                  <li><Link to="/register">Documentation</Link></li>
                  <li><Link to="/register">Support</Link></li>
                </ul>
              </div>
              <div className="footer-column">
                <h4 className="footer-title">Community</h4>
                <ul className="footer-links">
                  <li><Link to="/register">Discussion</Link></li>
                  <li><Link to="/register">Feedback</Link></li>
                </ul>
              </div>
            </div>
            <div className="footer-bottom">
              <p>© 2026 Gamified Digital Learning Platform. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </div>
    </PageTransition>
  );
};

export default Home;
