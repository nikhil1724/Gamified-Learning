import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { publicApi } from "../services/api";
import "./VerifyEmailOTP.css";

const VerifyEmailOTP = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState(location.state?.email || "");
  const [otp, setOtp] = useState(location.state?.otp || "");
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!email && location.state?.email) {
      setEmail(location.state.email);
    }
    if (!otp && location.state?.otp) {
      setOtp(location.state.otp);
    }
  }, [email, otp, location.state]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    if (!email || !otp) {
      setStatus("error");
      setMessage("Email and OTP are required.");
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
          <Link to="/resend-otp" state={{ email }}>
            Resend OTP
          </Link>
          <Link to="/login/student">Back to Login</Link>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmailOTP;
