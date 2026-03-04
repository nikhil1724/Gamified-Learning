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
  const [quizzes, setQuizzes] = useState([]);
  const [problems, setProblems] = useState([]);
  const [progress, setProgress] = useState({ total: 0, completed: 0 });
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
          quizzesResponse,
          problemsResponse,
          progressResponse,
        ] = await Promise.all([
          api.get(`/course/${courseId}`),
          api.get(`/course/${courseId}/lessons`),
          api.get(`/course/${courseId}/quizzes`),
          api.get(`/course/${courseId}/problems`),
          api.get(`/courses/${courseId}/progress`),
        ]);
        setCourse(courseResponse.data || null);
        setLessons(lessonsResponse.data || []);
        setQuizzes(quizzesResponse.data || []);
        setProblems(problemsResponse.data || []);
        setProgress({
          total: progressResponse.data?.total_lessons ?? 0,
          completed: progressResponse.data?.completed_count ?? 0,
        });
      } catch (err) {
        setError(err?.response?.data?.error || "Failed to load course data.");
      } finally {
        setLoading(false);
      }
    };

    fetchCourse();
  }, [courseId]);

  const nextLesson = useMemo(() => lessons[0], [lessons]);

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
                    Start lesson
                  </Link>
                ) : null}
              </div>

              <div className="course-detail-grid">
                <section className="course-detail-panel">
                  <h4>Lessons</h4>
                  {lessons.length ? (
                    <div className="course-detail-list">
                      {lessons.map((lesson, index) => (
                        <Link
                          key={lesson.id}
                          to={`/courses/${course.id}/lessons/${lesson.id}`}
                          className="course-detail-item"
                        >
                          <div>
                            <strong>Lesson {index + 1}</strong>
                            <span>{lesson.title}</span>
                          </div>
                          <span className="course-detail-chevron">→</span>
                        </Link>
                      ))}
                    </div>
                  ) : (
                    <div className="course-detail-empty">No lessons yet.</div>
                  )}
                </section>

                <section className="course-detail-panel">
                  <h4>Quizzes</h4>
                  {quizzes.length ? (
                    <div className="course-detail-list">
                      {quizzes.map((quiz) => (
                        <div key={quiz.id} className="course-detail-item">
                          <div>
                            <strong>{quiz.title}</strong>
                            <span>{quiz.topic}</span>
                          </div>
                          <span className="course-detail-pill">
                            {quiz.difficulty}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="course-detail-empty">No quizzes yet.</div>
                  )}
                </section>

                <section className="course-detail-panel">
                  <h4>Coding Practice</h4>
                  {problems.length ? (
                    <div className="course-detail-list">
                      {problems.map((problem) => (
                        <div key={problem.id} className="course-detail-item">
                          <div>
                            <strong>{problem.title}</strong>
                            <span>{problem.tags?.length ? problem.tags.join(", ") : ""}</span>
                          </div>
                          <span className="course-detail-pill">
                            {problem.difficulty}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="course-detail-empty">No coding problems yet.</div>
                  )}
                </section>
              </div>
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
