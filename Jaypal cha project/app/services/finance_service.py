from datetime import datetime, date
from collections import defaultdict
from sqlalchemy import func, extract
from app.models import db, User, Income, Expense, Budget, SavingsGoal, Category

def get_current_month_year():
    now = datetime.now()
    return now.month, now.year

def get_user_categories(user_id):
    """Fetch all default categories plus user-created custom categories."""
    return Category.query.filter(
        (Category.user_id == None) | (Category.user_id == user_id)
    ).order_by(Category.name.asc()).all()

def get_monthly_summary(user_id, month=None, year=None):
    """
    Compute comprehensive monthly financial summary for the user:
    - Total income
    - Total expenses
    - Net cash flow & savings rate
    - Needs vs Wants breakdown
    - Category-wise spending
    - Budget utilization
    """
    if month is None or year is None:
        month, year = get_current_month_year()

    # Total Income for selected month
    incomes = Income.query.filter(
        Income.user_id == user_id,
        extract('month', Income.date) == month,
        extract('year', Income.date) == year
    ).all()
    total_income = sum(i.amount for i in incomes)

    # If monthly income recorded is 0, check user's target profile monthly income
    user = db.session.get(User, user_id)
    effective_income = total_income if total_income > 0 else (user.monthly_income_target if user else 0.0)

    # Expenses for selected month
    expenses = Expense.query.filter(
        Expense.user_id == user_id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).all()
    total_expenses = sum(e.amount for e in expenses)

    # Net Cash flow and savings rate
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100.0) if total_income > 0 else 0.0
    if savings_rate < 0:
        savings_rate = 0.0

    # Needs vs Wants Breakdown
    needs_total = sum(e.amount for e in expenses if e.is_need)
    wants_total = sum(e.amount for e in expenses if not e.is_need)
    needs_pct = (needs_total / total_expenses * 100.0) if total_expenses > 0 else 0.0
    wants_pct = (wants_total / total_expenses * 100.0) if total_expenses > 0 else 0.0

    # Category Breakdown
    cat_spend = defaultdict(float)
    cat_details = {}
    for e in expenses:
        cat_spend[e.category_id] += e.amount
        if e.category_id not in cat_details and e.category:
            cat_details[e.category_id] = {
                'id': e.category.id,
                'name': e.category.name,
                'color': e.category.color,
                'icon': e.category.icon
            }

    # Budgets for month
    budgets = Budget.query.filter_by(user_id=user_id, month=month, year=year).all()
    budget_map = {b.category_id: b.budgeted_amount for b in budgets}
    total_budgeted = sum(budget_map.values())

    category_analytics = []
    # Include all categories with spending or budget
    all_cat_ids = set(cat_spend.keys()).union(set(budget_map.keys()))
    for cid in all_cat_ids:
        cat = db.session.get(Category, cid)
        spent = cat_spend.get(cid, 0.0)
        budgeted = budget_map.get(cid, 0.0)
        pct_used = (spent / budgeted * 100.0) if budgeted > 0 else (100.0 if spent > 0 else 0.0)
        is_over = spent > budgeted and budgeted > 0
        
        category_analytics.append({
            'category_id': cid,
            'name': cat.name if cat else 'Other',
            'color': cat.color if cat else '#6366f1',
            'icon': cat.icon if cat else 'fa-tag',
            'spent': spent,
            'budgeted': budgeted,
            'percent_used': round(pct_used, 1),
            'is_over': is_over,
            'over_amount': round(spent - budgeted, 2) if is_over else 0.0
        })

    # Sort categories by highest spend
    category_analytics.sort(key=lambda x: x['spent'], reverse=True)

    # Savings goals summary
    goals = SavingsGoal.query.filter_by(user_id=user_id).all()
    total_goal_target = sum(g.target_amount for g in goals)
    total_goal_saved = sum(g.current_amount for g in goals)
    goals_progress = (total_goal_saved / total_goal_target * 100.0) if total_goal_target > 0 else 0.0

    return {
        'month': month,
        'year': year,
        'total_income': round(total_income, 2),
        'effective_income': round(effective_income, 2),
        'total_expenses': round(total_expenses, 2),
        'net_savings': round(net_savings, 2),
        'savings_rate': round(savings_rate, 1),
        'needs_total': round(needs_total, 2),
        'wants_total': round(wants_total, 2),
        'needs_pct': round(needs_pct, 1),
        'wants_pct': round(wants_pct, 1),
        'total_budgeted': round(total_budgeted, 2),
        'budget_utilization': round((total_expenses / total_budgeted * 100.0), 1) if total_budgeted > 0 else 0.0,
        'category_analytics': category_analytics,
        'incomes_count': len(incomes),
        'expenses_count': len(expenses),
        'goals_count': len(goals),
        'total_goal_target': round(total_goal_target, 2),
        'total_goal_saved': round(total_goal_saved, 2),
        'goals_progress': round(goals_progress, 1)
    }

