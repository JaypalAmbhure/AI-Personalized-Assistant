from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User account model for authentication and profile management."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    currency = db.Column(db.String(10), default='$')
    monthly_income_target = db.Column(db.Float, default=0.0)
    emergency_fund_months = db.Column(db.Integer, default=6)
    risk_tolerance = db.Column(db.String(20), default='Moderate')  # Conservative, Moderate, Aggressive
    financial_goal = db.Column(db.String(255), default='Save 20% of monthly income & build emergency reserve')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    incomes = db.relationship('Income', backref='user', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    savings_goals = db.relationship('SavingsGoal', backref='user', lazy=True, cascade='all, delete-orphan')
    ai_recommendations = db.relationship('AIRecommendation', backref='user', lazy=True, cascade='all, delete-orphan')
    custom_categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    """Expense categories (both global defaults and custom user categories)."""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    name = db.Column(db.String(64), nullable=False)
    icon = db.Column(db.String(64), default='fa-tag')
    color = db.Column(db.String(20), default='#6366f1')
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    expenses = db.relationship('Expense', backref='category', lazy=True)
    budgets = db.relationship('Budget', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'color': self.color,
            'is_default': self.is_default
        }

    def __repr__(self):
        return f'<Category {self.name}>'


class Income(db.Model):
    """Income record tracking source, amount, and recurrence."""
    __tablename__ = 'incomes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    source_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(30), default='Monthly')  # Monthly, Weekly, Bi-Weekly, One-time
    date = db.Column(db.Date, default=date.today, nullable=False)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'source_name': self.source_name,
            'amount': self.amount,
            'frequency': self.frequency,
            'date': self.date.strftime('%Y-%m-%d'),
            'notes': self.notes
        }

    def __repr__(self):
        return f'<Income {self.source_name}: {self.amount}>'


class Expense(db.Model):
    """Expense transaction model with category, necessity classification, and payment method."""
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    payment_method = db.Column(db.String(50), default='Credit Card')  # Cash, Credit Card, Debit Card, UPI, Bank Transfer
    is_need = db.Column(db.Boolean, default=True)  # True = Need, False = Want (50/30/20 breakdown)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category.name if self.category else 'Uncategorized',
            'category_color': self.category.color if self.category else '#64748b',
            'category_icon': self.category.icon if self.category else 'fa-tag',
            'amount': self.amount,
            'date': self.date.strftime('%Y-%m-%d'),
            'description': self.description,
            'payment_method': self.payment_method,
            'is_need': self.is_need
        }

    def __repr__(self):
        return f'<Expense {self.description}: {self.amount}>'


class Budget(db.Model):
    """Monthly budget limits allocated per category."""
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)   # e.g., 2026
    budgeted_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'category_id', 'month', 'year', name='unique_user_cat_month_budget'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'category_name': self.category.name if self.category else 'General',
            'month': self.month,
            'year': self.year,
            'budgeted_amount': self.budgeted_amount
        }

    def __repr__(self):
        return f'<Budget {self.category_id} ({self.month}/{self.year}): {self.budgeted_amount}>'


class SavingsGoal(db.Model):
    """Savings goal tracking target amounts, progress, and deadlines."""
    __tablename__ = 'savings_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=True)
    category = db.Column(db.String(50), default='Emergency Fund')
    status = db.Column(db.String(20), default='In Progress')  # In Progress, Achieved, Paused
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def progress_percentage(self):
        if self.target_amount <= 0:
            return 100.0
        pct = (self.current_amount / self.target_amount) * 100.0
        return min(round(pct, 1), 100.0)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'progress_percentage': self.progress_percentage,
            'target_date': self.target_date.strftime('%Y-%m-%d') if self.target_date else None,
            'category': self.category,
            'status': self.status
        }

    def __repr__(self):
        return f'<SavingsGoal {self.title}: {self.current_amount}/{self.target_amount}>'


class AIRecommendation(db.Model):
    """Log of AI insights, audits, budget plans, and recommendation records."""
    __tablename__ = 'ai_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recommendation_type = db.Column(db.String(50), nullable=False)  # budget_plan, spending_analysis, general_advice
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    financial_health_score = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'recommendation_type': self.recommendation_type,
            'title': self.title,
            'content': self.content,
            'financial_health_score': self.financial_health_score,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

    def __repr__(self):
        return f'<AIRecommendation {self.title} ({self.created_at})>'
