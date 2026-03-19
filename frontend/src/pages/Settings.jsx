import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import PageTransition from "../components/PageTransition";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import api, { getApiErrorMessage } from "../services/api";
import "./Settings.css";

const Settings = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { theme, setTheme } = useTheme();

  const [profileForm, setProfileForm] = useState({ name: "", email: "" });
  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  const [loading, setLoading] = useState(true);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        const response = await api.get("/profile");
        setProfileForm({
          name: response.data?.name || "",
          email: response.data?.email || "",
        });
      } catch (err) {
        setError(getApiErrorMessage(err, "Failed to load settings."));
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, []);

  const onProfileChange = (event) => {
    const { name, value } = event.target;
    setProfileForm((prev) => ({ ...prev, [name]: value }));
  };

  const onPasswordChange = (event) => {
    const { name, value } = event.target;
    setPasswordForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSaveProfile = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    try {
      setSavingProfile(true);
      await api.patch("/profile", profileForm);
      setSuccess("Profile updated successfully.");
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to update profile."));
    } finally {
      setSavingProfile(false);
    }
  };

  const handleChangePassword = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!passwordForm.current_password || !passwordForm.new_password || !passwordForm.confirm_password) {
      setError("Please fill all password fields.");
      return;
    }

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setError("New password and confirm password do not match.");
      return;
    }

    try {
      setSavingPassword(true);
      const response = await api.post("/auth/change-password", passwordForm);
      setSuccess(response.data?.message || "Password updated successfully.");
      setPasswordForm({ current_password: "", new_password: "", confirm_password: "" });
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to update password."));
    } finally {
      setSavingPassword(false);
    }
  };

  const handleLogout = async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      // Even if API logout fails, clear local auth state.
    } finally {
      logout();
      navigate("/", { replace: true });
    }
  };

  return (
    <PageTransition>
      <div className="container py-5 settings-page">
        <div className="settings-header">
          <h2 className="mb-1">Settings</h2>
          <p className="text-muted mb-0">Manage your profile, password, and appearance.</p>
        </div>

        {error ? <div className="alert alert-danger">{error}</div> : null}
        {success ? <div className="alert alert-success">{success}</div> : null}

        {loading ? (
          <div className="settings-card">Loading settings...</div>
        ) : (
          <div className="settings-grid">
            <section className="settings-card">
              <h5>Profile</h5>
              <form onSubmit={handleSaveProfile}>
                <div className="mb-3">
                  <label className="form-label" htmlFor="settings-name">Name</label>
                  <input
                    id="settings-name"
                    name="name"
                    className="form-control"
                    value={profileForm.name}
                    onChange={onProfileChange}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label" htmlFor="settings-email">Email</label>
                  <input
                    id="settings-email"
                    type="email"
                    name="email"
                    className="form-control"
                    value={profileForm.email}
                    onChange={onProfileChange}
                    required
                  />
                </div>

                <button className="btn btn-primary" disabled={savingProfile} type="submit">
                  {savingProfile ? "Saving..." : "Save Profile"}
                </button>
              </form>
            </section>

            <section className="settings-card">
              <h5>Security</h5>
              <form onSubmit={handleChangePassword}>
                <div className="mb-3">
                  <label className="form-label" htmlFor="current-password">Current Password</label>
                  <input
                    id="current-password"
                    type="password"
                    name="current_password"
                    className="form-control"
                    value={passwordForm.current_password}
                    onChange={onPasswordChange}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label" htmlFor="new-password">New Password</label>
                  <input
                    id="new-password"
                    type="password"
                    name="new_password"
                    className="form-control"
                    value={passwordForm.new_password}
                    onChange={onPasswordChange}
                    minLength={8}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label" htmlFor="confirm-password">Confirm Password</label>
                  <input
                    id="confirm-password"
                    type="password"
                    name="confirm_password"
                    className="form-control"
                    value={passwordForm.confirm_password}
                    onChange={onPasswordChange}
                    minLength={8}
                    required
                  />
                </div>

                <button className="btn btn-primary" disabled={savingPassword} type="submit">
                  {savingPassword ? "Updating..." : "Change Password"}
                </button>
              </form>
            </section>

            <section className="settings-card">
              <h5>Appearance</h5>
              <div className="mb-3">
                <label className="form-label" htmlFor="theme-select">Theme</label>
                <select
                  id="theme-select"
                  className="form-select"
                  value={theme}
                  onChange={(event) => setTheme(event.target.value)}
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                </select>
              </div>

              <button type="button" className="btn btn-outline-danger" onClick={handleLogout}>
                Logout
              </button>
            </section>
          </div>
        )}
      </div>
    </PageTransition>
  );
};

export default Settings;