def calculate_financial_health_score(user_id, summary=None):
    """
    Calculates a comprehensive Financial Health Score (0 - 100):
    - Savings Rate (Max 25 pts)
    - Budget Adherence (Max 25 pts)
    - Needs vs Wants Balance (50/30 Rule) (Max 25 pts)
    - Emergency Fund Reserve (Max 25 pts)
    """
    if summary is None:
        summary = get_monthly_summary(user_id)

    user = db.session.get(User, user_id)
    total_income = summary['total_income']
    total_expenses = summary['total_expenses']
    savings_rate = summary['savings_rate']

    score_components = {}
    recommendations = []

    # 1. Savings Rate Score (0 - 25)
    if savings_rate >= 25.0:
        savings_score = 25
        score_components['savings'] = {'score': 25, 'max': 25, 'status': 'Excellent (Saving > 25%)'}
    elif savings_rate >= 20.0:
        savings_score = 22
        score_components['savings'] = {'score': 22, 'max': 25, 'status': 'Optimal (Hitting 20% rule)'}
    elif savings_rate >= 10.0:
        savings_score = 15
        score_components['savings'] = {'score': 15, 'max': 25, 'status': 'Moderate (10%-20% saved)'}
        recommendations.append("Increase your monthly savings rate to at least 20% to accelerate wealth building.")
    elif savings_rate > 0:
        savings_score = 8
        score_components['savings'] = {'score': 8, 'max': 25, 'status': 'Low (< 10% saved)'}
        recommendations.append("Your savings buffer is thin (<10%). Try trimming discretionary wants.")
    else:
        savings_score = 0
        score_components['savings'] = {'score': 0, 'max': 25, 'status': 'Deficit (Spending exceeds income)'}
        recommendations.append("CRITICAL: Spending exceeds income this month. Immediate expense cuts required.")

    # 2. Budget Adherence Score (0 - 25)
    over_categories = [c for c in summary['category_analytics'] if c['is_over']]
    if not summary['category_analytics'] or summary['total_budgeted'] == 0:
        budget_score = 15
        score_components['budget'] = {'score': 15, 'max': 25, 'status': 'No Budgets Configured'}
        recommendations.append("Set monthly budgets for your main spending categories to improve discipline.")
    elif len(over_categories) == 0:
        budget_score = 25
        score_components['budget'] = {'score': 25, 'max': 25, 'status': '100% On Track'}
    elif len(over_categories) == 1:
        budget_score = 18
        score_components['budget'] = {'score': 18, 'max': 25, 'status': '1 Category Overbudget'}
        recommendations.append(f"Category '{over_categories[0]['name']}' is over budget by {user.currency}{over_categories[0]['over_amount']}.")
    elif len(over_categories) <= 2:
        budget_score = 12
        score_components['budget'] = {'score': 12, 'max': 25, 'status': f'{len(over_categories)} Categories Over'}
        recommendations.append(f"Multiple categories exceeded limits: {', '.join([c['name'] for c in over_categories])}.")
    else:
        budget_score = 5
        score_components['budget'] = {'score': 5, 'max': 25, 'status': 'Severe Overspending Across Categories'}
        recommendations.append("Widespread budget overruns detected. Review all non-essential transactions.")

    # 3. Needs vs Wants Balance (0 - 25)
    needs_pct = summary['needs_pct']
    wants_pct = summary['wants_pct']
    if total_expenses == 0:
        balance_score = 20
        score_components['balance'] = {'score': 20, 'max': 25, 'status': 'No Expenses Logged'}
    elif needs_pct <= 55 and wants_pct <= 35:
        balance_score = 25
        score_components['balance'] = {'score': 25, 'max': 25, 'status': 'Ideal 50/30/20 Alignment'}
    elif wants_pct <= 45:
        balance_score = 16
        score_components['balance'] = {'score': 16, 'max': 25, 'status': 'Acceptable (Wants slightly elevated)'}
        recommendations.append(f"Discretionary wants account for {wants_pct}% of spending. Aim to keep under 30%.")
    else:
        balance_score = 7
        score_components['balance'] = {'score': 7, 'max': 25, 'status': 'High Discretionary Burn'}
        recommendations.append(f"Wants are consuming {wants_pct}% of spending, crowding out savings.")

    # 4. Emergency Fund Health (0 - 25)
    # Check savings goals with category 'Emergency Fund' or similar
    emergency_goal = SavingsGoal.query.filter(
        SavingsGoal.user_id == user_id,
        SavingsGoal.title.ilike('%emergency%')
    ).first()

    target_months = user.emergency_fund_months if user else 6
    monthly_burn = total_expenses if total_expenses > 0 else (user.monthly_income_target * 0.7 if user and user.monthly_income_target else 2000.0)
    target_emergency_amount = monthly_burn * target_months

    if emergency_goal:
        current_saved = emergency_goal.current_amount
        coverage_months = current_saved / monthly_burn if monthly_burn > 0 else 0
        if coverage_months >= target_months:
            emergency_score = 25
            score_components['emergency'] = {'score': 25, 'max': 25, 'status': f'Fully Funded ({coverage_months:.1f} months covered)'}
        elif coverage_months >= 3:
            emergency_score = 18
            score_components['emergency'] = {'score': 18, 'max': 25, 'status': f'Solid Start ({coverage_months:.1f} months covered)'}
            recommendations.append(f"Emergency fund covers {coverage_months:.1f} months. Strive for your {target_months}-month target.")
        elif coverage_months >= 1:
            emergency_score = 10
            score_components['emergency'] = {'score': 10, 'max': 25, 'status': f'Basic Buffer ({coverage_months:.1f} months covered)'}
            recommendations.append(f"Emergency reserve is modest ({coverage_months:.1f} mo). Prioritize this before aggressive investments.")
        else:
            emergency_score = 5
            score_components['emergency'] = {'score': 5, 'max': 25, 'status': 'Insufficient (< 1 month reserve)'}
            recommendations.append("Build a $1,000 starter emergency fund immediately to safeguard against unexpected events.")
    else:
        emergency_score = 8
        score_components['emergency'] = {'score': 8, 'max': 25, 'status': 'No Emergency Goal Set'}
        recommendations.append(f"Create an Emergency Fund goal targeting {target_months} months of essential expenses ({user.currency if user else '$'}{target_emergency_amount:,.0f}).")

    total_score = savings_score + budget_score + balance_score + emergency_score

    if total_score >= 85:
        tier = 'Excellent'
        badge_color = 'success'
        summary_text = "Outstanding financial control! You maintain strong savings discipline and controlled expenses."
    elif total_score >= 70:
        tier = 'Good'
        badge_color = 'primary'
        summary_text = "Solid financial foundation. A few minor optimizations will elevate your financial resilience."
    elif total_score >= 50:
        tier = 'Fair'
        badge_color = 'warning'
        summary_text = "Moderate financial health. Focus on reducing discretionary leaks and sticking to category budgets."
    else:
        tier = 'Needs Attention'
        badge_color = 'danger'
        summary_text = "Elevated financial vulnerability. Implement strict budgeting and prioritize spending reduction immediately."

    return {
        'total_score': total_score,
        'tier': tier,
        'badge_color': badge_color,
        'summary_text': summary_text,
        'components': score_components,
        'recommendations': recommendations
    }

