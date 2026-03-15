import { useState } from "react";

import api from "../services/api";
import "./LessonCompletionButton.css";

/**
 * Reusable "Mark as Completed" button for a lesson.
 *
 * Props:
 *   courseId        – numeric course ID
 *   lessonId        – numeric lesson ID
 *   initialCompleted – whether the lesson is already completed (default false)
 *   onComplete      – optional callback fired after successful completion
 */
const LessonCompletionButton = ({
  courseId,
  lessonId,
  initialCompleted = false,
  onComplete,
}) => {
  const [completed, setCompleted] = useState(initialCompleted);
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    if (completed || loading) return;
    try {
      const rawUser = localStorage.getItem("user");
      const currentUser = rawUser ? JSON.parse(rawUser) : null;
      const userId = Number(currentUser?.id);
      if (!userId) {
        return;
      }

      setLoading(true);
      await api.post("/lesson/complete", {
        user_id: userId,
        course_id: Number(courseId),
        lesson_id: Number(lessonId),
      });
      setCompleted(true);
      onComplete?.();
    } catch {
      /* keep button active so user can retry */
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      type="button"
      className={`lesson-completion-btn${completed ? " lesson-completion-btn--done" : ""}`}
      onClick={handleClick}
      disabled={loading || completed}
    >
      {completed ? (
        <>
          <span className="lesson-completion-btn__icon">✓</span>
          Lesson Completed
        </>
      ) : loading ? (
        "Saving…"
      ) : (
        <>
          <span className="lesson-completion-btn__icon">○</span>
          Mark as Completed
        </>
      )}
    </button>
  );
};

export default LessonCompletionButton;
