# 💰 FinAura — AI-Powered Personal Finance Advisor Bot

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.54-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o_Mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![Tests](https://img.shields.io/badge/Pytest-12%20Passed%20(100%25)-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](tests/)

**FinAura** is an enterprise-grade, AI-driven Personal Financial Planning Assistant built to help individuals master their finances through intelligent budgeting, automated 50/30/20 allocation, real-time expense tracking, forensic spending audits, and customized wealth advisory.

Powered by **Flask**, **SQLAlchemy**, **Jinja2**, **Chart.js**, and **Gemini / ChatGPT AI**, the platform delivers an executive glassmorphic interface with real-time analytics, instant PDF/CSV reporting, and single-click public deployment via **Ngrok**.

---

## 🌟 Key Features

### 1. 🤖 Multi-LLM AI Financial Advisory Engine
- **Dual AI Integration:** Native support for Google Gemini (`gemini-1.5-flash`) and OpenAI ChatGPT (`gpt-4o-mini`).
- **Zero-Downtime Heuristic Fallback:** If API keys are not supplied or quota limits are exceeded, a built-in algorithmic financial rule engine automatically takes over, guaranteeing 100% uptime without crashes.
- **Context-Aware Advisor Chat:** Chat in real time with the AI about your actual current financial situation (inflows, burn rate, category overruns, savings buffer).
- **Forensic Spending & Leakage Audits:** Pinpoint micro-leakages, impulse drains, and subscription bloat.
- **Automated 50/30/20 Budgeting:** One-click generation and application of optimal category ceilings (50% Needs, 30% Wants, 20% Savings).
- **Wealth Acceleration Roadmap:** Dynamic emergency reserve timeline and milestone sequencing.

### 2. 🔐 Secure Authentication & Financial Profile Management
- Secure user registration, login, and session management via **Flask-Login**.
- Password protection with **Werkzeug PBKDF2** cryptographic hashing.
- Comprehensive Profile Settings: Currency selector (`$`, `₹`, `€`, `£`, `C$`, `A$`, `AED`), monthly income target, emergency fund months, and risk tolerance profile (Conservative, Moderate, Aggressive).
- Role-protected routes and session isolation.

### 3. 📊 Interactive Dashboard & Financial Intelligence
- **Executive Glassmorphism UI:** Built with custom CSS tokens, Plus Jakarta Sans typography, and subtle micro-animations.
- **4 Real-time KPI Cards:** Inflows, Outflows, Net Cash Surplus, and AI Financial Health Score (0–100).
- **Dynamic Chart.js Visualizations:**
  - 6-Month Inflow vs Outflow Cash Flow Trend bar/line chart.
  - Categorical Expense Donut breakdown.
  - Needs vs Wants (50/30 rule) distribution chart.
- **Category Budget Progress:** Real-time progress bars with dynamic status badges (`Safe`, `Warning`, `Overbudget`).
- **Emergency Reserve Cushion Shield:** Live calculation of covered months vs target months.

### 4. 💳 Transaction Management & Expense Categorization
- **Inflow Tracking:** Record recurring salaries, freelance retainers, dividends, and one-time bonuses.
- **Expense Logging:** Categorized spending with payment method tags (Credit Card, Debit Card, UPI, Bank Transfer, Cash).
- **Need vs Want Classification:** Categorize expenses as essential (Need) or discretionary (Want) for strict 50/30/20 financial audits.
- **Custom Category Creator:** Create custom categories with custom FontAwesome icons and hex colors.
- **Search & Filters:** Real-time text search, category filtering, necessity filtering, and monthly pagination.

### 5. 🎯 Savings Goals & Emergency Reserve Buffer
- Create targeted milestones (e.g., Emergency Shield, Vehicle Downpayment, Vacation).
- Fluid contribution logging with visual completion percentages.
- Automatic status update to **Achieved** upon reaching goal targets.

### 6. 📑 Financial Reporting & Data Export
- Comprehensive **Monthly Financial Performance Statement**.
- Detailed category variance table (Budget vs Actual with over/under delta).
- **CSV Data Export:** One-click download of all transaction and income records for spreadsheet analysis.
- **Print / PDF-Ready Layout:** Dedicated `@media print` stylesheet for clean physical printing or PDF downloads.

### 7. 🌐 Public Deployment via Ngrok
- Deploy the local application to a public HTTPS URL with one command using `run_ngrok.py`.
- Perfect for remote demonstrations, mobile device testing, and stakeholder reviews.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | [Flask 3.0.3](https://flask.palletsprojects.com/) |
| **ORM & Database** | [SQLAlchemy 2.0.54](https://www.sqlalchemy.org/) / SQLite / PostgreSQL-ready |
| **Authentication** | [Flask-Login 0.6.3](https://flask-login.readthedocs.io/), [Werkzeug 3.1.8](https://werkzeug.palletsprojects.com/) |
| **Generative AI** | [google-generativeai 0.7.2](https://pypi.org/project/google-generativeai/), [openai 3.17.0](https://pypi.org/project/openai/) |
| **Tunneling / Deployment** | [pyngrok 8.1.2](https://pyngrok.readthedocs.io/) |
| **Testing** | [pytest 9.1.1](https://docs.pytest.org/) |
| **Data Processing** | [pandas 2.2.2](https://pandas.pydata.org/), [openpyxl 3.1.5](https://openpyxl.readthedocs.io/) |
| **Frontend** | Jinja2 Templates, Vanilla CSS Glassmorphism, Bootstrap 5.3.3, Chart.js 4.4, FontAwesome 6 |

---

## 📁 Project Architecture

```text
Jaypal cha project/
├── app/
│   ├── __init__.py               # Flask app factory, LoginManager, Jinja filters
│   ├── config.py                 # Configuration classes (Dev, Test, Prod)
│   ├── models.py                 # User, Category, Income, Expense, Budget, SavingsGoal, AIRecommendation
│   ├── routes/
│   │   ├── __init__.py           # Blueprint aggregation
│   │   ├── auth.py               # Register, Login, Logout, Profile settings
│   │   ├── dashboard.py          # KPI metrics & Chart.js API endpoint
│   │   ├── income.py             # Inflow tracking & management
│   │   ├── expenses.py           # Outflow tracking, filtering & custom categories
│   │   ├── budgets.py            # Category ceilings & 50/30/20 auto-generation
│   │   ├── savings.py            # Savings goals & emergency fund cushion
│   │   ├── ai_advisor.py         # AI chatbot, spending audit & plan generators
│   │   └── reports.py            # Monthly financial statement & CSV export
│   ├── services/
│   │   ├── __init__.py           # Service exports
│   │   ├── ai_service.py         # Gemini, OpenAI & smart heuristic fallback
│   │   └── finance_service.py    # Health score engine, 50/30/20 calculator & analytics
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css         # Executive dark theme, glassmorphism, responsive styles
│   │   └── js/
│   │       ├── main.js           # UI utilities & date helpers
│   │       ├── charts.js         # Dynamic Chart.js visualizations
│   │       └── ai_chat.js        # Interactive AI chat & audit triggers
│   └── templates/
│       ├── base.html             # Master layout with sidebar & quick action modals
│       ├── auth/                 # login.html, register.html, profile.html
│       ├── dashboard/            # index.html
│       ├── income/               # index.html
│       ├── expenses/             # index.html
│       ├── budgets/              # index.html
│       ├── savings/              # index.html
│       ├── ai_advisor/           # index.html
│       └── reports/              # index.html
├── tests/
│   ├── conftest.py               # Isolated in-memory SQLite fixtures
│   ├── test_auth.py              # Authentication & session tests
│   ├── test_finance.py           # Income, expense, budget & savings tests
│   ├── test_ai_service.py        # Heuristic & API resilience tests
│   └── test_reports.py           # Reports & CSV export tests
├── .env                          # Local environment variables
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore file
├── requirements.txt              # Project dependencies
├── run.py                        # Local development runner
├── run_ngrok.py                  # Public Ngrok deployment script
├── seed_data.py                  # Demo data populator
└── README.md                     # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Clone & Navigate to Project Directory
```bash
cd "Jaypal cha project"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and configure your keys (optional — the app works right out of the box with heuristic AI even if keys are omitted):
```ini
# Application Secret Key
SECRET_KEY=super-secret-finance-advisor-key-2026-prod

# Database Configuration (SQLite default, or PostgreSQL)
DATABASE_URL=sqlite:///finance_advisor.db

# AI Service Keys (Optional: Provide either or leave blank for built-in rule engine)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
AI_PROVIDER=gemini # or 'openai' or 'heuristic'

# Ngrok Public Deployment Token (Optional, get free from https://dashboard.ngrok.com)
NGROK_AUTHTOKEN=your_ngrok_token_here

# Server Port
PORT=5000
FLASK_DEBUG=True
```

### 4. Seed Realistic Demo Data
Run the seeding script to instantly create a ready-to-test portfolio with incomes, categorized transactions, budget limits, active savings goals, and historical trends:
```bash
python seed_data.py
```
**Demo Account Credentials:**
- **Username:** `alex_investor`
- **Password:** `password123`

### 5. Launch the Application Locally
```bash
python run.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🌐 Public Deployment with Ngrok

To expose your application to the internet for remote demonstrations or mobile testing:

1. Add your free Ngrok token to `.env`:
   ```ini
   NGROK_AUTHTOKEN=your_token_from_ngrok_dashboard
   ```
2. Launch the Ngrok deployment runner:
   ```bash
   python run_ngrok.py
   ```
3. Copy the generated **Public Live Demo URL** (e.g., `https://xxxx-xx-xx-xx.ngrok-free.app`) and open it on any device.

---

## 🧪 Running the Test Suite

The test suite validates authentication, financial calculations, budget allocations, savings goals, AI heuristics, and report generation using an in-memory SQLite database:

```bash
python -m pytest tests/
```

Expected output:
```text
============================= test session starts =============================
collected 12 items

tests\test_ai_service.py ..                                              [ 16%]
tests\test_auth.py .....                                                 [ 58%]
tests\test_finance.py ....                                               [ 91%]
tests\test_reports.py .                                                  [100%]

============================= 12 passed in 5.07s ==============================
```

---

## 📡 API & Route Overview

| Route | Method | Description |
| :--- | :--- | :--- |
| `/register` | GET/POST | Create new user account |
| `/login` | GET/POST | User sign-in with remember-me support |
| `/logout` | GET | Terminate active user session |
| `/profile` | GET/POST | Update currency, risk tolerance, goals & password |
| `/` or `/dashboard` | GET | Financial overview dashboard |
| `/api/chart-data` | GET | JSON data feed for Chart.js analytics |
| `/income` | GET | List and filter income records |
| `/income/add` | POST | Log new income source |
| `/income/delete/<id>` | POST | Delete income record |
| `/expenses` | GET | Filter and paginate expense transactions |
| `/expenses/add` | POST | Log expense with category & 50/30 classification |
| `/expenses/delete/<id>` | POST | Remove expense transaction |
| `/expenses/category/add`| POST | Create custom user category |
| `/budgets` | GET | View category budget discipline & variance |
| `/budgets/set` | POST | Set or update category budget ceiling |
| `/budgets/auto-generate`| POST | Auto-allocate 50/30/20 budgets based on income |
| `/savings` | GET | Track savings milestones & emergency reserve |
| `/savings/add` | POST | Create new milestone savings goal |
| `/savings/<id>/contribute`| POST | Contribute capital toward a savings goal |
| `/ai-advisor` | GET | AI Advisor Hub & audit history |
| `/ai-advisor/api/chat` | POST | Context-aware AI financial advisory chat |
| `/ai-advisor/api/generate-budget-plan` | POST | Generate AI 50/30/20 budget optimization plan |
| `/ai-advisor/api/analyze-spending` | POST | Execute forensic spending audit & detect leaks |
| `/ai-advisor/api/savings-strategy` | POST | Generate wealth roadmap & emergency reserve plan |
| `/reports` | GET | Monthly financial statement & variance audit |
| `/reports/export/csv` | GET | Download complete financial history as CSV |

---

## 💡 Financial Health Score Algorithm

FinAura computes an objective **0–100 Financial Health Score** derived from 4 foundational pillars:

$$\text{Total Score} = \text{Savings Rate (25)} + \text{Budget Discipline (25)} + \text{50/30/20 Balance (25)} + \text{Emergency Buffer (25)}$$

- **Savings Rate (25 pts):** Hitting $\ge 20\%$ earns full marks; negative savings rates indicate budget deficits.
- **Budget Discipline (25 pts):** Measures the count and magnitude of categories exceeding budgeted ceilings.
- **50/30/20 Balance (25 pts):** Evaluates whether essential needs are kept within $50\%$ and discretionary lifestyle wants within $30\%$.
- **Emergency Reserve (25 pts):** Evaluates liquid emergency capital coverage against target months of baseline burn.

**Tiers:**
- `85 – 100`: **Excellent** (Optimal wealth accumulation)
- `70 – 84`: **Good** (Solid foundation, minor lifestyle optimizations)
- `50 – 69`: **Fair** (Moderate vulnerability, discretionary trimming needed)
- `< 50`: **Needs Attention** (Urgent deficit containment required)

---

## 🔒 Security & Privacy Best Practices

- **Password Encryption:** Werkzeug PBKDF2 with SHA-256 and salted hashing.
- **Session Protection:** HTTP-only secure cookie sessions with Flask-Login.
- **Data Isolation:** All financial queries are strictly scoped to the authenticated `user_id`.
- **Secret Management:** API keys and database credentials are fully isolated in `.env` and excluded from source control.

---

## 📄 License

This project is licensed under the **MIT License**. Free for personal, commercial, and educational use.


https://github.com/user-attachments/assets/a299732f-685e-4f46-af0f-7f8734ea033c

