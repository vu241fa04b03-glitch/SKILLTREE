# 241fa04b03

from flask import Blueprint
from controllers.skill_controller import (
    get_all_skills, get_skill, assign_skill,
    submit_assignment, get_user_skills
)
from middleware.auth_middleware import token_required, get_current_user_id

skill_bp = Blueprint('skills', __name__, url_prefix='/api/skills')


@skill_bp.route('/', methods=['GET'])
@token_required
def all_skills():
    user_id = get_current_user_id()
    return get_all_skills(user_id)


@skill_bp.route('/<int:skill_id>', methods=['GET'])
@token_required
def one_skill(skill_id):
    user_id = get_current_user_id()
    return get_skill(user_id, skill_id)


@skill_bp.route('/assign', methods=['POST'])
@token_required
def assign():
    user_id = get_current_user_id()
    return assign_skill(user_id)    


@skill_bp.route('/submit', methods=['POST'])
@token_required
def submit():
    user_id = get_current_user_id()
    return submit_assignment(user_id)


@skill_bp.route('/my', methods=['GET'])
@token_required
def my_skills():
    user_id = get_current_user_id()
    return get_user_skills(user_id)
