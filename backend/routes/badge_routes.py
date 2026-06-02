# 241fa04b03


from flask import Blueprint
from backend.controllers.badge_controller import get_all_badges, get_user_badges
from backend.middleware.auth_middleware import token_required, get_current_user_id

badge_bp = Blueprint('badges', __name__, url_prefix='/api/badges')


@badge_bp.route('/', methods=['GET'])
@token_required
def all_badges():
    user_id = get_current_user_id()
    return get_all_badges(user_id)


@badge_bp.route('/my',methods=['GET'])
@token_required
def my_badges():
    user_id = get_current_user_id()
    return get_user_badges(user_id)
