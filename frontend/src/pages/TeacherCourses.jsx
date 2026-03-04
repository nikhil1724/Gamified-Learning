import { useEffect, useMemo, useState } from "react";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import "./TeacherCourses.css";

const TeacherCourses = () => {
  const [courses, setCourses] = useState([]);
  const [formData, setFormData] = useState({ title: "", description: "" });
  const [noteForm, setNoteForm] = useState({
    courseId: "",
    title: "",
    content: "",
  });
  const [notes, setNotes] = useState([]);
  const [notesLoading, setNotesLoading] = useState(false);
  const [notesSubmitting, setNotesSubmitting] = useState(false);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [notesError, setNotesError] = useState("");
  const [notesMessage, setNotesMessage] = useState("");

  const fetchCourses = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await api.get("/teacher/courses");
      setCourses(response.data || []);
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to load courses.");
    } finally {
      setLoading(false);
    }
  };

  const fetchNotes = async (courseId) => {
    if (!courseId) {
      setNotes([]);
      return;
    }

    try {
      setNotesLoading(true);
      setNotesError("");
      const response = await api.get(`/courses/${courseId}/notes`);
      setNotes(response.data || []);
    } catch (err) {
      setNotesError(err?.response?.data?.error || "Failed to load notes.");
    } finally {
      setNotesLoading(false);
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  useEffect(() => {
    if (!noteForm.courseId && courses.length) {
      setNoteForm((prev) => ({ ...prev, courseId: String(courses[0].id) }));
      return;
    }

    if (noteForm.courseId) {
      fetchNotes(noteForm.courseId);
    }
  }, [courses, noteForm.courseId]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleNoteChange = (event) => {
    const { name, value } = event.target;
    setNoteForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!formData.title.trim()) {
      setError("Course title is required.");
      return;
    }

    try {
      setSubmitting(true);
      setError("");
      const payload = {
        title: formData.title.trim(),
        description: formData.description.trim(),
      };
      const response = await api.post("/teacher/courses", payload);
      setCourses((prev) => [response.data, ...prev]);
      setFormData({ title: "", description: "" });
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to create course.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleNoteSubmit = async (event) => {
    event.preventDefault();
    if (!noteForm.courseId) {
      setNotesError("Select a course first.");
      return;
    }
    if (!noteForm.title.trim()) {
      setNotesError("Note title is required.");
      return;
    }
    if (!noteForm.content.trim()) {
      setNotesError("Note content is required.");
      return;
    }

    try {
      setNotesSubmitting(true);
      setNotesError("");
      setNotesMessage("");
      const payload = {
        course_id: Number(noteForm.courseId),
        title: noteForm.title.trim(),
        content: noteForm.content.trim(),
      };
      await api.post("/teacher/notes", payload);
      setNotesMessage("Note uploaded successfully.");
      setNoteForm((prev) => ({ ...prev, title: "", content: "" }));
      fetchNotes(noteForm.courseId);
    } catch (err) {
      setNotesError(err?.response?.data?.error || "Failed to upload note.");
    } finally {
      setNotesSubmitting(false);
    }
  };

  const selectedCourse = useMemo(
    () => courses.find((course) => String(course.id) === String(noteForm.courseId)),
    [courses, noteForm.courseId]
  );

  return (
    <PageTransition>
      <div className="teacher-courses-page py-5">
        <div className="container">
          <div className="teacher-courses-hero mb-4">
            <div>
              <span className="teacher-badge">Teacher Console</span>
              <h1 className="mb-2">Course Management</h1>
              <p className="text-muted mb-0">
                Create courses, publish notes, and guide your learners with structured
                journeys.
              </p>
            </div>
            <div className="teacher-courses-metric">
              <div className="teacher-courses-metric__label">Active Courses</div>
              <div className="teacher-courses-metric__value">{courses.length}</div>
            </div>
          </div>

          <div className="teacher-courses-grid">
            <section className="teacher-courses-form card">
              <div className="card-body">
                <h5 className="card-title mb-3">Create a new course</h5>
                <form onSubmit={handleSubmit}>
                  <div className="mb-3">
                    <label className="form-label" htmlFor="title">
                      Course title
                    </label>
                    <input
                      id="title"
                      name="title"
                      type="text"
                      className="form-control"
                      value={formData.title}
                      onChange={handleChange}
                      placeholder="e.g., Applied Machine Learning"
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label" htmlFor="description">
                      Description
                    </label>
                    <textarea
                      id="description"
                      name="description"
                      className="form-control"
                      rows="4"
                      value={formData.description}
                      onChange={handleChange}
                      placeholder="Highlight outcomes, structure, and expectations."
                    />
                  </div>
                  {error ? <div className="text-danger small mb-3">{error}</div> : null}
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={submitting}
                  >
                    {submitting ? "Creating..." : "Create course"}
                  </button>
                </form>
              </div>
            </section>

            <section className="teacher-courses-list">
              <div className="teacher-courses-list__header">
                <h5 className="mb-0">Your courses</h5>
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
                <div className="teacher-courses-loading">Loading courses...</div>
              ) : courses.length ? (
                <div className="teacher-courses-cards">
                  {courses.map((course) => (
                    <article className="teacher-course-card" key={course.id}>
                      <div className="teacher-course-card__header">
                        <h6 className="mb-1">{course.title}</h6>
                        <span className="teacher-course-card__date">
                          {new Date(course.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-muted mb-0">
                        {course.description || "No description provided yet."}
                      </p>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="teacher-courses-empty">
                  No courses yet. Create the first course to begin.
                </div>
              )}
            </section>
          </div>

          <section className="teacher-notes-section mt-4">
            <div className="teacher-notes-header">
              <div>
                <h4 className="mb-1">Course Notes</h4>
                <p className="text-muted mb-0">
                  Upload structured notes and learning content for your learners.
                </p>
              </div>
              {selectedCourse ? (
                <span className="teacher-notes-course">
                  {selectedCourse.title}
                </span>
              ) : null}
            </div>

            <div className="teacher-notes-grid">
              <div className="teacher-notes-form card">
                <div className="card-body">
                  <h5 className="card-title mb-3">Upload a note</h5>
                  <form onSubmit={handleNoteSubmit}>
                    <div className="mb-3">
                      <label className="form-label" htmlFor="courseId">
                        Select course
                      </label>
                      <select
                        id="courseId"
                        name="courseId"
                        className="form-select"
                        value={noteForm.courseId}
                        onChange={handleNoteChange}
                        disabled={!courses.length}
                      >
                        {courses.length ? (
                          courses.map((course) => (
                            <option key={course.id} value={course.id}>
                              {course.title}
                            </option>
                          ))
                        ) : (
                          <option value="">Create a course first</option>
                        )}
                      </select>
                    </div>
                    <div className="mb-3">
                      <label className="form-label" htmlFor="noteTitle">
                        Note title
                      </label>
                      <input
                        id="noteTitle"
                        name="title"
                        type="text"
                        className="form-control"
                        value={noteForm.title}
                        onChange={handleNoteChange}
                        placeholder="Week 1: Foundations and goals"
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label" htmlFor="noteContent">
                        Content
                      </label>
                      <textarea
                        id="noteContent"
                        name="content"
                        className="form-control teacher-notes-textarea"
                        rows="6"
                        value={noteForm.content}
                        onChange={handleNoteChange}
                        placeholder="Provide structured learning content, key points, and resources."
                      />
                    </div>
                    {notesError ? (
                      <div className="text-danger small mb-3">{notesError}</div>
                    ) : null}
                    {notesMessage ? (
                      <div className="text-success small mb-3">{notesMessage}</div>
                    ) : null}
                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={notesSubmitting || !courses.length}
                    >
                      {notesSubmitting ? "Uploading..." : "Upload note"}
                    </button>
                  </form>
                </div>
              </div>

              <div className="teacher-notes-list">
                <div className="teacher-notes-list__header">
                  <h5 className="mb-0">Notes library</h5>
                  <button
                    type="button"
                    className="btn btn-sm btn-outline-primary"
                    onClick={() => fetchNotes(noteForm.courseId)}
                    disabled={notesLoading || !noteForm.courseId}
                  >
                    {notesLoading ? "Refreshing..." : "Refresh"}
                  </button>
                </div>

                {notesLoading ? (
                  <div className="teacher-notes-loading">Loading notes...</div>
                ) : notes.length ? (
                  <div className="teacher-notes-cards">
                    {notes.map((note) => (
                      <article className="teacher-note-card" key={note.id}>
                        <div className="teacher-note-card__header">
                          <h6 className="mb-1">{note.title}</h6>
                          <span className="teacher-note-card__date">
                            {new Date(note.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-muted mb-0">
                          {note.content?.slice(0, 160) || "No content provided."}
                          {note.content && note.content.length > 160 ? "..." : ""}
                        </p>
                      </article>
                    ))}
                  </div>
                ) : (
                  <div className="teacher-notes-empty">
                    No notes yet for this course.
                  </div>
                )}
              </div>
            </div>
          </section>
        </div>
      </div>
    </PageTransition>
  );
};

export default TeacherCourses;
