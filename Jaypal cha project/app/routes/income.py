from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, date
from app.models import db, Income

income_bp = Blueprint('income', __name__, url_prefix='/income')

@income_bp.route('')
@income_bp.route('/')
@login_required
def index():
    now = datetime.now()
    month = request.args.get('month', None, type=int)
    year = request.args.get('year', None, type=int)

    query = Income.query.filter_by(user_id=current_user.id)
    if month and year:
        from sqlalchemy import extract
        query = query.filter(
            extract('month', Income.date) == month,
            extract('year', Income.date) == year
        )
    
    incomes = query.order_by(Income.date.desc(), Income.id.desc()).all()
    total_income = sum(i.amount for i in incomes)

    # Frequency breakdown
    freq_summary = {}
    for i in incomes:
        freq_summary[i.frequency] = freq_summary.get(i.frequency, 0) + i.amount

    return render_template(
        'income/index.html',
        incomes=incomes,
        total_income=total_income,
        freq_summary=freq_summary,
        selected_month=month,
        selected_year=year,
        current_year=now.year
    )

@income_bp.route('/add', methods=['POST'])
@login_required
def add():
    source_name = request.form.get('source_name', '').strip()
    amount_str = request.form.get('amount', '').strip()
    frequency = request.form.get('frequency', 'Monthly')
    date_str = request.form.get('date', '').strip()
    notes = request.form.get('notes', '').strip()

    if not source_name or not amount_str:
        flash('Source name and amount are required.', 'danger')
        return redirect(url_for('income.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash('Amount must be greater than zero.', 'danger')
            return redirect(url_for('income.index'))
    except ValueError:
        flash('Invalid amount entered.', 'danger')
        return redirect(url_for('income.index'))

    income_date = date.today()
    if date_str:
        try:
            income_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    income = Income(
        user_id=current_user.id,
        source_name=source_name,
        amount=amount,
        frequency=frequency,
        date=income_date,
        notes=notes
    )
    db.session.add(income)
    db.session.commit()
    flash(f'Income "{source_name}" of {current_user.currency}{amount:,.2f} recorded!', 'success')
    return redirect(url_for('income.index'))

@income_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    income = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    source_name = request.form.get('source_name', '').strip()
    amount_str = request.form.get('amount', '').strip()
    frequency = request.form.get('frequency', income.frequency)
    date_str = request.form.get('date', '').strip()
    notes = request.form.get('notes', '').strip()

    if not source_name or not amount_str:
        flash('Source name and amount are required.', 'danger')
        return redirect(url_for('income.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash('Amount must be positive.', 'danger')
            return redirect(url_for('income.index'))
    except ValueError:
        flash('Invalid amount.', 'danger')
        return redirect(url_for('income.index'))

    if date_str:
        try:
            income.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    income.source_name = source_name
    income.amount = amount
    income.frequency = frequency
    income.notes = notes

    db.session.commit()
    flash('Income updated successfully.', 'success')
    return redirect(url_for('income.index'))

@income_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    income = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(income)
    db.session.commit()
    flash('Income record deleted.', 'info')
    return redirect(url_for('income.index'))
