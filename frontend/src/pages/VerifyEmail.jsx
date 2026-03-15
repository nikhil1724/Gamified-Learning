import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { publicApi } from "../services/api";
import "./VerifyEmail.css";

const VerifyEmail = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState("verifying"); // verifying, success, error
  const [message, setMessage] = useState("");
  const [countdown, setCountdown] = useState(5);

  useEffect(() => {
    const verifyEmail = async () => {
      try {
        const response = await publicApi.get(`/verify-email/${token}`);
        setStatus("success");
        setMessage(response.data.message);

        // Countdown and redirect to login
        const timer = setInterval(() => {
          setCountdown((prev) => {
            if (prev <= 1) {
              clearInterval(timer);
              navigate("/login/student");
              return 0;
            }
            return prev - 1;
          });
        }, 1000);

        return () => clearInterval(timer);
      } catch (error) {
        setStatus("error");
        setMessage(
          error.response?.data?.message ||
            error.response?.data?.error ||
            "Failed to verify email. The link may be invalid or expired."
        );
      }
    };

    if (token) {
      verifyEmail();
    }
  }, [token, navigate]);

  return (
    <div className="verify-email-container">
      <div className="verify-email-card">
        {status === "verifying" && (
          <>
            <div className="spinner"></div>
            <h2>Verifying Your Email...</h2>
            <p>Please wait while we verify your email address.</p>
          </>
        )}

        {status === "success" && (
          <>
            <div className="success-icon">✓</div>
            <h2>Email Verified Successfully!</h2>
            <p>{message}</p>
            <p className="redirect-message">
              Redirecting to login in {countdown} seconds...
            </p>
            <Link to="/login/student" className="btn-primary">
              Go to Login Now
            </Link>
          </>
        )}

        {status === "error" && (
          <>
            <div className="error-icon">✕</div>
            <h2>Verification Failed</h2>
            <p>{message}</p>
            <div className="error-actions">
              <Link to="/resend-verification" className="btn-secondary">
                Request New Verification Link
              </Link>
              <Link to="/login/student" className="btn-outline">
                Back to Login
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default VerifyEmail;
