from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db
from models import Quiz, Skill, User, UserSkill


skill_bp = Blueprint("skills", __name__, url_prefix="/api")


def _serialize_skill(skill: Skill, unlocked_ids: set[int]) -> dict:
    return {
        "id": skill.id,
        "skill_name": skill.skill_name,
        "description": skill.description,
        "prerequisite_skill_id": skill.prerequisite_skill_id,
        "quiz_id": skill.quiz.id if skill.quiz else None,
        "unlocked": skill.id in unlocked_ids,
    }


def _build_tree(skills: list[Skill], unlocked_ids: set[int]) -> list[dict]:
    by_parent: dict[int | None, list[Skill]] = {}
    for skill in skills:
        by_parent.setdefault(skill.prerequisite_skill_id, []).append(skill)

    def build_node(node: Skill) -> dict:
        return {
            **_serialize_skill(node, unlocked_ids),
            "children": [build_node(child) for child in by_parent.get(node.id, [])],
        }

    return [build_node(root) for root in by_parent.get(None, [])]


def _get_unlocked_ids(user_id: int | None) -> set[int]:
    if not user_id:
        return set()
    return {
        user_skill.skill_id
        for user_skill in UserSkill.query.filter_by(user_id=user_id, unlocked=True).all()
    }


def _unlock_skill(user: User, skill: Skill) -> bool:
    existing = UserSkill.query.filter_by(user_id=user.id, skill_id=skill.id).first()
    if existing:
        if not existing.unlocked:
            existing.unlocked = True
            existing.unlocked_at = db.func.now()
        return False

    user_skill = UserSkill(user_id=user.id, skill_id=skill.id, unlocked=True)
    db.session.add(user_skill)
    return True


def unlock_skills_for_quiz(user: User, quiz: Quiz) -> list[dict]:
    if not quiz.skill_id:
        return []

    skill = Skill.query.get(quiz.skill_id)
    if not skill:
        return []

    unlocked = []
    unlocked_ids = _get_unlocked_ids(user.id)

    if skill.prerequisite_skill_id and skill.prerequisite_skill_id not in unlocked_ids:
        return []

    if _unlock_skill(user, skill):
        unlocked.append(_serialize_skill(skill, unlocked_ids | {skill.id}))

    next_skills = Skill.query.filter_by(prerequisite_skill_id=skill.id).all()
    for next_skill in next_skills:
        if _unlock_skill(user, next_skill):
            unlocked.append(_serialize_skill(next_skill, unlocked_ids | {next_skill.id}))

    if unlocked:
        db.session.commit()

    return unlocked


@skill_bp.get("/skills")
@jwt_required(optional=True)
def list_skills():
    user_id = get_jwt_identity()
    user_id_int = int(user_id) if user_id else None
    unlocked_ids = _get_unlocked_ids(user_id_int)

    skills = Skill.query.all()
    return jsonify(_build_tree(skills, unlocked_ids))


@skill_bp.get("/user/skills")
@jwt_required()
def list_user_skills():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_skills = UserSkill.query.filter_by(user_id=user.id, unlocked=True).all()
    skills = [Skill.query.get(user_skill.skill_id) for user_skill in user_skills]
    return jsonify([_serialize_skill(skill, {skill.id}) for skill in skills if skill])
