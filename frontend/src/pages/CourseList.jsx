import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import "./CourseList.css";

const CourseList = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);
        setError("");
        const response = await api.get("/courses");
        setCourses(response.data || []);
      } catch (err) {
        setError(err?.response?.data?.error || "Unable to load courses.");
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, []);

  const filteredCourses = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) {
      return courses;
    }
    return courses.filter((course) =>
      course.title.toLowerCase().includes(term)
    );
  }, [courses, search]);

  return (
    <PageTransition>
      <div className="course-list-page">
        <div className="container py-5">
          <div className="course-list-hero">
            <div>
              <span className="course-list-badge">Learning Tracks</span>
              <h1>Courses</h1>
              <p className="text-muted">
                Pick a path, follow structured lessons, and unlock practice.
              </p>
            </div>
            <div className="course-list-search">
              <input
                className="form-control"
                placeholder="Search courses"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>
          </div>

          {error ? <div className="alert alert-danger">{error}</div> : null}

          <div className="course-list-grid">
            {loading ? (
              <div className="course-list-empty">Loading courses...</div>
            ) : filteredCourses.length ? (
              filteredCourses.map((course) => (
                <Link
                  key={course.id}
                  to={`/courses/${course.id}`}
                  className="course-list-card"
                >
                  <div>
                    <h4>{course.title}</h4>
                    <p className="text-muted">
                      {course.description || "No description provided yet."}
                    </p>
                  </div>
                  <div className="course-list-meta">
                    <span>{course.teacher_name || "Instructor"}</span>
                    <span>{new Date(course.created_at).toLocaleDateString()}</span>
                  </div>
                </Link>
              ))
            ) : (
              <div className="course-list-empty">No courses match your search.</div>
            )}
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default CourseList;
