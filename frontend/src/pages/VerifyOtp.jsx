import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";

import AuthLayout from "../components/AuthLayout";
import { getApiErrorMessage } from "../services/api";
import { resendRegistrationOtp, verifyRegistrationOtp } from "../services/authApi";

const VerifyOtp = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const email = useMemo(() => (searchParams.get("email") || "").trim().toLowerCase(), [searchParams]);
  const initialCooldown = Number(location.state?.cooldownSeconds || 45);
  const initialSentAt = location.state?.sentAt ? new Date(location.state.sentAt) : new Date();

  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [showWakeMessage, setShowWakeMessage] = useState(false);
  const [cooldownSeconds, setCooldownSeconds] = useState(Math.max(0, initialCooldown));
  const [lastSentAt, setLastSentAt] = useState(
    Number.isNaN(initialSentAt.getTime()) ? new Date() : initialSentAt
  );

  useEffect(() => {
    if (!isSubmitting && !isResending) {
      setShowWakeMessage(false);
      return undefined;
    }

    const wakeTimer = window.setTimeout(() => {
      setShowWakeMessage(true);
    }, 1800);

    return () => window.clearTimeout(wakeTimer);
  }, [isSubmitting, isResending]);

  useEffect(() => {
    if (cooldownSeconds <= 0) {
      return undefined;
    }

    const timerId = window.setInterval(() => {
      setCooldownSeconds((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);

    return () => window.clearInterval(timerId);
  }, [cooldownSeconds]);

  const lastSentLabel = useMemo(() => {
    const secondsAgo = Math.max(0, Math.floor((Date.now() - lastSentAt.getTime()) / 1000));
    if (secondsAgo < 5) {
      return "Last OTP sent just now";
    }
    if (secondsAgo < 60) {
      return `Last OTP sent ${secondsAgo}s ago`;
    }
    const mins = Math.floor(secondsAgo / 60);
    return `Last OTP sent ${mins}m ago`;
  }, [lastSentAt]);

  const handleVerify = async (event) => {
    event.preventDefault();
    setError("");
    setInfo("");

    if (!email) {
      setError("Missing email. Please register again.");
      return;
    }

    if (otp.length !== 6) {
      setError("Enter a valid 6-digit OTP.");
      return;
    }

    try {
      setIsSubmitting(true);
      await verifyRegistrationOtp({ email, otp });
      setInfo("OTP verified successfully.");
      navigate("/login", { replace: true });
    } catch (err) {
      setError(getApiErrorMessage(err, "OTP verification failed."));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResend = async () => {
    setError("");
    setInfo("");

    if (!email) {
      setError("Missing email. Please register again.");
      return;
    }

    if (cooldownSeconds > 0) {
      setError(`Please wait ${cooldownSeconds}s before requesting another OTP.`);
      return;
    }

    try {
      setIsResending(true);
      const response = await resendRegistrationOtp({ email });
      const retryAfter = Number(response?.data?.resend_cooldown_seconds || 45);
      const sentAt = response?.data?.sent_at ? new Date(response.data.sent_at) : new Date();
      setLastSentAt(Number.isNaN(sentAt.getTime()) ? new Date() : sentAt);
      setCooldownSeconds(Math.max(0, retryAfter));
      setOtp("");
      setInfo("OTP sent to your email. Check spam/promotions if not found.");
    } catch (err) {
      const retryAfter = Number(err?.response?.data?.retry_after_seconds || 0);
      if (retryAfter > 0) {
        setCooldownSeconds(retryAfter);
      }
      setError(getApiErrorMessage(err, "Could not resend OTP."));
    } finally {
      setIsResending(false);
    }
  };

  return (
    <AuthLayout
      title="Verify Your Email"
      subtitle="Enter the 6-digit OTP sent to your email to activate your account"
    >
      <form onSubmit={handleVerify} className="register-form">
        <div className="alert alert-info" role="alert">
          OTP sent to <strong>{email || "your email"}</strong>. Check spam/promotions if not found.
        </div>

        <p className="small text-muted mb-3">{lastSentLabel}</p>

        <div className="form-group">
          <label htmlFor="otp" className="form-label">
            OTP
          </label>
          <input
            id="otp"
            type="text"
            className="form-control"
            placeholder="6-digit OTP"
            value={otp}
            onChange={(event) => setOtp(event.target.value.replace(/\D/g, "").slice(0, 6))}
            autoComplete="one-time-code"
            inputMode="numeric"
            pattern="[0-9]{6}"
            required
          />
        </div>

        {error ? (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        ) : null}

        {info ? (
          <div className="alert alert-info" role="alert">
            {info}
          </div>
        ) : null}

        {showWakeMessage ? (
          <div className="alert alert-warning" role="alert">
            Server waking up, please wait...
          </div>
        ) : null}

        <button type="submit" className="btn btn-primary btn-register w-100" disabled={isSubmitting}>
          {isSubmitting ? "Verifying..." : "Verify OTP"}
        </button>

        <button
          type="button"
          className="btn btn-outline-secondary w-100"
          onClick={handleResend}
          disabled={isResending || cooldownSeconds > 0}
        >
          {isResending
            ? "Resending..."
            : cooldownSeconds > 0
            ? `Resend OTP in ${cooldownSeconds}s`
            : "Resend OTP"}
        </button>
      </form>

      <p className="auth-footer mt-4 text-center">
        Already verified? <Link to="/login" className="fw-semibold">Sign In</Link>
      </p>
    </AuthLayout>
  );
};

export default VerifyOtp;
