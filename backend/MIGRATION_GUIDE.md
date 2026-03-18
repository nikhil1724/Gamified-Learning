# Full Data Migration Guide
## Local MySQL → Production (Railway)

---

## 📋 Overview

This guide explains how to migrate **all your real data** from your local development database to production (Railway MySQL) in a safe, automated way.

### What Gets Migrated?
- ✅ **Users** (with passwords, XP, levels, etc.)
- ✅ **Courses & Lessons** (full curriculum)
- ✅ **Quizzes & Questions** (all assessments)
- ✅ **Progress & Attempts** (user quiz history)
- ✅ **Enrollments** (user-course relationships)
- ✅ **Problems & Solutions** (coding challenges)
- ✅ **Leaderboard Data** (XP, coins, streaks)
- ✅ **Notifications & Activities** (user logs)
- ✅ **Everything else** in all 24+ tables

### Safety Features
- ✅ Checks if production is empty before proceeding
- ✅ Uses database transactions (rollback on failure)
- ✅ Skips duplicate records (by unique constraints)
- ✅ Preserves primary keys and foreign key relationships
- ✅ Detailed logging of all operations
- ✅ Dry-run mode available

---

## 🚀 Quick Start

### Step 1: Ensure LOCAL Database is Ready

```bash
# Make sure your local database has all the data you want to migrate
# Navigate to backend directory
cd backend

# Verify local database has content
python
>>> from database import db
>>> from app import create_app
>>> app = create_app()
>>> with app.app_context():
...     from models import User, Quiz
...     print(f"Users: {User.query.count()}")
...     print(f"Quizzes: {Quiz.query.count()}")
```

### Step 2: Verify PRODUCTION Database is Empty

The script will check this automatically, but you can verify manually:

```bash
# Connect to production (you'll need MySQL CLI or use your IDE)
# Or rely on script to check automatically
```

### Step 3: Run the Migration

```bash
# Recommended: Use ORM version (safer, type-checked)
cd backend
python migrate_full_data_orm.py

# OR use raw SQL version
python migrate_full_data.py
```

### Step 4 (Optional): Seed Leaderboard Data

If you want to populate random user stats (XP, levels, coins):

```bash
cd backend
python seed_leaderboard_data.py
```

---

## 📖 How to Use Each Script

### Option A: ORM Migration (RECOMMENDED ✨)

```bash
cd backend
python migrate_full_data_orm.py [--force]
```

**Advantages:**
- ✅ Type-safe (uses SQLAlchemy ORM)
- ✅ Automatic NULL handling
- ✅ Better error messages
- ✅ Preserves data types correctly

**Flags:**
- `--force`: Skip production empty check and migrate anyway

**Output Example:**
```
[14:23:45] ✓ Connected to LOCAL
[14:23:46] ✓ Connected to PRODUCTION
[14:23:47] ✓ Production is empty; safe to migrate
[14:23:48] ℹ Starting migration...

[14:23:49] ✓ users: 5 inserted
[14:23:50] ✓ courses: 3 inserted
[14:23:51] ✓ lessons: 9 inserted
[14:23:52] ✓ quizzes: 9 inserted
[14:23:53] ✓ questions: 45 inserted
...

📊 TOTAL: 312 records migrated
✓ MIGRATION COMPLETED SUCCESSFULLY!
```

---

### Option B: Raw SQL Migration

```bash
cd backend
python migrate_full_data.py
```

**Advantages:**
- ✅ Works with any SQLAlchemy-compatible DB
- ✅ Minimal ORM overhead
- ✅ Direct SQL control

**When to use:**
- If ORM version has compatibility issues
- For debugging specific table issues
- As a fallback option

---

## 🔒 Safety & Rollback

### What Happens on Error?

1. **Connection Failure**: Script exits safely, nothing changes
2. **Production Not Empty**: Asks for confirmation before proceeding
3. **Insert Failure**: Rolls back current table, logs error, continues with others
4. **Duplicate Detection**: Skips records that already exist (by unique constraints)

### Rollback (if needed)

If migration fails and you need to undo:

```bash
# Connect to production and clear tables (WARNING: destructive!)
# Only do this if migration failed partway through

# Option 1: Use Render dashboard to reset database
# (This is the safest way)

# Option 2: Manual SQL (if you have shell access)
# DELETE FROM enrollments;
# DELETE FROM courses;
# DELETE FROM users;
# etc.
```

---

## 📋 Pre-Migration Checklist

Before running migration:

- [ ] Local database has all the data you want to migrate
- [ ] Production database is `empty` (no users, quizzes, etc.)
- [ ] `.env` file has correct `DATABASE_URL` (production) or `DB_*` vars (local)
- [ ] Backend dependencies installed: `pip install -r requirements.txt`
- [ ] Network connection is stable (no interruptions during migration)
- [ ] You have a backup of production database (if it has any existing data)

---

## 🛠️ Environment Variables

### Local Database (.env)

```env
# Local Development Database
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=gamified_learning

# OR use DATABASE_URL instead
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/gamified_learning
```

### Production Database (.env)

```env
# Production - Railway MySQL
DATABASE_URL=mysql+pymysql://user:password@mysql.railway.internal:3306/railway

# OR set the full connection string
# DATABASE_URL=mysql+pymysql://admin:RandomPassword123@viaduct.proxy.rlwy.net:55432/railway
```

---

## 📊 Migration Order (Respects Foreign Keys)

The scripts migrate tables in this order to maintain referential integrity:

