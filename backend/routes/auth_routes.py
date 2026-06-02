# 241fa04b03

from flask import Blueprint
from controllers.auth_controller import signup, login, get_profile
from middleware.auth_middleware import token_required, get_current_user_id

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup_route():
    return signup()

@auth_bp.route('/login', methods=['POST'])
def login_route():
    return login()

@auth_bp.route('/profile', methods=['GET'])
@token_required
def profile_route():
    user_id = get_current_user_id()
    return get_profile(user_id)

