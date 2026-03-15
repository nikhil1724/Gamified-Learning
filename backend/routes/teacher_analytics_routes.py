from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func
from datetime import datetime, timedelta

from database import db
from models import (
    User, Course, Enrollment, Progress, LessonProgress, 
    ProblemProgress, CodeSubmission, Lesson, Quiz, CodingProblem
)


teacher_analytics_bp = Blueprint("teacher_analytics", __name__, url_prefix="/api/teacher")


def _get_teacher():
    """Get current teacher user"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id)) if user_id is not None else None
    if not user:
        return None, (jsonify({"error": "User not found"}), 404)
    if user.role not in {"teacher", "admin"}:
        return None, (jsonify({"error": "Teacher access required"}), 403)
    if user.role == "teacher" and not user.is_approved:
        return None, (jsonify({"error": "Teacher approval pending"}), 403)
    return user, None


def _verify_course_ownership(course_id, teacher_id):
    """Verify that the course belongs to the teacher"""
    course = Course.query.get(course_id)
    if not course:
        return None, (jsonify({"error": "Course not found"}), 404)
    if course.teacher_id != teacher_id:
        return None, (jsonify({"error": "Unauthorized access to this course"}), 403)
    return course, None


@teacher_analytics_bp.get("/stats")
@jwt_required()
def get_teacher_stats():
    """Get real-time statistics for instructor dashboard"""
    teacher, error_response = _get_teacher()
    if error_response:
        return error_response
    
    # Get all courses taught by this teacher
    courses = Course.query.filter_by(teacher_id=teacher.id).all()
    total_courses = len(courses)
    
    # Count total problems created
    total_problems = CodingProblem.query.filter_by(created_by=teacher.id).count()
    
    # Count unique students enrolled across all courses
    enrolled_student_ids = set()
    for course in courses:
        for enrollment in course.enrollments:
            enrolled_student_ids.add(enrollment.student_id)
    total_students = len(enrolled_student_ids)
    
    # Count total enrollments
    total_enrollments = sum(len(course.enrollments) for course in courses)
    
    return jsonify({
        "total_courses": total_courses,
        "total_problems": total_problems,
        "active_students": total_students,
        "total_enrollments": total_enrollments
    })


@teacher_analytics_bp.get("/course/<int:course_id>/students")
@jwt_required()
def get_course_students(course_id):
    """Get list of students enrolled in a specific course with their progress"""
    teacher, error_response = _get_teacher()
    if error_response:
        return error_response
    
    course, error_response = _verify_course_ownership(course_id, teacher.id)
    if error_response:
        return error_response
    
    # Get all enrollments for this course
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    
    # Get total lessons and quizzes in the course
    total_lessons = Lesson.query.filter_by(course_id=course_id).count()
    total_quizzes = Quiz.query.filter_by(course_id=course_id).count()
    total_problems = CodingProblem.query.filter_by(course_id=course_id).count()
    
    students_data = []
    for enrollment in enrollments:
        student = enrollment.student
        if not student:
            continue
        
        # Count completed lessons
        completed_lessons = LessonProgress.query.filter_by(
            user_id=student.id,
            course_id=course_id,
            completed=True
        ).count()
        
        # Get quiz attempts for this course
        quiz_ids = [q.id for q in Quiz.query.filter_by(course_id=course_id).all()]
        quiz_attempts = Progress.query.filter(
            Progress.user_id == student.id,
            Progress.quiz_id.in_(quiz_ids)
        ).all() if quiz_ids else []
        
        completed_quizzes = len(set(q.quiz_id for q in quiz_attempts))
        avg_quiz_score = (
            sum(q.score for q in quiz_attempts) / len(quiz_attempts)
            if quiz_attempts else 0
        )
        
        # Get problems solved for this course
        problem_ids = [p.id for p in CodingProblem.query.filter_by(course_id=course_id).all()]
        problems_solved = ProblemProgress.query.filter(
            ProblemProgress.user_id == student.id,
            ProblemProgress.problem_id.in_(problem_ids),
            ProblemProgress.solved == True
        ).count() if problem_ids else 0
        
        # Calculate overall progress percentage
        total_items = total_lessons + total_quizzes + total_problems
        completed_items = completed_lessons + completed_quizzes + problems_solved
        progress_percentage = (
            int((completed_items / total_items) * 100) if total_items > 0 else 0
        )
        
        students_data.append({
            "student_id": student.id,
            "name": student.name,
            "email": student.email,
            "enrolled_at": enrollment.enrolled_at.isoformat(),
            "level": student.level,
            "xp_points": student.xp_points,
            "progress_percentage": progress_percentage,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "completed_quizzes": completed_quizzes,
            "total_quizzes": total_quizzes,
            "problems_solved": problems_solved,
            "total_problems": total_problems,
            "avg_quiz_score": round(avg_quiz_score, 2),
            "last_activity": enrollment.enrolled_at.isoformat()  # Can be enhanced
        })
    
    return jsonify({
        "course_id": course_id,
        "course_title": course.title,
        "total_students": len(students_data),
        "students": students_data
    })


@teacher_analytics_bp.get("/student/<int:student_id>/performance")
@jwt_required()
def get_student_performance(student_id):
    """Get detailed performance data for a specific student across all teacher's courses"""
    teacher, error_response = _get_teacher()
    if error_response:
        return error_response
    
    student = User.query.get(student_id)
    if not student or student.role != "student":
        return jsonify({"error": "Student not found"}), 404
    
    # Get all courses where student is enrolled AND taught by this teacher
    teacher_courses = Course.query.filter_by(teacher_id=teacher.id).all()
    teacher_course_ids = [c.id for c in teacher_courses]
    
    student_enrollments = Enrollment.query.filter(
        Enrollment.student_id == student_id,
        Enrollment.course_id.in_(teacher_course_ids)
    ).all()
    
    if not student_enrollments:
        return jsonify({"error": "Student not enrolled in any of your courses"}), 403
    
    # Compile performance data
    courses_data = []
    for enrollment in student_enrollments:
        course = enrollment.course
        if not course:
            continue
        
        # Lesson progress
        total_lessons = Lesson.query.filter_by(course_id=course.id).count()
        completed_lessons = LessonProgress.query.filter_by(
            user_id=student_id,
            course_id=course.id,
            completed=True
        ).count()
        
        # Quiz performance
        quiz_attempts = Progress.query.join(Quiz).filter(
            Progress.user_id == student_id,
            Quiz.course_id == course.id
        ).all()
        
        quiz_details = []
        for attempt in quiz_attempts:
            total_questions = len(attempt.quiz.questions) if attempt.quiz.questions else 1
            percentage = (attempt.score / total_questions * 100) if total_questions > 0 else 0
            quiz_details.append({
                "quiz_title": attempt.quiz.title,
                "score": attempt.score,
                "total_questions": total_questions,
                "percentage": round(percentage, 1),
                "difficulty": attempt.quiz.difficulty,
                "attempted_at": attempt.attempted_at.isoformat()
            })
        
        # Problem solving
        problems_in_course = CodingProblem.query.filter_by(course_id=course.id).all()
        problem_ids = [p.id for p in problems_in_course]
        
        problems_solved = ProblemProgress.query.filter(
            ProblemProgress.user_id == student_id,
            ProblemProgress.problem_id.in_(problem_ids),
            ProblemProgress.solved == True
        ).count() if problem_ids else 0
        
        courses_data.append({
            "course_id": course.id,
            "course_title": course.title,
            "enrolled_at": enrollment.enrolled_at.isoformat(),
            "lessons": {
                "completed": completed_lessons,
                "total": total_lessons,
                "percentage": int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
            },
            "quizzes": {
                "attempts": len(quiz_attempts),
                "unique_quizzes": len(set(q.quiz_id for q in quiz_attempts)),
                "avg_score": round(sum(q.score for q in quiz_attempts) / len(quiz_attempts), 2) if quiz_attempts else 0,
                "details": quiz_details[-5:]  # Last 5 attempts
            },
            "problems": {
                "solved": problems_solved,
                "total": len(problem_ids)
            }
        })
    
    return jsonify({
        "student_id": student_id,
        "student_name": student.name,
        "student_email": student.email,
        "level": student.level,
        "xp_points": student.xp_points,
        "daily_streak": student.daily_streak,
        "courses": courses_data
    })


