import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import "./StudentCourses.css";

const StudentCourses = () => {
  const [availableCourses, setAvailableCourses] = useState([]);
  const [enrolledCourses, setEnrolledCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [enrollingId, setEnrollingId] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const fetchCourses = async () => {
    try {
      setLoading(true);
      setError("");
      const [availableResponse, enrolledResponse] = await Promise.all([
        api.get("/courses"),
        api.get("/student/courses"),
      ]);
      setAvailableCourses(availableResponse.data || []);
      setEnrolledCourses(enrolledResponse.data || []);
    } catch (err) {
      setError(err?.response?.data?.error || "Unable to load courses.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const enrolledIds = useMemo(
    () => new Set(enrolledCourses.map((course) => course.id ?? course.course_id)),
    [enrolledCourses]
  );

  const getInstructorName = (course) =>
    course.teacher_name ||
    course.instructor_name ||
    course.teacher?.name ||
    course.instructor?.name ||
    "Instructor";

  const handleEnroll = async (courseId) => {
    try {
      setEnrollingId(courseId);
      setMessage("");
      setError("");
      await api.post("/student/enroll", { course_id: courseId });
      setMessage("Enrollment successful.");
      const enrolledResponse = await api.get("/student/courses");
      setEnrolledCourses(enrolledResponse.data || []);
    } catch (err) {
      setError(err?.response?.data?.error || "Enrollment failed.");
    } finally {
      setEnrollingId(null);
    }
  };

  return (
    <PageTransition>
      <div className="student-courses-page py-5">
        <div className="container">
          <div className="student-courses-hero mb-4">
            <div>
              <span className="student-courses-badge">Student Courses</span>
              <h1 className="mb-2">Grow with guided learning paths</h1>
              <p className="text-muted mb-0">
                Explore instructor-led courses and keep your progress organized.
              </p>
            </div>
            <div className="student-courses-stat">
              <div className="student-courses-stat__label">Enrolled</div>
              <div className="student-courses-stat__value">{enrolledCourses.length}</div>
            </div>
          </div>

          {message ? <div className="alert alert-success">{message}</div> : null}
          {error ? <div className="alert alert-danger">{error}</div> : null}

          <section className="student-courses-section mb-5">
            <div className="student-courses-section__header">
              <h3 className="mb-0">Available Courses</h3>
              <button
                type="button"
                className="btn btn-sm btn-outline-primary"
                onClick={fetchCourses}
                disabled={loading}
              >
                {loading ? "Refreshing..." : "Refresh"}
              </button>
            </div>

            {loading ? (
              <div className="student-courses-grid">
                {Array.from({ length: 4 }).map((_, index) => (
                  <div className="student-course-card skeleton" key={`available-${index}`}>
                    <div className="skeleton-line skeleton-line--wide" />
                    <div className="skeleton-line" />
                    <div className="skeleton-line" />
                    <div className="skeleton-pill" />
                  </div>
                ))}
              </div>
            ) : availableCourses.length ? (
              <div className="student-courses-grid">
                {availableCourses.map((course) => {
                  const isEnrolled = enrolledIds.has(course.id);
                  return (
                    <article className="student-course-card" key={course.id}>
                      <div className="student-course-card__header">
                        <div>
                          <h5 className="mb-1">{course.title}</h5>
                          <span className="student-course-card__instructor">
                            {getInstructorName(course)}
                          </span>
                        </div>
                        <span className="student-course-card__tag">Open</span>
                      </div>
                      <p className="text-muted mb-3">
                        {course.description || "No description provided yet."}
                      </p>
                      <button
                        type="button"
                        className="btn btn-primary"
                        disabled={isEnrolled || enrollingId === course.id}
                        onClick={() => handleEnroll(course.id)}
                      >
                        {isEnrolled
                          ? "Enrolled"
                          : enrollingId === course.id
                          ? "Enrolling..."
                          : "Enroll"}
                      </button>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="student-courses-empty">
                No courses are available right now. Check back soon.
              </div>
            )}
          </section>

          <section className="student-courses-section">
            <div className="student-courses-section__header">
              <h3 className="mb-0">My Courses</h3>
              <span className="student-courses-section__hint">Your active enrollments</span>
            </div>

            {loading ? (
              <div className="student-courses-grid">
                {Array.from({ length: 3 }).map((_, index) => (
                  <div className="student-course-card skeleton" key={`enrolled-${index}`}>
                    <div className="skeleton-line skeleton-line--wide" />
                    <div className="skeleton-line" />
                    <div className="skeleton-line" />
                    <div className="skeleton-pill" />
                  </div>
                ))}
              </div>
            ) : enrolledCourses.length ? (
              <div className="student-courses-grid">
                {enrolledCourses.map((course) => (
                  <article className="student-course-card" key={course.id ?? course.course_id}>
                    <div className="student-course-card__header">
                      <div>
                        <h5 className="mb-1">{course.title}</h5>
                        <span className="student-course-card__instructor">
                          {getInstructorName(course)}
                        </span>
                      </div>
                      <span className="student-course-card__tag student-course-card__tag--enrolled">
                        Enrolled
                      </span>
                    </div>
                    <p className="text-muted mb-0">
                      {course.description || "No description provided yet."}
                    </p>
                    <Link
                      className="btn btn-outline-primary mt-3"
                      to={`/learn/courses/${course.id ?? course.course_id}`}
                      state={{ title: course.title }}
                    >
                      Open course
                    </Link>
                  </article>
                ))}
              </div>
            ) : (
              <div className="student-courses-empty">
                You are not enrolled in any courses yet.
              </div>
            )}
          </section>
        </div>
      </div>
    </PageTransition>
  );
};

export default StudentCourses;
