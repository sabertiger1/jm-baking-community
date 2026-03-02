"""经验值与等级服务"""
from sqlalchemy.orm import Session

from mealie.db.models.baking.experience import UserExperience
from mealie.db.models.baking.experience_history import UserExperienceHistory

EXP_SOURCE_CHECKIN = "checkin"
EXP_SOURCE_SUBMIT_WORK = "submit_work"
EXP_SOURCE_RECIPE_COMMENT = "recipe_comment"
EXP_SOURCE_WORK_EXCELLENT = "work_excellent"
EXP_SOURCE_RECEIVE_FLOWER = "receive_flower"

EXP_REWARD = {
    EXP_SOURCE_CHECKIN: 5,
    EXP_SOURCE_SUBMIT_WORK: 15,
    EXP_SOURCE_RECIPE_COMMENT: 5,
    EXP_SOURCE_WORK_EXCELLENT: 30,
    EXP_SOURCE_RECEIVE_FLOWER: 1,
}

LEVELS = [
    {"key": "level-1", "name": "烘焙小白", "emoji": "🧈", "min_exp": 0, "max_exp": 100},
    {"key": "level-2", "name": "面点学徒", "emoji": "🍞", "min_exp": 100, "max_exp": 350},
    {"key": "level-3", "name": "面包技工", "emoji": "🥐", "min_exp": 350, "max_exp": 800},
    {"key": "level-4", "name": "西点匠人", "emoji": "🧁", "min_exp": 800, "max_exp": 1500},
    {"key": "level-5", "name": "曲奇队长", "emoji": "🍪", "min_exp": 1500, "max_exp": 2500},
    {"key": "level-6", "name": "巧克力骑士", "emoji": "🍫", "min_exp": 2500, "max_exp": 4000},
    {"key": "level-7", "name": "马卡龙将军", "emoji": "🎀", "min_exp": 4000, "max_exp": 6500},
    {"key": "level-8", "name": "蛋糕国王", "emoji": "👑", "min_exp": 6500, "max_exp": None},
]


def get_level_meta(total_exp: int) -> dict:
    for level in reversed(LEVELS):
        if total_exp >= level["min_exp"]:
            return level
    return LEVELS[0]


def ensure_user_experience(session: Session, user_id):
    exp_model = session.query(UserExperience).filter(UserExperience.user_id == user_id).first()
    if exp_model:
        return exp_model

    exp_model = UserExperience(session=session, user_id=user_id, total_exp=1)
    session.add(exp_model)
    session.flush()
    return exp_model


def add_experience(session: Session, user_id, amount: int, source: str | None = None, note: str | None = None):
    if amount <= 0:
        return ensure_user_experience(session, user_id)
    exp_model = ensure_user_experience(session, user_id)
    exp_model.total_exp += amount
    if source:
        history = UserExperienceHistory(
            session=session,
            user_id=user_id,
            source=source,
            exp_delta=amount,
            total_exp_after=exp_model.total_exp,
            note=note,
        )
        session.add(history)
    return exp_model


def build_experience_profile(total_exp: int) -> dict:
    level = get_level_meta(total_exp)
    next_level = None
    for candidate in LEVELS:
        if candidate["min_exp"] > level["min_exp"]:
            next_level = candidate
            break
    return {
        "total_exp": total_exp,
        "level_key": level["key"],
        "level_name": level["name"],
        "level_emoji": level["emoji"],
        "current_level_min_exp": level["min_exp"],
        "next_level_min_exp": next_level["min_exp"] if next_level else None,
        "next_level_name": next_level["name"] if next_level else None,
    }


def get_user_experience_profile(session: Session, user_id) -> dict:
    exp_model = session.query(UserExperience).filter(UserExperience.user_id == user_id).first()
    if not exp_model:
        return build_experience_profile(1)
    return build_experience_profile(exp_model.total_exp)
