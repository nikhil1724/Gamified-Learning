"""
Database Migration: Add Email Verification Columns
Run this script to add email_verified, verification_token, and verification_token_expiry columns to the users table.
"""
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate():
    # Get database connection details from environment
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_name = os.getenv('DB_NAME', 'gamified_learning')
    
    try:
        # Connect to database
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("SHOW COLUMNS FROM users LIKE 'email_verified'")
        if cursor.fetchone():
            print("✅ Columns already exist. No migration needed.")
            cursor.close()
            conn.close()
            return
        
        print("🔄 Adding email verification columns to users table...")
        
        # Add email_verified column
        cursor.execute(
            "ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE NOT NULL"
        )
        print("  ✅ Added email_verified column")
        
        # Add verification_token column
        cursor.execute(
            "ALTER TABLE users ADD COLUMN verification_token VARCHAR(255) NULL"
        )
        print("  ✅ Added verification_token column")
        
        # Add verification_token_expiry column
        cursor.execute(
            "ALTER TABLE users ADD COLUMN verification_token_expiry DATETIME NULL"
        )
        print("  ✅ Added verification_token_expiry column")
        
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        print("   You can now register new users with email verification.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    migrate()
