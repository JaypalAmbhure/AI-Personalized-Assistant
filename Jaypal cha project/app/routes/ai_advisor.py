from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, AIRecommendation, Expense, SavingsGoal
from app.services.finance_service import get_monthly_summary, calculate_financial_health_score
from app.services.ai_service import AIService

ai_advisor_bp = Blueprint('ai_advisor', __name__, url_prefix='/ai-advisor')
ai_service = AIService()

def get_user_profile_payload():
    return {
        'username': current_user.username,
        'email': current_user.email,
        'currency': current_user.currency,
        'monthly_income_target': current_user.monthly_income_target,
        'emergency_fund_months': current_user.emergency_fund_months,
        'risk_tolerance': current_user.risk_tolerance,
        'financial_goal': current_user.financial_goal
    }

@ai_advisor_bp.route('')
@ai_advisor_bp.route('/')
@login_required
def index():
    summary = get_monthly_summary(current_user.id)
    health = calculate_financial_health_score(current_user.id, summary)

    history = AIRecommendation.query.filter_by(user_id=current_user.id)\
        .order_by(AIRecommendation.created_at.desc()).limit(10).all()

    return render_template(
        'ai_advisor/index.html',
        summary=summary,
        health=health,
        history=history
    )

@ai_advisor_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Message cannot be empty.'}), 400

    user_profile = get_user_profile_payload()
    summary = get_monthly_summary(current_user.id)

    reply = ai_service.chat_advisory(user_profile, summary, user_message)

    return jsonify({
        'reply': reply,
        'status': 'success'
    })

@ai_advisor_bp.route('/api/generate-budget-plan', methods=['POST'])
@login_required
def generate_budget_plan():
    user_profile = get_user_profile_payload()
    summary = get_monthly_summary(current_user.id)
    health = calculate_financial_health_score(current_user.id, summary)

    advice_content = ai_service.generate_budget_advice(user_profile, summary)

    # Save to history
    rec = AIRecommendation(
        user_id=current_user.id,
        recommendation_type='budget_plan',
        title='AI 50/30/20 Budget Optimization Plan',
        content=advice_content,
        financial_health_score=health['total_score']
    )
    db.session.add(rec)
    db.session.commit()

    return jsonify({
        'title': rec.title,
        'content': rec.content,
        'financial_health_score': rec.financial_health_score,
        'created_at': rec.created_at.strftime('%Y-%m-%d %H:%M')
    })

@ai_advisor_bp.route('/api/analyze-spending', methods=['POST'])
@login_required
def analyze_spending():
    user_profile = get_user_profile_payload()
    summary = get_monthly_summary(current_user.id)
    health = calculate_financial_health_score(current_user.id, summary)

    recent_expenses = Expense.query.filter_by(user_id=current_user.id)\
        .order_by(Expense.date.desc()).limit(15).all()
    expense_dicts = [e.to_dict() for e in recent_expenses]

    analysis = ai_service.analyze_spending_habits(user_profile, summary, expense_dicts)

    rec = AIRecommendation(
        user_id=current_user.id,
        recommendation_type='spending_analysis',
        title='Forensic Spending Audit & Overspending Detection',
        content=analysis,
        financial_health_score=health['total_score']
    )
    db.session.add(rec)
    db.session.commit()

    return jsonify({
        'title': rec.title,
        'content': rec.content,
        'financial_health_score': rec.financial_health_score,
        'created_at': rec.created_at.strftime('%Y-%m-%d %H:%M')
    })

@ai_advisor_bp.route('/api/savings-strategy', methods=['POST'])
@login_required
def savings_strategy():
    user_profile = get_user_profile_payload()
    summary = get_monthly_summary(current_user.id)
    health = calculate_financial_health_score(current_user.id, summary)

    goals = SavingsGoal.query.filter_by(user_id=current_user.id).all()
    goal_dicts = [g.to_dict() for g in goals]

    strategy = ai_service.generate_savings_strategy(user_profile, summary, goal_dicts)

    rec = AIRecommendation(
        user_id=current_user.id,
        recommendation_type='savings_strategy',
        title='Wealth Building & Savings Acceleration Roadmap',
        content=strategy,
        financial_health_score=health['total_score']
    )
    db.session.add(rec)
    db.session.commit()

    return jsonify({
        'title': rec.title,
        'content': rec.content,
        'financial_health_score': rec.financial_health_score,
        'created_at': rec.created_at.strftime('%Y-%m-%d %H:%M')
    })
