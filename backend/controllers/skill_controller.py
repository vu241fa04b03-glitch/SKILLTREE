# 241fa04b19

from flask import request, jsonify
from datetime import datetime
from backend.models import db, Skill, UserSkill, UserSkillProgress, UserBadge, Badge, UserXP
import json


def get_all_skills(user_id):
    skills = Skill.query.all()
    result = []
    for skill in skills:    
        skill_data = skill.to_dict()
        user_skill = UserSkill.query.filter_by(user_id=user_id, skill_id=skill.id).first()
        progress = UserSkillProgress.query.filter_by(user_skill_id=user_skill.id).first() if user_skill else None
        skill_data['user_status'] = user_skill.status if user_skill else 'locked'
        skill_data['attempts'] = user_skill.attempts if user_skill else 0
        skill_data['correct_count'] = progress.correct_count if progress else 0
        skill_data['required_correct'] = progress.required_correct if progress else 5
        result.append(skill_data)
    return jsonify({'skills': result}), 200


def get_skill(user_id, skill_id):
    skill = Skill.query.get(skill_id)
    if not skill:
        return jsonify({'error': 'Skill not found'}), 404
    skill_data = skill.to_dict()
    user_skill = UserSkill.query.filter_by(user_id=user_id, skill_id=skill_id).first()
    progress = UserSkillProgress.query.filter_by(user_skill_id=user_skill.id).first() if user_skill else None
    skill_data['user_status'] = user_skill.status if user_skill else 'locked'
    skill_data['attempts'] = user_skill.attempts if user_skill else 0
    skill_data['correct_count'] = progress.correct_count if progress else 0
    skill_data['required_correct'] = progress.required_correct if progress else 5
    return jsonify({'skill': skill_data}), 200


