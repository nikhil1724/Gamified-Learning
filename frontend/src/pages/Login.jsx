import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import PageTransition from "../components/PageTransition";
import api from "../services/api";
import "./Login.css";

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, role, isApproved } = useAuth();
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const getRoleHome = (userRole, approvalState) => {
    if (!userRole) {
      return "/role-select";
    }
    if (userRole === "admin") {
      return "/admin/dashboard";
    }
    if (userRole === "teacher" && approvalState === false) {
      return "/role-select";
    }
    return userRole === "teacher" ? "/teacher/dashboard" : "/learn";
  };

  const expectedRole = useMemo(() => {
    if (location.pathname.includes("/login/teacher")) {
      return "teacher";
    }
    if (location.pathname.includes("/login/student")) {
      return "student";
    }
    if (location.pathname.includes("/login/admin")) {
      return "admin";
    }
    return null;
  }, [location.pathname]);

  useEffect(() => {
    if (isAuthenticated) {
      navigate(getRoleHome(role, isApproved), { replace: true });
    }
  }, [isAuthenticated, role, isApproved, navigate]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!formData.email || !formData.password) {
      setError("Please enter email and password.");
      return;
    }

    try {
      setIsSubmitting(true);
      const response = await api.post("/login", {
        email: formData.email,
        password: formData.password,
      });

      const { token, user } = response.data;

      if (expectedRole && user?.role && user.role !== expectedRole) {
        setError(`This account is registered as a ${user.role}. Use the correct login.`);
        return;
      }

      login(token, user);
      navigate(getRoleHome(user?.role, user?.is_approved), { replace: true });
    } catch (err) {
      const message = err?.response?.data?.error || "Login failed.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PageTransition>
      <div className="login-page">
        <div className="login-container">
          <div className="login-card">
            <div className="login-header">
              <h2 className="login-title">Welcome Back</h2>
              <p className="login-subtitle">Sign in to your account and continue your learning journey</p>
            </div>
            <form onSubmit={handleSubmit} className="login-form">
              <div className="form-group">
                <input
                  id="email"
                  name="email"
                  type="email"
                  className="form-control"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Email address"
                  autoComplete="email"
                  required
                />
              </div>

              <div className="form-group">
                <div className="password-input-wrapper">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    className="form-control"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Password"
                    autoComplete="current-password"
                    required
                  />
                  <button
                    type="button"
                    className="password-toggle-btn"
                    onClick={() => setShowPassword((prev) => !prev)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? "👁️‍🗨️" : "👁️"}
                  </button>
                </div>
              </div>

              <div className="forgot-password-link">
                <a href="#">Forgot your password?</a>
              </div>

              {error && <div className="alert alert-danger">{error}</div>}

              <button type="submit" className="btn btn-primary btn-login" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
                    Signing in...
                  </>
                ) : (
                  "Sign In"
                )}
              </button>

              <div className="auth-footer">
                <p>
                  Don&apos;t have an account?{" "}
                  <Link to="/register">Create account</Link>
                </p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default Login;
