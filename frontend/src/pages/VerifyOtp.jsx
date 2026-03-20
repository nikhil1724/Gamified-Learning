import { useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import AuthLayout from "../components/AuthLayout";
import { getApiErrorMessage } from "../services/api";
import { resendRegistrationOtp, verifyRegistrationOtp } from "../services/authApi";

const VerifyOtp = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const email = useMemo(() => (searchParams.get("email") || "").trim().toLowerCase(), [searchParams]);

  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isResending, setIsResending] = useState(false);

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
      navigate("/login/student", { replace: true });
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

    try {
      setIsResending(true);
      await resendRegistrationOtp({ email });
      setInfo("A new OTP has been sent to your email.");
    } catch (err) {
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
        <div className="form-group">
          <label htmlFor="verify-email" className="form-label">
            Email
          </label>
          <input id="verify-email" className="form-control" type="email" value={email} readOnly />
        </div>

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

        <button type="submit" className="btn btn-primary btn-register w-100" disabled={isSubmitting}>
          {isSubmitting ? "Verifying..." : "Verify OTP"}
        </button>

        <button
          type="button"
          className="btn btn-outline-secondary w-100"
          onClick={handleResend}
          disabled={isResending}
        >
          {isResending ? "Resending..." : "Resend OTP"}
        </button>
      </form>

      <p className="auth-footer mt-4 text-center">
        Already verified? <Link to="/login" className="fw-semibold">Sign In</Link>
      </p>
    </AuthLayout>
  );
};

export default VerifyOtp;
