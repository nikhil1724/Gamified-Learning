import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import ProgressBar from "../components/ProgressBar";
import "./CourseDetail.css";

const CourseDetail = () => {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [lessons, setLessons] = useState([]);
  const [notes, setNotes] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [problems, setProblems] = useState([]);
  const [progress, setProgress] = useState({ total: 0, completed: 0, completedLessons: [] });
  const [activeTab, setActiveTab] = useState("lessons");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        setLoading(true);
        setError("");
        const [
          courseResponse,
          lessonsResponse,
          notesResponse,
          quizzesResponse,
          problemsResponse,
          progressResponse,
        ] = await Promise.all([
          api.get(`/course/${courseId}`),
          api.get(`/course/${courseId}/lessons`),
          api.get(`/courses/${courseId}/notes`),
          api.get(`/course/${courseId}/quizzes`),
          api.get(`/course/${courseId}/problems`),
          api.get(`/courses/${courseId}/progress`),
        ]);
        setCourse(courseResponse.data || null);
        setLessons(lessonsResponse.data || []);
        setNotes(Array.isArray(notesResponse.data) ? notesResponse.data : []);
        setQuizzes(quizzesResponse.data || []);
        setProblems(problemsResponse.data || []);
        setProgress({
          total: progressResponse.data?.total_lessons ?? 0,
          completed: progressResponse.data?.completed_count ?? 0,
          completedLessons: progressResponse.data?.completed_lessons ?? [],
        });
      } catch (err) {
        setError(err?.response?.data?.error || "Failed to load course data.");
      } finally {
        setLoading(false);
      }
    };

    fetchCourse();
  }, [courseId]);

  const nextLesson = useMemo(() => {
    if (!lessons.length) {
      return null;
    }

    const completedSet = new Set(progress.completedLessons.map((id) => Number(id)));
    for (let index = 0; index < lessons.length; index += 1) {
      const lesson = lessons[index];
      if (!completedSet.has(Number(lesson.id))) {
        return lesson;
      }
    }

    return lessons[0];
  }, [lessons, progress.completedLessons]);

  const completedSet = useMemo(
    () => new Set(progress.completedLessons.map((id) => Number(id))),
    [progress.completedLessons]
  );

  return (
    <PageTransition>
      <div className="course-detail-page">
        <div className="container py-5">
          {loading ? (
            <div className="course-detail-empty">Loading course...</div>
          ) : error ? (
            <div className="alert alert-danger">{error}</div>
          ) : course ? (
            <>
              <div className="course-detail-hero">
                <div>
                  <span className="course-detail-badge">Course Overview</span>
                  <h1>{course.title}</h1>
                  <p className="text-muted">
                    {course.description || "No description provided yet."}
                  </p>
                  <div className="course-detail-meta">
                    <span>{course.teacher_name || "Instructor"}</span>
                    <span>{new Date(course.created_at).toLocaleDateString()}</span>
                  </div>
                  <div className="course-detail-progress">
                    <ProgressBar
                      current={progress.completed}
                      total={progress.total}
                      size="large"
                    />
                  </div>
                </div>
                {nextLesson ? (
                  <Link
                    className="btn btn-primary"
                    to={`/courses/${course.id}/lessons/${nextLesson.id}`}
                  >
                    {progress.completed > 0 ? "Continue Learning" : "Start Learning"}
                  </Link>
                ) : null}
              </div>

              <div className="course-tabs">
                <button
                  className={`course-tab ${activeTab === "lessons" ? "active" : ""}`}
                  onClick={() => setActiveTab("lessons")}
                >
                  Lessons
                </button>
                <button
                  className={`course-tab ${activeTab === "notes" ? "active" : ""}`}
                  onClick={() => setActiveTab("notes")}
                >
                  Notes
                </button>
                <button
                  className={`course-tab ${activeTab === "quizzes" ? "active" : ""}`}
                  onClick={() => setActiveTab("quizzes")}
                >
                  Quizzes
                </button>
                <button
                  className={`course-tab ${activeTab === "problems" ? "active" : ""}`}
                  onClick={() => setActiveTab("problems")}
                >
                  Problems
                </button>
              </div>

              <section className="course-detail-panel">
                {activeTab === "lessons" ? (
                  lessons.length ? (
                    <div className="course-detail-list">
                      {lessons.map((lesson, index) => {
                        const isCompleted = completedSet.has(Number(lesson.id));
                        const isUnlocked = index === 0 || completedSet.has(Number(lessons[index - 1]?.id));

                        return isUnlocked ? (
                          <Link
                            key={lesson.id}
                            to={`/courses/${course.id}/lessons/${lesson.id}`}
                            className="course-detail-item"
                          >
                            <div>
                              <strong>Lesson {index + 1}</strong>
                              <span>{lesson.title}</span>
                            </div>
                            <span className={`course-status-pill ${isCompleted ? "done" : "open"}`}>
                              {isCompleted ? "Completed" : "Unlocked"}
                            </span>
                          </Link>
                        ) : (
                          <div key={lesson.id} className="course-detail-item course-detail-item--locked">
                            <div>
                              <strong>Lesson {index + 1}</strong>
                              <span>{lesson.title}</span>
                            </div>
                            <span className="course-status-pill locked">Locked</span>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="course-detail-empty">No lessons yet.</div>
                  )
                ) : null}

                {activeTab === "notes" ? (
                  notes.length ? (
                    <div className="course-detail-list">
                      {notes.map((note) => (
                        <div key={note.id} className="course-detail-item">
                          <div>
                            <strong>{note.title}</strong>
                            <span>{note.topic || "Course note"}</span>
                          </div>
                          {note.file_url ? (
                            <a href={note.file_url} target="_blank" rel="noreferrer" className="btn btn-sm btn-outline-primary">
                              Open
                            </a>
                          ) : null}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="course-detail-empty">No notes yet.</div>
                  )
                ) : null}

                {activeTab === "quizzes" ? (
                  quizzes.length ? (
                    <div className="course-detail-list">
                      {quizzes.map((quiz) => (
                        <Link key={quiz.id} to={`/quiz?quizId=${quiz.id}`} className="course-detail-item">
                          <div>
                            <strong>{quiz.title}</strong>
                            <span>{quiz.topic}</span>
                          </div>
                          <span className="course-detail-pill">{quiz.difficulty}</span>
                        </Link>
                      ))}
                    </div>
                  ) : (
                    <div className="course-detail-empty">No quizzes yet.</div>
                  )
                ) : null}

                {activeTab === "problems" ? (
                  problems.length ? (
                    <div className="course-detail-list">
                      {problems.map((problem) => (
                        <Link key={problem.id} to={`/problems/${problem.id}`} className="course-detail-item">
                          <div>
                            <strong>{problem.title}</strong>
                            <span>{problem.tags?.length ? problem.tags.join(", ") : "Coding problem"}</span>
                          </div>
                          <span className="course-detail-pill">{problem.difficulty}</span>
                        </Link>
                      ))}
                    </div>
                  ) : (
                    <div className="course-detail-empty">No coding problems yet.</div>
                  )
                ) : null}
              </section>
            </>
          ) : (
            <div className="course-detail-empty">Course not found.</div>
          )}
        </div>
      </div>
    </PageTransition>
  );
};

export default CourseDetail;
