-- AI-Based Learning Recommendation Queries (MySQL)

-- 1) Topic-level quiz performance by student using quiz_attempts + quizzes.
SELECT
  q.topic,
  ROUND(AVG((qa.score * 100.0) / NULLIF(qa.total_questions, 0)), 2) AS avg_score_pct,
  COUNT(*) AS attempts
FROM quiz_attempts qa
JOIN quizzes q ON q.id = qa.quiz_id
WHERE qa.user_id = :user_id
GROUP BY q.topic
ORDER BY avg_score_pct ASC;

-- 2) Weak topics where average score is below 50%.
SELECT
  q.topic,
  ROUND(AVG((qa.score * 100.0) / NULLIF(qa.total_questions, 0)), 2) AS avg_score_pct
FROM quiz_attempts qa
JOIN quizzes q ON q.id = qa.quiz_id
WHERE qa.user_id = :user_id
GROUP BY q.topic
HAVING avg_score_pct < 50
ORDER BY avg_score_pct ASC;

-- 3) Find courses linked to weak topics (title/description/topic match).
SELECT DISTINCT
  c.id AS course_id,
  c.title
FROM courses c
LEFT JOIN quizzes q ON q.course_id = c.id
WHERE
  c.title LIKE CONCAT('%', :topic, '%')
  OR c.description LIKE CONCAT('%', :topic, '%')
  OR q.topic LIKE CONCAT('%', :topic, '%')
ORDER BY c.created_at DESC
LIMIT 5;

-- 4) Next lesson in started-but-not-completed courses.
SELECT
  l.id AS lesson_id,
  l.course_id,
  l.title
FROM lessons l
LEFT JOIN user_progress up
  ON up.lesson_id = l.id
  AND up.user_id = :user_id
  AND up.completed = TRUE
WHERE l.course_id = :course_id
  AND up.id IS NULL
ORDER BY l.order_index ASC, l.id ASC
LIMIT 1;

-- 5) Beginner courses not started by user.
SELECT c.id AS course_id, c.title
FROM courses c
WHERE c.id NOT IN (
  SELECT DISTINCT course_id
  FROM user_progress
  WHERE user_id = :user_id
)
AND (
  LOWER(c.title) LIKE '%beginner%'
  OR LOWER(c.title) LIKE '%basics%'
  OR LOWER(c.title) LIKE '%intro%'
  OR LOWER(c.title) LIKE '%introduction%'
  OR LOWER(c.title) LIKE '%fundamentals%'
)
ORDER BY c.created_at DESC
LIMIT 5;
