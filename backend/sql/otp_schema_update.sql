-- Email OTP verification schema update for existing projects.
-- Run this once against the gamified_learning database.

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS otp_code VARCHAR(10) NULL,
    ADD COLUMN IF NOT EXISTS otp_expiry DATETIME NULL,
    ADD COLUMN IF NOT EXISTS otp_resend_count INT NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS otp_resend_window_start DATETIME NULL;

-- Backfill existing data so old verified users remain verified.
UPDATE users
SET is_verified = email_verified
WHERE is_verified <> email_verified;

-- Optional index to speed up OTP verification queries.
CREATE INDEX idx_users_email_otp ON users (email, otp_code);
