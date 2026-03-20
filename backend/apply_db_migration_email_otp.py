"""Add OTP verification columns to users table.

Usage:
  python apply_db_migration_email_otp.py
"""

from app import create_app
from database import db


def _column_exists(table_name: str, column_name: str) -> bool:
	result = db.session.execute(
		db.text(
			"""
			SELECT COUNT(*)
			FROM information_schema.COLUMNS
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = :table_name
			  AND COLUMN_NAME = :column_name
			"""
		),
		{"table_name": table_name, "column_name": column_name},
	)
	return bool(result.scalar())


def apply_migration() -> None:
	app = create_app()
	with app.app_context():
		statements = []

		if not _column_exists("users", "is_verified"):
			statements.append(
				"ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT FALSE"
			)

		if not _column_exists("users", "otp_code"):
			statements.append(
				"ALTER TABLE users ADD COLUMN otp_code VARCHAR(255) NULL"
			)

		if not _column_exists("users", "otp_expiry"):
			statements.append(
				"ALTER TABLE users ADD COLUMN otp_expiry DATETIME NULL"
			)

		for sql in statements:
			db.session.execute(db.text(sql))

		# Keep pre-existing accounts usable after introducing verification columns.
		db.session.execute(
			db.text(
				"""
				UPDATE users
				SET is_verified = TRUE
				WHERE is_verified = FALSE
				  AND (otp_code IS NULL OR otp_code = '')
				"""
			)
		)

		db.session.commit()
		print("OTP migration completed.")
		if statements:
			print(f"Applied {len(statements)} statement(s).")
		else:
			print("No changes required.")


if __name__ == "__main__":
	apply_migration()
