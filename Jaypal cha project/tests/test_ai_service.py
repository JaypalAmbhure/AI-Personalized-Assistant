from app.services.ai_service import AIService

def test_ai_service_heuristics():
    service = AIService()

    user_profile = {
        'username': 'alex',
        'currency': '$',
        'monthly_income_target': 5000.0,
        'emergency_fund_months': 6,
        'risk_tolerance': 'Moderate'
    }

    summary = {
        'total_income': 6000.0,
        'total_expenses': 3500.0,
        'net_savings': 2500.0,
        'savings_rate': 41.7,
        'needs_total': 2500.0,
        'wants_total': 1000.0,
        'needs_pct': 71.4,
        'wants_pct': 28.6,
        'category_analytics': [
            {'name': 'Food & Dining', 'spent': 450.0, 'budgeted': 300.0, 'is_over': True, 'over_amount': 150.0}
        ]
    }

    # 1. Test Budget Advice
    advice = service.generate_budget_advice(user_profile, summary)
    assert 'AI Budget Optimization Plan' in advice
    assert '50/30/20' in advice
    assert 'Food & Dining' in advice

    # 2. Test Spending Habits Audit
    recent_expenses = [{'description': 'Sushi Bar', 'amount': 120.0, 'category': 'Food & Dining', 'is_need': False}]
    audit = service.analyze_spending_habits(user_profile, summary, recent_expenses)
    assert 'Forensic Spending Audit' in audit
    assert 'Leakage' in audit

    # 3. Test Savings Strategy
    goals = [{'title': 'Emergency Fund', 'target_amount': 15000.0, 'current_amount': 5000.0, 'status': 'In Progress'}]
    strategy = service.generate_savings_strategy(user_profile, summary, goals)
    assert 'Wealth Building & Savings Acceleration Roadmap' in strategy

    # 4. Test Chat Advisory
    reply = service.chat_advisory(user_profile, summary, "How can I save more money?")
    assert 'savings' in reply.lower()
    assert '$' in reply

def test_ai_chat_api_endpoint(auth_client):
    res = auth_client.post('/ai-advisor/api/chat', json={
        'message': 'Hello, what is my current savings rate?'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert 'FinAura' in data['reply'] or 'savings' in data['reply'].lower()
