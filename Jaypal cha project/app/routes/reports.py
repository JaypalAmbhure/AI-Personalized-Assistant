import csv
import io
from flask import Blueprint, render_template, request, Response
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import extract
from app.models import Expense, Income, AIRecommendation
from app.services.finance_service import get_monthly_summary, calculate_financial_health_score

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('')
@reports_bp.route('/')
@login_required
def index():
    now = datetime.now()
    month = request.args.get('month', now.month, type=int)
    year = request.args.get('year', now.year, type=int)

    summary = get_monthly_summary(current_user.id, month=month, year=year)
    health = calculate_financial_health_score(current_user.id, summary)

    # Detailed expenses for selected month
    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).order_by(Expense.date.desc()).all()

    # Incomes for selected month
    incomes = Income.query.filter(
        Income.user_id == current_user.id,
        extract('month', Income.date) == month,
        extract('year', Income.date) == year
    ).order_by(Income.date.desc()).all()

    latest_ai_audit = AIRecommendation.query.filter_by(user_id=current_user.id)\
        .order_by(AIRecommendation.created_at.desc()).first()

    return render_template(
        'reports/index.html',
        summary=summary,
        health=health,
        expenses=expenses,
        incomes=incomes,
        latest_ai_audit=latest_ai_audit,
        selected_month=month,
        selected_year=year,
        current_year=now.year
    )

@reports_bp.route('/export/csv')
@login_required
def export_csv():
    now = datetime.now()
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    # Fetch expenses & incomes
    exp_q = Expense.query.filter_by(user_id=current_user.id)
    inc_q = Income.query.filter_by(user_id=current_user.id)

    if month and year:
        exp_q = exp_q.filter(extract('month', Expense.date) == month, extract('year', Expense.date) == year)
        inc_q = inc_q.filter(extract('month', Income.date) == month, extract('year', Income.date) == year)

    expenses = exp_q.order_by(Expense.date.desc()).all()
    incomes = inc_q.order_by(Income.date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # CSV Header
    writer.writerow(['Type', 'Date', 'Category / Source', 'Description / Frequency', 'Amount', 'Payment Method / Notes', 'Classification'])

    for inc in incomes:
        writer.writerow([
            'Income',
            inc.date.strftime('%Y-%m-%d'),
            inc.source_name,
            inc.frequency,
            f"{inc.amount:.2f}",
            inc.notes or '',
            'Inflow'
        ])

    for exp in expenses:
        writer.writerow([
            'Expense',
            exp.date.strftime('%Y-%m-%d'),
            exp.category.name if exp.category else 'General',
            exp.description,
            f"-{exp.amount:.2f}",
            exp.payment_method,
            'Need' if exp.is_need else 'Want'
        ])

    output.seek(0)
    filename = f"finance_report_{current_user.username}_{month or 'all'}_{year or 'all'}.csv"

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
