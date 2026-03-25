import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import AuthField from "../components/auth/AuthField";
import PageTransition from "../components/PageTransition";
import { useAuth } from "../context/AuthContext";
import { getApiErrorMessage } from "../services/api";
import { loginUser } from "../services/authApi";

const getLoginRedirectPath = (role) => {
  if (role === "teacher") {
    return "/teacher-dashboard";
  }
  if (role === "admin") {
    return "/admin/dashboard";
  }
  return "/student-dashboard";
};

const Login = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated, role } = useAuth();
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [activePersona, setActivePersona] = useState("student");

  useEffect(() => {
    if (isAuthenticated) {
      navigate(getLoginRedirectPath(role), { replace: true });
    }
  }, [isAuthenticated, role, navigate]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: "" }));
    setApiError("");
  };

  const validateForm = () => {
    const nextErrors = {};

    if (!formData.email.trim()) {
      nextErrors.email = "Email is required.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
      nextErrors.email = "Enter a valid email address.";
    }

    if (!formData.password) {
      nextErrors.password = "Password is required.";
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setApiError("");

    if (!validateForm()) {
      return;
    }

    try {
      setIsSubmitting(true);
      const response = await loginUser({
        email: formData.email.trim(),
        password: formData.password,
      });

      const { token, user } = response.data;

      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(user));
      login(token, user);

      navigate(getLoginRedirectPath(user?.role), { replace: true });
    } catch (error) {
      if (error?.response?.data?.requires_otp && error?.response?.data?.email) {
        navigate(`/verify-otp?email=${encodeURIComponent(error.response.data.email)}`, { replace: true });
        return;
      }

      setApiError(getApiErrorMessage(error, "Invalid email or password."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PageTransition>
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-sky-100 via-indigo-100 to-violet-100 px-4 py-10 sm:px-6">
        <div className="w-full max-w-[430px] rounded-2xl border border-white/70 bg-white/95 p-6 shadow-2xl shadow-indigo-200/60 backdrop-blur sm:p-8">
          <div className="mb-6 rounded-xl bg-slate-100 p-1.5">
            <div className="grid grid-cols-2 gap-1">
              <button
                type="button"
                onClick={() => setActivePersona("student")}
                className={`rounded-lg px-3 py-2 text-sm font-semibold transition-all duration-200 ${
                  activePersona === "student"
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-slate-600 hover:bg-white"
                }`}
              >
                Student 👨‍🎓
              </button>
              <button
                type="button"
                onClick={() => setActivePersona("teacher")}
                className={`rounded-lg px-3 py-2 text-sm font-semibold transition-all duration-200 ${
                  activePersona === "teacher"
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-slate-600 hover:bg-white"
                }`}
              >
                Teacher 👨‍🏫
              </button>
            </div>
          </div>

          <div className="mb-6 text-center">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">Welcome Back</h1>
            <p className="mt-2 text-sm text-slate-600">
              Sign in to your account and continue your learning journey
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <AuthField
              id="email"
              name="email"
              type="email"
              label="Email"
              value={formData.email}
              onChange={handleChange}
              autoComplete="email"
              placeholder="you@example.com"
              error={errors.email}
            />

            <AuthField
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              label="Password"
              value={formData.password}
              onChange={handleChange}
              autoComplete="current-password"
              placeholder="Enter your password"
              error={errors.password}
              rightSlot={
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="rounded-md p-1 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.8">
                      <path d="M3 3l18 18" />
                      <path d="M10.58 10.58a2 2 0 102.83 2.83" />
                      <path d="M9.88 5.09A10.94 10.94 0 0112 5c6 0 10 7 10 7a18.7 18.7 0 01-3.07 3.86" />
                      <path d="M6.1 6.1A18.48 18.48 0 002 12s4 7 10 7a9.76 9.76 0 004.59-1.08" />
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.8">
                      <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  )}
                </button>
              }
            />

            <div className="text-right">
              <a
                href="mailto:support@gamifiedlearning.quest?subject=Password%20Reset%20Request"
                className="text-sm font-medium text-blue-600 hover:text-blue-700"
              >
                Forgot password?
              </a>
            </div>

            {apiError ? (
              <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                {apiError}
              </div>
            ) : null}

            <button
              type="submit"
              disabled={isSubmitting}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-300/50 transition duration-200 hover:scale-[1.01] hover:from-blue-700 hover:to-indigo-700 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isSubmitting ? (
                <>
                  <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/90 border-r-transparent" />
                  Signing in...
                </>
              ) : (
                "Sign In"
              )}
            </button>

            <p className="text-center text-sm text-slate-600">
              Don&apos;t have an account?{" "}
              <Link to="/register" className="font-semibold text-blue-600 hover:text-blue-700">
                Create account
              </Link>
            </p>
          </form>
        </div>
      </div>
    </PageTransition>
  );
};

export default Login;