1. **users** - Parent of everything
2. **courses** - Depends on users (teacher_id)
3. **lessons** - Depends on courses
4. **enrollments** - Depends on users + courses
5. **quizzes** - Depends on courses
6. **questions** - Depends on quizzes
7. **progress** - Depends on users + quizzes
8. **quiz_attempts** - Depends on users + quizzes
9. **skills** - Can self-reference
10. **user_skills** - Depends on users + skills
11. ... and so on

This order ensures that all parent records exist before their children are inserted.

---

## ✅ Post-Migration Verification

### 1. Check via API

```bash
# From project root
npm run deploy:check

# Expected output:
# [✓] frontend / (200)
# [✓] frontend /register (200)
# [✓] backend / (200)
# [✓] backend /api/test (200)
# [✓] backend /api/login (401 Invalid credentials)
```

### 2. Check via SQL

```bash
# Connect to production and verify record counts
SELECT COUNT(*) as users FROM users;
SELECT COUNT(*) as courses FROM courses;
SELECT COUNT(*) as quizzes FROM quizzes;
SELECT COUNT(*) as questions FROM questions;
```

### 3. Test in Frontend

```bash
# Try logging in with a migrated user account
# Email: rahul@student.com
# Password: Demo@123 (or whatever your demo password is)

# Should see:
# ✓ Login succeeds
# ✓ Dashboard loads with courses/quizzes
# ✓ User profile shows correct XP/level
```

---

## 🆘 Troubleshooting

### Error: "Missing DATABASE_URL in .env"

**Solution:** Add to `.env`:
```env
DATABASE_URL=mysql+pymysql://user:password@host:port/database
```

### Error: "PRODUCTION HAS USERS"

This means production database already has data. Options:

1. **Only migrate new data:**
   ```bash
   python migrate_full_data_orm.py --force
   ```
   (Will skip duplicates)

2. **Clear production (WARNING: destructive):**
   - Go to Render dashboard
   - Navigate to Database tab
   - Delete and recreate database
   - Re-run migration

### Error: "Foreign key constraint fails"

**Cause:** Trying to insert child before parent

**Solution:** Check table order - ensure parents migrate first. This should be automatic, but if it's a custom table, ensure dependencies are correct.

### Error: "Connection timeout"

**Cause:** Network issue or invalid credentials

**Solution:**
```bash
# Test connection manually
python
>>> from sqlalchemy import create_engine
>>> engine = create_engine("mysql+pymysql://user:pwd@host:port/db")
>>> engine.connect()
```

### Error: "Table 'database.table' doesn't exist"

**Cause:** Production database not initialized with schema

**Solution:** Run bootstrap before migration:
```bash
# Run on production (or it runs automatically on Render startup)
python bootstrap_db.py
```

---

## 🎯 Optional: Leaderboard Seeding

To populate user leaderboard stats (XP, levels, coins):

```bash
cd backend
python seed_leaderboard_data.py
```

**What it does:**
- Assigns XP points (500-5000 for random users, 4800-8000 for demo users)
- Assigns levels (1-10)
- Assigns coins (100-1000)
- Sets daily streaks
- Creates UserCodingStats records

**Demo user values (hardcoded):**
- `admin@lms.com`: 8000 XP, Level 8, 2000 coins
- `john@lms.com`: 6500 XP, Level 7, 1500 coins
- `priya@lms.com`: 7200 XP, Level 7, 1800 coins
- `rahul@student.com`: 5000 XP, Level 6, 1000 coins
- `anita@student.com`: 4800 XP, Level 5, 950 coins

---

## 🔍 Duplicate Detection

The migration automatically skips duplicates found by:

- **users**: Check by email (unique)
- **enrollments**: Check by (student_id, course_id)
- **user_skills**: Check by (user_id, skill_id)
- **problem_progress**: Check by (user_id, problem_id)
- **lesson_progress**: Check by (user_id, course_id, lesson_id)

This allows you to run migration multiple times safely.

---

## 📈 Performance Notes

- **Small DB (< 10,000 records)**: ~10-30 seconds
- **Medium DB (10K-100K records)**: ~1-5 minutes
- **Large DB (> 100K records)**: ~5-30 minutes

The ORM version is slightly slower but much safer.

---

## 🚨 Important Warnings

1. **This migrates EVERYTHING** - all users, including test/demo users
2. **Primary keys are preserved** - if your local DB has ID=1, it will be ID=1 in production
3. **Passwords are NOT reset** - all user passwords are copied as-is
4. **Timestamps are preserved** - created_at, updated_at dates remain the same
5. **This is one-way** - no data flows back from production to local

---

## 📝 Script Comparison

| Feature | ORM Version | Raw SQL Version |
|---------|------------|-----------------|
| Safety | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Type Safety | Yes | No |
| Error Messages | Detailed | Basic |
| Speed | Medium | Fast |
| Compatibility | Better | Original |
| Recommended | ✅ YES | Fallback |

---

## 📞 Support

If migration fails:

1. Check `.env` variables (DATABASE_URL, DB_* vars)
2. Ensure local DB has data to migrate
3. Ensure production DB is empty (or use --force)
4. Check network connection to both databases
5. Review error messages in script output
6. Check Render logs for backend errors

---

## ✨ All Done!

After successful migration:

1. **Production DB is now identical to local DB**
2. **All users, courses, quizzes, and data are ready**
3. **Run health check**: `npm run deploy:check`
4. **Test login**: Use any migrated user account
5. **Verify dashboard**: Should show courses, quizzes, etc.

Happy migrating! 🎉
