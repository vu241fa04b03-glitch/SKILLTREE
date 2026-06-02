# 241fa04b19

from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from backend.models import db, User, UserXP, UserSkill, UserSkillProgress, Skill


def signup():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not username or not email or not password:
        return jsonify({'error': 'Username, email and password are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    hashed_pw = generate_password_hash(password)
    user = User(username=username, email=email, password_hash=hashed_pw)
    db.session.add(user)
    db.session.flush()


    xp = UserXP(user_id=user.id, total_xp=0, level=1)
    db.session.add(xp)

    starter_skills = Skill.query.filter_by(prerequisite_skill_id=None).all()
    db.session.flush()
    for skill in starter_skills:
        us = UserSkill(user_id=user.id, skill_id=skill.id, status='assigned')
        db.session.add(us)
    db.session.flush()
    for skill in starter_skills:
        user_skill = UserSkill.query.filter_by(user_id=user.id, skill_id=skill.id).first()
        if user_skill:
            db.session.add(UserSkillProgress(user_skill_id=user_skill.id, correct_count=0, required_correct=5))

    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return jsonify({'message': 'Account created successfully', 'token': token, 'user': user.to_dict()}), 201


def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({'message': 'Login successful', 'token': token, 'user': user.to_dict()}), 200


def get_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    xp = UserXP.query.filter_by(user_id=user_id).first()
    return jsonify({
        'user': user.to_dict(),
        'xp': xp.to_dict() if xp else {'total_xp': 0, 'level': 1}
    }), 200