def get_last_six_months_trends(user_id):
    """Return historical 6-month data for income vs expense chart."""
    today = date.today()
    months_data = []

    for i in range(5, -1, -1):
        # Calculate past month offset
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1

        month_label = date(year, month, 1).strftime('%b %Y')
        
        inc = db.session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(
            Income.user_id == user_id,
            extract('month', Income.date) == month,
            extract('year', Income.date) == year
        ).scalar()

        exp = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
            Expense.user_id == user_id,
            extract('month', Expense.date) == month,
            extract('year', Expense.date) == year
        ).scalar()

        months_data.append({
            'month': month_label,
            'income': float(inc),
            'expense': float(exp),
            'savings': max(0.0, float(inc) - float(exp))
        })

    return months_data

def generate_smart_50_30_20_budget(user_id, monthly_income):
    """
    Applies the proven 50/30/20 financial rule customized to user's registered categories:
    - 50% Needs: Housing, Groceries, Utilities, Transport, Healthcare
    - 30% Wants: Dining, Entertainment, Shopping, Personal
    - 20% Savings: Emergency Fund, Investments, Debt
    """
    categories = get_user_categories(user_id)

    needs_budget = monthly_income * 0.50
    wants_budget = monthly_income * 0.30
    savings_budget = monthly_income * 0.20

    # Categorize into needs, wants, savings groups
    needs_names = {'Housing & Rent', 'Groceries', 'Utilities & Bills', 'Transportation', 'Healthcare & Medical'}
    wants_names = {'Food & Dining', 'Entertainment & Leisure', 'Shopping & Personal', 'Miscellaneous'}
    savings_names = {'Investments & Savings', 'Debt & Loan Repayment', 'Education'}

    allocated_budgets = []

    # Proportions within needs
    needs_cats = [c for c in categories if c.name in needs_names]
    wants_cats = [c for c in categories if c.name in wants_names]
    savings_cats = [c for c in categories if c.name in savings_names]
    other_cats = [c for c in categories if c not in needs_cats and c not in wants_cats and c not in savings_cats]

    # Distribute needs
    if needs_cats:
        weights = {
            'Housing & Rent': 0.50,
            'Groceries': 0.22,
            'Utilities & Bills': 0.12,
            'Transportation': 0.10,
            'Healthcare & Medical': 0.06
        }
        for cat in needs_cats:
            w = weights.get(cat.name, 1.0 / len(needs_cats))
            amt = round(needs_budget * w, 2)
            allocated_budgets.append({'category_id': cat.id, 'category_name': cat.name, 'amount': amt, 'type': 'Need (50%)'})

    # Distribute wants
    if wants_cats:
        weights = {
            'Food & Dining': 0.40,
            'Entertainment & Leisure': 0.25,
            'Shopping & Personal': 0.25,
            'Miscellaneous': 0.10
        }
        for cat in wants_cats:
            w = weights.get(cat.name, 1.0 / len(wants_cats))
            amt = round(wants_budget * w, 2)
            allocated_budgets.append({'category_id': cat.id, 'category_name': cat.name, 'amount': amt, 'type': 'Want (30%)'})

    # Distribute savings
    if savings_cats:
        for cat in savings_cats:
            amt = round(savings_budget / len(savings_cats), 2)
            allocated_budgets.append({'category_id': cat.id, 'category_name': cat.name, 'amount': amt, 'type': 'Savings (20%)'})

    # Any remaining custom categories
    for cat in other_cats:
        allocated_budgets.append({'category_id': cat.id, 'category_name': cat.name, 'amount': round(monthly_income * 0.02, 2), 'type': 'Custom'})

    return {
        'total_income': monthly_income,
        'needs_target': round(needs_budget, 2),
        'wants_target': round(wants_budget, 2),
        'savings_target': round(savings_budget, 2),
        'allocations': allocated_budgets
    }
