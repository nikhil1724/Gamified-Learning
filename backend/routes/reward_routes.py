from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db
from models import Reward, User, UserReward


reward_bp = Blueprint("rewards", __name__, url_prefix="/api")

REWARD_DEFINITIONS = [
    {
        "badge_name": "Beginner Badge",
        "description": "Complete your first quiz.",
        "xp_required": 0,
        "criteria": "first_quiz",
    },
    {
        "badge_name": "Learner Badge",
        "description": "Earn 100 XP.",
        "xp_required": 100,
        "criteria": "xp_100",
    },
    {
        "badge_name": "Champion Badge",
        "description": "Reach level 5.",
        "xp_required": 0,
        "criteria": "level_5",
    },
]


def _ensure_rewards():
    existing = {reward.badge_name for reward in Reward.query.all()}
    new_rewards = [
        Reward(
            badge_name=definition["badge_name"],
            description=definition["description"],
            xp_required=definition["xp_required"],
        )
        for definition in REWARD_DEFINITIONS
        if definition["badge_name"] not in existing
    ]

    if new_rewards:
        db.session.add_all(new_rewards)
        db.session.commit()


def _serialize_reward(reward: Reward) -> dict:
    return {
        "id": reward.id,
        "badge_name": reward.badge_name,
        "description": reward.description,
        "xp_required": reward.xp_required,
    }


def check_and_unlock_rewards(user: User, first_quiz_completed: bool) -> list[dict]:
    _ensure_rewards()
    unlocked = []

    rewards = Reward.query.all()
    reward_by_name = {reward.badge_name: reward for reward in rewards}
    unlocked_ids = {
        user_reward.reward_id
        for user_reward in UserReward.query.filter_by(user_id=user.id).all()
    }

    def _unlock(badge_name: str):
        reward = reward_by_name.get(badge_name)
        if not reward or reward.id in unlocked_ids:
            return
        user_reward = UserReward(user_id=user.id, reward_id=reward.id)
        db.session.add(user_reward)
        unlocked.append(_serialize_reward(reward))

    if first_quiz_completed:
        _unlock("Beginner Badge")

    if user.xp_points >= 100:
        _unlock("Learner Badge")

    if user.level >= 5:
        _unlock("Champion Badge")

    if unlocked:
        db.session.commit()

    return unlocked


@reward_bp.get("/rewards")
def list_rewards():
    _ensure_rewards()
    rewards = Reward.query.all()
    return jsonify([_serialize_reward(reward) for reward in rewards])


@reward_bp.get("/user/rewards")
@jwt_required()
def list_user_rewards():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_rewards = UserReward.query.filter_by(user_id=user.id).all()
    rewards = [Reward.query.get(ur.reward_id) for ur in user_rewards]
    return jsonify([_serialize_reward(reward) for reward in rewards if reward])
