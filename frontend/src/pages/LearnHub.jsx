import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
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
    category: 'Programming',
    xpReward: 220,
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
    category: 'Programming',
    xpReward: 200,
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
    category: 'Web Development',
    xpReward: 260,
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
    category: 'Data Structures',
    xpReward: 320,
    topics: ['Pointers', 'STL', 'Templates', 'Memory', 'Performance'],
    students: 0,
    rating: 0,
    comingSoon: true
  }
];

const LearnHub = () => {
  const [filter, setFilter] = useState('all');
  const [category, setCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [courseProgress, setCourseProgress] = useState({});

  useEffect(() => {
    const fetchAllProgress = async () => {
      try {
        const response = await api.get('/lesson-progress');
        // Backend returns { progress: { "courseId": [lessonIds] } } — use directly
        setCourseProgress(response.data.progress || {});
      } catch (error) {
        console.error('Error fetching progress:', error);
      }
    };

    fetchAllProgress();
  }, []);

  const filteredCourses = courses.filter(course => {
    const matchesFilter = filter === 'all' || course.level.toLowerCase() === filter;
    const matchesCategory = category === 'all' || course.category === category;
    const matchesSearch = course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         course.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesCategory && matchesSearch;
  });

  return (
    <PageTransition>
      <div className="learn-hub">
        {/* Hero Section */}
        <section className="learn-hero">
          <div className="learn-hub__container">
            <motion.div
              className="learn-hero-content"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h1 className="learn-hero-title">
                Level Up Your <span className="learn-highlight">Coding Skills</span>
              </h1>
              <p className="learn-hero-subtitle">
                Master programming with interactive lessons, hands-on practice, and real-world projects from industry experts.
              </p>
              <div className="learn-hero-buttons">
                <Link to="/course/python/lessons" className="btn btn-hero-primary">
                  Start Learning
                </Link>
                <button className="btn btn-hero-secondary" onClick={() => document.querySelector('.courses-section').scrollIntoView({ behavior: 'smooth' })}>
                  Explore Courses
                </button>
              </div>
            </motion.div>
          </div>
        </section>



        {/* Search and Filters */}
        <section className="learn-controls-section">
          <div className="learn-hub__container">
            <div className="learn-controls">
              <div className="search-bar">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor">
                  <circle cx="9" cy="9" r="7"></circle>
                  <path d="m14 14 4 4"></path>
                </svg>
                <input
                  type="text"
                  placeholder="Search courses by name or topic..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
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

              <div className="search-bar" style={{ maxWidth: 240 }}>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="search-input"
                >
                  <option value="all">All Categories</option>
                  <option value="Programming">Programming</option>
                  <option value="Web Development">Web Development</option>
                  <option value="Data Structures">Data Structures</option>
                </select>
              </div>
            </div>
          </div>
        </section>

        {/* Courses Grid */}
        <section className="courses-section" ref={(el) => { if (el) window.coursesSection = el; }}>
          <div className="learn-hub__container">
            <div className="courses-header">
              <h2 className="courses-title">
                {filter === 'all' ? 'All Courses' : `${filter.charAt(0).toUpperCase() + filter.slice(1)} Courses`}
              </h2>
              <p className="courses-subtitle">
                {filteredCourses.length} course{filteredCourses.length !== 1 ? 's' : ''} available
              </p>
            </div>

            {filteredCourses.length > 0 ? (
              <div className="courses-grid">
                {filteredCourses.map((course, index) => (
                  (() => {
                    const completedCount = courseProgress[course.id]?.length || 0;
                    const hasProgress = completedCount > 0;
                    const percent = Math.min(100, Math.round((completedCount / Math.max(1, course.lessons)) * 100));
                    return (
                  <motion.div
                    key={course.id}
                    className="course-card"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                  >
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

                      <div className="meta-row" style={{ marginBottom: 10 }}>
                        <span>
                          <span className="meta-icon">🏷️</span>
                          {course.category}
                        </span>
                        <span>
                          <span className="meta-icon">⚡</span>
                          +{course.xpReward} XP
                        </span>
                      </div>

                      <p className="course-description">{course.description}</p>

                      <div className="course-meta">
                        <div className="meta-row">
                          <span>
                            <span className="meta-icon">📖</span>
                            {course.lessons} lessons
                          </span>
                          <span>
                            <span className="meta-icon">⏱️</span>
                            {course.duration}
                          </span>
                        </div>
                        {!course.comingSoon && (
                          <div className="meta-row">
                            <span>
                              <span className="meta-icon">👥</span>
                              {course.students.toLocaleString()} students
                            </span>
                            <span>
                              <span className="meta-icon">⭐</span>
                              {course.rating} rating
                            </span>
                          </div>
                        )}
                      </div>

                      <div className="course-topics">
                        {course.topics.slice(0, 3).map((topic, i) => (
                          <span key={i} className="topic-tag">{topic}</span>
                        ))}
                        {course.topics.length > 3 && (
                          <span className="topic-tag more">+{course.topics.length - 3} more</span>
                        )}
                      </div>

                      {!course.comingSoon && hasProgress && (
                        <div className="course-progress-wrapper">
                          <ProgressBar 
                            current={completedCount}
                            total={course.lessons}
                            size="small"
                          />
                          <p className="mt-2 mb-0 text-muted" style={{ fontSize: 12 }}>
                            {percent}% completed
                          </p>
                        </div>
                      )}
                    </div>

                    <div className="course-footer">
                      {course.comingSoon ? (
                        <button className="btn btn-course disabled" disabled>
                          Coming Soon
                        </button>
                      ) : (
                        <Link 
                          to={`/course/${course.id}/lessons`} 
                          className="btn btn-course"
                        >
                          {hasProgress ? 'Continue' : 'Start'}
                        </Link>
                      )}
                    </div>
                  </motion.div>
                    );
                  })()
                ))}
              </div>
            ) : (
              <div className="no-courses">
                <p>No courses found matching your criteria.</p>
              </div>
            )}
          </div>
        </section>
      </div>
    </PageTransition>
  );
};

export default LearnHub;
