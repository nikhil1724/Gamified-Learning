import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";
import ProgressBar from "./ProgressBar";
import "./CourseProgress.css";

/**
 * Standalone course-progress card.
 * Fetches /api/courses/:courseId/progress on its own.
 *
 * Props:
 *   courseId    – numeric course ID (required)
 *   courseTitle – optional title override (falls back to API title)
 */
const CourseProgress = ({ courseId, courseTitle }) => {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!courseId) return;
    const fetchProgress = async () => {
      try {
        const res = await api.get(`/courses/${courseId}/progress`);
        setProgress(res.data || null);
      } catch {
        setProgress(null);
      } finally {
        setLoading(false);
      }
    };
    fetchProgress();
  }, [courseId]);

  if (loading) {
    return (
      <div className="course-progress-card course-progress-card--loading">
        <div className="skeleton-line skeleton-line--wide" />
        <div className="skeleton-line" style={{ height: 10, marginTop: 8 }} />
      </div>
    );
  }

  if (!progress) return null;

  const title = courseTitle || progress.course_title || `Course ${courseId}`;
  const pct = progress.percent_complete ?? 0;

  return (
    <div className="course-progress-card">
      <div className="course-progress-card__header">
        <Link to={`/courses/${courseId}`} className="course-progress-card__title">
          {title}
        </Link>
        <span
          className={`course-progress-card__badge${
            pct === 100 ? " course-progress-card__badge--done" : ""
          }`}
        >
          {pct === 100 ? "✓ Complete" : `${pct}%`}
        </span>
      </div>
      <ProgressBar
        current={progress.completed_count}
        total={progress.total_lessons}
        showPercentage={false}
      />
      <p className="course-progress-card__meta">
        {progress.completed_count} / {progress.total_lessons} lessons completed
      </p>
    </div>
  );
};

export default CourseProgress;