def assign_skill(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    skill_id = data.get('skill_id')
    if not skill_id:
        return jsonify({'error': 'skill_id is required'}), 400

    skill = Skill.query.get(skill_id)
    if not skill:
        return jsonify({'error': 'Skill not found'}), 404

    # Check prerequisite
    if skill.prerequisite_skill_id:
        pre = UserSkill.query.filter_by(
            user_id=user_id,
            skill_id=skill.prerequisite_skill_id,
            status='completed'
        ).first()
        if not pre:
            return jsonify({'error': 'You must complete the prerequisite skill first'}), 403

    existing = UserSkill.query.filter_by(user_id=user_id, skill_id=skill_id).first()
    if existing:
        if existing.status in ('assigned', 'completed'):
            progress = UserSkillProgress.query.filter_by(user_skill_id=existing.id).first()
            if not progress and existing.status != 'completed':
                db.session.add(UserSkillProgress(user_skill_id=existing.id, correct_count=0, required_correct=5))
                db.session.commit()
            return jsonify({'message': 'Skill already assigned or completed', 'user_skill': existing.to_dict()}), 200
        existing.status = 'assigned'
        user_skill = existing
    else:
        user_skill = UserSkill(user_id=user_id, skill_id=skill_id, status='assigned')
        db.session.add(user_skill)
        db.session.flush()

    progress = UserSkillProgress.query.filter_by(user_skill_id=user_skill.id).first()
    if not progress and user_skill.status != 'completed':
        db.session.add(UserSkillProgress(user_skill_id=user_skill.id, correct_count=0, required_correct=5))

    db.session.commit()
    return jsonify({'message': 'Skill assigned successfully', 'user_skill': user_skill.to_dict()}), 200


def submit_assignment(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    skill_id = data.get('skill_id')
    answer = data.get('answer', '')
    try:
        answer = answer.strip()
    except Exception:
        pass
    # optional question index for multi-question assignments
    question_index = data.get('question_index', 0)
    try:
        question_index = int(question_index)
    except Exception:
        question_index = 0

    if not skill_id or answer is None or (isinstance(answer, str) and answer == ''):
        return jsonify({'error': 'skill_id and answer are required'}), 400

    skill = Skill.query.get(skill_id)
    if not skill:
        return jsonify({'error': 'Skill not found'}), 404

    user_skill = UserSkill.query.filter_by(user_id=user_id, skill_id=skill_id).first()
    if not user_skill:
        return jsonify({'error': 'Skill not assigned to you'}), 403
    if user_skill.status == 'completed':
        return jsonify({'message': 'Skill already completed!', 'user_skill': user_skill.to_dict()}), 200

    progress = UserSkillProgress.query.filter_by(user_skill_id=user_skill.id).first()
    if not progress:
        progress = UserSkillProgress(user_skill_id=user_skill.id, correct_count=0, required_correct=5)
        db.session.add(progress)

    user_skill.attempts += 1

    # determine correct answer: support JSON question banks stored in assignment_question
    correct_answer = None
    try:
        questions = json.loads(skill.assignment_question) if skill.assignment_question else None
        if isinstance(questions, list) and len(questions) > 0:
            q = questions[question_index] if 0 <= question_index < len(questions) else questions[0]
            correct_answer = q.get('answer', '')
        else:
            correct_answer = skill.assignment_answer or ''
    except Exception:
        correct_answer = skill.assignment_answer or ''

    # compare answers (case-insensitive for short/mcq)
    is_correct = False
    if correct_answer is None:
        is_correct = False
    else:
        try:
            if isinstance(correct_answer, str):
                if correct_answer.strip().lower() == answer.strip().lower():
                    is_correct = True
                else:
                    # for coding questions, allow substring match of sample answer
                    if len(correct_answer) > 10 and answer.strip().lower().find(correct_answer.strip().lower()) != -1:
                        is_correct = True
            else:
                is_correct = (str(correct_answer).strip().lower() == str(answer).strip().lower())
        except Exception:
            is_correct = False

    if is_correct:
        progress.correct_count += 1
        if progress.correct_count >= progress.required_correct:
            user_skill.status = 'completed'
            user_skill.completed_at = datetime.utcnow()
            db.session.flush()

            xp_record = UserXP.query.filter_by(user_id=user_id).first()
            if not xp_record:
                xp_record = UserXP(user_id=user_id, total_xp=0, level=1)
                db.session.add(xp_record)
            xp_record.total_xp += skill.xp_reward
            xp_record.level = max(1, xp_record.total_xp // 50 + 1)

            next_skills = Skill.query.filter_by(prerequisite_skill_id=skill_id).all()
            unlocked = []
            for ns in next_skills:
                existing = UserSkill.query.filter_by(user_id=user_id, skill_id=ns.id).first()
                if not existing:
                    new_us = UserSkill(user_id=user_id, skill_id=ns.id, status='assigned')
                    db.session.add(new_us)
                    unlocked.append(ns.name)

            badges_earned = []
            badges = Badge.query.filter_by(skill_id=skill_id).all()
            for badge in badges:
                already = UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first()
                if not already:
                    ub = UserBadge(user_id=user_id, badge_id=badge.id)
                    db.session.add(ub)
                    badges_earned.append(badge.to_dict())

            db.session.commit()
            return jsonify({
                'message': 'Correct! Skill completed!',
                'xp_earned': skill.xp_reward,
                'skills_unlocked': unlocked,
                'badges_earned': badges_earned,
                'user_skill': user_skill.to_dict()
            }), 200
        else:
            db.session.commit()
            return jsonify({
                'message': f'Correct! {progress.correct_count}/{progress.required_correct} answers completed. Keep going.',
                'progress': {'correct_count': progress.correct_count, 'required_correct': progress.required_correct},
                'user_skill': user_skill.to_dict()
            }), 200
    else:
        db.session.commit()
        return jsonify({
            'message': 'Wrong answer. Try again!',
            'attempts': user_skill.attempts,
            'progress': {'correct_count': progress.correct_count, 'required_correct': progress.required_correct},
            'user_skill': user_skill.to_dict()
        }), 400


def get_user_skills(user_id):
    user_skills = UserSkill.query.filter_by(user_id=user_id).all()
    return jsonify({'user_skills': [us.to_dict() for us in user_skills]}), 200
