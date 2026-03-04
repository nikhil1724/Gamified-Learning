import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import "./LessonViewer.css";

const LessonViewer = () => {
  const { courseId, lessonId } = useParams();
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isCompleted, setIsCompleted] = useState(false);
  const [marking, setMarking] = useState(false);

  useEffect(() => {
    const fetchLessons = async () => {
      try {
        setLoading(true);
        setError("");
        const response = await api.get(`/course/${courseId}/lessons`);
        setLessons(response.data || []);
      } catch (err) {
        setError(err?.response?.data?.error || "Failed to load lessons.");
      } finally {
        setLoading(false);
      }
    };

    fetchLessons();
  }, [courseId]);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const response = await api.get(`/courses/${courseId}/progress`);
        const completed = response.data?.completed_lessons || [];
        setIsCompleted(completed.includes(Number(lessonId)));
      } catch {
        setIsCompleted(false);
      }
    };

    if (courseId && lessonId) {
      fetchProgress();
    }
  }, [courseId, lessonId]);

  const handleMarkComplete = async () => {
    try {
      setMarking(true);
      await api.post(`/courses/${courseId}/lessons/${lessonId}/complete`);
      setIsCompleted(true);
    } catch {
      setIsCompleted(false);
    } finally {
      setMarking(false);
    }
  };

  const currentLesson = useMemo(
    () => lessons.find((lesson) => String(lesson.id) === String(lessonId)),
    [lessons, lessonId]
  );

  const lessonIndex = useMemo(() => {
    return lessons.findIndex((lesson) => String(lesson.id) === String(lessonId));
  }, [lessons, lessonId]);

  const prevLesson = lessonIndex > 0 ? lessons[lessonIndex - 1] : null;
  const nextLesson =
    lessonIndex >= 0 && lessonIndex < lessons.length - 1
      ? lessons[lessonIndex + 1]
      : null;

  return (
    <PageTransition>
      <div className="lesson-viewer-page">
        <div className="container py-5">
          {loading ? (
            <div className="lesson-viewer-empty">Loading lesson...</div>
          ) : error ? (
            <div className="alert alert-danger">{error}</div>
          ) : currentLesson ? (
            <>
              <div className="lesson-viewer-header">
                <div>
                  <span className="lesson-viewer-badge">Lesson</span>
                  <h1>{currentLesson.title}</h1>
                  <p className="text-muted mb-0">
                    Course {courseId} · Lesson {lessonIndex + 1}
                  </p>
                </div>
                <div className="lesson-viewer-actions">
                  <button
                    type="button"
                    className={`btn ${isCompleted ? "btn-success" : "btn-outline-success"}`}
                    onClick={handleMarkComplete}
                    disabled={marking}
                  >
                    {isCompleted ? "Completed" : marking ? "Saving..." : "Mark complete"}
                  </button>
                  <Link className="btn btn-outline-light" to={`/courses/${courseId}`}>
                    Back to course
                  </Link>
                </div>
              </div>

              <div className="lesson-viewer-grid">
                <section className="lesson-viewer-content">
                  <h4>Lesson Content</h4>
                  <div className="lesson-viewer-text">
                    {currentLesson.content}
                  </div>
                </section>

                <aside className="lesson-viewer-media">
                  <div className="lesson-viewer-card">
                    <h5>Video</h5>
                    {currentLesson.video_url ? (
                      <a
                        href={currentLesson.video_url}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-outline-primary w-100"
                      >
                        Watch video
                      </a>
                    ) : (
                      <div className="lesson-viewer-empty">No video link.</div>
                    )}
                  </div>
                  <div className="lesson-viewer-card">
                    <h5>Audio</h5>
                    {currentLesson.audio_url ? (
                      <audio controls src={currentLesson.audio_url} />
                    ) : (
                      <div className="lesson-viewer-empty">No audio provided.</div>
                    )}
                  </div>
                </aside>
              </div>

              <div className="lesson-viewer-nav">
                {prevLesson ? (
                  <Link
                    className="btn btn-outline-primary"
                    to={`/courses/${courseId}/lessons/${prevLesson.id}`}
                  >
                    ← Previous lesson
                  </Link>
                ) : (
                  <span />
                )}
                {nextLesson ? (
                  <Link
                    className="btn btn-primary"
                    to={`/courses/${courseId}/lessons/${nextLesson.id}`}
                  >
                    Next lesson →
                  </Link>
                ) : (
                  <Link className="btn btn-primary" to={`/courses/${courseId}`}>
                    Go to practice
                  </Link>
                )}
              </div>
            </>
          ) : (
            <div className="lesson-viewer-empty">Lesson not found.</div>
          )}
        </div>
      </div>
    </PageTransition>
  );
};

export default LessonViewer;
