import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import AuthLayout from "../components/AuthLayout";
import api from "../services/api";
import "./Register.css";

const Register = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, role, isApproved } = useAuth();
  const isTeacherRegister = location.pathname.includes("/register/teacher");
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    role: isTeacherRegister ? "teacher" : "student",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitAttempted, setSubmitAttempted] = useState(false);

  useEffect(() => {
    if (isTeacherRegister) {
      setFormData((prev) => ({ ...prev, role: "teacher" }));
    }
  }, [isTeacherRegister]);

  useEffect(() => {
    if (isTeacherRegister && isAuthenticated) {
      const redirectTo = !role
        ? "/role-select"
        : role === "teacher" && isApproved === false
        ? "/role-select"
        : role === "teacher"
        ? "/teacher/dashboard"
        : "/learn";
      navigate(redirectTo, { replace: true });
    }
  }, [isTeacherRegister, isAuthenticated, role, isApproved, navigate]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitAttempted(true);

    if (!formData.name || !formData.email || !formData.password) {
      setError("Please fill out all fields.");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setIsSubmitting(true);
      await api.post("/register", {
        name: formData.name,
        email: formData.email,
        role: formData.role,
        password: formData.password,
      });

      navigate("/login", { replace: true });
    } catch (err) {
      const message = err?.response?.data?.error || "Registration failed.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const passwordStrength = useMemo(() => {
    const value = formData.password;
    if (!value) {
      return { label: "", score: 0 };
    }

    let score = 0;
    if (value.length >= 8) score += 1;
    if (/[A-Z]/.test(value)) score += 1;
    if (/[0-9]/.test(value)) score += 1;
    if (/[^A-Za-z0-9]/.test(value)) score += 1;

    if (score <= 1) {
      return { label: "Weak", score, color: "bg-danger" };
    }

    if (score <= 3) {
      return { label: "Medium", score, color: "bg-warning" };
    }

    return { label: "Strong", score, color: "bg-success" };
  }, [formData.password]);

  const inlineErrors = useMemo(
    () => ({
      name: submitAttempted && !formData.name ? "Full name is required." : "",
      email: submitAttempted && !formData.email ? "Email is required." : "",
      password: submitAttempted && !formData.password ? "Password is required." : "",
      confirmPassword:
        submitAttempted && !formData.confirmPassword
          ? "Please confirm your password."
          : formData.confirmPassword && formData.password !== formData.confirmPassword
          ? "Passwords do not match."
          : "",
    }),
    [formData, submitAttempted]
  );

  return (
    <AuthLayout
      title="Create Your Account"
      subtitle="Join thousands of focused learners and start mastering new skills"
    >
      <form onSubmit={handleSubmit} className="register-form">
        <div className="form-group">
          <label htmlFor="name" className="form-label">
            Full Name
          </label>
          <input
            id="name"
            name="name"
            type="text"
            className="form-control"
            placeholder="John Doe"
            value={formData.name}
            onChange={handleChange}
            autoComplete="name"
            required
          />
          {inlineErrors.name ? (
            <div className="text-danger small mt-1">{inlineErrors.name}</div>
          ) : null}
        </div>

        <div className="form-group">
          <label htmlFor="email" className="form-label">
            Email Address
          </label>
          <input
            id="email"
            name="email"
            type="email"
            className="form-control"
            placeholder="you@example.com"
            value={formData.email}
            onChange={handleChange}
            autoComplete="email"
            required
          />
          {inlineErrors.email ? (
            <div className="text-danger small mt-1">{inlineErrors.email}</div>
          ) : null}
        </div>

        {isTeacherRegister ? null : (
          <div className="form-group">
            <label htmlFor="role" className="form-label">
              I am a
            </label>
            <select
              id="role"
              name="role"
              className="form-control"
              value={formData.role}
              onChange={handleChange}
              autoComplete="off"
            >
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
            </select>
          </div>
        )}

        <div className="form-group">
          <label htmlFor="password" className="form-label">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            className="form-control"
            placeholder="••••••••"
            value={formData.password}
            onChange={handleChange}
            autoComplete="new-password"
            required
          />
          {inlineErrors.password ? (
            <div className="text-danger small mt-1">{inlineErrors.password}</div>
          ) : null}
        </div>

        {formData.password ? (
          <div className="password-strength mb-3">
            <div className="d-flex justify-content-between small text-muted mb-1">
              <span>Strength</span>
              <span>{passwordStrength.label}</span>
            </div>
            <div className="progress" style={{ height: "6px" }}>
              <div
                className={`progress-bar ${passwordStrength.color || "bg-secondary"}`}
                role="progressbar"
                style={{ width: `${(passwordStrength.score / 4) * 100}%` }}
                aria-valuenow={passwordStrength.score}
                aria-valuemin="0"
                aria-valuemax="4"
              />
            </div>
          </div>
        ) : null}

        <div className="form-group">
          <label htmlFor="confirmPassword" className="form-label">
            Confirm Password
          </label>
          <input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            className="form-control"
            placeholder="••••••••"
            value={formData.confirmPassword}
            onChange={handleChange}
            autoComplete="new-password"
            required
          />
          {inlineErrors.confirmPassword ? (
            <div className="text-danger small mt-1">
              {inlineErrors.confirmPassword}
            </div>
          ) : null}
        </div>

        {error ? (
          <div className="alert alert-danger mb-3" role="alert">
            {error}
          </div>
        ) : null}

        <button
          type="submit"
          className="btn btn-primary btn-register w-100"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Creating account..." : "Create Account"}
        </button>
      </form>

      <p className="auth-footer mt-4 text-center">
        Already have an account? <Link to="/login" className="fw-semibold">Sign In</Link>
      </p>
    </AuthLayout>
  );
};

export default Register;
