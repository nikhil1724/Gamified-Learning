import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import "./TeacherCourses.css";

const TeacherCourses = () => {
  const [courses, setCourses] = useState([]);
  const [formData, setFormData] = useState({ title: "", description: "" });
  const EMPTY_LESSON = {
    courseId: "",
    title: "",
    lessonNumber: "",
    topic: "",
    objectives: "",
    duration: "",
    difficulty: "Beginner",
    videoUrl: "",
    content: "",
  };
  const [noteForm, setNoteForm] = useState(EMPTY_LESSON);
  const [pdfFile, setPdfFile] = useState(null);
  const fileInputRef = useRef(null);
  const [notes, setNotes] = useState([]);
  const [notesLoading, setNotesLoading] = useState(false);
  const [notesSubmitting, setNotesSubmitting] = useState(false);
  const [deletingNoteId, setDeletingNoteId] = useState(null);
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
    if (!noteForm.courseId) { setNotesError("Select a course first."); return; }
    if (!noteForm.title.trim()) { setNotesError("Lesson title is required."); return; }
    if (
      !pdfFile &&
      !noteForm.content.trim() &&
      !noteForm.objectives.trim() &&
      !noteForm.videoUrl.trim()
    ) {
      setNotesError("Provide at least one of: content, PDF, video link, or learning objectives.");
      return;
    }

    try {
      setNotesSubmitting(true);
      setNotesError("");
      setNotesMessage("");

      const fd = new FormData();
      fd.append("course_id", noteForm.courseId);
      fd.append("title", noteForm.title.trim());
      fd.append("lesson_number", noteForm.lessonNumber || "");
      fd.append("topic", noteForm.topic.trim());
      fd.append("objectives", noteForm.objectives.trim());
      fd.append("duration", noteForm.duration || "");
      fd.append("difficulty", noteForm.difficulty);
      fd.append("video_url", noteForm.videoUrl.trim());
      if (noteForm.content.trim()) fd.append("content", noteForm.content.trim());
      if (pdfFile) fd.append("file", pdfFile);

      await api.post("/teacher/notes/upload-pdf", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setNotesMessage("✓ Lesson published successfully!");
      const savedCourse = noteForm.courseId;
      setNoteForm({ ...EMPTY_LESSON, courseId: savedCourse });
      setPdfFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      fetchNotes(savedCourse);
    } catch (err) {
      setNotesError(err?.response?.data?.error || "Failed to publish lesson.");
    } finally {
      setNotesSubmitting(false);
    }
  };

  const handleDeletePdf = async (noteId) => {
    try {
      setDeletingNoteId(noteId);
      setNotesError("");
      setNotesMessage("");

      const response = await api.delete(`/teacher/notes/${noteId}/pdf`);
      const action = response?.data?.action;

      if (action === "lesson_deleted") {
        setNotesMessage("PDF removed. The lesson was also deleted because it had no other content.");
      } else {
        setNotesMessage("PDF removed successfully.");
      }

      if (noteForm.courseId) {
        await fetchNotes(noteForm.courseId);
      }
    } catch (err) {
      setNotesError(err?.response?.data?.error || "Failed to delete PDF.");
    } finally {
      setDeletingNoteId(null);
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
                      <p className="text-muted mb-3">
                        {course.description || "No description provided yet."}
                      </p>
                      <div className="d-grid gap-2">
                        <Link 
                          to={`/instructor/analytics/${course.id}`}
                          className="btn btn-sm btn-primary w-100"
                        >
                          <i className="bi bi-bar-chart-line me-2"></i>
                          Instructor Dashboard
                        </Link>
                        <Link 
                          to={`/teacher/course/${course.id}/analytics`}
                          className="btn btn-sm btn-outline-primary w-100"
                        >
                          <i className="bi bi-graph-up me-2"></i>
                          Detailed Analytics
                        </Link>
                      </div>
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
                <h4 className="mb-1">Lesson Creator</h4>
                <p className="text-muted mb-0">
                  Build structured lessons with objectives, resources, and materials.
                </p>
              </div>
              {selectedCourse && (
                <span className="teacher-notes-course">{selectedCourse.title}</span>
              )}
            </div>

            <div className="teacher-notes-grid">
              {/* ── FORM ── */}
              <div className="teacher-notes-form card">
                <div className="card-body">
                  <h5 className="card-title mb-1">Create Lesson</h5>
                  <p className="text-muted small mb-4">Fill in the details below and publish to your students.</p>

                  <form onSubmit={handleNoteSubmit}>

                    {/* Course */}
                    <div className="mb-3">
                      <label className="form-label fw-semibold" htmlFor="courseId">Course</label>
                      <select
                        id="courseId" name="courseId"
                        className="form-select"
                        value={noteForm.courseId}
                        onChange={handleNoteChange}
                        disabled={!courses.length}
                      >
                        {courses.length ? (
                          courses.map((c) => <option key={c.id} value={c.id}>{c.title}</option>)
                        ) : (
                          <option value="">Create a course first</option>
                        )}
                      </select>
                    </div>

                    {/* ── Lesson Info ── */}
                    <div className="lesson-form-section">
                      <span className="lesson-form-section__label">Lesson Info</span>
                    </div>

                    <div className="lesson-form-row mb-3">
                      <div>
                        <label className="form-label" htmlFor="lessonNumber">Lesson / Week #</label>
                        <input
                          id="lessonNumber" name="lessonNumber" type="number" min="1"
                          className="form-control"
                          value={noteForm.lessonNumber}
                          onChange={handleNoteChange}
                          placeholder="e.g. 1"
                        />
                      </div>
                      <div>
                        <label className="form-label" htmlFor="noteTopic">Topic Name</label>
                        <input
                          id="noteTopic" name="topic" type="text"
                          className="form-control"
                          value={noteForm.topic}
                          onChange={handleNoteChange}
                          placeholder="e.g. HTML Basics"
                        />
                      </div>
                    </div>

                    <div className="mb-3">
                      <label className="form-label" htmlFor="noteTitle">Lesson Title <span className="text-danger">*</span></label>
                      <input
                        id="noteTitle" name="title" type="text"
                        className="form-control"
                        value={noteForm.title}
                        onChange={handleNoteChange}
                        placeholder="e.g. Week 1: Introduction to HTML"
                        required
                      />
                    </div>

                    {/* ── Details ── */}
                    <div className="lesson-form-section">
                      <span className="lesson-form-section__label">Details</span>
                    </div>

                    <div className="lesson-form-row mb-3">
                      <div>
                        <label className="form-label" htmlFor="noteDuration">Duration (minutes)</label>
                        <input
                          id="noteDuration" name="duration" type="number" min="1"
                          className="form-control"
                          value={noteForm.duration}
                          onChange={handleNoteChange}
                          placeholder="e.g. 45"
                        />
                      </div>
                      <div>
                        <label className="form-label" htmlFor="noteDifficulty">Difficulty</label>
                        <select
                          id="noteDifficulty" name="difficulty"
                          className="form-select"
                          value={noteForm.difficulty}
                          onChange={handleNoteChange}
                        >
                          <option>Beginner</option>
                          <option>Intermediate</option>
                          <option>Advanced</option>
                        </select>
                      </div>
                    </div>

                    <div className="mb-3">
                      <label className="form-label" htmlFor="noteVideo">Video Link <span className="text-muted">(YouTube, optional)</span></label>
                      <input
                        id="noteVideo" name="videoUrl" type="url"
                        className="form-control"
                        value={noteForm.videoUrl}
                        onChange={handleNoteChange}
                        placeholder="https://youtube.com/watch?v=..."
                      />
                    </div>

                    {/* ── Content ── */}
                    <div className="lesson-form-section">
                      <span className="lesson-form-section__label">Content</span>
                    </div>

                    <div className="mb-3">
                      <label className="form-label" htmlFor="noteObjectives">Learning Objectives</label>
                      <textarea
                        id="noteObjectives" name="objectives"
                        className="form-control"
                        rows="3"
                        value={noteForm.objectives}
                        onChange={handleNoteChange}
                        placeholder="By the end of this lesson, students will be able to..."
                      />
                    </div>

                    <div className="mb-3">
                      <label className="form-label" htmlFor="noteContent">Lesson Notes <span className="text-muted">(optional)</span></label>
                      <textarea
                        id="noteContent" name="content"
                        className="form-control teacher-notes-textarea"
                        rows="4"
                        value={noteForm.content}
                        onChange={handleNoteChange}
                        placeholder="Key concepts, explanations, and study points..."
                      />
                    </div>

                    <div className="mb-4">
                      <label className="form-label" htmlFor="notePdf">Upload PDF <span className="text-muted">(optional, max 20 MB)</span></label>
                      <input
                        id="notePdf" ref={fileInputRef}
                        type="file" accept=".pdf"
                        className="form-control"
                        onChange={(e) => setPdfFile(e.target.files[0] || null)}
                      />
                      {pdfFile && (
                        <div className="text-muted small mt-1">📎 {pdfFile.name}</div>
                      )}
                    </div>

                    {notesError && (
                      <div className="alert alert-danger py-2 small mb-3">{notesError}</div>
                    )}
                    {notesMessage && (
                      <div className="alert alert-success py-2 small mb-3">{notesMessage}</div>
                    )}

                    <button
                      type="submit"
                      className="btn btn-primary w-100"
                      disabled={notesSubmitting || !courses.length}
                    >
                      {notesSubmitting ? "Publishing..." : "Publish Lesson"}
                    </button>
                  </form>
                </div>
              </div>

              {/* ── LIBRARY ── */}
              <div className="teacher-notes-list">
                <div className="teacher-notes-list__header">
                  <h5 className="mb-0">Lessons Library</h5>
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
                  <div className="teacher-notes-loading">Loading lessons...</div>
                ) : notes.length ? (
                  <div className="teacher-notes-cards">
                    {notes.map((note) => (
                      <article className="teacher-note-card" key={note.id}>
                        <div className="teacher-note-card__header">
                          <div className="teacher-note-card__title-row">
                            {note.lesson_number != null && (
                              <span className="lesson-week-badge">Week {note.lesson_number}</span>
                            )}
                            <h6 className="mb-0">{note.title}</h6>
                          </div>
                          <span className="teacher-note-card__date">
                            {new Date(note.created_at).toLocaleDateString()}
                          </span>
                        </div>

                        {note.topic && (
                          <div className="lesson-card-topic">📌 {note.topic}</div>
                        )}

                        <div className="lesson-card-meta">
                          {note.difficulty && (
                            <span className={`lesson-difficulty-badge lesson-difficulty-badge--${note.difficulty.toLowerCase()}`}>
                              {note.difficulty}
                            </span>
                          )}
                          {note.duration && (
                            <span className="lesson-duration-badge">⏱ {note.duration} min</span>
                          )}
                        </div>

                        {note.objectives && (
                          <p className="lesson-card-objectives">
                            {note.objectives.slice(0, 120)}{note.objectives.length > 120 ? "..." : ""}
                          </p>
                        )}

                        <div className="lesson-card-links">
                          {note.file_url && (
                            <>
                              <a href={note.file_url} target="_blank" rel="noopener noreferrer" className="lesson-card-link lesson-card-link--pdf">
                                📄 View PDF
                              </a>
                              <button
                                type="button"
                                className="lesson-card-link lesson-card-link--delete"
                                onClick={() => handleDeletePdf(note.id)}
                                disabled={deletingNoteId === note.id}
                              >
                                {deletingNoteId === note.id ? "Deleting..." : "Delete PDF"}
                              </button>
                            </>
                          )}
                          {note.video_url && (
                            <a href={note.video_url} target="_blank" rel="noopener noreferrer" className="lesson-card-link lesson-card-link--video">
                              🎥 Watch Video
                            </a>
                          )}
                        </div>
                      </article>
                    ))}
                  </div>
                ) : (
                  <div className="teacher-notes-empty">
                    No lessons yet for this course.
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
