from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime, timedelta
from sqlalchemy import func

from database import db
from models import User, Progress, CodeSubmission, ProblemProgress

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api")


@analytics_bp.get("/analytics/xp-history")
@jwt_required()
def get_xp_history():
    """Get XP progression over the last 30 days"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get quiz submissions from the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    quizzes = Progress.query.filter(
        Progress.user_id == user.id,
        Progress.attempted_at >= thirty_days_ago
    ).order_by(Progress.attempted_at).all()
    
    # Aggregate XP by date
    xp_by_date = {}
    for quiz in quizzes:
        date_key = quiz.attempted_at.strftime("%Y-%m-%d")
        xp_earned = quiz.score * 10  # Assuming 10 XP per question
        
        if date_key not in xp_by_date:
            xp_by_date[date_key] = {"xp": 0, "quizzes": 0}
        
        xp_by_date[date_key]["xp"] += xp_earned
        xp_by_date[date_key]["quizzes"] += 1
    
    # Create list of data points for the last 30 days
    data = []
    current_date = datetime.utcnow().date()
    
    for i in range(29, -1, -1):
        date = current_date - timedelta(days=i)
        date_key = date.strftime("%Y-%m-%d")
        entry = xp_by_date.get(date_key, {"xp": 0, "quizzes": 0})
        
        data.append({
            "date": date_key,
            "xp": entry["xp"],
            "quizzes": entry["quizzes"]
        })
    
    return jsonify({
        "data": data,
        "total_xp": user.xp_points,
        "level": user.level
    })


@analytics_bp.get("/analytics/quiz-scores")
@jwt_required()
def get_quiz_scores():
    """Get quiz scores over time"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get last 20 quiz attempts
    quizzes = Progress.query.filter_by(user_id=user.id).order_by(
        Progress.attempted_at.desc()
    ).limit(20).all()
    
    # Reverse to show chronologically
    quizzes = list(reversed(quizzes))
    
    data = []
    for idx, quiz in enumerate(quizzes):
        total_questions = len(quiz.quiz.questions) if quiz.quiz.questions else 1
        score_percentage = (quiz.score / total_questions * 100) if total_questions > 0 else 0
        
        data.append({
            "id": idx + 1,
            "quiz_title": quiz.quiz.title[:15] + "..." if len(quiz.quiz.title) > 15 else quiz.quiz.title,
            "full_title": quiz.quiz.title,
            "score": quiz.score,
            "total_questions": total_questions,
            "percentage": round(score_percentage, 1),
            "date": quiz.attempted_at.strftime("%Y-%m-%d %H:%M"),
            "difficulty": quiz.quiz.difficulty
        })
    
    return jsonify({
        "data": data,
        "total_quizzes": Progress.query.filter_by(user_id=user.id).count(),
        "average_score": sum(d["score"] for d in data) / len(data) if data else 0
    })


@analytics_bp.get("/analytics/problems-solved")
@jwt_required()
def get_problems_solved():
    """Get problems solved over time"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get problems solved in the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    submissions = CodeSubmission.query.filter(
        CodeSubmission.user_id == user.id,
        CodeSubmission.status == "Accepted",
        CodeSubmission.created_at >= thirty_days_ago
    ).order_by(CodeSubmission.created_at).all()
    
    # Aggregate by date
    solved_by_date = {}
    for submission in submissions:
        date_key = submission.created_at.strftime("%Y-%m-%d")
        
        if date_key not in solved_by_date:
            solved_by_date[date_key] = {"solved": 0, "failed": 0}
        
        solved_by_date[date_key]["solved"] += 1
    
    # Also get failed submissions for the same period
    failed_submissions = CodeSubmission.query.filter(
        CodeSubmission.user_id == user.id,
        CodeSubmission.status != "Accepted",
        CodeSubmission.created_at >= thirty_days_ago
    ).order_by(CodeSubmission.created_at).all()
    
    for submission in failed_submissions:
        date_key = submission.created_at.strftime("%Y-%m-%d")
        
        if date_key not in solved_by_date:
            solved_by_date[date_key] = {"solved": 0, "failed": 0}
        
        solved_by_date[date_key]["failed"] += 1
    
    # Create list of data points for the last 30 days
    data = []
    current_date = datetime.utcnow().date()
    
    for i in range(29, -1, -1):
        date = current_date - timedelta(days=i)
        date_key = date.strftime("%Y-%m-%d")
        entry = solved_by_date.get(date_key, {"solved": 0, "failed": 0})
        
        data.append({
            "date": date_key,
            "solved": entry["solved"],
            "failed": entry["failed"],
            "total": entry["solved"] + entry["failed"]
        })
    
    # Get total stats
    total_solved = ProblemProgress.query.filter(
        ProblemProgress.user_id == user.id,
        ProblemProgress.solved == True
    ).count()
    
    return jsonify({
        "data": data,
        "total_solved": total_solved,
        "total_submissions": CodeSubmission.query.filter_by(user_id=user.id).count()
    })


@analytics_bp.get("/analytics/summary")
@jwt_required()
def get_analytics_summary():
    """Get overall analytics summary"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Total quizzes completed
    total_quizzes = Progress.query.filter_by(user_id=user.id).count()
    
    # Average quiz score
    quizzes = Progress.query.filter_by(user_id=user.id).all()
    avg_quiz_score = sum(q.score for q in quizzes) / len(quizzes) if quizzes else 0
    
    # Total problems solved
    total_problems_solved = ProblemProgress.query.filter(
        ProblemProgress.user_id == user.id,
        ProblemProgress.solved == True
    ).count()
    
    # Total submissions
    total_submissions = CodeSubmission.query.filter_by(user_id=user.id).count()
    
    # Acceptance rate
    accepted = CodeSubmission.query.filter(
        CodeSubmission.user_id == user.id,
        CodeSubmission.status == "Accepted"
    ).count()
    acceptance_rate = (accepted / total_submissions * 100) if total_submissions > 0 else 0
    
    return jsonify({
        "total_quizzes": total_quizzes,
        "average_quiz_score": round(avg_quiz_score, 2),
        "total_problems_solved": total_problems_solved,
        "total_submissions": total_submissions,
        "acceptance_rate": round(acceptance_rate, 1),
        "current_level": user.level,
        "current_xp": user.xp_points
    })
