from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, Category

auth_bp = Blueprint('auth', __name__)

DEFAULT_CATEGORIES = [
    ('Housing & Rent', 'fa-house', '#6366f1'),
    ('Groceries', 'fa-cart-shopping', '#10b981'),
    ('Food & Dining', 'fa-utensils', '#f59e0b'),
    ('Utilities & Bills', 'fa-bolt', '#06b6d4'),
    ('Transportation', 'fa-car', '#3b82f6'),
    ('Healthcare & Medical', 'fa-heart-pulse', '#ef4444'),
    ('Entertainment & Leisure', 'fa-film', '#ec4899'),
    ('Shopping & Personal', 'fa-bag-shopping', '#8b5cf6'),
    ('Debt & Loan Repayment', 'fa-credit-card', '#f97316'),
    ('Investments & Savings', 'fa-arrow-trend-up', '#14b8a6'),
    ('Education', 'fa-graduation-cap', '#38bdf8'),
    ('Miscellaneous', 'fa-shapes', '#64748b'),
]

def seed_default_categories():
    """Ensure system default categories exist in the database."""
    for name, icon, color in DEFAULT_CATEGORIES:
        exists = Category.query.filter_by(name=name, user_id=None).first()
        if not exists:
            cat = Category(name=name, icon=icon, color=color, is_default=True)
            db.session.add(cat)
    db.session.commit()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        currency = request.form.get('currency', '$').strip()
        monthly_income = request.form.get('monthly_income_target', '0').strip()

        if not username or not email or not password:
            flash('All primary fields are required.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'warning')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'warning')
            return render_template('auth/register.html')

        try:
            monthly_income_val = float(monthly_income) if monthly_income else 0.0
        except ValueError:
            monthly_income_val = 0.0

        user = User(
            username=username,
            email=email,
            currency=currency,
            monthly_income_target=monthly_income_val
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Seed global categories if not yet done
        seed_default_categories()

        login_user(user)
        flash('Account created successfully! Welcome to your AI Personal Finance Advisor.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            seed_default_categories()
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        currency = request.form.get('currency', current_user.currency).strip()
        monthly_income = request.form.get('monthly_income_target', '0').strip()
        emergency_months = request.form.get('emergency_fund_months', '6').strip()
        risk_tolerance = request.form.get('risk_tolerance', current_user.risk_tolerance)
        financial_goal = request.form.get('financial_goal', current_user.financial_goal).strip()
        
        new_password = request.form.get('new_password', '').strip()

        try:
            current_user.currency = currency
            current_user.monthly_income_target = float(monthly_income)
            current_user.emergency_fund_months = int(emergency_months)
            current_user.risk_tolerance = risk_tolerance
            current_user.financial_goal = financial_goal

            if new_password:
                if len(new_password) < 6:
                    flash('New password must be at least 6 characters long.', 'danger')
                    return render_template('auth/profile.html')
                current_user.set_password(new_password)

            db.session.commit()
            flash('Financial profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

    return render_template('auth/profile.html')
