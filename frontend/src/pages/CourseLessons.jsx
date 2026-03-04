import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import PageTransition from '../components/PageTransition';
import ProgressBar from '../components/ProgressBar';
import api from '../services/api';
import './CourseLessons.css';

// Course metadata (same as LessonPage)
const courseData = {
  python: {
    name: 'Python Programming',
    icon: '🐍',
    color: '#3776ab',
    description: 'Master Python from basics to advanced concepts with hands-on lessons and practice.',
    lessons: [
      { 
        id: 1, 
        title: 'Introduction to Python', 
        duration: '15 min',
        description: 'Learn Python basics, variables, data types, and your first program',
        topics: ['Variables', 'Data Types', 'Print', 'Operators']
      },
      { 
        id: 2, 
        title: 'Control Flow', 
        duration: '20 min',
        description: 'Master if-else statements, loops, and control flow in Python',
        topics: ['If-Else', 'For Loops', 'While Loops', 'Break/Continue']
      },
      { 
        id: 3, 
        title: 'Functions and Modules', 
        duration: '25 min',
        description: 'Create reusable functions, work with modules, and organize code',
        topics: ['Functions', 'Parameters', 'Return', 'Modules', 'Lambda']
      },
    ]
  },
  java: {
    name: 'Java Programming',
    icon: '☕',
    color: '#007396',
    description: 'Learn Java fundamentals, OOP concepts, and build robust applications.',
    lessons: [
      { 
        id: 1, 
        title: 'Introduction to Java', 
        duration: '18 min',
        description: 'Understand Java basics, syntax, variables, and data types',
        topics: ['Syntax', 'Variables', 'Data Types', 'Operators', 'Scanner']
      },
      { 
        id: 2, 
        title: 'Control Flow in Java', 
        duration: '22 min',
        description: 'Learn decision making with if-else, switch, and loops',
        topics: ['If-Else', 'Switch', 'Loops', 'Break/Continue', 'Patterns']
      },
    ]
  }
};

const CourseLessons = () => {
  const { course } = useParams();
  const courseInfo = courseData[course?.toLowerCase()];
  const [completedLessons, setCompletedLessons] = useState([]);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const response = await api.get(`/api/lesson-progress/${course}`);
        setCompletedLessons(response.data.completed_lessons || []);
      } catch (error) {
        console.error('Error fetching progress:', error);
      }
    };

    if (course) {
      fetchProgress();
    }
  }, [course]);

  if (!courseInfo) {
    return (
      <PageTransition>
        <div className="course-lessons-page">
          <div className="error-container">
            <i className="bi bi-exclamation-triangle"></i>
            <h2>Course Not Found</h2>
            <p>The requested course could not be found.</p>
            <Link to="/learn" className="btn btn-primary">
              <i className="bi bi-arrow-left me-2"></i>
              Back to Courses
            </Link>
          </div>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="course-lessons-page">
        {/* Course Header */}
        <div className="course-header-section" style={{ background: `linear-gradient(135deg, ${courseInfo.color} 0%, ${courseInfo.color}dd 100%)` }}>
          <div className="container">
            <Link to="/learn" className="back-link">
              <i className="bi bi-arrow-left me-2"></i>
              All Courses
            </Link>
            <div className="course-header-content">
              <div className="course-icon-hero">{courseInfo.icon}</div>
              <div className="course-details">
                <h1>{courseInfo.name}</h1>
                <p className="course-description">{courseInfo.description}</p>
                <div className="course-stats">
                  <span className="stat">
                    <i className="bi bi-journal-text"></i>
                    {courseInfo.lessons.length} Lessons
                  </span>
                  <span className="stat">
                    <i className="bi bi-clock"></i>
                    {courseInfo.lessons.reduce((total, lesson) => {
                      const mins = parseInt(lesson.duration);
                      return total + mins;
                    }, 0)} minutes total
                  </span>
                  <span className="stat">
                    <i className="bi bi-award"></i>
                    Certificate included
                  </span>
                </div>
                
                {/* Progress Bar */}
                <div style={{ marginTop: '20px' }}>
                  <ProgressBar 
                    current={completedLessons.length} 
                    total={courseInfo.lessons.length}
                    size="large"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Lessons List */}
        <div className="container">
          <div className="lessons-section">
            <div className="section-header">
              <h2>Course Content</h2>
              <p>Follow the lessons in order for the best learning experience</p>
            </div>

            <div className="lessons-list-grid">
              {courseInfo.lessons.map((lesson, index) => (
                <Link 
                  key={lesson.id}
                  to={`/course/${course}/${lesson.id}`}
                  className={`lesson-card ${completedLessons.includes(lesson.id) ? 'completed' : ''}`}
                >
                  <div className="lesson-number-badge">
                    {completedLessons.includes(lesson.id) ? (
                      <i className="bi bi-check-circle-fill" style={{ fontSize: '24px', color: '#22c55e' }}></i>
                    ) : (
                      <span className="lesson-number">{index + 1}</span>
                    )}
                  </div>

                  <div className="lesson-content">
                    <div className="lesson-header-row">
                      <h3>{lesson.title}</h3>
                      <span className="lesson-duration">
                        <i className="bi bi-clock"></i>
                        {lesson.duration}
                      </span>
                    </div>

                    <p className="lesson-desc">{lesson.description}</p>

                    <div className="lesson-topics">
                      {lesson.topics.map((topic, idx) => (
                        <span key={idx} className="topic-pill">{topic}</span>
                      ))}
                    </div>
                  </div>

                  <div className="lesson-action">
                    {completedLessons.includes(lesson.id) ? (
                      <>
                        <i className="bi bi-arrow-repeat"></i>
                        <span>Review</span>
                      </>
                    ) : (
                      <>
                        <i className="bi bi-play-circle-fill"></i>
                        <span>Start</span>
                      </>
                    )}
                  </div>
                </Link>
              ))}
            </div>

            {/* Call to Action */}
            <div className="cta-section">
              <div className="cta-card">
                <div className="cta-icon">
                  <i className="bi bi-rocket-takeoff-fill"></i>
                </div>
                <div className="cta-content">
                  <h3>Ready to begin your journey?</h3>
                  <p>Start with the first lesson and progress at your own pace.</p>
                </div>
                <Link 
                  to={`/course/${course}/1`} 
                  className="btn btn-primary-large"
                >
                  <i className="bi bi-play-fill me-2"></i>
                  Start First Lesson
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default CourseLessons;
