import pymysql

conn = pymysql.connect(
    host="localhost",
    user="gamified_user",
    password="gamified_pass",
    database="gamified_learning",
)

try:
    with conn.cursor() as cur:
        def ensure_column(name, ddl):
            cur.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = %s
                """,
                ("gamified_learning", name),
            )
            exists = cur.fetchone()[0] > 0
            if not exists:
                cur.execute(f"ALTER TABLE users ADD COLUMN {ddl}")

        ensure_column("is_verified", "is_verified BOOLEAN NOT NULL DEFAULT FALSE")
        ensure_column("otp_code", "otp_code VARCHAR(10) NULL")
        ensure_column("otp_expiry", "otp_expiry DATETIME NULL")
        ensure_column("otp_resend_count", "otp_resend_count INT NOT NULL DEFAULT 0")
        ensure_column("otp_resend_window_start", "otp_resend_window_start DATETIME NULL")
        cur.execute("UPDATE users SET is_verified = email_verified WHERE is_verified != email_verified")
    conn.commit()
    print("OTP schema updated successfully")
finally:
    conn.close()
