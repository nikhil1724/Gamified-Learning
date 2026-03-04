import { useEffect, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";

import ProfileDropdown from "./ProfileDropdown";
import NotificationBell from "./NotificationBell";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

const Navbar = () => {
  const navigate = useNavigate();
  const { isAuthenticated, logout, role, user } = useAuth();
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 4);
    };

    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleLogout = async () => {
    try {
      await api.post("/auth/logout");
    } catch (error) {
      console.error("Logout failed", error);
    } finally {
      logout();
      navigate("/", { replace: true });
    }
  };

  return (
    <nav
      className={`navbar navbar-expand-lg navbar-light navbar-theme ${
        isScrolled ? "navbar-theme--scrolled" : ""
      }`}
    >
      <div className="container navbar-container">
        <Link className="navbar-brand fw-bold" to="/">
          Gamified Learning
        </Link>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#mainNavbar"
          aria-controls="mainNavbar"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon" />
        </button>
        <div className="collapse navbar-collapse" id="mainNavbar">
          {isAuthenticated ? (
            <div className="navbar-primary-wrap">
              <ul className="navbar-nav navbar-primary">
                {role === "admin" ? (
                  <>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/admin/dashboard">
                        Dashboard
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/admin/teachers">
                        Teachers
                      </NavLink>
                    </li>
                  </>
                ) : role === "teacher" ? (
                  <>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/teacher/dashboard">
                        Dashboard
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/teacher/courses">
                        Courses
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/teacher/problems">
                        Problems
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/teacher/course-content">
                        Content
                      </NavLink>
                    </li>
                  </>
                ) : (
                  <>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/learn">
                        Learn
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/courses">
                        Tracks
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/problems">
                        Problems
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link navbar-link" to="/learn/courses">
                        Courses
                      </NavLink>
                    </li>
                  </>
                )}
              </ul>
              <div className="navbar-actions">
                <NotificationBell />
                <ProfileDropdown user={user} role={role} onLogout={handleLogout} />
              </div>
            </div>
          ) : (
            <div className="navbar-primary-wrap">
              <ul className="navbar-nav navbar-primary">
                <li className="nav-item">
                  <NavLink className="nav-link navbar-link" to="/learn">
                    Learn
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link navbar-link" to="/courses">
                    Tracks
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link navbar-link" to="/problems">
                    Problems
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link navbar-link" to="/learn/courses">
                    Courses
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link navbar-link" to="/leaderboard">
                    Leaderboard
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link navbar-link" to="/rewards">
                    Rewards
                  </NavLink>
                </li>
              </ul>
              <div className="navbar-actions">
                <Link to="/role-select" className="btn btn-outline-primary btn-sm me-2">
                  Login
                </Link>
                <Link to="/register" className="btn btn-primary btn-sm">
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
