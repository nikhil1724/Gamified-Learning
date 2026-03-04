import { useEffect, useMemo, useState } from "react";

import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import "./FloatingTutor.css";

const FloatingTutor = () => {
  const { isAuthenticated } = useAuth();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [recommendations, setRecommendations] = useState(null);

  useEffect(() => {
    if (!open || !isAuthenticated) {
      return;
    }

    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        setError("");
        const response = await api.get("/recommendations");
        setRecommendations(response.data);
      } catch (err) {
        setRecommendations(null);
        setError(
          err?.response?.data?.error ||
            err?.response?.data?.msg ||
            "Unable to load tutor insights."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [open, isAuthenticated]);

  const suggestions = useMemo(() => {
    if (!recommendations?.performance_summary) {
      return [];
    }

    const items = [];
    const summary = recommendations.performance_summary;
    items.push(`Suggested difficulty: ${recommendations.difficulty_suggestion}`);

    if (summary.accuracy_percentage < 50) {
      items.push("Focus on fundamentals to boost accuracy.");
    } else if (summary.accuracy_percentage > 80) {
      items.push("You are ready for tougher challenges.");
    } else {
      items.push("Maintain your momentum with steady practice.");
    }

    if (summary.weak_topics?.length) {
      items.push(`Review weak topics: ${summary.weak_topics.join(", ")}.`);
    }

    return items;
  }, [recommendations]);

  const quizzes = recommendations?.recommended_quizzes || [];

  return (
    <div className="tutor-widget">
      <button
        type="button"
        className="tutor-button"
        onClick={() => setOpen((prev) => !prev)}
        aria-label="Open AI Tutor"
      >
        🤖
      </button>

      <div className={`tutor-panel ${open ? "open" : "closed"}`}>
        <div className="tutor-header">
          <div>
            <h6 className="mb-1">AI Tutor</h6>
            <span className="text-muted small">Personalized learning coach</span>
          </div>
          <button
            type="button"
            className="btn btn-sm btn-light"
            onClick={() => setOpen(false)}
          >
            Close
          </button>
        </div>

        {!isAuthenticated ? (
          <div className="tutor-empty">
            <p className="mb-1">Log in to unlock personalized tips.</p>
            <p className="text-muted small mb-0">
              Your tutor will suggest quizzes and focus areas.
            </p>
          </div>
        ) : loading ? (
          <div className="tutor-loading">
            <div className="tutor-skeleton" />
            <div className="tutor-skeleton" />
            <div className="tutor-skeleton" />
          </div>
        ) : error ? (
          <div className="alert alert-warning py-2 mb-0">{error}</div>
        ) : (
          <div className="tutor-content">
            <div className="mb-3">
              <h6 className="mb-2">Learning Suggestions</h6>
              {suggestions.length === 0 ? (
                <p className="text-muted small mb-0">
                  Complete a quiz to get tailored suggestions.
                </p>
              ) : (
                <ul className="tutor-list">
                  {suggestions.map((item, index) => (
                    <li key={`${item}-${index}`}>{item}</li>
                  ))}
                </ul>
              )}
            </div>
            <div>
              <h6 className="mb-2">Recommended Quizzes</h6>
              {quizzes.length === 0 ? (
                <p className="text-muted small mb-0">
                  No quiz recommendations yet.
                </p>
              ) : (
                <ul className="tutor-list">
                  {quizzes.map((quiz) => (
                    <li key={quiz.id}>
                      <strong>{quiz.title}</strong>
                      <span className="text-muted small">
                        {" "}• {quiz.topic} • {quiz.difficulty}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FloatingTutor;
