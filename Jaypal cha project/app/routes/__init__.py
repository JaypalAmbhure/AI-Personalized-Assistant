from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.income import income_bp
from app.routes.expenses import expenses_bp
from app.routes.budgets import budgets_bp
from app.routes.savings import savings_bp
from app.routes.ai_advisor import ai_advisor_bp
from app.routes.reports import reports_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'income_bp',
    'expenses_bp',
    'budgets_bp',
    'savings_bp',
    'ai_advisor_bp',
    'reports_bp'
]
