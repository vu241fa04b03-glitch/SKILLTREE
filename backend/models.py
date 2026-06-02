#241fa04b19
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    skills = db.relationship('UserSkill', backref='user', lazy=True)
    badges = db.relationship('UserBadge', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, default=1)
    xp_reward = db.Column(db.Integer, default=10)
    assignment_question = db.Column(db.Text, nullable=False)
    assignment_answer = db.Column(db.String(500), nullable=False)
    prerequisite_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'level': self.level,
            'xp_reward': self.xp_reward,
            'assignment_question': self.assignment_question,
            'prerequisite_skill_id': self.prerequisite_skill_id
        }


class UserSkill(db.Model):
    __tablename__ = 'user_skills'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    status = db.Column(db.String(20), default='locked')  # locked, assigned, completed
    attempts = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime, nullable=True)
    skill = db.relationship('Skill', backref='user_skills')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'status': self.status,
            'attempts': self.attempts,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Badge(db.Model):
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), default='⭐')
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)
    xp_required = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'skill_id': self.skill_id,
            'xp_required': self.xp_required
        }


class UserBadge(db.Model):
    __tablename__ = 'user_badges'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    badge = db.relationship('Badge', backref='user_badges')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'badge_name': self.badge.name if self.badge else None,
            'badge_icon': self.badge.icon if self.badge else None,
            'earned_at': self.earned_at.isoformat()
        }


class UserXP(db.Model):
    __tablename__ = 'user_xp'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    total_xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'total_xp': self.total_xp,
            'level': self.level
        }


class UserSkillProgress(db.Model):
    __tablename__ = 'user_skill_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_skill_id = db.Column(db.Integer, db.ForeignKey('user_skills.id'), nullable=False, unique=True)
    correct_count = db.Column(db.Integer, default=0)
    required_correct = db.Column(db.Integer, default=3)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    user_skill = db.relationship('UserSkill', backref='progress', uselist=False)

    def to_dict(self):
        return {
            'user_skill_id': self.user_skill_id,
            'correct_count': self.correct_count,
            'required_correct': self.required_correct,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
