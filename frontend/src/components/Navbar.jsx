import { useEffect, useState } from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { GraduationCap } from "lucide-react";

import ProfileDropdown from "./ProfileDropdown";
import NotificationBell from "./NotificationBell";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, logout, role, user } = useAuth();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 4);
    };

    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    setIsMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const isMobileView = typeof window !== "undefined" && window.innerWidth <= 991;
    if (!isMobileView) {
      document.body.style.overflow = "";
      return () => {
        document.body.style.overflow = "";
      };
    }

    document.body.style.overflow = isMenuOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [isMenuOpen]);

  useEffect(() => {
    if (!isMenuOpen) {
      return undefined;
    }

    const onEscape = (event) => {
      if (event.key === "Escape") {
        setIsMenuOpen(false);
      }
    };

    window.addEventListener("keydown", onEscape);
    return () => {
      window.removeEventListener("keydown", onEscape);
    };
  }, [isMenuOpen]);

  const handleLogout = async () => {
    try {
      await api.post("/auth/logout");
    } catch (error) {
      console.error("Logout failed", error);
    } finally {
      logout();
      setIsMenuOpen(false);
      navigate("/", { replace: true });
    }
  };

  const closeMenu = () => setIsMenuOpen(false);

  return (
    <nav
      className={`navbar navbar-expand-lg navbar-light navbar-theme ${
        isScrolled ? "navbar-theme--scrolled" : ""
      }`}
    >
      <div className="container navbar-container">
        <Link className="navbar-brand fw-bold" to="/">
          <span className="brand-logo" aria-hidden="true">
            <GraduationCap size={16} strokeWidth={2.4} />
          </span>
          <span className="brand-text">Gamified Learning</span>
        </Link>
        <button
          className={`navbar-toggler ${isMenuOpen ? "" : "collapsed"}`}
          type="button"
          aria-controls="mainNavbar"
          aria-expanded={isMenuOpen}
          aria-label="Toggle navigation"
          onClick={() => setIsMenuOpen((prev) => !prev)}
        >
          <span className="navbar-toggler-icon" />
        </button>
        <div className={`navbar-collapse collapse ${isMenuOpen ? "show" : ""}`} id="mainNavbar">
          {isAuthenticated ? (
            <div className="navbar-primary-wrap">
              <ul className="navbar-nav navbar-primary">
                {role === "admin" ? (
                  <>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/admin/dashboard" onClick={closeMenu}>
                        Dashboard
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/admin/teachers" onClick={closeMenu}>
                        Teachers
                      </NavLink>
                    </li>
                  </>
                ) : role === "teacher" ? (
                  <>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/teacher/dashboard" onClick={closeMenu}>
                        Dashboard
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/teacher/courses" onClick={closeMenu}>
                        Courses
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/teacher/problems" onClick={closeMenu}>
                        Problems
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/teacher/course-content" onClick={closeMenu}>
                        Content
                      </NavLink>
                    </li>
                  </>
                ) : (
                  <>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/learn" onClick={closeMenu}>
                        Learn
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/courses" onClick={closeMenu}>
                        Tracks
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/problems" onClick={closeMenu}>
                        Problems
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/learn/courses" onClick={closeMenu}>
                        Courses
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/student/dashboard" onClick={closeMenu}>
                        My Progress
                      </NavLink>
                    </li>
                  </>
                )}
              </ul>
              <div className="navbar-actions">
                {role === "teacher" ? (
                  <Link to="/teacher/courses" className="btn btn-outline-primary btn-sm d-none d-lg-inline-flex navbar-analytics-btn" onClick={closeMenu}>
                    Analytics Hub
                  </Link>
                ) : null}
                <NotificationBell />
                <ProfileDropdown user={user} role={role} onLogout={handleLogout} />
              </div>
            </div>
          ) : (
            <div className="navbar-primary-wrap">
              <ul className="navbar-nav navbar-primary">
                <li className="nav-item">
                  <NavLink className="nav-link navbar-link" to="/learn" onClick={closeMenu}>
                    Learn
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link navbar-link" to="/courses" onClick={closeMenu}>
                    Tracks
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link navbar-link" to="/problems" onClick={closeMenu}>
                    Problems
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link navbar-link" to="/learn/courses" onClick={closeMenu}>
                    Courses
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link navbar-link" to="/leaderboard" onClick={closeMenu}>
                    Leaderboard
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link navbar-link" to="/rewards" onClick={closeMenu}>
                    Rewards
                  </NavLink>
                </li>
              </ul>
              <div className="navbar-actions">
                <Link to="/login" className="btn btn-outline-primary btn-sm me-2 navbar-login-btn" onClick={closeMenu}>
                  Login
                </Link>
                <Link to="/register" className="btn btn-primary btn-sm navbar-register-btn" onClick={closeMenu}>
                  Register
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
