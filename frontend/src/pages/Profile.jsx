import { useEffect, useMemo, useState } from "react";

import PageTransition from "../components/PageTransition";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import "./Profile.css";

const Profile = () => {
  const { user, updateUser } = useAuth();
  const [profile, setProfile] = useState(user);
  const [formData, setFormData] = useState({
    name: user?.name || "",
    email: user?.email || "",
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const loadProfile = async () => {
      try {
        setLoading(true);
        const response = await api.get("/profile");
        if (!isMounted) {
          return;
        }
        setProfile(response.data);
        setFormData({
          name: response.data?.name || "",
          email: response.data?.email || "",
        });
        setError("");
      } catch (err) {
        if (!isMounted) {
          return;
        }
        const message = err?.response?.data?.error || "Failed to load profile.";
        setError(message);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadProfile();
    return () => {
      isMounted = false;
    };
  }, []);

  const stats = useMemo(() => {
    const statValues = profile?.stats || {};
    if (profile?.role === "teacher") {
      return [
        { label: "Courses Created", value: statValues.courses_created ?? 0 },
        { label: "Problems Created", value: statValues.problems_created ?? 0 },
        { label: "Students Enrolled", value: statValues.students_enrolled ?? 0 },
        { label: "Notes Uploaded", value: statValues.notes_uploaded ?? 0 },
      ];
    }

    return [
      { label: "Courses Enrolled", value: statValues.courses_enrolled ?? 0 },
      { label: "Quizzes Completed", value: statValues.quizzes_completed ?? 0 },
      { label: "Problems Solved", value: statValues.problems_solved ?? 0 },
      { label: "Badges Earned", value: statValues.badges_earned ?? 0 },
      { label: "Lessons Completed", value: statValues.lessons_completed ?? 0 },
    ];
  }, [profile]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleReset = () => {
    setFormData({
      name: profile?.name || "",
      email: profile?.email || "",
    });
    setSuccess("");
    setError("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!formData.name.trim() || !formData.email.trim()) {
      setError("Name and email are required.");
      return;
    }

    try {
      setSaving(true);
      const response = await api.patch("/profile", {
        name: formData.name,
        email: formData.email,
      });
      setProfile(response.data);
      updateUser(response.data);
      setSuccess("Profile updated successfully.");
    } catch (err) {
      const message = err?.response?.data?.error || "Update failed.";
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  const initials = useMemo(() => {
    if (!profile?.name) {
      return "U";
    }
    return profile.name
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0])
      .join("")
      .toUpperCase();
  }, [profile?.name]);

  return (
    <PageTransition>
      <div className="container-fluid py-5 profile-page">
        <div className="profile-hero mb-4">
          <div className="profile-hero__avatar">{initials}</div>
          <div>
            <h1 className="mb-1">{profile?.name || "Your Profile"}</h1>
            <p className="text-muted mb-0">
              {profile?.role ? `${profile.role} account` : "Account overview"}
              {profile?.created_at ? ` - Joined ${new Date(profile.created_at).toLocaleDateString()}` : ""}
            </p>
          </div>
        </div>

        {loading ? (
          <div className="profile-loading">Loading your profile...</div>
        ) : null}

        {error ? <div className="alert alert-danger">{error}</div> : null}
        {success ? <div className="alert alert-success">{success}</div> : null}

        {!loading ? (
          <div className="row g-4">
            <div className="col-12 col-lg-8 order-lg-1">
              <div className="profile-card">
                <h5 className="mb-3">Progress Snapshot</h5>
                <div className="profile-metrics">
                  <div>
                    <span className="metric-label">Level</span>
                    <span className="metric-value">{profile?.level ?? 1}</span>
                  </div>
                  <div>
                    <span className="metric-label">XP</span>
                    <span className="metric-value">{profile?.xp_points ?? 0}</span>
                  </div>
                  <div>
                    <span className="metric-label">Coins</span>
                    <span className="metric-value">{profile?.coins ?? 0}</span>
                  </div>
                  <div>
                    <span className="metric-label">Daily Streak</span>
                    <span className="metric-value">{profile?.daily_streak ?? 0}</span>
                  </div>
                </div>
              </div>

              <div className="profile-card mt-4">
                <h5 className="mb-3">Key Stats</h5>
                <div className="row g-3">
                  {stats.map((stat) => (
                    <div className="col-6 col-lg-4" key={stat.label}>
                      <div className="stat-tile">
                        <span className="stat-value">{stat.value}</span>
                        <span className="stat-label">{stat.label}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="col-12 col-lg-4 order-lg-2 profile-side">
              <div className="profile-card profile-card--circle">
                <h5 className="mb-3">Account Details</h5>
                <form onSubmit={handleSubmit} className="profile-form">
                  <div className="mb-3">
                    <label className="form-label" htmlFor="name">
                      Full Name
                    </label>
                    <input
                      id="name"
                      name="name"
                      type="text"
                      className="form-control"
                      value={formData.name}
                      onChange={handleChange}
                      autoComplete="name"
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label" htmlFor="email">
                      Email
                    </label>
                    <input
                      id="email"
                      name="email"
                      type="email"
                      className="form-control"
                      value={formData.email}
                      onChange={handleChange}
                      autoComplete="email"
                      required
                    />
                  </div>
                  <div className="profile-actions">
                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={saving}
                    >
                      {saving ? "Saving..." : "Save Changes"}
                    </button>
                    <button
                      type="button"
                      className="btn btn-outline-secondary"
                      onClick={handleReset}
                      disabled={saving}
                    >
                      Reset
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </PageTransition>
  );
};

export default Profile;
