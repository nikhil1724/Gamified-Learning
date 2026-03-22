import { useEffect, useMemo, useState } from "react";

import BadgeShowcase from "../components/BadgeShowcase";
import PageTransition from "../components/PageTransition";
import { useAuth } from "../context/AuthContext";
import api, { getApiErrorMessage } from "../services/api";
import "./Profile.css";

const Profile = () => {
  const { user, updateUser } = useAuth();
  const [profile, setProfile] = useState(user);
  const [badges, setBadges] = useState([]);
  const [streak, setStreak] = useState({
    current_streak: user?.streak_count ?? user?.daily_streak ?? 0,
    longest_streak: user?.longest_streak ?? 0,
    last_active_date: user?.last_active_date ?? null,
  });
  const [formData, setFormData] = useState({
    name: user?.name || "",
    email: user?.email || "",
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!user) {
      return;
    }

    setProfile((prev) => prev || user);
    setFormData({
      name: user.name || "",
      email: user.email || "",
    });
  }, [user]);

  useEffect(() => {
    let isMounted = true;

    const loadProfile = async () => {
      try {
        setLoading(true);
        const profileResponse = await api.get("/profile");
        if (!isMounted) {
          return;
        }
        setProfile(profileResponse.data);
        setFormData({
          name: profileResponse.data?.name || "",
          email: profileResponse.data?.email || "",
        });

        const [streakResult, badgesResult] = await Promise.allSettled([
          api.get("/streak"),
          api.get("/badges"),
        ]);

        const streakData =
          streakResult.status === "fulfilled" ? streakResult.value?.data : null;
        setStreak({
          current_streak:
            streakData?.current_streak ??
            profileResponse.data?.streak_count ??
            profileResponse.data?.daily_streak ??
            0,
          longest_streak:
            streakData?.longest_streak ?? profileResponse.data?.longest_streak ?? 0,
          last_active_date:
            streakData?.last_active_date ?? profileResponse.data?.last_active_date ?? null,
        });

        if (badgesResult.status === "fulfilled") {
          setBadges(Array.isArray(badgesResult.value?.data) ? badgesResult.value.data : []);
        } else {
          setBadges([]);
        }

        const warnings = [];
        if (streakResult.status === "rejected") {
          warnings.push("streak");
        }
        if (badgesResult.status === "rejected") {
          warnings.push("badges");
        }

        if (warnings.length > 0) {
          setError(`Some profile sections could not load (${warnings.join(", ")}).`);
        } else {
          setError("");
        }
      } catch (err) {
        if (!isMounted) {
          return;
        }
        const message = getApiErrorMessage(err, "Failed to load profile.");
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
    
    if (profile?.role === "admin") {
      return [
        { label: "Total Users", value: statValues.total_users ?? 0 },
        { label: "Total Courses", value: statValues.total_courses ?? 0 },
        { label: "Total Problems", value: statValues.total_problems ?? 0 },
        { label: "Total Enrollments", value: statValues.total_enrollments ?? 0 },
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
    setError("");
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
      const nextName = formData.name.trim();
      const nextEmail = formData.email.trim().toLowerCase();

      if (nextName === (profile?.name || "").trim() && nextEmail === (profile?.email || "").trim().toLowerCase()) {
        setSuccess("No changes to save.");
        return;
      }

      const response = await api.patch("/profile", {
        name: nextName,
        email: nextEmail,
      });
      setProfile(response.data);
      setFormData({
        name: response.data?.name || "",
        email: response.data?.email || "",
      });
      updateUser(response.data);
      setSuccess("Profile updated successfully.");
    } catch (err) {
      const message = getApiErrorMessage(err, "Unable to update profile right now.");
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
          <div className="streak-pill" aria-label="Current streak">
            <span className="streak-pill__fire" role="img" aria-hidden="true">
              🔥
            </span>
            <div className="streak-pill__text">
              <strong>{streak.current_streak} day streak</strong>
              <small>
                Best: {streak.longest_streak} day{streak.longest_streak === 1 ? "" : "s"}
                {streak.last_active_date
                  ? ` • Active ${new Date(streak.last_active_date).toLocaleDateString()}`
                  : ""}
              </small>
            </div>
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
                    <span className="metric-value">{streak.current_streak ?? profile?.daily_streak ?? 0}</span>
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

              <div className="mt-4">
                <BadgeShowcase badges={badges} />
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
                      className="btn btn-primary profile-btn-primary"
                      disabled={saving}
                    >
                      {saving ? "Saving..." : "Save Changes"}
                    </button>
                    <button
                      type="button"
                      className="btn btn-outline-secondary profile-btn-secondary"
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
