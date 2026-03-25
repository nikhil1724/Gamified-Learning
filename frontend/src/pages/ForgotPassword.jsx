import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import AuthField from "../components/auth/AuthField";
import PageTransition from "../components/PageTransition";
import { useAuth } from "../context/AuthContext";
import { getApiErrorMessage } from "../services/api";
import { confirmPasswordReset, requestPasswordReset } from "../services/authApi";

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { isAuthenticated, role } = useAuth();

  const [step, setStep] = useState("request");
  const [formData, setFormData] = useState({
    email: searchParams.get("email") || "",
    token: "",
    newPassword: "",
    confirmPassword: "",
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
  };

  const validateRequest = () => {
    const nextErrors = {};
    if (!formData.email.trim()) {
      nextErrors.email = "Email is required.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
      nextErrors.email = "Enter a valid email address.";
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const validateReset = () => {
    const nextErrors = {};

    if (!formData.email.trim()) {
      nextErrors.email = "Email is required.";
    }

    if (!formData.token.trim()) {
      nextErrors.token = "Reset code is required.";
    } else if (!/^\d{6}$/.test(formData.token.trim())) {
      nextErrors.token = "Reset code must be 6 digits.";
    }

    if (!formData.newPassword) {
      nextErrors.newPassword = "New password is required.";
    } else if (formData.newPassword.length < 8) {
      nextErrors.newPassword = "Password must be at least 8 characters.";
    }

    if (!formData.confirmPassword) {
      nextErrors.confirmPassword = "Confirm your new password.";
    } else if (formData.newPassword !== formData.confirmPassword) {
      nextErrors.confirmPassword = "Passwords do not match.";
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleRequestCode = async (event) => {
    event.preventDefault();
    setApiError("");
    setSuccessMessage("");

    if (!validateRequest()) {
      return;
    }

    try {
      setIsSubmitting(true);
      const response = await requestPasswordReset({ email: formData.email.trim() });
      setSuccessMessage(
        response?.data?.message || "If the account exists, a reset code has been sent to your email."
      );
      setStep("reset");
    } catch (error) {
      setApiError(getApiErrorMessage(error, "Could not send reset code."));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResetPassword = async (event) => {
    event.preventDefault();
    setApiError("");
    setSuccessMessage("");

    if (!validateReset()) {
      return;
    }

    try {
      setIsSubmitting(true);
      const response = await confirmPasswordReset({
        email: formData.email.trim(),
        token: formData.token.trim(),
        new_password: formData.newPassword,
      });

      setSuccessMessage(response?.data?.message || "Password reset successful. You can now sign in.");
      setTimeout(() => {
        navigate("/login", { replace: true });
      }, 1200);
    } catch (error) {
      setApiError(getApiErrorMessage(error, "Unable to reset password."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PageTransition>
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-sky-100 via-indigo-100 to-violet-100 px-4 py-10 sm:px-6">
        <div className="w-full max-w-[430px] rounded-2xl border border-white/70 bg-white/95 p-6 shadow-2xl shadow-indigo-200/60 backdrop-blur sm:p-8">
          <div className="mb-6 text-center">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">Reset Password</h1>
            <p className="mt-2 text-sm text-slate-600">
              {step === "request"
                ? "Enter your email and we will send a 6-digit reset code"
                : "Enter the code and choose a new password"}
            </p>
          </div>

          <form onSubmit={step === "request" ? handleRequestCode : handleResetPassword} className="space-y-4" noValidate>
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

            {step === "reset" ? (
              <>
                <AuthField
                  id="token"
                  name="token"
                  label="Reset Code"
                  value={formData.token}
                  onChange={handleChange}
                  placeholder="Enter 6-digit code"
                  error={errors.token}
                />

                <AuthField
                  id="newPassword"
                  name="newPassword"
                  type="password"
                  label="New Password"
                  value={formData.newPassword}
                  onChange={handleChange}
                  autoComplete="new-password"
                  placeholder="Create a new password"
                  error={errors.newPassword}
                />

                <AuthField
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  label="Confirm New Password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  autoComplete="new-password"
                  placeholder="Confirm your new password"
                  error={errors.confirmPassword}
                />
              </>
            ) : null}

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
                  {step === "request" ? "Sending code..." : "Updating password..."}
                </>
              ) : step === "request" ? (
                "Send Reset Code"
              ) : (
                "Reset Password"
              )}
            </button>

            {step === "reset" ? (
              <button
                type="button"
                onClick={() => {
                  setStep("request");
                  setApiError("");
                  setSuccessMessage("");
                  setErrors({});
                }}
                className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
              >
                Resend code
              </button>
            ) : null}
          </form>

          <p className="mt-4 text-center text-sm text-slate-600">
            Remembered your password?{" "}
            <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-700">
              Back to Sign In
            </Link>
          </p>
        </div>
      </div>
    </PageTransition>
  );
};

export default ForgotPassword;
