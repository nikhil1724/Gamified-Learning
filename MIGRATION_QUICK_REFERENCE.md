# Migration Scripts - Quick Reference

## 3 Scripts, 3 Purposes

### Script 1: `migrate_full_data_orm.py` (RECOMMENDED ✨)
**The safest, most recommended approach**

```bash
cd backend
python migrate_full_data_orm.py

# With force flag (skip safety checks)
python migrate_full_data_orm.py --force
```

**Best for:**
- First-time migrations
- Production deployments
- When you want maximum safety
- When accuracy matters more than speed

**What it does:**
- Connects to LOCAL database
- Connects to PRODUCTION database
- Checks if production is empty
- Migrates all 24+ tables in correct dependency order
- Skips duplicates automatically
- Preserves primary keys and relationships
- Type-safe ORM inserts

**Expected output:**
```
✓ Connected to LOCAL
✓ Connected to PRODUCTION
✓ Production is empty; safe to migrate
Starting migration...

✓ users: 5 inserted
✓ courses: 3 inserted
✓ lessons: 9 inserted
✓ quizzes: 9 inserted
...

TOTAL: 312 records migrated
✓ MIGRATION COMPLETED SUCCESSFULLY!
```

---

### Script 2: `migrate_full_data.py` (BACKUP)
**Raw SQL version - use if ORM version has issues**

```bash
cd backend
python migrate_full_data.py
```

**When to use:**
- If ORM version fails
- For specific table debugging
- As a fallback option

**Same features as ORM version but uses raw SQL instead of models**

---

### Script 3: `seed_leaderboard_data.py` (OPTIONAL)
**Populates user stats after migration**

```bash
cd backend
python seed_leaderboard_data.py
```

**What it does:**
- Assigns XP points to users (500-5000 random, 4800-8000 for demo users)
- Assigns levels (1-10)
- Assigns coins (100-1000)
- Sets daily streaks
- Creates UserCodingStats records

**Run this AFTER migration is complete**

---

## 📋 Complete Migration Workflow

### Step 1: Verify Local Database
```bash
cd backend
python
>>> from database import db
>>> from app import create_app
>>> app = create_app()
>>> with app.app_context():
...     from models import User, Quiz, Course
...     print(f"Users: {User.query.count()}")
...     print(f"Courses: {Course.query.count()}")
...     print(f"Quizzes: {Quiz.query.count()}")
>>> exit()
```

### Step 2: Run Migration
```bash
cd backend
python migrate_full_data_orm.py
```

Sit back and watch the magic happen! ✨

### Step 3 (Optional): Seed Leaderboard
```bash
cd backend
python seed_leaderboard_data.py
```

### Step 4: Verify Success
```bash
# From project root
npm run deploy:check

# Or manually check endpoints
curl https://gamified-learning.onrender.com/api/quizzes
curl https://gamified-learning.onrender.com/api/courses
```

### Step 5: Test in App
1. Go to https://gamified-learning-flame.vercel.app
2. Login with: `rahul@student.com` / `Demo@123`
3. Should see: Courses, Quizzes, Dashboard populated
4. Check profile for XP/levels

---

## 🛠️ Requirements

### Before running migration:

**1. .env file with DATABASE_URL:**
```env
DATABASE_URL=mysql+pymysql://admin:password@host:port/railway
```

**2. OR local DB variables:**
```env
DB_USER=root
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=gamified_learning
```

**3. Python dependencies installed:**
```bash
pip install -r requirements.txt
```

**4. Both databases must be accessible:**
- Local database running on specified host
- Production (Railway) MySQL accessible

---

## ⚡ Speed & Performance

| Database Size | ORM Version | Raw SQL Version |
|---|---|---|
| < 5K records | ~10 sec | ~5 sec |
| 5K-50K | ~1 min | ~30 sec |
| > 50K | ~5 min | ~2 min |

ORM is slightly slower but much safer.

---

## ✅ Migration Checklist

Before clicking "Run":
- [ ] Local DB has data ready
- [ ] Production DB is empty
- [ ] .env configured correctly
- [ ] Network stable
- [ ] 15+ minutes of time available
- [ ] No one else accessing databases

---

## 🚨 Important Notes

1. **Preserves Primary Keys**: ID=1 in local will be ID=1 in production
2. **Copies Passwords**: All password hashes copied as-is
3. **One-way Sync**: Data flows LOCAL → PROD only
4. **Safe to Rerun**: Duplicates are skipped
5. **All Tables**: Everything is migrated (users, courses, quizzes, progress, etc.)

---

## 🔍 What Gets Migrated?

✅ Users (id, email, password, role, level, xp, coins, etc.)
✅ Courses
✅ Lessons
✅ Quizzes
✅ Questions
✅ User Progress
✅ Quiz Attempts
✅ Enrollments
✅ Problems & Coding Challenges
✅ Code Submissions
✅ Badges & Rewards
✅ Leaderboard Stats
✅ Notifications
✅ Learning Activities
✅ User Skills
✅ Daily Challenges
✅ Notes
✅ Everything else (24+ tables total)

---

## 🆘 Common Issues & Solutions

### Issue: "Missing DATABASE_URL"
```bash
# Solution: Add to .env
DATABASE_URL=mysql+pymysql://user:pwd@host:port/db
```

### Issue: "Production has users - won't overwrite"
```bash
# Option 1: Use --force flag
python migrate_full_data_orm.py --force

# Option 2: Type 'yes' when prompted
```

### Issue: "Connection refused"
```bash
# Check credentials in .env
# Verify database is running
# Test connectivity:
mysql -h hostname -u user -p database_name
```

### Issue: Script hangs or times out
```bash
# Likely large database transfer
# Wait up to 30 minutes
# Or increase timeout in script if needed
```

---

## 📊 What the Scripts Log

During migration, you'll see:
- ✓ Successful connections
- ✓ Table-by-table progress
- ✓ Record counts
- ⚠️ Warnings (duplicates skipped, etc.)
- ✗ Errors with details

Example output:
```
[14:23:45] ✓ Connected to LOCAL
[14:23:46] ✓ Connected to PRODUCTION
[14:23:47] ℹ Starting migration...

[14:23:49] ✓ users: 5 inserted
[14:23:50] ✓ courses: 3 inserted, 0 skipped
[14:23:51] ✓ enrollments: 8 inserted
[14:23:52] ⚠ user_coding_stats: 4 inserted, 1 skipped
...

📊 TOTAL: 312 records migrated
✓ MIGRATION COMPLETED SUCCESSFULLY!
```

---

## 🎯 Next Steps After Migration

1. **Verify data:**
   ```bash
   npm run deploy:check
   ```

2. **Test login:**
   ```
   Email: rahul@student.com
   Password: Demo@123
   ```

3. **Check frontend:**
   - Navigate to https://gamified-learning-flame.vercel.app
   - Should see courses and quizzes
   - User profile should show XP/levels

4. **Monitor production:**
   - Check Render logs
   - Watch for any 500 errors
   - Verify no data loss

---

## 📚 Full Documentation

See `MIGRATION_GUIDE.md` for:
- Detailed step-by-step instructions
- Complete troubleshooting guide
- Safety features explained
- Rollback procedures
- Performance notes
- Advanced options

---

## ❓ Still Have Questions?

1. Read `MIGRATION_GUIDE.md` for detailed docs
2. Check script source code for comments
3. Review `.env` configuration
4. Check Render logs for errors
5. Verify network connectivity

---

**You've got this! Happy migrating 🚀**
