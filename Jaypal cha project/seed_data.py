import os
from datetime import date, datetime, timedelta
from app import create_app
from app.models import db, User, Category, Income, Expense, Budget, SavingsGoal, AIRecommendation

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

app = create_app()

def seed():
    with app.app_context():
        print("[*] Seeding database with realistic personal finance data...")

        # 1. Create or retrieve demo user
        user = User.query.filter_by(username='alex_investor').first()
        if not user:
            user = User(
                username='alex_investor',
                email='alex@example.com',
                currency='$',
                monthly_income_target=6900.0,
                emergency_fund_months=6,
                risk_tolerance='Moderate',
                financial_goal='Build $30k Emergency Shield & Invest 20% in Index Funds'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            print("  [+] Created user: alex_investor (password: password123)")
        else:
            print("  [-] User alex_investor already exists.")

        # Ensure categories exist
        cats = {c.name: c for c in Category.query.all()}
        today = date.today()

        # 2. Clear existing entries for alex to ensure fresh clean demo
        Expense.query.filter_by(user_id=user.id).delete()
        Income.query.filter_by(user_id=user.id).delete()
        Budget.query.filter_by(user_id=user.id).delete()
        SavingsGoal.query.filter_by(user_id=user.id).delete()
        AIRecommendation.query.filter_by(user_id=user.id).delete()
        db.session.commit()

        # 3. Seed Income records for current & past 5 months
        for m_offset in range(6):
            # approximate month
            d = today - timedelta(days=m_offset * 30)
            month_date = date(d.year, d.month, 1)

            # Salary
            db.session.add(Income(
                user_id=user.id,
                source_name='Tech Senior Salary',
                amount=5800.0,
                frequency='Monthly',
                date=date(d.year, d.month, 1),
                notes='Direct deposit net salary'
            ))

            # Freelance
            db.session.add(Income(
                user_id=user.id,
                source_name='FinTech Cloud Consulting',
                amount=950.0,
                frequency='Monthly',
                date=date(d.year, d.month, 15),
                notes='Bi-weekly consulting retainer'
            ))

            # Dividend
            db.session.add(Income(
                user_id=user.id,
                source_name='Vanguard Index Dividends',
                amount=150.0,
                frequency='Monthly',
                date=date(d.year, d.month, 22),
                notes='Quarterly reinvested dividend'
            ))

        # 4. Seed Current Month Expenses
        expenses_data = [
            # Needs (Essentials)
            ('Housing & Rent', 1850.0, 'Downtown Apartment Rent', True, 'Bank Transfer', today - timedelta(days=2)),
            ('Groceries', 285.50, 'Whole Foods Organic Groceries', True, 'Credit Card', today - timedelta(days=4)),
            ('Groceries', 210.00, 'Trader Joe Weekly Stockup', True, 'Debit Card', today - timedelta(days=12)),
            ('Utilities & Bills', 145.00, 'Electric & City Water Bill', True, 'Bank Transfer', today - timedelta(days=5)),
            ('Utilities & Bills', 85.00, 'Fiber High-Speed Internet', True, 'Credit Card', today - timedelta(days=8)),
            ('Transportation', 120.00, 'Metro Transit Monthly Pass', True, 'Credit Card', today - timedelta(days=1)),
            ('Transportation', 65.00, 'Gas Station Refuel', True, 'Credit Card', today - timedelta(days=10)),
            ('Healthcare & Medical', 80.00, 'Prescription & Pharmacy', True, 'Debit Card', today - timedelta(days=14)),

            # Wants (Discretionary)
            ('Food & Dining', 115.00, 'Sushi Dinner with Friends', False, 'Credit Card', today - timedelta(days=3)),
            ('Food & Dining', 75.00, 'Artisan Coffee & Lunches', False, 'Credit Card', today - timedelta(days=7)),
            ('Food & Dining', 180.00, 'Weekend Bistro & Drinks', False, 'Credit Card', today - timedelta(days=11)),
            ('Food & Dining', 95.00, 'Doordash Gourmet Delivery', False, 'Credit Card', today - timedelta(days=16)),
            ('Entertainment & Leisure', 55.00, 'Concert Ticket', False, 'Credit Card', today - timedelta(days=6)),
            ('Entertainment & Leisure', 35.00, 'Streaming Bundle (Netflix/Spotify)', False, 'Credit Card', today - timedelta(days=9)),
            ('Shopping & Personal', 185.00, 'Nike Running Shoes', False, 'Credit Card', today - timedelta(days=13)),
            ('Shopping & Personal', 65.00, 'Books & Technical Guides', False, 'Debit Card', today - timedelta(days=15)),
            ('Miscellaneous', 40.00, 'Courier & Home Supplies', False, 'Cash', today - timedelta(days=17))
        ]

        for cat_name, amt, desc, is_need, pay_method, exp_date in expenses_data:
            cat = cats.get(cat_name)
            if cat:
                db.session.add(Expense(
                    user_id=user.id,
                    category_id=cat.id,
                    amount=amt,
                    date=exp_date,
                    description=desc,
                    payment_method=pay_method,
                    is_need=is_need
                ))

        # 5. Seed Past 5 Months Trend Data for Charts
        for m_offset in range(1, 6):
            d = today - timedelta(days=m_offset * 30)
            past_month_date = date(d.year, d.month, 10)
            # Add typical monthly cluster
            db.session.add(Expense(
                user_id=user.id,
                category_id=cats['Housing & Rent'].id,
                amount=1850.0,
                date=past_month_date,
                description='Apartment Rent',
                payment_method='Bank Transfer',
                is_need=True
            ))
            db.session.add(Expense(
                user_id=user.id,
                category_id=cats['Groceries'].id,
                amount=520.0 + (m_offset * 15),
                date=past_month_date,
                description='Monthly Groceries',
                payment_method='Credit Card',
                is_need=True
            ))
            db.session.add(Expense(
                user_id=user.id,
                category_id=cats['Food & Dining'].id,
                amount=380.0 + (m_offset * 20),
                date=past_month_date,
                description='Dining & Takeout',
                payment_method='Credit Card',
                is_need=False
            ))
            db.session.add(Expense(
                user_id=user.id,
                category_id=cats['Utilities & Bills'].id,
                amount=230.0,
                date=past_month_date,
                description='Monthly Utilities',
                payment_method='Bank Transfer',
                is_need=True
            ))

        # 6. Seed Monthly Budgets for Current Month
        budget_specs = [
            ('Housing & Rent', 1900.0),
            ('Groceries', 550.0),
            ('Food & Dining', 350.0), # Will show overbudget!
            ('Utilities & Bills', 250.0),
            ('Transportation', 220.0),
            ('Healthcare & Medical', 150.0),
            ('Entertainment & Leisure', 150.0),
            ('Shopping & Personal', 300.0),
            ('Miscellaneous', 100.0)
        ]

        for cat_name, b_amt in budget_specs:
            cat = cats.get(cat_name)
            if cat:
                db.session.add(Budget(
                    user_id=user.id,
                    category_id=cat.id,
                    month=today.month,
                    year=today.year,
                    budgeted_amount=b_amt
                ))

        # 7. Seed Savings Goals
        db.session.add(SavingsGoal(
            user_id=user.id,
            title='6-Month Emergency Shield',
            target_amount=18000.0,
            current_amount=11500.0,
            target_date=date(today.year, 12, 31),
            category='Emergency Reserve',
            status='In Progress'
        ))

        db.session.add(SavingsGoal(
            user_id=user.id,
            title='EV Downpayment Fund',
            target_amount=8000.0,
            current_amount=4500.0,
            target_date=date(today.year + 1, 6, 30),
            category='Major Purchase',
            status='In Progress'
        ))

        db.session.add(SavingsGoal(
            user_id=user.id,
            title='Tokyo Autumn Trip',
            target_amount=3200.0,
            current_amount=3200.0,
            target_date=date(today.year, 10, 15),
            category='Travel & Vacation',
            status='Achieved'
        ))

        # 8. Seed AI Recommendation record
        db.session.add(AIRecommendation(
            user_id=user.id,
            recommendation_type='budget_plan',
            title='Initial 50/30/20 Wealth Calibration',
            content="""### 📊 FinAura Financial Baseline Assessment
- **Monthly Net Surplus:** `$3,414.50` (Savings Rate: **49.5%**)
- **Emergency Reserve:** Currently funded for **3.4 months** of living expenses.
- **Immediate Optimization:** Food & Dining is exceeding the `$350` budget limit by `$115`. Capping dining delivery will immediately reclaim `$1,380` annually.""",
            financial_health_score=82
        ))

        db.session.commit()
        print("[SUCCESS] Seed data successfully populated! Demo account ready.")

if __name__ == '__main__':
    seed()
