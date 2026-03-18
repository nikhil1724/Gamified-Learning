import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { publicApi } from "../services/api";
import "./ResendVerification.css";

const ResendVerification = () => {
  const location = useLocation();
  const [email, setEmail] = useState(location.state?.email || "");
  const [status, setStatus] = useState("idle"); // idle, loading, success, error
  const [message, setMessage] = useState("");
  const [retryAfter, setRetryAfter] = useState(0);

  useEffect(() => {
    if (retryAfter <= 0) {
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      setRetryAfter((prev) => (prev > 1 ? prev - 1 : 0));
    }, 1000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [retryAfter]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email) {
      setStatus("error");
      setMessage("Please enter your email address");
      return;
    }

    if (retryAfter > 0) {
      setStatus("error");
      setMessage(`Please wait ${retryAfter}s before requesting another OTP.`);
      return;
    }

    setStatus("loading");
    setMessage("");

    try {
      const response = await publicApi.post("/resend-verification", { email });
      setStatus("success");
      setMessage(response.data.message);
    } catch (error) {
      const cooldown = Number(error?.response?.data?.retry_after_seconds || 0);
      if (cooldown > 0) {
        setRetryAfter(cooldown);
      }
      setStatus("error");
      setMessage(
        error.response?.data?.message ||
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

          <button
            type="submit"
            className="submit-btn"
            disabled={status === "loading" || retryAfter > 0}
          >
            {status === "loading" ? (
              <>
                <span className="spinner-small"></span>
                Sending...
              </>
            ) : retryAfter > 0 ? (
              `Retry in ${retryAfter}s`
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
