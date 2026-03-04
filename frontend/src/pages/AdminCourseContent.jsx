import { useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import "./AdminCourseContent.css";

const emptyLesson = {
  title: "",
  content: "",
  video_url: "",
  audio_url: "",
  order_index: 0,
};

const emptyProblem = {
  title: "",
  difficulty: "Easy",
  tags: "",
  description: "",
  constraints: "",
  example_input: "",
  example_output: "",
};

const AdminCourseContent = () => {
  const [courses, setCourses] = useState([]);
  const [selectedCourseId, setSelectedCourseId] = useState("");
  const [lessons, setLessons] = useState([]);
  const [codingProblems, setCodingProblems] = useState([]);
  const [lessonForm, setLessonForm] = useState(emptyLesson);
  const [problemForm, setProblemForm] = useState(emptyProblem);
  const [editingLessonId, setEditingLessonId] = useState(null);
  const [editingProblemId, setEditingProblemId] = useState(null);
  const [lessonMode, setLessonMode] = useState("edit");
  const [problemMode, setProblemMode] = useState("edit");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);
        setError("");
        const response = await api.get("/courses");
        const items = response.data || [];
        setCourses(items);
        if (items.length && !selectedCourseId) {
          setSelectedCourseId(String(items[0].id));
        }
      } catch (err) {
        setError(err?.response?.data?.error || "Failed to load courses.");
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, [selectedCourseId]);

  const fetchCourseContent = async (courseId) => {
    if (!courseId) {
      setLessons([]);
      setCodingProblems([]);
      return;
    }

    try {
      setError("");
      const [lessonsResponse, problemsResponse] = await Promise.all([
        api.get(`/course/${courseId}/lessons`),
        api.get(`/course/${courseId}/problems`),
      ]);
      setLessons(lessonsResponse.data || []);
      setCodingProblems(problemsResponse.data || []);
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to load course content.");
    }
  };

  useEffect(() => {
    fetchCourseContent(selectedCourseId);
  }, [selectedCourseId]);

  const selectedCourse = useMemo(
    () => courses.find((course) => String(course.id) === String(selectedCourseId)),
    [courses, selectedCourseId]
  );

  const handleLessonChange = (event) => {
    const { name, value } = event.target;
    setLessonForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleProblemChange = (event) => {
    const { name, value } = event.target;
    setProblemForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleEditLesson = (lesson) => {
    setEditingLessonId(lesson.id);
    setLessonMode("edit");
    setLessonForm({
      title: lesson.title || "",
      content: lesson.content || "",
      video_url: lesson.video_url || "",
      audio_url: lesson.audio_url || "",
      order_index: lesson.order_index || 0,
    });
  };

  const handleEditProblem = (problem) => {
    setEditingProblemId(problem.id);
    setProblemMode("edit");
    setProblemForm({
      title: problem.title || "",
      difficulty: problem.difficulty || "Easy",
      tags: problem.tags?.join(", ") || "",
      description: problem.description || "",
      constraints: problem.constraints || "",
      example_input: problem.example_input || "",
      example_output: problem.example_output || "",
    });
  };

  const handleLessonSubmit = async (event) => {
    event.preventDefault();
    if (!selectedCourseId) {
      setError("Select a course first.");
      return;
    }

    try {
      setSaving(true);
      setError("");
      const payload = {
        course_id: Number(selectedCourseId),
        title: lessonForm.title.trim(),
        content: lessonForm.content,
        video_url: lessonForm.video_url || null,
        audio_url: lessonForm.audio_url || null,
        order_index: Number(lessonForm.order_index) || 0,
      };

      if (editingLessonId) {
        await api.put(`/admin/lessons/${editingLessonId}`, payload);
      } else {
        await api.post("/admin/lessons", payload);
      }

      setLessonForm(emptyLesson);
      setEditingLessonId(null);
      setLessonMode("edit");
      fetchCourseContent(selectedCourseId);
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to save lesson.");
    } finally {
      setSaving(false);
    }
  };

  const handleProblemSubmit = async (event) => {
    event.preventDefault();
    if (!selectedCourseId) {
      setError("Select a course first.");
      return;
    }

    try {
      setSaving(true);
      setError("");
      const payload = {
        course_id: Number(selectedCourseId),
        title: problemForm.title.trim(),
        difficulty: problemForm.difficulty,
        tags: problemForm.tags
          ? problemForm.tags.split(",").map((tag) => tag.trim()).filter(Boolean)
          : [],
        description: problemForm.description,
        constraints: problemForm.constraints,
        example_input: problemForm.example_input,
        example_output: problemForm.example_output,
      };

      if (editingProblemId) {
        await api.put(`/admin/coding-problems/${editingProblemId}`, payload);
      } else {
        await api.post("/admin/coding-problems", payload);
      }

      setProblemForm(emptyProblem);
      setEditingProblemId(null);
      setProblemMode("edit");
      fetchCourseContent(selectedCourseId);
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to save coding problem.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <PageTransition>
      <div className="admin-course-content-page py-5">
        <div className="container">
          <div className="admin-course-content-hero">
            <div>
              <span className="admin-badge">Admin Console</span>
              <h1 className="mb-2">Course Content Studio</h1>
              <p className="text-muted mb-0">
                Add lessons and coding practice to your learning tracks.
              </p>
            </div>
            <select
              className="form-select admin-course-select"
              value={selectedCourseId}
              onChange={(event) => setSelectedCourseId(event.target.value)}
              disabled={loading}
            >
              {courses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.title}
                </option>
              ))}
            </select>
          </div>

          {error ? <div className="alert alert-danger">{error}</div> : null}

          <div className="admin-course-grid">
            <section className="admin-panel">
              <div className="admin-panel__header">
                <h5 className="mb-0">Lessons</h5>
                <span className="admin-panel__hint">
                  {selectedCourse?.title || "Select a course"}
                </span>
              </div>
              <div className="admin-list">
                {lessons.length ? (
                  lessons.map((lesson, index) => (
                    <button
                      key={lesson.id}
                      type="button"
                      className={`admin-list-item ${
                        editingLessonId === lesson.id ? "is-active" : ""
                      }`}
                      onClick={() => handleEditLesson(lesson)}
                    >
                      <div>
                        <strong>Lesson {index + 1}</strong>
                        <span>{lesson.title}</span>
                      </div>
                      <small>Order {lesson.order_index}</small>
                    </button>
                  ))
                ) : (
                  <div className="admin-empty">No lessons yet.</div>
                )}
              </div>
              <form onSubmit={handleLessonSubmit} className="admin-form">
                <h6>{editingLessonId ? "Edit Lesson" : "New Lesson"}</h6>
                <div className="editor-toggle">
                  <button
                    type="button"
                    className={`btn btn-sm ${
                      lessonMode === "edit" ? "btn-primary" : "btn-outline-primary"
                    }`}
                    onClick={() => setLessonMode("edit")}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className={`btn btn-sm ${
                      lessonMode === "preview" ? "btn-primary" : "btn-outline-primary"
                    }`}
                    onClick={() => setLessonMode("preview")}
                  >
                    Preview
                  </button>
                </div>
                <input
                  className="form-control"
                  name="title"
                  placeholder="Lesson title"
                  value={lessonForm.title}
                  onChange={handleLessonChange}
                  required
                />
                {lessonMode === "preview" ? (
                  <div className="markdown-preview">
                    <ReactMarkdown>
                      {lessonForm.content || "Nothing to preview yet."}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <textarea
                    className="form-control"
                    name="content"
                    placeholder="Lesson content (Markdown supported)"
                    rows="6"
                    value={lessonForm.content}
                    onChange={handleLessonChange}
                    required
                  />
                )}
                <input
                  className="form-control"
                  name="video_url"
                  placeholder="Video URL (optional)"
                  value={lessonForm.video_url}
                  onChange={handleLessonChange}
                />
                <input
                  className="form-control"
                  name="audio_url"
                  placeholder="Audio URL (optional)"
                  value={lessonForm.audio_url}
                  onChange={handleLessonChange}
                />
                <input
                  className="form-control"
                  name="order_index"
                  type="number"
                  min="0"
                  placeholder="Order"
                  value={lessonForm.order_index}
                  onChange={handleLessonChange}
                />
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? "Saving..." : editingLessonId ? "Update Lesson" : "Create Lesson"}
                </button>
              </form>
            </section>

            <section className="admin-panel">
              <div className="admin-panel__header">
                <h5 className="mb-0">Coding Problems</h5>
                <span className="admin-panel__hint">
                  {selectedCourse?.title || "Select a course"}
                </span>
              </div>
              <div className="admin-list">
                {codingProblems.length ? (
                  codingProblems.map((problem) => (
                    <button
                      key={problem.id}
                      type="button"
                      className={`admin-list-item ${
                        editingProblemId === problem.id ? "is-active" : ""
                      }`}
                      onClick={() => handleEditProblem(problem)}
                    >
                      <div>
                        <strong>{problem.title}</strong>
                        <span>{problem.difficulty}</span>
                      </div>
                      <small>{problem.tags?.length ? problem.tags.join(", ") : "No tags"}</small>
                    </button>
                  ))
                ) : (
                  <div className="admin-empty">No coding problems yet.</div>
                )}
              </div>
              <form onSubmit={handleProblemSubmit} className="admin-form">
                <h6>{editingProblemId ? "Edit Problem" : "New Problem"}</h6>
                <div className="editor-toggle">
                  <button
                    type="button"
                    className={`btn btn-sm ${
                      problemMode === "edit" ? "btn-primary" : "btn-outline-primary"
                    }`}
                    onClick={() => setProblemMode("edit")}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className={`btn btn-sm ${
                      problemMode === "preview" ? "btn-primary" : "btn-outline-primary"
                    }`}
                    onClick={() => setProblemMode("preview")}
                  >
                    Preview
                  </button>
                </div>
                <input
                  className="form-control"
                  name="title"
                  placeholder="Problem title"
                  value={problemForm.title}
                  onChange={handleProblemChange}
                  required
                />
                <select
                  className="form-select"
                  name="difficulty"
                  value={problemForm.difficulty}
                  onChange={handleProblemChange}
                >
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Hard">Hard</option>
                </select>
                <input
                  className="form-control"
                  name="tags"
                  placeholder="Tags (comma separated)"
                  value={problemForm.tags}
                  onChange={handleProblemChange}
                />
                {problemMode === "preview" ? (
                  <div className="markdown-preview">
                    <ReactMarkdown>
                      {problemForm.description || "Nothing to preview yet."}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <textarea
                    className="form-control"
                    name="description"
                    placeholder="Problem description (Markdown supported)"
                    rows="5"
                    value={problemForm.description}
                    onChange={handleProblemChange}
                    required
                  />
                )}
                <textarea
                  className="form-control"
                  name="constraints"
                  placeholder="Constraints"
                  rows="2"
                  value={problemForm.constraints}
                  onChange={handleProblemChange}
                />
                <textarea
                  className="form-control"
                  name="example_input"
                  placeholder="Example input"
                  rows="2"
                  value={problemForm.example_input}
                  onChange={handleProblemChange}
                />
                <textarea
                  className="form-control"
                  name="example_output"
                  placeholder="Example output"
                  rows="2"
                  value={problemForm.example_output}
                  onChange={handleProblemChange}
                />
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? "Saving..." : editingProblemId ? "Update Problem" : "Create Problem"}
                </button>
              </form>
            </section>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default AdminCourseContent;
