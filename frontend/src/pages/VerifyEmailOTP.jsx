import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { publicApi } from "../services/api";
import "./VerifyEmailOTP.css";

const VerifyEmailOTP = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState(location.state?.email || "");
  const [otp, setOtp] = useState("");
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("");
  const [resendCooldown, setResendCooldown] = useState(0);

  useEffect(() => {
    if (resendCooldown <= 0) {
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      setResendCooldown((prev) => (prev > 1 ? prev - 1 : 0));
    }, 1000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [resendCooldown]);

  useEffect(() => {
    if (!email && location.state?.email) {
      setEmail(location.state.email);
    }
  }, [email, location.state]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    if (!email || !otp) {
      setStatus("error");
      setMessage("Email and OTP are required.");
      return;
    }

    if (otp.length !== 6) {
      setStatus("error");
      setMessage("OTP must be exactly 6 digits.");
      return;
    }

    try {
      setStatus("loading");
      const response = await publicApi.post("/verify-email-otp", {
        email,
        otp,
      });
      setStatus("success");
      setMessage(response.data.message || "Email verified successfully.");
      setTimeout(() => navigate("/login/student"), 1400);
    } catch (error) {
      setStatus("error");
      setMessage(
        error.response?.data?.message ||
          error.response?.data?.error ||
          "OTP verification failed."
      );
    }
  };

  const handleResendOtp = async () => {
    if (!email || resendCooldown > 0) {
      return;
    }

    try {
      setStatus("loading");
      const response = await publicApi.post("/resend-otp", { email });
      setStatus("success");
      setMessage(response.data?.message || "Verification OTP sent.");
      setResendCooldown(60);
    } catch (error) {
      const retryAfter = Number(error?.response?.data?.retry_after_seconds || 0);
      if (retryAfter > 0) {
        setResendCooldown(retryAfter);
      }
      setStatus("error");
      setMessage(
        error.response?.data?.message ||
          error.response?.data?.error ||
          "Failed to resend OTP."
      );
    }
  };

  const resendLabel = useMemo(() => {
    if (resendCooldown > 0) {
      return `Resend OTP in ${resendCooldown}s`;
    }
    return "Resend OTP";
  }, [resendCooldown]);

  return (
    <div className="verify-otp-page">
      <div className="verify-otp-card">
        <h2>Verify Email With OTP</h2>
        <p className="subtitle">Enter the OTP sent to your email address.</p>

        <form onSubmit={handleSubmit} className="verify-otp-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="otp">OTP</label>
            <input
              id="otp"
              type="text"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/[^0-9]/g, "").slice(0, 6))}
              placeholder="6-digit OTP"
              inputMode="numeric"
              maxLength={6}
              required
            />
          </div>

          {message ? (
            <div className={`message ${status === "success" ? "success" : "error"}`}>
              {message}
            </div>
          ) : null}

          <button type="submit" disabled={status === "loading"}>
            {status === "loading" ? "Verifying..." : "Verify OTP"}
          </button>
        </form>

        <div className="actions">
          <button
            type="button"
            className="resend-otp-btn"
            onClick={handleResendOtp}
            disabled={status === "loading" || resendCooldown > 0 || !email}
          >
            {resendLabel}
          </button>
          <Link to="/login/student">Back to Login</Link>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmailOTP;
