import calendar
from flask import Flask
from flask_login import LoginManager
from app.config import config_by_name
from app.models import db, User, Category
from app.routes.auth import auth_bp, seed_default_categories
from app.routes.dashboard import dashboard_bp
from app.routes.income import income_bp
from app.routes.expenses import expenses_bp
from app.routes.budgets import budgets_bp
from app.routes.savings import savings_bp
from app.routes.ai_advisor import ai_advisor_bp
from app.routes.reports import reports_bp

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def create_app(config_name='default'):
    """Application factory for Personal Finance Advisor Bot."""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(savings_bp)
    app.register_blueprint(ai_advisor_bp)
    app.register_blueprint(reports_bp)

    # Jinja2 template filters
    @app.template_filter('currency')
    def currency_filter(val, symbol='$'):
        try:
            return f"{symbol}{float(val):,.2f}"
        except (ValueError, TypeError):
            return f"{symbol}0.00"

    @app.template_filter('month_name')
    def month_name_filter(month_num):
        try:
            return calendar.month_name[int(month_num)]
        except (IndexError, ValueError, TypeError):
            return str(month_num)

    # Initialize DB schema & seed categories
    with app.app_context():
        db.create_all()
        seed_default_categories()

    return app
