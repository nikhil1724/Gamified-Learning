# Gamified Digital Learning Platform - Production Blueprint

## 1) Complete Folder Structure (Frontend + Backend)

### Root
- frontend/: React app (pages, services, context, styles, components)
- backend/: Flask API (routes, models, services, migrations, SQL)
- scripts/: deployment and validation scripts
- .github/workflows/: CI pipeline definitions

### Frontend Key Modules
- src/context/: auth and theme state
- src/services/: API and Socket.IO clients
- src/pages/: role dashboards, quizzes, leaderboards, learning pages
- src/components/: reusable UI elements and widgets
- src/styles/: shared styling and design system layers

### Backend Key Modules
- app.py: Flask app factory, CORS, JWT handlers, blueprint registration
- models.py: SQLAlchemy entities and relationships
- routes/: modular REST endpoints by feature
- leaderboard_service.py: ranking payload generation
- badge_service.py: badge and reward logic
- activity_service.py: activity/streak logic
- seed_*.py: demo data bootstrap scripts
- sql/: schema and migration SQL files

## 2) Database Schema (MySQL)

The complete production schema is provided in:
- backend/sql/full_platform_schema.sql

It includes all major entities requested:
- users, courses, enrollments, lessons
- quizzes, questions, quiz_attempts, progresses
- rewards, badges, user_badges, user_rewards
- notifications, learning_activity
- problems, test_cases, code_submissions, problem_progress
- teacher analytics supporting tables and indexes

## 3) API Design (All Endpoints)

All routes are implemented under Flask blueprints with role-aware access checks and JWT.

### Authentication and Account
- POST /api/register
- POST /api/login
- GET /api/profile
- PATCH /api/profile
- POST /api/auth/logout
- POST /api/auth/change-password

### User and Health
- GET /api/users/health

### Course and Enrollment
- POST /api/teacher/courses
- GET /api/teacher/courses
- GET /api/courses
- GET /api/course/{course_id}
- GET /api/course/{course_id}/lessons
- GET /api/course/{course_id}/quizzes
- GET /api/course/{course_id}/problems
- POST /api/student/enroll
- GET /api/student/courses

### Quiz and Evaluation
- GET /api/quizzes
- GET /api/quiz/{quiz_id}
- POST /api/teacher/quizzes
- POST /api/quiz/submit
- GET /api/courses/{course_id}/quizzes
- GET /api/quiz/history

### Coding Problems
- GET /api/problems
- GET /api/problem/{problem_id}
- POST /api/run
- POST /api/submit
- GET /api/submissions/{user_id}

### Admin
- GET /api/admin/teachers/pending
- POST /api/admin/teachers/approve/{teacher_id}
- POST /api/admin/teachers/reject/{teacher_id}
- GET /api/admin/users
- PUT /api/admin/approve-teacher/{teacher_id}
- GET /api/admin/stats

### Coding Admin (Instructor/Admin Content)
- POST /api/admin/problems
- POST /api/admin/course
- PUT /api/admin/problems/{problem_id}
- POST /api/admin/problems/{problem_id}/test-cases
- PUT /api/admin/test-cases/{test_case_id}
- DELETE /api/admin/test-cases/{test_case_id}
- POST /api/admin/lessons
- POST /api/admin/course/{course_id}/lesson
- PUT /api/admin/lessons/{lesson_id}
- DELETE /api/admin/lessons/{lesson_id}
- POST /api/admin/coding-problems
- PUT /api/admin/coding-problems/{problem_id}
- DELETE /api/admin/coding-problems/{problem_id}

### Notes and Content Assets
- POST /api/teacher/notes
- POST /api/teacher/notes/upload-pdf
- DELETE /api/teacher/notes/{note_id}/pdf
- GET /api/uploads/{filename}
- GET /api/courses/{course_id}/notes

### Progress and Learning Tracking
- POST /api/lesson-progress/{course}/{lesson_id}
- GET /api/lesson-progress/{course}
- GET /api/lesson-progress
- DELETE /api/lesson-progress/{course}/{lesson_id}
- POST /api/courses/{course_id}/lessons/{lesson_id}/complete
- GET /api/courses/{course_id}/progress
- GET /api/learning-dashboard
- POST /api/lesson/complete
- GET /api/progress/{user_id}/{course_id}
- GET /api/student/dashboard
- GET /api/instructor/analytics/{course_id}
- GET /api/certificate/{user_id}/{course_id}

### Gamification, Rewards, Skills
- GET /api/rewards
- GET /api/user/rewards
- GET /api/badges
- GET /api/skills
- GET /api/user/skills
- POST /api/activity
- GET /api/streak

