import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import ProgressBar from "../components/ProgressBar";
import "./CourseContent.css";

const CourseContent = () => {
  const { courseId } = useParams();
  const location = useLocation();
  const [notes, setNotes] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [notesLoading, setNotesLoading] = useState(true);
  const [quizzesLoading, setQuizzesLoading] = useState(true);
  const [notesError, setNotesError] = useState("");
  const [quizzesError, setQuizzesError] = useState("");
  const [progress, setProgress] = useState({ total: 0, completed: 0 });

  const courseTitle = useMemo(() => {
    const stateTitle = location.state?.title;
    return stateTitle || "Course";
  }, [location.state]);

  useEffect(() => {
    const fetchNotes = async () => {
      try {
        setNotesLoading(true);
        setNotesError("");
        const response = await api.get(`/courses/${courseId}/notes`);
        setNotes(response.data || []);
      } catch (err) {
        setNotesError(
          err?.response?.data?.error || "Unable to load course notes."
        );
      } finally {
        setNotesLoading(false);
      }
    };

    fetchNotes();
  }, [courseId]);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const response = await api.get(`/courses/${courseId}/progress`);
        setProgress({
          total: response.data?.total_lessons ?? 0,
          completed: response.data?.completed_count ?? 0,
        });
      } catch {
        setProgress({ total: 0, completed: 0 });
      }
    };

    if (courseId) {
      fetchProgress();
    }
  }, [courseId]);

  useEffect(() => {
    const fetchQuizzes = async () => {
      try {
        setQuizzesLoading(true);
        setQuizzesError("");
        const response = await api.get(`/courses/${courseId}/quizzes`);
        setQuizzes(response.data || []);
      } catch (err) {
        setQuizzesError(
          err?.response?.data?.error || "Unable to load course quizzes."
        );
      } finally {
        setQuizzesLoading(false);
      }
    };

    fetchQuizzes();
  }, [courseId]);

  const getQuizResult = (quizId) => {
    try {
      const raw = localStorage.getItem(`quiz_result_${quizId}`);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  };

  return (
    <PageTransition>
      <div className="course-content-page py-5">
        <div className="container">
          <div className="course-content-hero mb-4">
            <div>
              <span className="course-content-badge">Course Notes</span>
              <h1 className="mb-2">{courseTitle}</h1>
              <p className="text-muted mb-0">
                Review instructor notes and keep your learning on track.
              </p>
            </div>
            <div className="course-content-progress">
              <ProgressBar
                current={progress.completed}
                total={progress.total}
                size="large"
              />
            </div>
          </div>

          {notesError ? <div className="alert alert-danger">{notesError}</div> : null}

          {notesLoading ? (
            <div className="course-content-list">
              {Array.from({ length: 4 }).map((_, index) => (
                <div className="course-note-card skeleton" key={`note-${index}`}>
                  <div className="skeleton-line skeleton-line--wide" />
                  <div className="skeleton-line" />
                  <div className="skeleton-line" />
                </div>
              ))}
            </div>
          ) : notes.length ? (
            <div className="course-content-list">
              {notes.map((note) => (
                <article className="course-note-card" key={note.id}>
                  <div className="course-note-card__header">
                    <h4 className="mb-1">{note.title}</h4>
                    <span className="course-note-card__date">
                      {new Date(note.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {note.content ? (
                    <div className="course-note-card__body">{note.content}</div>
                  ) : (
                    <div className="course-note-card__body course-note-card__body--muted">
                      No written notes provided.
                    </div>
                  )}
                  {note.file_url ? (
                    <a
                      className="course-note-card__link"
                      href={note.file_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Download attachment
                    </a>
                  ) : null}
                </article>
              ))}
            </div>
          ) : (
            <div className="course-content-empty">
              No notes have been posted for this course yet.
            </div>
          )}

          <div className="course-practice-section mt-5">
            <div className="course-practice-header">
              <div>
                <span className="course-practice-badge">Course Practice</span>
                <h2 className="mb-1">Test your understanding</h2>
                <p className="text-muted mb-0">
                  Attempt quizzes linked to this course and track your score.
                </p>
              </div>
            </div>

            {quizzesError ? (
              <div className="alert alert-danger">{quizzesError}</div>
            ) : null}

            {quizzesLoading ? (
              <div className="course-practice-grid">
                {Array.from({ length: 3 }).map((_, index) => (
                  <div className="course-quiz-card skeleton" key={`quiz-${index}`}>
                    <div className="skeleton-line skeleton-line--wide" />
                    <div className="skeleton-line" />
                    <div className="skeleton-line" />
                    <div className="skeleton-line skeleton-line--wide" />
                  </div>
                ))}
              </div>
            ) : quizzes.length ? (
              <div className="course-practice-grid">
                {quizzes.map((quiz) => {
                  const result = getQuizResult(quiz.id);
                  const isCompleted = Boolean(result);
                  const scoreText = result
                    ? `${result.score}/${result.total_questions}`
                    : "--";
                  const completedAt = result?.completed_at
                    ? new Date(result.completed_at).toLocaleDateString()
                    : null;

                  return (
                    <article className="course-quiz-card" key={quiz.id}>
                      <div className="course-quiz-card__header">
                        <h5 className="mb-1">{quiz.title}</h5>
                        <span
                          className={`course-quiz-badge course-quiz-badge--${
                            quiz.difficulty?.toLowerCase() || "easy"
                          }`}
                        >
                          {quiz.difficulty}
                        </span>
                      </div>
                      <div className="course-quiz-card__meta">
                        <span
                          className={
                            isCompleted
                              ? "course-quiz-status course-quiz-status--done"
                              : "course-quiz-status"
                          }
                        >
                          {isCompleted ? "Completed" : "Not attempted"}
                        </span>
                        <span className="course-quiz-score">Score: {scoreText}</span>
                        {completedAt ? (
                          <span className="course-quiz-date">
                            Last attempt: {completedAt}
                          </span>
                        ) : null}
                      </div>
                      <Link
                        className="btn btn-outline-primary mt-auto"
                        to={`/quiz?quizId=${quiz.id}`}
                      >
                        {isCompleted ? "Retry Quiz" : "Attempt Quiz"}
                      </Link>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="course-content-empty">
                No quizzes have been assigned to this course yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default CourseContent;
