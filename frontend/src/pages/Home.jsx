import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { BookOpen, Code2, Trophy, LineChart } from "lucide-react";
import PageTransition from "../components/PageTransition";
import "./Home.css";

const features = [
  {
    icon: BookOpen,
    title: "Learn",
    description: "Follow structured courses with clear lesson paths.",
  },
  {
    icon: Code2,
    title: "Practice",
    description: "Solve coding problems to build real confidence.",
  },
  {
    icon: Trophy,
    title: "Earn Rewards",
    description: "Unlock badges, streak milestones, and achievement boosts.",
  },
  {
    icon: LineChart,
    title: "Track Progress",
    description: "Visual dashboards show exactly how your skills are growing.",
  },
];

const stats = [
  { value: "50+", label: "Courses" },
  { value: "20+", label: "Problems" },
  { value: "10+", label: "Quizzes" },
  { value: "Live", label: "Real-time Leaderboard" },
];

const Home = () => {
  const pageRef = useRef(null);

  useEffect(() => {
    const root = pageRef.current;
    if (!root) {
      return undefined;
    }

    const revealNodes = root.querySelectorAll(".reveal-on-scroll");

    if (!("IntersectionObserver" in window)) {
      revealNodes.forEach((node) => node.classList.add("is-visible"));
      return undefined;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.12,
        rootMargin: "0px 0px -40px 0px",
      }
    );

    revealNodes.forEach((node) => observer.observe(node));

    return () => observer.disconnect();
  }, []);

  return (
    <PageTransition>
      <div className="landing-page" ref={pageRef}>
        <section className="hero-section">
          <div className="hero-orb hero-orb--one" aria-hidden="true" />
          <div className="hero-orb hero-orb--two" aria-hidden="true" />
          <div className="container">
            <div className="hero-content">
              <p className="hero-tagline">🚀 Gamified Learning Platform</p>
              <h1 className="hero-title">
                Learn Smarter, Practice Faster, and Grow with <span className="highlight">Learning</span>
              </h1>
              <p className="hero-subtitle">
                A premium coding education experience inspired by top product platforms with courses, challenges,
                rewards, and analytics in one place.
              </p>
              <div className="hero-buttons">
                <Link to="/register" className="btn btn-primary">
                  Start Learning Free
                </Link>
                <Link to="/learn" className="btn btn-outline-primary">
                  Explore Courses
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="features-section">
          <div className="container">
            <div className="section-head reveal-on-scroll">
              <h2>Everything You Need to Level Up</h2>
              <p>Modern learning workflows designed for clarity, confidence, and consistency.</p>
            </div>
            <div className="feature-grid reveal-on-scroll">
              {features.map((feature, index) => (
                <article
                  className="feature-card"
                  key={feature.title}
                  style={{ "--stagger-delay": `${index * 90}ms` }}
                >
                  <span className="feature-icon" aria-hidden="true">
                    <feature.icon size={22} strokeWidth={2.25} />
                  </span>
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="stats-section">
          <div className="container">
            <div className="stats-grid reveal-on-scroll">
              {stats.map((item, index) => (
                <div
                  className="stat-item"
                  key={item.label}
                  style={{ "--stagger-delay": `${index * 80}ms` }}
                >
                  <p className="stat-value">{item.value}</p>
                  <p className="stat-label">{item.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="cta-section">
          <div className="container cta-content reveal-on-scroll">
            <h2>Start Your Learning Journey Today 🚀</h2>
            <p>
              Join learners building real coding skills with focused practice and gamified progress.
            </p>
            <Link to="/register" className="btn btn-primary">
              Create Your Free Account
            </Link>
          </div>
        </section>
      </div>
    </PageTransition>
  );
};

export default Home;
