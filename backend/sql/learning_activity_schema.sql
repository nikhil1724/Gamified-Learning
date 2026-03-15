-- Learning streak activity table
CREATE TABLE IF NOT EXISTS learning_activity (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  activity_date DATE NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_learning_activity_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE KEY uq_learning_activity_user_date (user_id, activity_date)
);

-- Streak-support query: recent activity dates for one user
-- SELECT activity_date
-- FROM learning_activity
-- WHERE user_id = :user_id
-- ORDER BY activity_date DESC;
