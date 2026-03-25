import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import AuthField from "../components/auth/AuthField";
import PageTransition from "../components/PageTransition";
import { useAuth } from "../context/AuthContext";
import { getApiErrorMessage } from "../services/api";
import { registerUser } from "../services/authApi";

const Register = () => {
  const navigate = useNavigate();
  const { isAuthenticated, role } = useAuth();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    role: "student",
  });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate(role === "teacher" ? "/teacher-dashboard" : "/student-dashboard", { replace: true });
    }
  }, [isAuthenticated, role, navigate]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: "" }));
    setApiError("");
    setSuccessMessage("");
  };

  const validateForm = () => {
    const nextErrors = {};

    if (!formData.name.trim()) {
      nextErrors.name = "Full Name is required.";
    }

    if (!formData.email.trim()) {
      nextErrors.email = "Email is required.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
      nextErrors.email = "Enter a valid email address.";
    }

    if (!formData.password) {
      nextErrors.password = "Password is required.";
    }

    if (!formData.confirmPassword) {
      nextErrors.confirmPassword = "Confirm Password is required.";
    } else if (formData.password !== formData.confirmPassword) {
      nextErrors.confirmPassword = "Passwords do not match.";
    }

    if (!["student", "teacher"].includes(formData.role)) {
      nextErrors.role = "Select a valid role.";
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setApiError("");
    setSuccessMessage("");

    if (!validateForm()) {
      return;
    }

    try {
      setIsSubmitting(true);
      const response = await registerUser({
        name: formData.name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        role: formData.role,
      });

      const message = response?.data?.message || "Registration successful. You can now sign in.";
      setSuccessMessage(message);

      if (response?.data?.requires_otp) {
        setTimeout(() => {
          navigate(`/verify-otp?email=${encodeURIComponent(response.data.email || formData.email.trim())}`, {
            state: {
              cooldownSeconds: Number(response?.data?.resend_cooldown_seconds || 45),
              sentAt: response?.data?.sent_at || null,
            },
            replace: true,
          });
        }, 1200);
        return;
      }

      setFormData({
        name: "",
        email: "",
        password: "",
        confirmPassword: "",
        role: "student",
      });
    } catch (error) {
      setApiError(getApiErrorMessage(error, "Registration failed."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PageTransition>
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-sky-100 via-indigo-100 to-violet-100 px-4 py-10 sm:px-6">
        <div className="w-full max-w-[430px] rounded-2xl border border-white/70 bg-white/95 p-6 shadow-2xl shadow-indigo-200/60 backdrop-blur sm:p-8">
          <div className="mb-6 text-center">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">Create Your Account</h1>
            <p className="mt-2 text-sm text-slate-600">
              Join as a student or teacher and start your learning journey
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <AuthField
              id="name"
              name="name"
              label="Full Name"
              value={formData.name}
              onChange={handleChange}
              autoComplete="name"
              placeholder="John Doe"
              error={errors.name}
            />

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
              type="password"
              label="Password"
              value={formData.password}
              onChange={handleChange}
              autoComplete="new-password"
              placeholder="Create a password"
              error={errors.password}
            />

            <AuthField
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              label="Confirm Password"
              value={formData.confirmPassword}
              onChange={handleChange}
              autoComplete="new-password"
              placeholder="Confirm your password"
              error={errors.confirmPassword}
            />

            <AuthField
              as="select"
              id="role"
              name="role"
              label="Role"
              value={formData.role}
              onChange={handleChange}
              options={[
                { value: "student", label: "Student" },
                { value: "teacher", label: "Teacher" },
              ]}
              error={errors.role}
            />

            {apiError ? (
              <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                {apiError}
              </div>
            ) : null}

            {successMessage ? (
              <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
                {successMessage}
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
                  Creating account...
                </>
              ) : (
                "Create Account"
              )}
            </button>
          </form>

          <p className="mt-4 text-center text-sm text-slate-600">
            Already have an account?{" "}
            <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-700">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </PageTransition>
  );
};

export default Register;
