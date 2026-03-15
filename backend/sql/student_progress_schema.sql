-- Student Progress Tracking schema + migration helpers (MySQL)
-- Safe for college project demos. Review before running in production.

-- 1) If an older coding-progress table used the name `user_progress`,
-- rename it to avoid conflict with lesson progress tracking.
-- Run only when that table exists.
-- RENAME TABLE user_progress TO problem_progress;

-- 2) Create lesson progress table required by project brief.
CREATE TABLE IF NOT EXISTS user_progress (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  course_id INT NOT NULL,
  lesson_id INT NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT TRUE,
  completed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_user_progress_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_user_progress_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  CONSTRAINT fk_user_progress_lesson FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
  UNIQUE KEY uq_user_course_lesson (user_id, course_id, lesson_id)
);

-- 2b) Quiz attempts table for analytics-friendly score tracking.
CREATE TABLE IF NOT EXISTS quiz_attempts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  quiz_id INT NOT NULL,
  score INT NOT NULL,
  total_questions INT NOT NULL,
  attempted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_quiz_attempts_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_quiz_attempts_quiz FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);

-- 3) Optional one-time migration from old `lesson_progress` shape
-- (when old table has string-based course column).
-- INSERT INTO user_progress (user_id, course_id, lesson_id, completed, completed_at)
-- SELECT lp.user_id,
--        CAST(lp.course AS UNSIGNED),
--        lp.lesson_id,
--        lp.completed,
--        COALESCE(lp.completed_at, CURRENT_TIMESTAMP)
-- FROM lesson_progress lp
-- WHERE lp.completed = TRUE
--   AND lp.course REGEXP '^[0-9]+$'
-- ON DUPLICATE KEY UPDATE
--   completed = VALUES(completed),
--   completed_at = VALUES(completed_at);

-- API support query: upsert lesson completion
-- INSERT INTO user_progress (user_id, course_id, lesson_id, completed, completed_at)
-- VALUES (?, ?, ?, TRUE, NOW())
-- ON DUPLICATE KEY UPDATE completed = TRUE, completed_at = NOW();

-- API support query: fetch course progress summary
-- SELECT
--   COUNT(*) AS completed_lessons,
--   (SELECT COUNT(*) FROM lessons l WHERE l.course_id = ?) AS total_lessons
-- FROM user_progress up
-- WHERE up.user_id = ?
--   AND up.course_id = ?
--   AND up.completed = TRUE;

-- API support query: insert a quiz attempt
-- INSERT INTO quiz_attempts (user_id, quiz_id, score, total_questions, attempted_at)
-- VALUES (?, ?, ?, ?, NOW());

-- API support query: instructor summary analytics by course
-- SELECT
--   (SELECT COUNT(*) FROM enrollments e WHERE e.course_id = :course_id) AS students_enrolled,
--   COALESCE(
--     AVG((qa.score / NULLIF(qa.total_questions, 0)) * 100),
--     0
--   ) AS average_quiz_score
-- FROM quiz_attempts qa
-- JOIN quizzes q ON q.id = qa.quiz_id
-- WHERE q.course_id = :course_id;