@teacher_analytics_bp.get("/course/<int:course_id>/analytics")
@jwt_required()
def get_course_analytics(course_id):
    """Get comprehensive analytics for a specific course"""
    teacher, error_response = _get_teacher()
    if error_response:
        return error_response
    
    course, error_response = _verify_course_ownership(course_id, teacher.id)
    if error_response:
        return error_response
    
    # Basic course info
    total_students = Enrollment.query.filter_by(course_id=course_id).count()
    
    # Lesson analytics
    total_lessons = Lesson.query.filter_by(course_id=course_id).count()
    lesson_completion_data = []
    
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order_index).all()
    for lesson in lessons:
        completed_count = LessonProgress.query.filter_by(
            lesson_id=lesson.id,
            completed=True
        ).count()
        lesson_completion_data.append({
            "lesson_id": lesson.id,
            "lesson_title": lesson.title,
            "completed_by": completed_count,
            "completion_rate": round((completed_count / total_students * 100), 1) if total_students > 0 else 0
        })
    
    # Quiz analytics
    quizzes = Quiz.query.filter_by(course_id=course_id).all()
    quiz_analytics = []
    
    for quiz in quizzes:
        attempts = Progress.query.filter_by(quiz_id=quiz.id).all()
        if attempts:
            avg_score = sum(a.score for a in attempts) / len(attempts)
            total_questions = len(quiz.questions) if quiz.questions else 1
            avg_percentage = (avg_score / total_questions * 100) if total_questions > 0 else 0
            
            quiz_analytics.append({
                "quiz_id": quiz.id,
                "quiz_title": quiz.title,
                "difficulty": quiz.difficulty,
                "total_attempts": len(attempts),
                "unique_students": len(set(a.user_id for a in attempts)),
                "avg_score": round(avg_score, 2),
                "avg_percentage": round(avg_percentage, 1)
            })
    
    # Problem analytics
    problems = CodingProblem.query.filter_by(course_id=course_id).all()
    problem_analytics = []
    
    for problem in problems:
        solved_count = ProblemProgress.query.filter_by(
            problem_id=problem.id,
            solved=True
        ).count()
        
        total_attempts = CodeSubmission.query.filter_by(problem_id=problem.id).count()
        
        problem_analytics.append({
            "problem_id": problem.id,
            "problem_title": problem.title,
            "difficulty": problem.difficulty,
            "solved_by": solved_count,
            "total_attempts": total_attempts,
            "success_rate": round((solved_count / total_attempts * 100), 1) if total_attempts > 0 else 0
        })
    
    # Engagement metrics - last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    recent_enrollments = Enrollment.query.filter(
        Enrollment.course_id == course_id,
        Enrollment.enrolled_at >= thirty_days_ago
    ).count()
    
    # Get quiz attempts in last 30 days
    quiz_ids = [q.id for q in quizzes]
    recent_quiz_attempts = Progress.query.filter(
        Progress.quiz_id.in_(quiz_ids),
        Progress.attempted_at >= thirty_days_ago
    ).count() if quiz_ids else 0
    
    return jsonify({
        "course_id": course_id,
        "course_title": course.title,
        "course_description": course.description,
        "created_at": course.created_at.isoformat(),
        "overview": {
            "total_students": total_students,
            "total_lessons": total_lessons,
            "total_quizzes": len(quizzes),
            "total_problems": len(problems),
            "recent_enrollments": recent_enrollments,
            "recent_activity": recent_quiz_attempts
        },
        "lesson_analytics": lesson_completion_data,
        "quiz_analytics": quiz_analytics,
        "problem_analytics": problem_analytics
    })


