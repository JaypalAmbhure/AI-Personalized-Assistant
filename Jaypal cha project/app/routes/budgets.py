from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, Budget, Category, Expense, Income
from app.services.finance_service import get_user_categories, generate_smart_50_30_20_budget

budgets_bp = Blueprint('budgets', __name__, url_prefix='/budgets')

@budgets_bp.route('')
@budgets_bp.route('/')
@login_required
def index():
    now = datetime.now()
    month = request.args.get('month', now.month, type=int)
    year = request.args.get('year', now.year, type=int)

    categories = get_user_categories(current_user.id)
    budgets = Budget.query.filter_by(user_id=current_user.id, month=month, year=year).all()
    budget_map = {b.category_id: b for b in budgets}

    # Fetch actual spent per category for this month
    from sqlalchemy import extract
    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).all()

    spent_map = {}
    for e in expenses:
        spent_map[e.category_id] = spent_map.get(e.category_id, 0.0) + e.amount

    # Build card data
    budget_items = []
    total_budgeted = 0.0
    total_spent = 0.0
    overbudget_count = 0

    for cat in categories:
        b = budget_map.get(cat.id)
        budgeted = b.budgeted_amount if b else 0.0
        spent = spent_map.get(cat.id, 0.0)
        remaining = budgeted - spent
        pct = (spent / budgeted * 100.0) if budgeted > 0 else (100.0 if spent > 0 else 0.0)
        is_over = spent > budgeted and budgeted > 0

        if is_over:
            overbudget_count += 1

        total_budgeted += budgeted
        total_spent += spent

        budget_items.append({
            'budget_id': b.id if b else None,
            'category_id': cat.id,
            'category_name': cat.name,
            'category_color': cat.color,
            'category_icon': cat.icon,
            'budgeted': budgeted,
            'spent': spent,
            'remaining': remaining,
            'percent_used': round(pct, 1),
            'is_over': is_over
        })

    # Sort: items with budgets first, then highest spend
    budget_items.sort(key=lambda x: (x['budgeted'] > 0, x['spent']), reverse=True)

    overall_utilization = (total_spent / total_budgeted * 100.0) if total_budgeted > 0 else 0.0

    return render_template(
        'budgets/index.html',
        budget_items=budget_items,
        total_budgeted=total_budgeted,
        total_spent=total_spent,
        overbudget_count=overbudget_count,
        overall_utilization=round(overall_utilization, 1),
        categories=categories,
        selected_month=month,
        selected_year=year,
        current_year=now.year
    )

@budgets_bp.route('/set', methods=['POST'])
@login_required
def set_budget():
    category_id = request.form.get('category_id', type=int)
    month = request.form.get('month', datetime.now().month, type=int)
    year = request.form.get('year', datetime.now().year, type=int)
    amount_str = request.form.get('budgeted_amount', '').strip()

    if not category_id or not amount_str:
        flash('Category and budgeted amount are required.', 'danger')
        return redirect(url_for('budgets.index', month=month, year=year))

    try:
        amount = float(amount_str)
        if amount < 0:
            flash('Budget amount cannot be negative.', 'danger')
            return redirect(url_for('budgets.index', month=month, year=year))
    except ValueError:
        flash('Invalid budget amount.', 'danger')
        return redirect(url_for('budgets.index', month=month, year=year))

    budget = Budget.query.filter_by(
        user_id=current_user.id,
        category_id=category_id,
        month=month,
        year=year
    ).first()

    if budget:
        budget.budgeted_amount = amount
    else:
        budget = Budget(
            user_id=current_user.id,
            category_id=category_id,
            month=month,
            year=year,
            budgeted_amount=amount
        )
        db.session.add(budget)

    db.session.commit()
    cat = db.session.get(Category, category_id)
    cat_name = cat.name if cat else 'Category'
    flash(f'Budget for "{cat_name}" set to {current_user.currency}{amount:,.2f} for {month}/{year}.', 'success')
    return redirect(url_for('budgets.index', month=month, year=year))

@budgets_bp.route('/auto-generate', methods=['POST'])
@login_required
def auto_generate():
    month = request.form.get('month', datetime.now().month, type=int)
    year = request.form.get('year', datetime.now().year, type=int)

    # Determine baseline monthly income
    from sqlalchemy import extract
    monthly_incomes = Income.query.filter(
        Income.user_id == current_user.id,
        extract('month', Income.date) == month,
        extract('year', Income.date) == year
    ).all()
    total_income = sum(i.amount for i in monthly_incomes)

    if total_income <= 0:
        total_income = current_user.monthly_income_target

    if total_income <= 0:
        flash('Please record your monthly income or update your profile monthly income target first.', 'warning')
        return redirect(url_for('budgets.index', month=month, year=year))

    smart_plan = generate_smart_50_30_20_budget(current_user.id, total_income)

    for item in smart_plan['allocations']:
        b = Budget.query.filter_by(
            user_id=current_user.id,
            category_id=item['category_id'],
            month=month,
            year=year
        ).first()

        if b:
            b.budgeted_amount = item['amount']
        else:
            b = Budget(
                user_id=current_user.id,
                category_id=item['category_id'],
                month=month,
                year=year,
                budgeted_amount=item['amount']
            )
            db.session.add(b)

    db.session.commit()
    flash(f'AI Smart 50/30/20 Budget generated & applied based on {current_user.currency}{total_income:,.2f} income!', 'success')
    return redirect(url_for('budgets.index', month=month, year=year))

@budgets_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    month = budget.month
    year = budget.year
    db.session.delete(budget)
    db.session.commit()
    flash('Budget allocation cleared.', 'info')
    return redirect(url_for('budgets.index', month=month, year=year))
