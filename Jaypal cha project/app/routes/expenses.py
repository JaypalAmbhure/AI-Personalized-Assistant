from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, date
from sqlalchemy import extract
from app.models import db, Expense, Category
from app.services.finance_service import get_user_categories

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@expenses_bp.route('')
@expenses_bp.route('/')
@login_required
def index():
    now = datetime.now()
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    category_id = request.args.get('category_id', type=int)
    search_q = request.args.get('q', '').strip()
    necessity = request.args.get('necessity', '')  # 'need', 'want', or ''
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Expense.query.filter_by(user_id=current_user.id)

    if month and year:
        query = query.filter(
            extract('month', Expense.date) == month,
            extract('year', Expense.date) == year
        )
    if category_id:
        query = query.filter(Expense.category_id == category_id)
    if search_q:
        query = query.filter(Expense.description.ilike(f'%{search_q}%'))
    if necessity == 'need':
        query = query.filter(Expense.is_need == True)
    elif necessity == 'want':
        query = query.filter(Expense.is_need == False)

    pagination = query.order_by(Expense.date.desc(), Expense.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    expenses = pagination.items

    # Compute overall stats on filtered query (or month query)
    all_filtered = query.all()
    total_spent = sum(e.amount for e in all_filtered)
    needs_spent = sum(e.amount for e in all_filtered if e.is_need)
    wants_spent = sum(e.amount for e in all_filtered if not e.is_need)

    categories = get_user_categories(current_user.id)

    return render_template(
        'expenses/index.html',
        expenses=expenses,
        pagination=pagination,
        categories=categories,
        total_spent=total_spent,
        needs_spent=needs_spent,
        wants_spent=wants_spent,
        selected_month=month,
        selected_year=year,
        selected_category=category_id,
        selected_necessity=necessity,
        search_q=search_q,
        current_year=now.year
    )

@expenses_bp.route('/add', methods=['POST'])
@login_required
def add():
    amount_str = request.form.get('amount', '').strip()
    category_id_str = request.form.get('category_id', '').strip()
    description = request.form.get('description', '').strip()
    date_str = request.form.get('date', '').strip()
    payment_method = request.form.get('payment_method', 'Credit Card')
    is_need = request.form.get('is_need') == 'true'

    if not amount_str or not category_id_str or not description:
        flash('Amount, category, and description are required.', 'danger')
        return redirect(url_for('expenses.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash('Expense amount must be positive.', 'danger')
            return redirect(url_for('expenses.index'))
    except ValueError:
        flash('Invalid expense amount.', 'danger')
        return redirect(url_for('expenses.index'))

    try:
        category_id = int(category_id_str)
    except ValueError:
        flash('Invalid category selected.', 'danger')
        return redirect(url_for('expenses.index'))

    expense_date = date.today()
    if date_str:
        try:
            expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    expense = Expense(
        user_id=current_user.id,
        category_id=category_id,
        amount=amount,
        date=expense_date,
        description=description,
        payment_method=payment_method,
        is_need=is_need
    )
    db.session.add(expense)
    db.session.commit()

    flash(f'Expense "{description}" ({current_user.currency}{amount:,.2f}) recorded successfully!', 'success')
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    amount_str = request.form.get('amount', '').strip()
    category_id_str = request.form.get('category_id', '').strip()
    description = request.form.get('description', '').strip()
    date_str = request.form.get('date', '').strip()
    payment_method = request.form.get('payment_method', expense.payment_method)
    is_need = request.form.get('is_need') == 'true'

    if not amount_str or not description:
        flash('Amount and description are required.', 'danger')
        return redirect(url_for('expenses.index'))

    try:
        expense.amount = float(amount_str)
        if expense.amount <= 0:
            flash('Amount must be positive.', 'danger')
            return redirect(url_for('expenses.index'))
    except ValueError:
        flash('Invalid amount.', 'danger')
        return redirect(url_for('expenses.index'))

    if category_id_str:
        expense.category_id = int(category_id_str)

    if date_str:
        try:
            expense.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    expense.description = description
    expense.payment_method = payment_method
    expense.is_need = is_need

    db.session.commit()
    flash('Expense updated successfully.', 'success')
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash('Expense transaction removed.', 'info')
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/category/add', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name', '').strip()
    icon = request.form.get('icon', 'fa-tag').strip()
    color = request.form.get('color', '#6366f1').strip()

    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('expenses.index'))

    existing = Category.query.filter(
        (Category.name.ilike(name)) &
        ((Category.user_id == current_user.id) | (Category.user_id == None))
    ).first()

    if existing:
        flash(f'Category "{name}" already exists.', 'warning')
        return redirect(url_for('expenses.index'))

    cat = Category(
        user_id=current_user.id,
        name=name,
        icon=icon if icon.startswith('fa-') else f'fa-{icon}',
        color=color,
        is_default=False
    )
    db.session.add(cat)
    db.session.commit()
    flash(f'Custom category "{name}" created!', 'success')
    return redirect(url_for('expenses.index'))