@teacher_analytics_bp.get("/students/overview")
@jwt_required()
def get_all_students_overview():
    """Get overview of all students across all teacher's courses"""
    teacher, error_response = _get_teacher()
    if error_response:
        return error_response
    
    # Get all courses by this teacher
    courses = Course.query.filter_by(teacher_id=teacher.id).all()
    course_ids = [c.id for c in courses]
    
    # Get all unique students
    enrollments = Enrollment.query.filter(
        Enrollment.course_id.in_(course_ids)
    ).all()
    
    student_dict = {}
    for enrollment in enrollments:
        student = enrollment.student
        if not student:
            continue
        
        if student.id not in student_dict:
            student_dict[student.id] = {
                "student_id": student.id,
                "name": student.name,
                "email": student.email,
                "level": student.level,
                "xp_points": student.xp_points,
                "courses_enrolled": [],
                "total_courses": 0
            }
        
        student_dict[student.id]["courses_enrolled"].append({
            "course_id": enrollment.course.id,
            "course_title": enrollment.course.title,
            "enrolled_at": enrollment.enrolled_at.isoformat()
        })
        student_dict[student.id]["total_courses"] += 1
    
    students_list = sorted(
        student_dict.values(),
        key=lambda x: x["xp_points"],
        reverse=True
    )
    
    return jsonify({
        "total_students": len(students_list),
        "students": students_list
    })
