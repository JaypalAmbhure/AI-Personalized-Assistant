from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Expense, SavingsGoal, AIRecommendation, Category
from app.services.finance_service import (
    get_monthly_summary,
    calculate_financial_health_score,
    get_last_six_months_trends,
    get_user_categories
)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    now = datetime.now()
    month = request.args.get('month', now.month, type=int)
    year = request.args.get('year', now.year, type=int)

    summary = get_monthly_summary(current_user.id, month=month, year=year)
    health = calculate_financial_health_score(current_user.id, summary)

    recent_expenses = Expense.query.filter_by(user_id=current_user.id)\
        .order_by(Expense.date.desc(), Expense.id.desc())\
        .limit(8).all()

    active_goals = SavingsGoal.query.filter_by(user_id=current_user.id)\
        .order_by(SavingsGoal.status.asc(), SavingsGoal.target_date.asc())\
        .limit(4).all()

    latest_ai_advice = AIRecommendation.query.filter_by(user_id=current_user.id)\
        .order_by(AIRecommendation.created_at.desc()).first()

    categories = get_user_categories(current_user.id)

    return render_template(
        'dashboard/index.html',
        summary=summary,
        health=health,
        recent_expenses=recent_expenses,
        active_goals=active_goals,
        latest_ai_advice=latest_ai_advice,
        categories=categories,
        selected_month=month,
        selected_year=year,
        current_year=now.year
    )

@dashboard_bp.route('/api/chart-data')
@login_required
def chart_data():
    now = datetime.now()
    month = request.args.get('month', now.month, type=int)
    year = request.args.get('year', now.year, type=int)

    summary = get_monthly_summary(current_user.id, month=month, year=year)
    trends = get_last_six_months_trends(current_user.id)

    # Prepare category donut chart data
    cat_labels = []
    cat_values = []
    cat_colors = []
    for cat in summary['category_analytics']:
        if cat['spent'] > 0:
            cat_labels.append(cat['name'])
            cat_values.append(cat['spent'])
            cat_colors.append(cat['color'])

    # Trend data
    trend_labels = [t['month'] for t in trends]
    trend_incomes = [t['income'] for t in trends]
    trend_expenses = [t['expense'] for t in trends]
    trend_savings = [t['savings'] for t in trends]

    # Needs vs Wants
    needs_wants = {
        'labels': ['Needs (Essentials)', 'Wants (Lifestyle)', 'Net Savings'],
        'values': [summary['needs_total'], summary['wants_total'], max(0, summary['net_savings'])],
        'colors': ['#10b981', '#f59e0b', '#6366f1']
    }

    return jsonify({
        'categories': {
            'labels': cat_labels,
            'values': cat_values,
            'colors': cat_colors
        },
        'trends': {
            'labels': trend_labels,
            'incomes': trend_incomes,
            'expenses': trend_expenses,
            'savings': trend_savings
        },
        'needs_wants': needs_wants,
        'health_score': summary.get('health_score', 0)
    })
