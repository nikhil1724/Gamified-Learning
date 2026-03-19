-- Demo seed data for viva/demo showcase
-- Run after schema creation and before frontend demo

SET NAMES utf8mb4;

INSERT IGNORE INTO users (id, name, email, password_hash, role, is_approved, level, xp_points, coins, daily_streak)
VALUES
  (1, 'Admin User', 'admin@lms.com', 'demo-hash', 'admin', 1, 6, 1800, 450, 7),
  (2, 'John Parker', 'john@lms.com', 'demo-hash', 'instructor', 1, 4, 1200, 220, 3),
  (3, 'Priya Sharma', 'priya@lms.com', 'demo-hash', 'instructor', 1, 5, 1500, 300, 5),
  (4, 'Rahul Verma', 'rahul@student.com', 'demo-hash', 'student', 1, 2, 420, 90, 2),
  (5, 'Anita Nair', 'anita@student.com', 'demo-hash', 'student', 1, 3, 680, 130, 4);

INSERT IGNORE INTO courses (id, title, description, teacher_id)
VALUES
  (1, 'Python Basics', 'Foundations of Python programming.', 3),
  (2, 'Java Programming', 'Object-oriented Java development.', 2),
  (3, 'Data Structures', 'Core data structures and algorithms.', 2),
  (4, 'Web Development', 'Frontend and backend web essentials.', 3),
  (5, 'DBMS', 'Relational database and SQL fundamentals.', 2);

-- Problem inventory target: 20 (Easy 10, Medium 7, Hard 3)
-- Use backend/seed_data.py for complete generated problem/test-case population.

INSERT IGNORE INTO quizzes (id, title, topic, difficulty, course_id)
VALUES
  (1, 'Python Basics Quiz 1 (XP 50)', 'Python', 'Easy', 1),
  (2, 'Python Basics Quiz 2 (XP 75)', 'Python', 'Easy', 1),
  (3, 'Python Basics Quiz 3 (XP 100)', 'Python', 'Medium', 1),
  (4, 'Java Mastery Quiz 1 (XP 50)', 'Java', 'Easy', 2),
  (5, 'Java Mastery Quiz 2 (XP 75)', 'Java', 'Medium', 2),
  (6, 'Java Mastery Quiz 3 (XP 100)', 'Java', 'Medium', 2),
  (7, 'DSA Quiz 1 (XP 75)', 'DSA', 'Medium', 3),
  (8, 'DSA Quiz 2 (XP 100)', 'DSA', 'Medium', 3),
  (9, 'DSA Quiz 3 (XP 150)', 'DSA', 'Hard', 3),
  (10, 'Web Development Quiz 1 (XP 80)', 'Web', 'Medium', 4);

INSERT IGNORE INTO badges (id, name, description, rule_type, rule_value)
VALUES
  (1, 'First Quiz', 'Complete your first quiz.', 'quiz_count', 1),
  (2, '100 XP', 'Reach 100 total XP.', 'xp_points', 100),
  (3, 'Streak 3 Days', 'Maintain a 3-day learning streak.', 'streak_days', 3);