### Leaderboard and Recommendations
- GET /api/leaderboard
- GET /api/recommendations
- GET /api/recommendations/{user_id}

### Notifications
- GET /api/notifications
- GET /api/notifications/unread-count
- PUT /api/notifications/{notification_id}/read
- PUT /api/notifications/read-all
- DELETE /api/notifications/{notification_id}

### Analytics
- GET /api/analytics/xp-history
- GET /api/analytics/quiz-scores
- GET /api/analytics/problems-solved
- GET /api/analytics/summary
- GET /api/teacher/stats
- GET /api/teacher/course/{course_id}/students
- GET /api/teacher/student/{student_id}/performance
- GET /api/teacher/course/{course_id}/analytics
- GET /api/teacher/students/overview

### Daily Challenge
- GET /api/daily-challenge
- GET /api/daily-challenge/status
- POST /api/daily-challenge/complete

## 4) Backend Implementation Design (Flask)

### Architecture
- App factory pattern in backend/app.py
- Blueprint-per-module routing under backend/routes/
- Shared SQLAlchemy models in backend/models.py
- JWT auth and role checks in route-level guards
- Service modules for leaderboard, badges, activity, recommendations

### Production Practices Already Applied
- Structured JSON error handlers (400/401/403/404/500)
- CORS allow-list for Vercel deployment domains
- Socket.IO configured for production workers
- Deployment and contract-check scripts in scripts/

## 5) Frontend Implementation Design (React)

### Architecture
- Page-level modules by role and feature in frontend/src/pages/
- Shared API abstraction in frontend/src/services/api.js
- Socket-based leaderboard updates in frontend/src/services/leaderboardSocket.js
- Auth/session state in frontend/src/context/AuthContext.jsx
- Theme state and persistence in frontend/src/context/ThemeContext.jsx

### Core UI Pages (Sample and Demo-Ready)
- Student Dashboard, Learning Hub, Course Detail, Lesson Viewer
- Quiz page with instant result review and history
- Leaderboard page with real-time updates
- Instructor dashboard and analytics pages
- Admin dashboard, teacher approval, content management
- Settings page with profile/password/theme controls

## 6) Gamification Logic Implementation

### XP and Level
- XP awarded from quiz completion and daily challenge completion
- Level computed from XP milestones
- Streak tracking for daily learning continuity

Recommended formula used for extensibility:
- Level threshold for level n: XP >= 100 * n^2
- Coins reward bands can be tied to quiz percentage and streak bonus

### Badge Awards
- Rule-driven badges via badges and user_badges tables
- Badge service checks conditions after key events:
  - first quiz completion
  - streak milestones
  - XP milestones
  - coding problem solve milestones

### Reward Economy
- rewards and user_rewards support unlocks by XP or achievements
- notifications are generated for badge/reward/XP events

## 7) Leaderboard Algorithm

Ranking score can use weighted gamification metrics:
- rank_score = xp_points + 3 * completed_quizzes + 10 * solved_problems + 5 * daily_streak

Sorting order:
1. rank_score DESC
2. xp_points DESC
3. updated/attempted timestamp ASC (earlier achiever ranks higher on tie)

This supports:
- Global leaderboard (all students)
- Course-wise leaderboard (filter by enrolled course)

## 8) Real-Time Tracking Strategy

- Quiz submissions persist to progresses and quiz_attempts
- Leaderboard payload emitted through Socket.IO events
- Notifications and unread counts refreshed from API + realtime triggers
- Dashboard charts consume analytics and progress endpoints

## 9) Validation, Error Handling, and Seed Data

### Validation and Error Handling
- JWT guards for protected resources
- role-based authorization for admin/instructor routes
- graceful JSON error envelopes
- deployment health and API contract checks in scripts/

### Seed and Demo Utilities
- backend/seed_data.py
- backend/seed_leaderboard_data.py
- backend/seed_student_progress_demo.py
- backend/bootstrap_db.py

## 10) Deployment Readiness

### Included Production Checks
- npm run contract:check
- npm run smoke:check
- npm run deploy:check

### CI Workflow
- .github/workflows/ci-validation.yml runs on push/PR:
  - Frontend build
  - Backend compile checks
  - API contract checks
  - Core smoke checks

## 11) Final-Year Demo Narrative

Use this flow in project demo:
1. Student registration and login
2. Enrollment into a course
3. Complete lessons and attempt quiz
4. Show instant feedback, XP gain, level movement
5. Show leaderboard rank update in near real-time
6. Show badges/rewards and dashboard analytics
7. Show instructor analytics and admin governance (teacher approvals)

This repository now provides a complete, modular, production-oriented implementation aligned to your stated objective: improving student engagement through gamified learning.
