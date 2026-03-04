import { useEffect, useMemo, useState } from "react";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import ProgressBar from "../components/ProgressBar";
import "./MyLearningDashboard.css";

const MyLearningDashboard = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        setError("");
        const response = await api.get("/learning-dashboard");
        setSummary(response.data || null);
      } catch (err) {
        setError(err?.response?.data?.error || "Unable to load learning summary.");
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  const stats = useMemo(() => {
    return [
      {
        label: "Total XP",
        value: summary?.total_xp ?? 0,
      },
      {
        label: "Quizzes Attempted",
        value: summary?.total_quizzes_attempted ?? 0,
      },
      {
        label: "Average Quiz Score",
        value: summary?.average_quiz_score ?? 0,
      },
      {
        label: "Avg. Completion",
        value: `${summary?.average_quiz_completion ?? 0}%`,
      },
    ];
  }, [summary]);

  return (
    <PageTransition>
      <div className="learning-dashboard-page py-5">
        <div className="container">
          <div className="learning-dashboard-hero mb-4">
            <div>
              <span className="learning-dashboard-badge">My Learning Dashboard</span>
              <h1 className="mb-2">Track your progress</h1>
              <p className="text-muted mb-0">
                See quiz performance, course progress, and recent activity in one place.
              </p>
            </div>
          </div>

          {error ? <div className="alert alert-danger">{error}</div> : null}

          {loading ? (
            <div className="learning-dashboard-loading">Loading dashboard...</div>
          ) : summary ? (
            <div className="learning-dashboard-grid">
              <section className="learning-dashboard-panel">
                <h4>Learning Stats</h4>
                <div className="learning-dashboard-stats">
                  {stats.map((stat) => (
                    <div key={stat.label} className="learning-dashboard-stat">
                      <span className="learning-dashboard-stat__label">{stat.label}</span>
                      <span className="learning-dashboard-stat__value">{stat.value}</span>
                    </div>
                  ))}
                </div>
              </section>

              <section className="learning-dashboard-panel">
                <h4>Course Progress</h4>
                {summary.course_progress?.length ? (
                  <div className="learning-dashboard-course-list">
                    {summary.course_progress.map((course) => (
                      <div className="learning-dashboard-course" key={course.course_id}>
                        <div className="learning-dashboard-course__header">
                          <div>
                            <h5 className="mb-1">{course.title}</h5>
                            <span className="text-muted">
                              Instructor: {course.teacher_name || "Instructor"}
                            </span>
                          </div>
                          <span className="learning-dashboard-course__percent">
                            {course.percent_complete}%
                          </span>
                        </div>
                        <ProgressBar
                          current={course.completed_lessons}
                          total={course.total_lessons}
                          showPercentage={false}
                        />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="learning-dashboard-empty">
                    Enroll in a course to see your progress here.
                  </div>
                )}
              </section>

              <section className="learning-dashboard-panel">
                <h4>Recent Activity</h4>
                {summary.recent_activity?.length ? (
                  <div className="learning-dashboard-activity">
                    {summary.recent_activity.map((item, index) => (
                      <div className="learning-dashboard-activity__item" key={`${item.type}-${index}`}>
                        <span className={`learning-dashboard-activity__type learning-dashboard-activity__type--${item.type}`}>
                          {item.type}
                        </span>
                        <div>
                          <div className="learning-dashboard-activity__title">{item.title}</div>
                          <div className="learning-dashboard-activity__time">
                            {new Date(item.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="learning-dashboard-empty">
                    No recent activity yet. Complete a lesson or quiz.
                  </div>
                )}
              </section>
            </div>
          ) : (
            <div className="learning-dashboard-empty">No data available.</div>
          )}
        </div>
      </div>
    </PageTransition>
  );
};

export default MyLearningDashboard;
