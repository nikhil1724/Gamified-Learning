import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { publicApi } from "../services/api";
import "./ResendVerification.css";

const ResendVerification = () => {
  const location = useLocation();
  const [email, setEmail] = useState(location.state?.email || "");
  const [status, setStatus] = useState("idle"); // idle, loading, success, error
  const [message, setMessage] = useState("");
  const [verificationOtp, setVerificationOtp] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email) {
      setStatus("error");
      setMessage("Please enter your email address");
      return;
    }

    setStatus("loading");
    setMessage("");
    setVerificationOtp("");

    try {
      const response = await publicApi.post("/resend-verification", { email });
      setStatus("success");
      setMessage(response.data.message);
      setVerificationOtp(response.data.verification_otp || "");
    } catch (error) {
      setStatus("error");
      setMessage(
        error.response?.data?.error ||
          "Failed to send verification email. Please try again."
      );
    }
  };

  return (
    <div className="resend-verification-container">
      <div className="resend-verification-card">
        <div className="header-section">
          <h1>📧 Resend Verification OTP</h1>
          <p>
            Didn't receive the OTP? Enter your email address and
            we'll send you a new verification OTP.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="resend-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your-email@example.com"
              required
              disabled={status === "loading"}
            />
          </div>

          {message && (
            <div className={`message-box ${status}`}>
              <span className="message-icon">
                {status === "success" ? "✓" : "⚠"}
              </span>
              <p>{message}</p>
            </div>
          )}

          {verificationOtp ? (
            <div className="message-box success">
              <p className="mb-2">Use this OTP:</p>
              <p><strong>{verificationOtp}</strong></p>
              <Link to="/verify-otp" state={{ email, otp: verificationOtp }} className="link">Go to OTP Verification</Link>
            </div>
          ) : null}

          <button
            type="submit"
            className="submit-btn"
            disabled={status === "loading"}
          >
            {status === "loading" ? (
              <>
                <span className="spinner-small"></span>
                Sending...
              </>
            ) : (
              "Send Verification OTP"
            )}
          </button>
        </form>

        <div className="footer-links">
          <p>
            Already verified?{" "}
            <Link to="/login/student" className="link">
              Go to Login
            </Link>
          </p>
          <p>
            Don't have an account?{" "}
            <Link to="/register/teacher" className="link">
              Register Here
            </Link>
          </p>
        </div>

        <div className="help-text">
          <h4>Tips:</h4>
          <ul>
            <li>Check your spam/junk folder</li>
            <li>Make sure you entered the correct email address</li>
            <li>OTP expires after 5 minutes</li>
            <li>Resend requests are rate limited for security</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ResendVerification;
