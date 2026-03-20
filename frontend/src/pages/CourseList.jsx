import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import "./CourseList.css";

const CourseList = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [category, setCategory] = useState("");

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);
        setError("");
        const params = {};
        if (search.trim()) params.search = search.trim();
        if (difficulty) params.difficulty = difficulty;
        if (category) params.category = category;

        const response = await api.get("/courses", { params });
        setCourses(response.data || []);
      } catch (err) {
        setError(err?.response?.data?.error || "Unable to load courses.");
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, [search, difficulty, category]);

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
            <div className="course-list-filters">
              <div className="course-list-search">
                <input
                  className="form-control"
                  placeholder="Search by title"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
              </div>
              <select
                className="form-select course-list-select"
                value={difficulty}
                onChange={(event) => setDifficulty(event.target.value)}
              >
                <option value="">All Difficulty</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
              <select
                className="form-select course-list-select"
                value={category}
                onChange={(event) => setCategory(event.target.value)}
              >
                <option value="">All Category</option>
                <option value="programming">Programming</option>
                <option value="dsa">DSA</option>
                <option value="web">Web</option>
                <option value="database">Database</option>
                <option value="systems">Systems</option>
              </select>
            </div>
          </div>

          {error ? <div className="alert alert-danger">{error}</div> : null}

          <div className="course-list-grid">
            {loading ? (
              <div className="course-list-empty">Loading courses...</div>
            ) : courses.length ? (
              courses.map((course) => (
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
                    {(course.difficulty || course.category) ? (
                      <div className="course-list-tags">
                        {course.difficulty ? (
                          <span className="course-list-tag">{course.difficulty}</span>
                        ) : null}
                        {course.category ? (
                          <span className="course-list-tag">{course.category}</span>
                        ) : null}
                        {course.xp_reward ? (
                          <span className="course-list-tag">⚡ {course.xp_reward} XP</span>
                        ) : null}
                        {Array.isArray(course.tags)
                          ? course.tags.slice(0, 3).map((tag) => (
                              <span className="course-list-tag" key={`${course.id}-${tag}`}>
                                #{tag}
                              </span>
                            ))
                          : null}
                      </div>
                    ) : null}
                  </div>
                  <div className="course-list-meta">
                    <span>{course.teacher_name || "Instructor"}</span>
                    <span>{new Date(course.created_at).toLocaleDateString()}</span>
                  </div>
                </Link>
              ))
            ) : (
              <div className="course-list-empty">No courses match your filters.</div>
            )}
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default CourseList;
