import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import PageTransition from "../components/PageTransition";
import ProgressBar from "../components/ProgressBar";
import Recommendations from "../components/Recommendations";
import "./StudentDashboard.css";

const STAT_CONFIG = [
  { key: "total_xp", icon: "⚡", label: "Total XP", suffix: "" },
  { key: "learning_streak_days", icon: "🔥", label: "Learning Streak", suffix: " Days" },
  { key: "courses_enrolled", icon: "📚", label: "Courses Enrolled", suffix: "" },
  { key: "lessons_completed", icon: "✅", label: "Lessons Completed", suffix: "" },
  { key: "quizzes_attempted", icon: "🧠", label: "Quizzes Attempted", suffix: "" },
  { key: "average_score", icon: "🎯", label: "Avg. Quiz Score", suffix: "%" },
];

const StudentDashboard = () => {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [certificateLoadingByCourse, setCertificateLoadingByCourse] = useState({});
  const [certificateError, setCertificateError] = useState("");
  const [issuedCertificates, setIssuedCertificates] = useState({});

  const getCertificateSignature = (course) => `${course.completed_lessons}:${course.total_lessons}`;

  useEffect(() => {
    if (!user?.id) {
      setIssuedCertificates({});
      return;
    }

    try {
      const key = `issued_certificates_${user.id}`;
      const raw = window.localStorage.getItem(key);
      setIssuedCertificates(raw ? JSON.parse(raw) : {});
    } catch {
      setIssuedCertificates({});
    }
  }, [user?.id]);

  useEffect(() => {
    if (!user?.id) return;
    const key = `issued_certificates_${user.id}`;
    window.localStorage.setItem(key, JSON.stringify(issuedCertificates));
  }, [issuedCertificates, user?.id]);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);
        setError("");
        const res = await api.get("/student/dashboard");
        setData(res.data || null);
      } catch (err) {
        setError(err?.response?.data?.error || "Failed to load dashboard.");
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  const stats = useMemo(() => {
    if (!data) return [];
    return STAT_CONFIG.map(({ key, icon, label, suffix }) => ({
      icon,
      label,
      value: `${data[key] ?? 0}${suffix}`,
    }));
  }, [data]);

  const downloadCertificate = async (courseId) => {
    if (!user?.id) {
      setCertificateError("Please log in again to download your certificate.");
      return;
    }

    try {
      setCertificateError("");
      setCertificateLoadingByCourse((prev) => ({ ...prev, [courseId]: true }));

      const response = await api.get(`/certificate/${user.id}/${courseId}`, {
        responseType: "blob",
      });

      const blob =
        response.data instanceof Blob
          ? response.data
          : new Blob([response.data], { type: "application/pdf" });

      if (!blob.size) {
        throw new Error("Empty certificate file received from server.");
      }

      if (blob.type && !blob.type.toLowerCase().includes("pdf")) {
        try {
          const text = await blob.text();
          const parsed = JSON.parse(text);
          throw new Error(parsed?.error || "Invalid certificate payload.");
        } catch {
          throw new Error("Invalid certificate file received.");
        }
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;

      const fallbackFilename = `certificate_user_${user.id}_course_${courseId}.pdf`;
      const contentDisposition = response.headers["content-disposition"] || "";
      const match = contentDisposition.match(/filename="?([^\"]+)"?/i);
      link.download = match?.[1] || fallbackFilename;

      document.body.appendChild(link);
      link.click();
      link.remove();

      // Delay revocation to avoid race conditions where browsers write partial files.
      window.setTimeout(() => {
        window.URL.revokeObjectURL(url);
      }, 1500);

      const selectedCourse = data?.course_progress?.find((course) => course.course_id === courseId);
      if (selectedCourse) {
        const signature = getCertificateSignature(selectedCourse);
        setIssuedCertificates((prev) => ({ ...prev, [courseId]: signature }));
      }
    } catch (err) {
      let message = "Certificate is available only after completing all lessons in a course.";

      if (err instanceof Error && err.message) {
        message = err.message;
      }

      const maybeBlob = err?.response?.data;
      if (maybeBlob instanceof Blob) {
        try {
          const text = await maybeBlob.text();
          const parsed = JSON.parse(text);
          message = parsed?.error || message;
        } catch {
          // Keep fallback message when parsing fails.
        }
      } else {
        message = err?.response?.data?.error || message;
      }

      setCertificateError(message);
    } finally {
      setCertificateLoadingByCourse((prev) => ({ ...prev, [courseId]: false }));
    }
  };

  const isCertificateAlreadyIssued = (course) => {
    const signature = getCertificateSignature(course);
    return issuedCertificates[course.course_id] === signature;
  };

  return (
    <PageTransition>
      <div className="student-dashboard-page py-5">
        <div className="container">
          {/* Header */}
          <div className="student-dashboard-hero mb-4">
            <div>
              <span className="student-dashboard-badge">Student Progress</span>
              <h1 className="mb-2">My Dashboard</h1>
              <p className="text-muted mb-0">
                Track your XP, completed lessons, quiz scores, and per-course progress.
              </p>
            </div>
            <Link to="/my-learning" className="btn btn-outline-primary btn-sm">
              Full Activity Log →
            </Link>
          </div>

          {error && <div className="alert alert-danger">{error}</div>}
          {certificateError && <div className="alert alert-warning">{certificateError}</div>}

          {!loading && data ? (
            <div className="student-dashboard-streak-panel mb-4">
              <div className="alert alert-info py-2 px-3 mb-2">
                🔥 Learning Streak: {data.learning_streak_days ?? 0} Days
              </div>
              <div className="streak-mini-chart" aria-label="Last 7 days learning activity">
                {(data.learning_activity_last_7_days || []).map((item) => (
                  <div className="streak-mini-chart__item" key={item.date} title={`${item.label} - ${item.active ? "Active" : "No activity"}`}>
                    <div
                      className={`streak-mini-chart__bar${item.active ? " is-active" : ""}`}
                    />
                    <span className="streak-mini-chart__label">{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          {loading ? (
            <div className="student-dashboard-loading">
              <div className="student-dashboard-stats mb-4">
                {STAT_CONFIG.map((s) => (
                  <div className="student-dashboard-stat-card skeleton" key={s.key}>
                    <div className="skeleton-line" style={{ width: 40, height: 32, margin: "0 auto 8px" }} />
                    <div className="skeleton-line skeleton-line--wide" />
                  </div>
                ))}
              </div>
            </div>
          ) : data ? (
            <>
              {/* Stats row */}
              <div className="student-dashboard-stats mb-5">
                {stats.map((stat) => (
                  <div className="student-dashboard-stat-card" key={stat.label}>
                    <span className="student-dashboard-stat-card__icon">{stat.icon}</span>
                    <span className="student-dashboard-stat-card__value">{stat.value}</span>
                    <span className="student-dashboard-stat-card__label">{stat.label}</span>
                  </div>
                ))}
              </div>

              <Recommendations />

              {/* Course progress */}
              <section className="student-dashboard-panel">
                <div className="student-dashboard-panel-header">
                  <h4>Course Progress</h4>
                  <Link to="/courses" className="student-dashboard-panel-link">
                    Browse courses →
                  </Link>
                </div>

                {data.course_progress?.length ? (
                  <div className="student-dashboard-courses">
                    {data.course_progress.map((course) => (
                      <div className="student-dashboard-course-card" key={course.course_id}>
                        <div className="student-dashboard-course-card__header">
                          <div className="student-dashboard-course-card__info">
                            <Link
                              to={`/courses/${course.course_id}`}
                              className="student-dashboard-course-card__title"
                            >
                              {course.title}
                            </Link>
                            {course.teacher_name && (
                              <span className="student-dashboard-course-card__teacher">
                                {course.teacher_name}
                              </span>
                            )}
                          </div>
                          <span
                            className={`student-dashboard-course-card__pct${
                              course.percent_complete === 100
                                ? " student-dashboard-course-card__pct--done"
                                : ""
                            }`}
                          >
                            {course.percent_complete === 100
                              ? "✓ Done"
                              : `${course.percent_complete}%`}
                          </span>
                        </div>

                        <ProgressBar
                          current={course.completed_lessons}
                          total={course.total_lessons}
                          showPercentage={false}
                        />

                        <p className="student-dashboard-course-card__meta">
                          {course.completed_lessons} / {course.total_lessons} lessons completed
                        </p>

                        {course.percent_complete === 100 ? (
                          <div className="student-dashboard-certificate-wrap mt-2">
                            {isCertificateAlreadyIssued(course) ? (
                              <span className="student-dashboard-certificate-badge">
                                Certificate Issued
                              </span>
                            ) : null}
                            <button
                              type="button"
                              className="btn btn-sm btn-success"
                              onClick={() => downloadCertificate(course.course_id)}
                              disabled={Boolean(certificateLoadingByCourse[course.course_id])}
                            >
                              {certificateLoadingByCourse[course.course_id]
                                ? "Preparing certificate..."
                                : isCertificateAlreadyIssued(course)
                                  ? "Download Again"
                                  : "Download Certificate"}
                            </button>
                          </div>
                        ) : null}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="student-dashboard-empty">
                    You are not enrolled in any courses yet.{" "}
                    <Link to="/courses">Browse courses →</Link>
                  </div>
                )}
              </section>
            </>
          ) : (
            <div className="student-dashboard-empty">No data available.</div>
          )}
        </div>
      </div>
    </PageTransition>
  );
};

export default StudentDashboard;
