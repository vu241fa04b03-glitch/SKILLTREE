# 241fa04b19

from flask import jsonify
from backend.models import Badge, UserBadge


def get_all_badges(user_id):
    all_badges = Badge.query.all()
    result = []
    for badge in all_badges:
        badge_data = badge.to_dict()
        earned = UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first()
        badge_data['earned'] = earned is not None
        badge_data['earned_at'] = earned.earned_at.isoformat() if earned else None
        result.append(badge_data)
    return jsonify({'badges': result}), 200


def get_user_badges(user_id):
    user_badges = UserBadge.query.filter_by(user_id=user_id).all()
    return jsonify({'user_badges': [ub.to_dict() for ub in user_badges]}), 200
