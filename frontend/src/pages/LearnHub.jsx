import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import PageTransition from '../components/PageTransition';
import ProgressBar from '../components/ProgressBar';
import api from '../services/api';
import './LearnHub.css';

// Course data
const courses = [
  {
    id: 'python',
    name: 'Python Programming',
    description: 'Master Python from basics to advanced concepts. Perfect for beginners and experienced developers.',
    icon: '🐍',
    color: '#3776ab',
    lessons: 3,
    duration: '60 min',
    level: 'Beginner',
    topics: ['Variables', 'Control Flow', 'Functions', 'Modules', 'OOP'],
    students: 1245,
    rating: 4.8
  },
  {
    id: 'java',
    name: 'Java Programming',
    description: 'Learn Java fundamentals, OOP concepts, and build real-world applications.',
    icon: '☕',
    color: '#007396',
    lessons: 2,
    duration: '40 min',
    level: 'Beginner',
    topics: ['Syntax', 'Control Flow', 'OOP', 'Collections', 'Spring'],
    students: 987,
    rating: 4.7
  },
  {
    id: 'javascript',
    name: 'JavaScript Essentials',
    description: 'Master modern JavaScript including ES6+, async programming, and DOM manipulation.',
    icon: '🟨',
    color: '#f7df1e',
    lessons: 0,
    duration: 'Coming Soon',
    level: 'Beginner',
    topics: ['ES6+', 'DOM', 'Async/Await', 'APIs', 'React'],
    students: 0,
    rating: 0,
    comingSoon: true
  },
  {
    id: 'cpp',
    name: 'C++ Fundamentals',
    description: 'Deep dive into C++ with modern features, data structures, and algorithms.',
    icon: '⚙️',
    color: '#00599c',
    lessons: 0,
    duration: 'Coming Soon',
    level: 'Intermediate',
    topics: ['Pointers', 'STL', 'Templates', 'Memory', 'Performance'],
    students: 0,
    rating: 0,
    comingSoon: true
  }
];

const LearnHub = () => {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [courseProgress, setCourseProgress] = useState({});

  useEffect(() => {
    const fetchAllProgress = async () => {
      try {
        const response = await api.get('/api/lesson-progress');
        // Convert array of progress to object keyed by course
        const progressByCourse = {};
        response.data.progress.forEach(item => {
          if (!progressByCourse[item.course]) {
            progressByCourse[item.course] = [];
          }
          progressByCourse[item.course].push(item.lesson_id);
        });
        setCourseProgress(progressByCourse);
      } catch (error) {
        console.error('Error fetching progress:', error);
      }
    };

    fetchAllProgress();
  }, []);

  const filteredCourses = courses.filter(course => {
    const matchesFilter = filter === 'all' || course.level.toLowerCase() === filter;
    const matchesSearch = course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         course.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <PageTransition>
      <div className="learn-hub">
        {/* Hero Section */}
        <div className="learn-hero">
          <div className="learn-hero-content">
            <h1 className="learn-hero-title">
              <span className="learn-gradient-text">Learn to Code</span>
            </h1>
            <p className="learn-hero-subtitle">
              Master programming with our interactive lessons, hands-on practice, and real-world projects.
            </p>
            <div className="learn-hero-stats">
              <div className="learn-stat-item">
                <i className="bi bi-book-fill"></i>
                <div>
                  <strong>5+ Courses</strong>
                  <span>Available</span>
                </div>
              </div>
              <div className="learn-stat-item">
                <i className="bi bi-people-fill"></i>
                <div>
                  <strong>2,200+</strong>
                  <span>Students</span>
                </div>
              </div>
              <div className="learn-stat-item">
                <i className="bi bi-trophy-fill"></i>
                <div>
                  <strong>1,000+</strong>
                  <span>Challenges</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="learn-controls">
          <div className="container">
            <div className="search-bar">
              <i className="bi bi-search"></i>
              <input
                type="text"
                placeholder="Search courses..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <div className="filter-buttons">
              <button
                className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                onClick={() => setFilter('all')}
              >
                All Courses
              </button>
              <button
                className={`filter-btn ${filter === 'beginner' ? 'active' : ''}`}
                onClick={() => setFilter('beginner')}
              >
                Beginner
              </button>
              <button
                className={`filter-btn ${filter === 'intermediate' ? 'active' : ''}`}
                onClick={() => setFilter('intermediate')}
              >
                Intermediate
              </button>
              <button
                className={`filter-btn ${filter === 'advanced' ? 'active' : ''}`}
                onClick={() => setFilter('advanced')}
              >
                Advanced
              </button>
            </div>
          </div>
        </div>

        {/* Courses Grid */}
        <div className="container">
          <div className="courses-grid">
            {filteredCourses.map(course => (
              <div key={course.id} className="course-card">
                <div className="course-header" style={{ background: course.color }}>
                  <div className="course-icon-large">{course.icon}</div>
                  {course.comingSoon && (
                    <div className="coming-soon-badge">Coming Soon</div>
                  )}
                </div>

                <div className="course-body">
                  <div className="course-title-section">
                    <h3>{course.name}</h3>
                    <span className={`level-badge ${course.level.toLowerCase()}`}>
                      {course.level}
                    </span>
                  </div>

                  <p className="course-description">{course.description}</p>

                  <div className="course-meta">
                    <div className="meta-row">
                      <span>
                        <i className="bi bi-journal-text"></i>
                        {course.lessons} lessons
                      </span>
                      <span>
                        <i className="bi bi-clock"></i>
                        {course.duration}
                      </span>
                    </div>
                    {!course.comingSoon && (
                      <div className="meta-row">
                        <span>
                          <i className="bi bi-people"></i>
                          {course.students.toLocaleString()} students
                        </span>
                        <span>
                          <i className="bi bi-star-fill"></i>
                          {course.rating} rating
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="course-topics">
                    {course.topics.slice(0, 3).map((topic, index) => (
                      <span key={index} className="topic-tag">{topic}</span>
                    ))}
                    {course.topics.length > 3 && (
                      <span className="topic-tag more">+{course.topics.length - 3} more</span>
                    )}
                  </div>

                  {/* Progress Bar for started courses */}
                  {!course.comingSoon && courseProgress[course.id] && courseProgress[course.id].length > 0 && (
                    <div style={{ marginTop: '15px' }}>
                      <ProgressBar 
                        current={courseProgress[course.id].length} 
                        total={course.lessons}
                        size="small"
                      />
                    </div>
                  )}
                </div>

                <div className="course-footer">
                  {course.comingSoon ? (
                    <button className="btn-course disabled" disabled>
                      <i className="bi bi-hourglass-split me-2"></i>
                      Coming Soon
                    </button>
                  ) : (
                    <Link 
                      to={`/course/${course.id}/lessons`} 
                      className="btn-course"
                    >
                      <i className={`bi ${courseProgress[course.id]?.length > 0 ? 'bi-arrow-right-circle-fill' : 'bi-play-circle-fill'} me-2`}></i>
                      {courseProgress[course.id]?.length > 0 ? 'Continue Learning' : 'Start Learning'}
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>

          {filteredCourses.length === 0 && (
            <div className="no-results">
              <i className="bi bi-search"></i>
              <h3>No courses found</h3>
              <p>Try adjusting your search or filters</p>
            </div>
          )}
        </div>
      </div>
    </PageTransition>
  );
};

export default LearnHub;
