ALTER TABLE badges
  ADD COLUMN icon VARCHAR(32) NULL;

ALTER TABLE badges
  ADD CONSTRAINT uq_badges_name UNIQUE (name);

ALTER TABLE user_badges
  ADD CONSTRAINT uq_user_badges_user_badge UNIQUE (user_id, badge_id);

CREATE INDEX idx_user_badges_user_earned
  ON user_badges(user_id, earned_at);