from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, SavingsGoal, Expense
from app.services.finance_service import get_monthly_summary

savings_bp = Blueprint('savings', __name__, url_prefix='/savings')

@savings_bp.route('')
@savings_bp.route('/')
@login_required
def index():
    goals = SavingsGoal.query.filter_by(user_id=current_user.id)\
        .order_by(SavingsGoal.status.asc(), SavingsGoal.created_at.desc()).all()

    total_target = sum(g.target_amount for g in goals)
    total_saved = sum(g.current_amount for g in goals)
    overall_progress = (total_saved / total_target * 100.0) if total_target > 0 else 0.0

    summary = get_monthly_summary(current_user.id)
    monthly_burn = summary['total_expenses'] if summary['total_expenses'] > 0 else (current_user.monthly_income_target * 0.7 if current_user.monthly_income_target else 2000.0)
    emergency_target = monthly_burn * current_user.emergency_fund_months

    # Find emergency fund goal if exists
    emergency_goal = next((g for g in goals if 'emergency' in g.title.lower()), None)
    emergency_saved = emergency_goal.current_amount if emergency_goal else 0.0
    emergency_months_covered = (emergency_saved / monthly_burn) if monthly_burn > 0 else 0.0

    return render_template(
        'savings/index.html',
        goals=goals,
        total_target=total_target,
        total_saved=total_saved,
        overall_progress=round(overall_progress, 1),
        monthly_burn=monthly_burn,
        emergency_target=emergency_target,
        emergency_saved=emergency_saved,
        emergency_months_covered=round(emergency_months_covered, 1),
        emergency_goal=emergency_goal
    )

@savings_bp.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form.get('title', '').strip()
    target_amount_str = request.form.get('target_amount', '').strip()
    current_amount_str = request.form.get('current_amount', '0').strip()
    target_date_str = request.form.get('target_date', '').strip()
    category = request.form.get('category', 'General Savings')

    if not title or not target_amount_str:
        flash('Goal title and target amount are required.', 'danger')
        return redirect(url_for('savings.index'))

    try:
        target_amount = float(target_amount_str)
        current_amount = float(current_amount_str) if current_amount_str else 0.0
        if target_amount <= 0:
            flash('Target amount must be positive.', 'danger')
            return redirect(url_for('savings.index'))
    except ValueError:
        flash('Invalid numeric amount.', 'danger')
        return redirect(url_for('savings.index'))

    target_date = None
    if target_date_str:
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    goal = SavingsGoal(
        user_id=current_user.id,
        title=title,
        target_amount=target_amount,
        current_amount=current_amount,
        target_date=target_date,
        category=category,
        status='Achieved' if current_amount >= target_amount else 'In Progress'
    )
    db.session.add(goal)
    db.session.commit()
    flash(f'Savings Goal "{title}" created!', 'success')
    return redirect(url_for('savings.index'))

@savings_bp.route('/<int:id>/contribute', methods=['POST'])
@login_required
def contribute(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    amount_str = request.form.get('amount', '').strip()

    if not amount_str:
        flash('Contribution amount is required.', 'danger')
        return redirect(url_for('savings.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash('Contribution must be positive.', 'danger')
            return redirect(url_for('savings.index'))
    except ValueError:
        flash('Invalid amount.', 'danger')
        return redirect(url_for('savings.index'))

    goal.current_amount += amount
    if goal.current_amount >= goal.target_amount:
        goal.status = 'Achieved'
        flash(f'🎉 Congratulations! You achieved your savings goal "{goal.title}"!', 'success')
    else:
        flash(f'Added {current_user.currency}{amount:,.2f} to "{goal.title}". New balance: {current_user.currency}{goal.current_amount:,.2f}.', 'success')

    db.session.commit()
    return redirect(url_for('savings.index'))

@savings_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Savings goal deleted.', 'info')
    return redirect(url_for('savings.index'))
