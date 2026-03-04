from __future__ import annotations

from collections import Counter
from statistics import mean

from models import Progress, Quiz, Skill, UserSkill


def _get_recent_progress(user_id: int, limit: int = 10) -> list[Progress]:
    return (
        Progress.query.filter_by(user_id=user_id)
        .order_by(Progress.attempted_at.desc())
        .limit(limit)
        .all()
    )


def _compute_accuracy(progress_entries: list[Progress]) -> float:
    if not progress_entries:
        return 0.0

    total_correct = 0
    total_questions = 0

    for entry in progress_entries:
        quiz = Quiz.query.get(entry.quiz_id)
        if not quiz:
            continue
        question_count = len(quiz.questions)
        if question_count == 0:
            continue
        total_correct += entry.score
        total_questions += question_count

    if total_questions == 0:
        return 0.0

    return (total_correct / total_questions) * 100


def _compute_average_score(progress_entries: list[Progress]) -> float:
    scores = [entry.score for entry in progress_entries]
    return float(mean(scores)) if scores else 0.0


def _compute_trend(progress_entries: list[Progress]) -> str:
    if len(progress_entries) < 2:
        return "steady"

    recent_scores = [entry.score for entry in progress_entries[:3]]
    if len(recent_scores) < 2:
        return "steady"

    if recent_scores[0] > recent_scores[-1]:
        return "declining"
    if recent_scores[0] < recent_scores[-1]:
        return "improving"
    return "steady"


def _find_weak_topics(progress_entries: list[Progress]) -> list[str]:
    weak_topics = []
    for entry in progress_entries:
        quiz = Quiz.query.get(entry.quiz_id)
        if not quiz or not quiz.questions:
            continue
        accuracy = entry.score / len(quiz.questions)
        if accuracy < 0.5:
            weak_topics.append(quiz.topic)

    return [topic for topic, _ in Counter(weak_topics).most_common(3)]


def _compute_topic_accuracy(progress_entries: list[Progress]) -> list[dict]:
    topic_totals: dict[str, dict[str, float]] = {}

    for entry in progress_entries:
        quiz = Quiz.query.get(entry.quiz_id)
        if not quiz or not quiz.questions:
            continue

        topic = quiz.topic or "General"
        total_questions = len(quiz.questions)
        correct = entry.score

        if topic not in topic_totals:
            topic_totals[topic] = {"correct": 0.0, "total": 0.0}

        topic_totals[topic]["correct"] += float(correct)
        topic_totals[topic]["total"] += float(total_questions)

    topic_accuracy = []
    for topic, totals in topic_totals.items():
        total = totals["total"]
        correct = totals["correct"]
        accuracy = (correct / total) * 100 if total else 0.0
        topic_accuracy.append(
            {
                "topic": topic,
                "accuracy": round(accuracy, 2),
                "correct": int(correct),
                "total_questions": int(total),
            }
        )

    return sorted(topic_accuracy, key=lambda item: item["accuracy"], reverse=True)


def _recommend_quizzes(
    difficulty: str,
    weak_topics: list[str],
    attempted_quiz_ids: set[int],
    limit: int = 5,
) -> list[dict]:
    query = Quiz.query

    if weak_topics:
        query = query.filter(Quiz.topic.in_(weak_topics))
    elif difficulty:
        query = query.filter_by(difficulty=difficulty)

    if attempted_quiz_ids:
        query = query.filter(~Quiz.id.in_(attempted_quiz_ids))

    quizzes = query.limit(limit).all()

    return [
        {
            "id": quiz.id,
            "title": quiz.title,
            "topic": quiz.topic,
            "difficulty": quiz.difficulty,
        }
        for quiz in quizzes
    ]


def _recommend_skills(user_id: int, limit: int = 5) -> list[dict]:
    unlocked_skill_ids = {
        user_skill.skill_id
        for user_skill in UserSkill.query.filter_by(user_id=user_id, unlocked=True).all()
    }

    recommended = []

    if unlocked_skill_ids:
        next_skills = Skill.query.filter(Skill.prerequisite_skill_id.in_(unlocked_skill_ids)).all()
        for skill in next_skills:
            if skill.id not in unlocked_skill_ids:
                recommended.append(skill)
    else:
        recommended = Skill.query.filter_by(prerequisite_skill_id=None).all()

    return [
        {
            "id": skill.id,
            "skill_name": skill.skill_name,
            "description": skill.description,
            "prerequisite_skill_id": skill.prerequisite_skill_id,
        }
        for skill in recommended[:limit]
    ]


def analyze_user_performance(user_id: int) -> dict:
    progress_entries = _get_recent_progress(user_id)
    accuracy = _compute_accuracy(progress_entries)
    average_score = _compute_average_score(progress_entries)
    trend = _compute_trend(progress_entries)
    topic_accuracy = _compute_topic_accuracy(progress_entries)

    weak_topics = _find_weak_topics(progress_entries)
    attempted_quiz_ids = {entry.quiz_id for entry in progress_entries}

    difficulty_suggestion = "Medium"
    if accuracy > 80:
        difficulty_suggestion = "Hard"
    elif accuracy < 50:
        difficulty_suggestion = "Easy"

    recommended_quizzes = _recommend_quizzes(
        difficulty=difficulty_suggestion,
        weak_topics=weak_topics,
        attempted_quiz_ids=attempted_quiz_ids,
    )

    recommended_skills = _recommend_skills(user_id)

    return {
        "recommended_quizzes": recommended_quizzes,
        "recommended_skills": recommended_skills,
        "difficulty_suggestion": difficulty_suggestion,
        "performance_summary": {
            "accuracy_percentage": round(accuracy, 2),
            "average_score": round(average_score, 2),
            "trend": trend,
            "weak_topics": weak_topics,
            "topic_accuracy": topic_accuracy,
        },
    }
