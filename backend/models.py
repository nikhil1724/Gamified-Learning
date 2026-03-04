from datetime import datetime

from database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="student", nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    level = db.Column(db.Integer, default=1, nullable=False)
    xp_points = db.Column(db.Integer, default=0, nullable=False)
    coins = db.Column(db.Integer, default=0, nullable=False)
    daily_streak = db.Column(db.Integer, default=0, nullable=False)
    last_daily_completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    progresses = db.relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    user_rewards = db.relationship("UserReward", back_populates="user", cascade="all, delete-orphan")
    courses_taught = db.relationship("Course", back_populates="teacher", cascade="all, delete-orphan")
    enrollments = db.relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    notes_uploaded = db.relationship("Note", back_populates="uploader", cascade="all, delete-orphan")
    submissions = db.relationship("Submission", back_populates="student", cascade="all, delete-orphan")
    code_submissions = db.relationship(
        "CodeSubmission",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    problem_progress = db.relationship(
        "ProblemProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    coding_stats = db.relationship(
        "UserCodingStats",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    created_problems = db.relationship(
        "Problem",
        back_populates="creator",
        cascade="all, delete-orphan",
    )
    user_badges = db.relationship(
        "UserBadge",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    lesson_progress = db.relationship(
        "LessonProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    notifications = db.relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(
        db.Enum("Easy", "Medium", "Hard", name="quiz_difficulty"),
        nullable=False,
    )
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=True)

    questions = db.relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    progresses = db.relationship("Progress", back_populates="quiz", cascade="all, delete-orphan")
    submissions = db.relationship("Submission", back_populates="quiz", cascade="all, delete-orphan")
    skill = db.relationship("Skill", back_populates="quiz", uselist=False)
    course = db.relationship("Course", back_populates="quizzes")

    def __repr__(self):
        return f"<Quiz id={self.id} title={self.title} difficulty={self.difficulty}>"


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)

    quiz = db.relationship("Quiz", back_populates="questions")

    def __repr__(self):
        return f"<Question id={self.id} quiz_id={self.quiz_id}>"


class Progress(db.Model):
    __tablename__ = "progresses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    completion_percentage = db.Column(db.Float, nullable=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="progresses")
    quiz = db.relationship("Quiz", back_populates="progresses")

    def __repr__(self):
        return (
            f"<Progress id={self.id} user_id={self.user_id} "
            f"quiz_id={self.quiz_id} score={self.score}>"
        )


class Reward(db.Model):
    __tablename__ = "rewards"

    id = db.Column(db.Integer, primary_key=True)
    badge_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    xp_required = db.Column(db.Integer, nullable=False)

    user_rewards = db.relationship("UserReward", back_populates="reward", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Reward id={self.id} badge_name={self.badge_name}>"


class UserReward(db.Model):
    __tablename__ = "user_rewards"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey("rewards.id"), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="user_rewards")
    reward = db.relationship("Reward", back_populates="user_rewards")

    def __repr__(self):
        return f"<UserReward id={self.id} user_id={self.user_id} reward_id={self.reward_id}>"


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    teacher = db.relationship("User", back_populates="courses_taught")
    enrollments = db.relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    notes = db.relationship("Note", back_populates="course", cascade="all, delete-orphan")
    quizzes = db.relationship("Quiz", back_populates="course")
    lessons = db.relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    coding_problems = db.relationship(
        "CodingProblem",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Course id={self.id} title={self.title} teacher_id={self.teacher_id}>"


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    __table_args__ = (
        db.UniqueConstraint("student_id", "course_id", name="uq_enrollments_student_course"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship("User", back_populates="enrollments")
    course = db.relationship("Course", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment id={self.id} student_id={self.student_id} course_id={self.course_id}>"


class Note(db.Model):
    __tablename__ = "notes"
    __table_args__ = (
        db.CheckConstraint(
            "content IS NOT NULL OR file_url IS NOT NULL",
            name="ck_notes_content_or_file",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.String(1024), nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    course = db.relationship("Course", back_populates="notes")
    uploader = db.relationship("User", back_populates="notes_uploaded")

    def __repr__(self):
        return f"<Note id={self.id} course_id={self.course_id} uploaded_by={self.uploaded_by}>"


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship("User", back_populates="submissions")
    quiz = db.relationship("Quiz", back_populates="submissions")

    def __repr__(self):
        return f"<Submission id={self.id} student_id={self.student_id} quiz_id={self.quiz_id}>"


class DailyChallenge(db.Model):
    __tablename__ = "daily_challenges"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    quiz = db.relationship("Quiz")

    def __repr__(self):
        return f"<DailyChallenge id={self.id} date={self.date} quiz_id={self.quiz_id}>"


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    prerequisite_skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=True)

    prerequisite = db.relationship("Skill", remote_side=[id], backref="unlock_next")
    quiz = db.relationship("Quiz", back_populates="skill", uselist=False)
    user_skills = db.relationship("UserSkill", back_populates="skill", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Skill id={self.id} skill_name={self.skill_name}>"


class UserSkill(db.Model):
    __tablename__ = "user_skills"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    unlocked = db.Column(db.Boolean, default=False, nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    user = db.relationship("User", backref="user_skills")
    skill = db.relationship("Skill", back_populates="user_skills")

    def __repr__(self):
        return f"<UserSkill id={self.id} user_id={self.user_id} skill_id={self.skill_id}>"


class Problem(db.Model):
    __tablename__ = "problems"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(
        db.Enum("Easy", "Medium", "Hard", name="problem_difficulty"),
        nullable=False,
    )
    tags = db.Column(db.JSON, nullable=True)
    description = db.Column(db.Text, nullable=False)
    constraints = db.Column(db.Text, nullable=True)
    example_input = db.Column(db.Text, nullable=True)
    example_output = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    creator = db.relationship("User", back_populates="created_problems")
    test_cases = db.relationship(
        "ProblemTestCase",
        back_populates="problem",
        cascade="all, delete-orphan",
    )
    code_submissions = db.relationship(
        "CodeSubmission",
        back_populates="problem",
        cascade="all, delete-orphan",
    )
    progress_entries = db.relationship(
        "ProblemProgress",
        back_populates="problem",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Problem id={self.id} title={self.title} difficulty={self.difficulty}>"


class ProblemTestCase(db.Model):
    __tablename__ = "test_cases"

    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey("problems.id"), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    problem = db.relationship("Problem", back_populates="test_cases")

    def __repr__(self):
        return (
            f"<ProblemTestCase id={self.id} problem_id={self.problem_id} "
            f"hidden={self.is_hidden}>"
        )


class CodeSubmission(db.Model):
    __tablename__ = "code_submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey("problems.id"), nullable=False)
    language = db.Column(db.String(30), nullable=False, default="python")
    code = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum(
            "Accepted",
            "Wrong Answer",
            "Time Limit Exceeded",
            "Runtime Error",
            name="submission_status",
        ),
        nullable=False,
    )
    runtime_ms = db.Column(db.Integer, nullable=True)
    passed_count = db.Column(db.Integer, default=0, nullable=False)
    total_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="code_submissions")
    problem = db.relationship("Problem", back_populates="code_submissions")
    progress_entry = db.relationship(
        "ProblemProgress",
        back_populates="last_submission",
        uselist=False,
    )

    def __repr__(self):
        return (
            f"<CodeSubmission id={self.id} user_id={self.user_id} "
            f"problem_id={self.problem_id} status={self.status}>"
        )


class ProblemProgress(db.Model):
    __tablename__ = "user_progress"
    __table_args__ = (
        db.UniqueConstraint("user_id", "problem_id", name="uq_progress_user_problem"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey("problems.id"), nullable=False)
    solved = db.Column(db.Boolean, default=False, nullable=False)
    best_runtime_ms = db.Column(db.Integer, nullable=True)
    last_submission_id = db.Column(
        db.Integer, db.ForeignKey("code_submissions.id"), nullable=True
    )
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="problem_progress")
    problem = db.relationship("Problem", back_populates="progress_entries")
    last_submission = db.relationship("CodeSubmission", back_populates="progress_entry")

    def __repr__(self):
        return (
            f"<ProblemProgress id={self.id} user_id={self.user_id} "
            f"problem_id={self.problem_id} solved={self.solved}>"
        )


class Badge(db.Model):
    __tablename__ = "badges"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    rule_type = db.Column(db.String(60), nullable=True)
    rule_value = db.Column(db.Integer, nullable=True)

    user_badges = db.relationship("UserBadge", back_populates="badge")

    def __repr__(self):
        return f"<Badge id={self.id} name={self.name}>"


class UserBadge(db.Model):
    __tablename__ = "user_badges"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id"), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="user_badges")
    badge = db.relationship("Badge", back_populates="user_badges")

    def __repr__(self):
        return f"<UserBadge id={self.id} user_id={self.user_id} badge_id={self.badge_id}>"


class UserCodingStats(db.Model):
    __tablename__ = "user_coding_stats"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    solved_count = db.Column(db.Integer, default=0, nullable=False)
    streak_days = db.Column(db.Integer, default=0, nullable=False)
    last_solved_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="coding_stats")

    def __repr__(self):
        return f"<UserCodingStats id={self.id} user_id={self.user_id} streak={self.streak_days}>"


class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(1024), nullable=True)
    audio_url = db.Column(db.String(1024), nullable=True)
    order_index = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    course = db.relationship("Course", back_populates="lessons")

    def __repr__(self):
        return f"<Lesson id={self.id} course_id={self.course_id} title={self.title}>"


class CodingProblem(db.Model):
    __tablename__ = "coding_problems"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(
        db.Enum("Easy", "Medium", "Hard", name="coding_problem_difficulty"),
        nullable=False,
    )
    tags = db.Column(db.JSON, nullable=True)
    description = db.Column(db.Text, nullable=False)
    example_input = db.Column(db.Text, nullable=True)
    example_output = db.Column(db.Text, nullable=True)
    constraints = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    course = db.relationship("Course", back_populates="coding_problems")

    def __repr__(self):
        return f"<CodingProblem id={self.id} course_id={self.course_id} title={self.title}>"


class LessonProgress(db.Model):
    __tablename__ = "lesson_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course = db.Column(db.String(50), nullable=False)
    lesson_id = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="lesson_progress")

    def __repr__(self):
        return f"<LessonProgress user_id={self.user_id} course={self.course} lesson={self.lesson_id}>"


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(
        db.Enum("XP_EARNED", "QUIZ_COMPLETED", "BADGE_EARNED", "COURSE_ADDED", name="notification_type"),
        nullable=False,
    )
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON, nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification id={self.id} user_id={self.user_id} type={self.type} is_read={self.is_read}>"
