import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import "./Recommendations.css";

const Recommendations = () => {
  const { user, isAuthenticated } = useAuth();
  const [data, setData] = useState({
    recommended_courses: [],
    recommended_lessons: [],
    ai_signals: { weak_topics: [] },
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!isAuthenticated || !user?.id) {
        setData({
          recommended_courses: [],
          recommended_lessons: [],
          ai_signals: { weak_topics: [] },
        });
        return;
      }

      try {
        setLoading(true);
        setError("");
        const res = await api.get(`/recommendations/${user.id}`);
        setData({
          recommended_courses: res.data?.recommended_courses || [],
          recommended_lessons: res.data?.recommended_lessons || [],
          ai_signals: {
            weak_topics: res.data?.ai_signals?.weak_topics || [],
          },
        });
      } catch (err) {
        setError(err?.response?.data?.error || "Could not load recommendations.");
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [isAuthenticated, user?.id]);

  const hasItems = data.recommended_courses.length > 0 || data.recommended_lessons.length > 0;
  const weakTopics = data.ai_signals?.weak_topics || [];

  return (
    <section className="student-dashboard-panel recommendation-panel">
      <div className="student-dashboard-panel-header">
        <h4>Recommended for You</h4>
      </div>

      {weakTopics.length ? (
        <div className="recommendation-signals" title="Detected weak topics based on recent quiz attempts.">
          <span className="recommendation-signals__label">Weak topics:</span>
          {weakTopics.slice(0, 3).map((topic) => (
            <span className="recommendation-topic-chip" key={topic.topic}>
              {topic.topic} ({topic.avg_score_pct}%)
            </span>
          ))}
        </div>
      ) : null}

      {loading ? <div className="text-muted">Loading recommendations...</div> : null}
      {error ? <div className="alert alert-warning py-2">{error}</div> : null}

      {!loading && !error && !hasItems ? (
        <div className="student-dashboard-empty">
          Complete more quizzes to unlock smarter recommendations.
        </div>
      ) : null}

      {!loading && !error && hasItems ? (
        <div className="recommendation-grid">
          {data.recommended_courses.map((course) => (
            <article className="recommendation-card" key={`course-${course.course_id}`}>
              <div className="recommendation-card__tag">Course</div>
              <Link className="recommendation-card__title" to={`/courses/${course.course_id}`}>
                {course.title}
              </Link>
              <p className="recommendation-card__reason">{course.reason}</p>
              <details className="recommendation-card__details">
                <summary>Why this recommendation?</summary>
                <div>
                  {course.related_topic ? `Related weak topic: ${course.related_topic}. ` : ""}
                  Rule: low quiz score topic alignment.
                </div>
              </details>
            </article>
          ))}

          {data.recommended_lessons.map((lesson) => (
            <article className="recommendation-card" key={`lesson-${lesson.lesson_id}`}>
              <div className="recommendation-card__tag recommendation-card__tag--lesson">Lesson</div>
              <div className="recommendation-card__title">{lesson.title}</div>
              <p className="recommendation-card__reason">{lesson.reason}</p>
              <details className="recommendation-card__details">
                <summary>Why this recommendation?</summary>
                <div>
                  {lesson.related_topic ? `Related weak topic: ${lesson.related_topic}. ` : ""}
                  Rule: reinforce weak topics or continue next pending lesson.
                </div>
              </details>
              {lesson.course_id ? (
                <Link className="recommendation-card__link" to={`/courses/${lesson.course_id}`}>
                  Open course →
                </Link>
              ) : null}
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
};

export default Recommendations;
