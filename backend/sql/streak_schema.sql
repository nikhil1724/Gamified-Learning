ALTER TABLE users
  ADD COLUMN streak_count INT NOT NULL DEFAULT 0,
  ADD COLUMN longest_streak INT NOT NULL DEFAULT 0,
  ADD COLUMN last_active_date DATE NULL;

UPDATE users
SET
  streak_count = COALESCE(daily_streak, 0),
  longest_streak = GREATEST(COALESCE(longest_streak, 0), COALESCE(daily_streak, 0))
WHERE streak_count = 0;