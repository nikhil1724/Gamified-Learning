import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import MarkdownLessonViewer from '../components/MarkdownLessonViewer';
import CodePlayground from '../components/CodePlayground';
import ProgressBar from '../components/ProgressBar';
import PageTransition from '../components/PageTransition';
import api from '../services/api';
import './LessonPage.css';

// Course metadata
const courseData = {
  python: {
    name: 'Python Programming',
    icon: '🐍',
    color: '#3776ab',
    lessons: [
      { id: 1, title: 'Introduction to Python', duration: '15 min' },
      { id: 2, title: 'Control Flow', duration: '20 min' },
      { id: 3, title: 'Functions and Modules', duration: '25 min' },
    ]
  },
  java: {
    name: 'Java Programming',
    icon: '☕',
    color: '#007396',
    lessons: [
      { id: 1, title: 'Introduction to Java', duration: '18 min' },
      { id: 2, title: 'Control Flow in Java', duration: '22 min' },
    ]
  }
};

const LessonPage = () => {
  const { course, lesson } = useParams();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentCourse, setCurrentCourse] = useState(null);
  const [currentLesson, setCurrentLesson] = useState(null);
  const [completedLessons, setCompletedLessons] = useState([]);
  const [isCompleted, setIsCompleted] = useState(false);
  const [showPlayground, setShowPlayground] = useState(false);

  // Fetch completed lessons
  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const response = await api.get(`/api/lesson-progress/${course}`);
        setCompletedLessons(response.data.completed_lessons || []);
        setIsCompleted(response.data.completed_lessons?.includes(parseInt(lesson)));
      } catch (error) {
        console.error('Error fetching progress:', error);
      }
    };

    if (course) {
      fetchProgress();
    }
  }, [course, lesson]);

  useEffect(() => {
    const courseInfo = courseData[course?.toLowerCase()];
    if (courseInfo) {
      setCurrentCourse(courseInfo);
      const lessonInfo = courseInfo.lessons.find(l => l.id === parseInt(lesson));
      setCurrentLesson(lessonInfo);
    }
  }, [course, lesson]);

  const handleMarkComplete = async () => {
    try {
      await api.post(`/api/lesson-progress/${course}/${lesson}`);
      setIsCompleted(true);
      setCompletedLessons([...completedLessons, parseInt(lesson)]);
    } catch (error) {
      console.error('Error marking lesson complete:', error);
    }
  };

  const handleLessonChange = (lessonId) => {
    navigate(`/course/${course}/${lessonId}`);
  };

  const handlePrevious = () => {
    const prevLesson = parseInt(lesson) - 1;
    if (prevLesson >= 1) {
      navigate(`/course/${course}/${prevLesson}`);
    }
  };

  const handleNext = () => {
    const nextLesson = parseInt(lesson) + 1;
    const totalLessons = currentCourse?.lessons.length || 0;
    if (nextLesson <= totalLessons) {
      navigate(`/course/${course}/${nextLesson}`);
    }
  };

  const handleStartQuiz = () => {
    navigate(`/quiz?course=${course}`);
  };

  if (!currentCourse || !currentLesson) {
    return (
      <PageTransition>
        <div className="lesson-page">
          <div className="error-container">
            <i className="bi bi-exclamation-circle"></i>
            <h2>Course or Lesson Not Found</h2>
            <p>The requested course or lesson could not be found.</p>
            <Link to="/learn" className="btn btn-primary">
              <i className="bi bi-arrow-left me-2"></i>
              Back to Courses
            </Link>
          </div>
        </div>
      </PageTransition>
    );
  }

  const currentLessonIndex = currentCourse.lessons.findIndex(l => l.id === parseInt(lesson));
  const hasPrevious = currentLessonIndex > 0;
  const hasNext = currentLessonIndex < currentCourse.lessons.length - 1;

  return (
    <PageTransition>
      <div className="lesson-page">
        {/* Sidebar Toggle Button (Mobile) */}
        <button 
          className="sidebar-toggle"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle sidebar"
        >
          <i className={`bi bi-${sidebarOpen ? 'x' : 'list'}`}></i>
        </button>

        {/* Sidebar */}
        <aside className={`lesson-sidebar ${sidebarOpen ? 'open' : ''}`}>
          <div className="sidebar-header">
            <div className="course-badge" style={{ background: currentCourse.color }}>
              <span className="course-icon">{currentCourse.icon}</span>
            </div>
            <div className="course-info">
              <h3>{currentCourse.name}</h3>
              <p className="lesson-count">{currentCourse.lessons.length} Lessons</p>
            </div>
          </div>

          <div className="lessons-list">
            {currentCourse.lessons.map((lessonItem, index) => (
              <div
                key={lessonItem.id}
                className={`lesson-item ${lessonItem.id === parseInt(lesson) ? 'active' : ''} ${completedLessons.includes(lessonItem.id) ? 'completed' : ''}`}
                onClick={() => handleLessonChange(lessonItem.id)}
              >
                <div className="lesson-marker">
                  {completedLessons.includes(lessonItem.id) ? (
                    <i className="bi bi-check-circle-fill"></i>
                  ) : lessonItem.id === parseInt(lesson) ? (
                    <i className="bi bi-play-circle-fill"></i>
                  ) : (
                    <span className="lesson-number">{index + 1}</span>
                  )}
                </div>
                <div className="lesson-details">
                  <h4>{lessonItem.title}</h4>
                  <span className="lesson-duration">
                    <i className="bi bi-clock me-1"></i>
                    {lessonItem.duration}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="sidebar-footer">
            <Link to="/learn" className="back-to-courses-btn">
              <i className="bi bi-grid-3x3-gap me-2"></i>
              All Courses
            </Link>
          </div>
        </aside>

        {/* Main Content */}
        <main className="lesson-content">
          {/* Breadcrumb */}
          <div className="breadcrumb-nav">
            <Link to="/learn">Courses</Link>
            <i className="bi bi-chevron-right"></i>
            <span>{currentCourse.name}</span>
            <i className="bi bi-chevron-right"></i>
            <span className="current">Lesson {lesson}</span>
          </div>

          {/* Lesson Header */}
          <div className="lesson-header">
            <div className="lesson-title-section">
              <span className="lesson-badge">Lesson {lesson}</span>
              <h1>{currentLesson.title}</h1>
              <div className="lesson-meta">
                <span className="meta-item">
                  <i className="bi bi-clock"></i>
                  {currentLesson.duration}
                </span>
                <span className="meta-item">
                  <i className="bi bi-book"></i>
                  {currentCourse.name}
                </span>
              </div>
            </div>
          </div>

          {/* Markdown Content */}
          <div className="lesson-body">
            <MarkdownLessonViewer course={course} lesson={lesson} />
          </div>

          {/* Code Playground */}
          {showPlayground && (
            <div style={{ marginTop: '30px' }}>
              <CodePlayground 
                language={course === 'python' ? 'python' : course === 'java' ? 'java' : 'javascript'}
              />
            </div>
          )}

          {/* Lesson Actions */}
          <div className="lesson-actions">
            <hr className="mb-4" />
            
            {/* Completion and Playground Buttons */}
            <div style={{ display: 'flex', gap: '15px', marginBottom: '30px', flexWrap: 'wrap' }}>
              <button 
                className={`btn ${isCompleted ? 'btn-success' : 'btn-outline-success'}`}
                onClick={handleMarkComplete}
                style={{ flex: '1', minWidth: '200px' }}
              >
                {isCompleted ? (
                  <>
                    <i className="bi bi-check-circle-fill me-2"></i>
                    Lesson Completed
                  </>
                ) : (
                  <>
                    <i className="bi bi-circle me-2"></i>
                    Mark as Complete
                  </>
                )}
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => setShowPlayground(!showPlayground)}
                style={{ flex: '1', minWidth: '200px' }}
              >
                <i className={`bi bi-code-slash me-2`}></i>
                {showPlayground ? 'Hide' : 'Try'} Code Playground
              </button>
            </div>

            {/* Quiz Section */}
            <div className="quiz-section">
              <div className="quiz-info">
                <i className="bi bi-trophy-fill"></i>
                <div>
                  <h3>Test Your Knowledge</h3>
                  <p>Complete a quiz to reinforce what you've learned in this lesson.</p>
                </div>
              </div>
              <button className="btn btn-quiz" onClick={handleStartQuiz}>
                <i className="bi bi-play-fill me-2"></i>
                Start Quiz
              </button>
            </div>
          </div>

          {/* Navigation Buttons */}
          <div className="lesson-navigation">
            <button 
              className="nav-btn prev-btn"
              onClick={handlePrevious}
              disabled={!hasPrevious}
            >
              <i className="bi bi-chevron-left me-2"></i>
              Previous Lesson
            </button>
            <button 
              className="nav-btn next-btn"
              onClick={handleNext}
              disabled={!hasNext}
            >
              Next Lesson
              <i className="bi bi-chevron-right ms-2"></i>
            </button>
          </div>
        </main>
      </div>
    </PageTransition>
  );
};

export default LessonPage;
