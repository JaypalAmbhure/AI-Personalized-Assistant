from datetime import date
from app.models import Income, Expense, Budget, SavingsGoal, Category
from app.services.finance_service import get_monthly_summary, calculate_financial_health_score, generate_smart_50_30_20_budget

def test_income_flow(auth_client, app):
    # Add income
    res = auth_client.post('/income/add', data={
        'source_name': 'Software Salary',
        'amount': '4500.00',
        'frequency': 'Monthly',
        'date': date.today().strftime('%Y-%m-%d'),
        'notes': 'Primary salary'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Software Salary' in res.data

    with app.app_context():
        inc = Income.query.filter_by(source_name='Software Salary').first()
        assert inc is not None
        assert inc.amount == 4500.00

def test_expense_flow_and_summary(auth_client, app):
    with app.app_context():
        cat = Category.query.first()
        cat_id = cat.id

    # Add need expense
    auth_client.post('/expenses/add', data={
        'amount': '1200.00',
        'category_id': str(cat_id),
        'description': 'Apartment Rent',
        'date': date.today().strftime('%Y-%m-%d'),
        'payment_method': 'Bank Transfer',
        'is_need': 'true'
    }, follow_redirects=True)

    # Add want expense
    auth_client.post('/expenses/add', data={
        'amount': '300.00',
        'category_id': str(cat_id),
        'description': 'Weekend Dining',
        'date': date.today().strftime('%Y-%m-%d'),
        'payment_method': 'Credit Card',
        'is_need': 'false'
    }, follow_redirects=True)

    # Add income
    auth_client.post('/income/add', data={
        'source_name': 'Monthly Retainer',
        'amount': '3000.00',
        'frequency': 'Monthly',
        'date': date.today().strftime('%Y-%m-%d')
    }, follow_redirects=True)

    with app.app_context():
        from app.models import User
        user = User.query.filter_by(username='testuser').first()
        summary = get_monthly_summary(user.id)
        assert summary['total_income'] == 3000.00
        assert summary['total_expenses'] == 1500.00
        assert summary['net_savings'] == 1500.00
        assert summary['savings_rate'] == 50.0
        assert summary['needs_total'] == 1200.00
        assert summary['wants_total'] == 300.00

def test_budget_setting_and_auto_generate(auth_client, app):
    with app.app_context():
        cat = Category.query.first()
        cat_id = cat.id

    # Manually set budget
    res = auth_client.post('/budgets/set', data={
        'category_id': str(cat_id),
        'month': str(date.today().month),
        'year': str(date.today().year),
        'budgeted_amount': '800.00'
    }, follow_redirects=True)
    assert res.status_code == 200

    # Auto-generate 50/30/20 budget
    res_auto = auth_client.post('/budgets/auto-generate', data={
        'month': str(date.today().month),
        'year': str(date.today().year)
    }, follow_redirects=True)
    assert res_auto.status_code == 200
    assert b'AI Smart 50/30/20 Budget generated' in res_auto.data

def test_savings_goal_and_contribute(auth_client, app):
    # Create goal
    auth_client.post('/savings/add', data={
        'title': 'Emergency Cushion',
        'target_amount': '5000.00',
        'current_amount': '1000.00',
        'category': 'Emergency Reserve'
    }, follow_redirects=True)

    with app.app_context():
        goal = SavingsGoal.query.filter_by(title='Emergency Cushion').first()
        assert goal is not None
        assert goal.progress_percentage == 20.0
        goal_id = goal.id

    # Contribute funds
    auth_client.post(f'/savings/{goal_id}/contribute', data={
        'amount': '1500.00'
    }, follow_redirects=True)

    with app.app_context():
        updated_goal = app.extensions['sqlalchemy'].session.get(SavingsGoal, goal_id)
        assert updated_goal.current_amount == 2500.00
        assert updated_goal.progress_percentage == 50.0
