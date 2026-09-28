import os
import json
import logging
from app.config import Config

logger = logging.getLogger(__name__)

class AIService:
    """
    Unified AI Financial Advisor Service supporting:
    - Google Gemini AI (gemini-1.5-flash / gemini-pro)
    - OpenAI ChatGPT (gpt-4o-mini / gpt-3.5-turbo)
    - Intelligent Rule-Based Financial Advisor Fallback
    """

    def __init__(self, app_config=None):
        self.gemini_key = os.environ.get('GEMINI_API_KEY') or (app_config.GEMINI_API_KEY if app_config else '')
        self.openai_key = os.environ.get('OPENAI_API_KEY') or (app_config.OPENAI_API_KEY if app_config else '')
        self.provider = os.environ.get('AI_PROVIDER', 'gemini').lower()
        
        self.gemini_client = None
        self.openai_client = None
        
        self._init_clients()

    def _init_clients(self):
        # Initialize Gemini if key available
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self.gemini_client = genai
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini AI: {e}")

        # Initialize OpenAI if key available
        if self.openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")

    def _call_llm(self, prompt: str, system_instruction: str = None) -> str:
        """Execute prompt against Gemini or OpenAI with graceful fallback."""
        # Try Gemini first if selected or available
        if (self.provider == 'gemini' or not self.openai_client) and self.gemini_client:
            try:
                model_name = 'gemini-1.5-flash'
                model = self.gemini_client.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_instruction
                )
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini call failed: {e}. Trying fallback...")

        # Try OpenAI
        if self.openai_client:
            try:
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                completion = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                if completion.choices and completion.choices[0].message.content:
                    return completion.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"OpenAI call failed: {e}. Falling back to Rule Engine...")

        return None

    def generate_budget_advice(self, user_profile: dict, summary: dict) -> str:
        """Generate tailored AI Budget Recommendations."""
        system_prompt = (
            "You are an expert CFP (Certified Financial Planner) and Personal Finance Advisor AI. "
            "Provide structured, clear, empathetic, and actionable budgeting recommendations. "
            "Use Markdown formatting with bold headers, bullet points, and percentage breakdowns."
        )

        user_prompt = f"""
Analyze this user's monthly financial profile and generate a comprehensive Budget Optimization Plan:
- Currency: {user_profile.get('currency', '$')}
- Monthly Income: {user_profile.get('currency', '$')}{summary.get('total_income', 0)}
- Total Expenses: {user_profile.get('currency', '$')}{summary.get('total_expenses', 0)}
- Current Net Savings: {user_profile.get('currency', '$')}{summary.get('net_savings', 0)} ({summary.get('savings_rate', 0)}%)
- Needs Spending: {user_profile.get('currency', '$')}{summary.get('needs_total', 0)} ({summary.get('needs_pct', 0)}%)
- Wants Spending: {user_profile.get('currency', '$')}{summary.get('wants_total', 0)} ({summary.get('wants_pct', 0)}%)
- Risk Tolerance: {user_profile.get('risk_tolerance', 'Moderate')}
- Financial Goal: {user_profile.get('financial_goal', 'Build Wealth')}

Top Categories Spent:
{json.dumps([{ 'category': c['name'], 'spent': c['spent'], 'budgeted': c['budgeted'] } for c in summary.get('category_analytics', [])[:6]], indent=2)}

Please deliver:
1. Executive Diagnosis (Current financial posture)
2. 50/30/20 Alignment Assessment & adjustments
3. Three Highest-Impact Category Cutbacks
4. Exact Recommended Budget Allocation Table
5. Immediate 7-Day Action Plan
"""
        response = self._call_llm(user_prompt, system_prompt)
        if response:
            return response

        # Intelligent Heuristic Fallback
        return self._heuristic_budget_advice(user_profile, summary)

    def analyze_spending_habits(self, user_profile: dict, summary: dict, recent_expenses: list) -> str:
        """Deep AI audit of spending behavior and leakage detection."""
        system_prompt = (
            "You are a Forensic Financial Analyst and Personal Finance AI. "
            "Audit the user's spending habits, flag anomalies, identify micro-leakages, "
            "and suggest high-leverage cost optimization measures."
        )

        sample_txs = [{
            'desc': e.get('description'),
            'amount': e.get('amount'),
            'cat': e.get('category'),
            'type': 'Need' if e.get('is_need') else 'Want'
        } for e in recent_expenses[:10]]

        user_prompt = f"""
Audit the following financial spending data:
- Currency: {user_profile.get('currency', '$')}
- Monthly Income: {user_profile.get('currency', '$')}{summary.get('total_income', 0)}
- Monthly Expenses: {user_profile.get('currency', '$')}{summary.get('total_expenses', 0)}
- Discretionary Wants: {summary.get('wants_pct', 0)}% of expenses
- Recent Sample Transactions: {json.dumps(sample_txs, indent=2)}

Provide:
1. Spending Leakage Identification (unnecessary repeat items, impulse purchases)
2. Overspending Risks (categories exceeding safe limits)
3. Three Concrete Substitution Tactics (e.g. meal-prepping, subscription audit)
4. Projected Annual Savings from optimizations
"""
        response = self._call_llm(user_prompt, system_prompt)
        if response:
            return response

        return self._heuristic_spending_analysis(user_profile, summary, recent_expenses)

    def generate_savings_strategy(self, user_profile: dict, summary: dict, goals: list) -> str:
        """AI strategy for emergency reserve, debt paydown, and goal acceleration."""
        goals_data = [{'title': g.get('title'), 'target': g.get('target_amount'), 'current': g.get('current_amount'), 'status': g.get('status')} for g in goals]
        
        system_prompt = "You are a Wealth Management Advisor specialized in retail savings and emergency resilience."
        user_prompt = f"""
Evaluate these financial goals and design a high-velocity savings roadmap:
- Currency: {user_profile.get('currency', '$')}
- Monthly Savings Capacity: {user_profile.get('currency', '$')}{summary.get('net_savings', 0)}
- Target Emergency Months: {user_profile.get('emergency_fund_months', 6)}
- Active Goals: {json.dumps(goals_data, indent=2)}

Deliver:
1. Emergency Cushion Readiness Assessment
2. Goal Priority Sequencing (Which goal to fund first and why)
3. Month-by-month contribution roadmap
4. High-yield savings / smart cash buffer suggestions
"""
        response = self._call_llm(user_prompt, system_prompt)
        if response:
            return response

        return self._heuristic_savings_strategy(user_profile, summary, goals)

    def chat_advisory(self, user_profile: dict, summary: dict, user_message: str, chat_history: list = None) -> str:
        """Interactive conversational financial assistant with real user context."""
        system_prompt = (
            "You are 'FinAura', an elite AI Personal Finance Advisor built into the user's dashboard. "
            "You have direct access to their real-time financial stats. Be concise, encouraging, direct, "
            "and cite their actual figures (income, expenses, top categories) where relevant. "
            "Never give formal legal or tax advice, but provide premier financial education and budgeting coaching."
        )

        context_prompt = f"""
User Real-Time Financial Snapshot:
- Currency: {user_profile.get('currency', '$')}
- Username: {user_profile.get('username')}
- Monthly Income: {user_profile.get('currency', '$')}{summary.get('total_income', 0)}
- Monthly Spend: {user_profile.get('currency', '$')}{summary.get('total_expenses', 0)}
- Net Monthly Cash Flow: {user_profile.get('currency', '$')}{summary.get('net_savings', 0)} (Savings Rate: {summary.get('savings_rate', 0)}%)
- Needs: {summary.get('needs_pct', 0)}% | Wants: {summary.get('wants_pct', 0)}%
- Target Emergency Fund: {user_profile.get('emergency_fund_months', 6)} months
- Goals Tracked: {summary.get('goals_count', 0)}

User Question:
"{user_message}"
"""
        response = self._call_llm(context_prompt, system_prompt)
        if response:
            return response

        return self._heuristic_chat_response(user_profile, summary, user_message)

    # -------------------------------------------------------------
    # Intelligent Heuristic Fallback Engines
    # -------------------------------------------------------------
    def _heuristic_budget_advice(self, user_profile: dict, summary: dict) -> str:
        cur = user_profile.get('currency', '$')
        income = summary.get('total_income', 0)
        expenses = summary.get('total_expenses', 0)
        net = summary.get('net_savings', 0)
        rate = summary.get('savings_rate', 0)
        needs_pct = summary.get('needs_pct', 0)
        wants_pct = summary.get('wants_pct', 0)

        ideal_needs = income * 0.50
        ideal_wants = income * 0.30
        ideal_savings = income * 0.20

        over_cats = [c for c in summary.get('category_analytics', []) if c['is_over']]

        advice = f"""### 📊 AI Budget Optimization Plan

#### 1. Executive Diagnosis
- **Monthly Inflow:** `{cur}{income:,.2f}` | **Current Burn:** `{cur}{expenses:,.2f}`
- **Net Monthly Surplus:** `{cur}{net:,.2f}` (Savings Rate: **{rate}%**)
- **50/30/20 Status:** Your spending is split into **{needs_pct}% Needs** and **{wants_pct}% Wants**.
"""
        if rate >= 20:
            advice += "\n> 🟢 **Health Verdict:** You are meeting the baseline 20% savings threshold. Your financial foundation is secure!\n"
        elif rate > 0:
            advice += f"\n> 🟡 **Health Verdict:** You are saving {rate}%, which is below the recommended 20% benchmark. Trimming wants can unlock an extra {cur}{max(0, ideal_savings - net):,.0f}/mo.\n"
        else:
            advice += "\n> 🔴 **Health Verdict Alert:** Spending currently exceeds income! Immediate cost containment is required to prevent debt accumulation.\n"

        advice += f"""
#### 2. Ideal 50/30/20 Targets for Your Income
| Allocation Category | Target (50/30/20) | Recommended Ceiling | Current Actual |
| :--- | :--- | :--- | :--- |
| **Needs (Essentials)** | 50% | `{cur}{ideal_needs:,.2f}` | `{cur}{summary.get('needs_total', 0):,.2f}` ({needs_pct}%) |
| **Wants (Lifestyle)** | 30% | `{cur}{ideal_wants:,.2f}` | `{cur}{summary.get('wants_total', 0):,.2f}` ({wants_pct}%) |
| **Savings & Investments** | 20% | `{cur}{ideal_savings:,.2f}` | `{cur}{max(0, net):,.2f}` ({rate}%) |

#### 3. Category Optimization Actions
"""
        if over_cats:
            for c in over_cats:
                advice += f"- ⚠️ **{c['name']}**: Exceeded budget by `{cur}{c['over_amount']:,.2f}`. Cap spending here immediately.\n"
        else:
            advice += "- ✅ **Budget Compliance**: All your category budgets are currently within allocated ceilings.\n"

        advice += f"""
#### 4. Immediate 7-Day Action Plan
1. **Automate Payday Transfer**: Set up an automatic sweep of `{cur}{(income * 0.20):,.2f}` directly into your savings account on income day.
2. **Review Recurring Subscriptions**: Cancel at least one unused recurring monthly digital service.
3. **Weekly Discretionary Allowance**: Limit lifestyle and dining outings to `{cur}{(ideal_wants / 4):,.2f}` per week.
"""
        return advice

    def _heuristic_spending_analysis(self, user_profile: dict, summary: dict, recent_expenses: list) -> str:
        cur = user_profile.get('currency', '$')
        wants_pct = summary.get('wants_pct', 0)
        total_exp = summary.get('total_expenses', 0)
        
        top_cats = summary.get('category_analytics', [])[:3]
        top_names = ", ".join([f"{c['name']} ({cur}{c['spent']:,.0f})" for c in top_cats]) if top_cats else "General"

        return f"""### 🔍 Forensic Spending Audit & Leakage Report

#### 1. Spending Concentration
- **Highest Drain Categories:** {top_names}
- **Discretionary Ratio:** Wants make up **{wants_pct}%** of your total monthly outflow (`{cur}{summary.get('wants_total', 0):,.2f}`).

#### 2. Identified Micro-Leakages
- **Impulse & Micro-Purchases:** Dining out and casual delivery orders tend to compound by 15-25% without strict weekly tracking.
- **Payment Method Visibility:** Cashless and credit card payments often induce a 12% higher perceived spending tolerance.

#### 3. High-Leverage Substitution Tactics
1. **The 48-Hour Purchase Rule**: Enforce a mandatory 48-hour cooling-off period on all non-essential items exceeding `{cur}50`.
2. **Batch Cooking & Coffee Routine**: Shift 2 dining meals/week to home preparation to reclaim an estimated `{cur}{total_exp * 0.08:,.2f}` per month.
3. **Subscription Hygiene**: Conduct a quarterly audit to prune neglected cloud, streaming, or app subscriptions.

#### 4. Projected Annual Wealth Recovery
- By curbing discretionary leakage by just 15%, you will retain approximately **`{cur}{(summary.get('wants_total', 0) * 0.15 * 12):,.2f}`** every year for high-growth investments.
"""

    def _heuristic_savings_strategy(self, user_profile: dict, summary: dict, goals: list) -> str:
        cur = user_profile.get('currency', '$')
        burn = summary.get('total_expenses', 1000)
        target_months = user_profile.get('emergency_fund_months', 6)
        target_reserve = burn * target_months
        monthly_surplus = max(0, summary.get('net_savings', 0))

        return f"""### 🛡️ Wealth Building & Savings Acceleration Roadmap

#### 1. Emergency Fund Health Assessment
- **Estimated Monthly Burn:** `{cur}{burn:,.2f}`
- **Recommended Emergency Reserve ({target_months} Months):** `{cur}{target_reserve:,.2f}`
- **Current Monthly Savings Velocity:** `{cur}{monthly_surplus:,.2f}/month`

#### 2. Strategic Goal Sequencing
1. **Tier 1 - Immediate Safety Net**: Fund a `{cur}1,000` rapid-response emergency buffer before any aggressive non-essential goal.
2. **Tier 2 - Full Emergency Shield**: Build toward `{cur}{target_reserve:,.2f}` in a high-yield liquid account.
3. **Tier 3 - Wealth & Milestone Goals**: Once 3 months of expenses are secured, divide your surplus 60% toward milestone goals and 40% toward index funds.

#### 3. Velocity Forecast
{"At your current surplus pace of `" + cur + f"{monthly_surplus:,.2f}/mo`, you can achieve your primary emergency fund target within " + f"{max(1, int(target_reserve / monthly_surplus if monthly_surplus > 0 else 24))} months." if monthly_surplus > 0 else "Focus first on creating a positive monthly cash flow so savings contributions can begin."}
"""

    def _heuristic_chat_response(self, user_profile: dict, summary: dict, user_message: str) -> str:
        cur = user_profile.get('currency', '$')
        msg = user_message.lower()
        income = summary.get('total_income', 0)
        expenses = summary.get('total_expenses', 0)
        net = summary.get('net_savings', 0)
        rate = summary.get('savings_rate', 0)

        if any(w in msg for w in ['hello', 'hi', 'hey', 'start']):
            return f"Hello {user_profile.get('username', 'there')}! 👋 I am **FinAura**, your personal AI Finance Advisor. Your current monthly income is `{cur}{income:,.2f}`, with `{cur}{expenses:,.2f}` in expenses ({rate}% savings rate). How can I assist you with your budget, savings, or spending today?"
        
        elif any(w in msg for w in ['save', 'saving', 'more money']):
            return f"To increase your savings from `{cur}{net:,.2f}`/month:\n\n1. **Focus on Wants**: Your discretionary spending is currently `{cur}{summary.get('wants_total', 0):,.2f}` ({summary.get('wants_pct', 0)}%). Trimming just 15% adds `{cur}{(summary.get('wants_total', 0) * 0.15):,.2f}` straight to savings.\n2. **Target 50/30/20**: An ideal 20% savings target for your income is `{cur}{(income * 0.20):,.2f}`/month.\n3. **Automate**: Move funds to savings the same day your income arrives."

        elif any(w in msg for w in ['budget', '50/30/20', 'rule', 'plan']):
            return f"Based on your `{cur}{income:,.2f}` monthly income, here is the golden 50/30/20 breakdown:\n\n- **50% Needs**: `{cur}{(income * 0.50):,.2f}` (Rent, groceries, utilities)\n- **30% Wants**: `{cur}{(income * 0.30):,.2f}` (Dining, hobbies, leisure)\n- **20% Savings**: `{cur}{(income * 0.20):,.2f}` (Emergency fund & investments)\n\nHead to the **Budgets** tab to auto-generate and apply these category caps directly!"

        elif any(w in msg for w in ['afford', 'buy', 'purchase', 'spend']):
            return f"Before making an unscheduled purchase, evaluate:\n1. **Do you have `{cur}{net:,.2f}` net cash flow remaining this month?**\n2. **Will this purchase push your discretionary wants above 30% of your income?**\n3. **Is your emergency fund currently funded?**\n\nIf the cost is more than 50% of your monthly surplus (`{cur}{(net * 0.50):,.2f}`), consider waiting 30 days before buying."

        elif any(w in msg for w in ['emergency', 'reserve']):
            burn = expenses if expenses > 0 else 2000
            months = user_profile.get('emergency_fund_months', 6)
            return f"Your target emergency reserve is **{months} months of essential burn**, which equates to approximately **`{cur}{(burn * months):,.2f}`**. Keep this in a high-yield liquid savings account so it is insulated from market fluctuations."

        else:
            return f"Based on your current numbers (`{cur}{income:,.2f}` income, `{cur}{expenses:,.2f}` expenses, `{rate}%` savings rate), my recommendation is to maintain strict adherence to your monthly category budgets. Would you like me to analyze your top spending categories, suggest an emergency fund plan, or draft a 50/30/20 budget?"
