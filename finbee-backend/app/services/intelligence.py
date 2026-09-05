"""
Intelligence service — deterministic financial health calculations.
No AI involved anywhere in this file. Every number is a fixed rule.
"""

from datetime import datetime, date, timezone
from typing import Optional

from app.database import (
    financial_profiles_collection,
    goals_collection,
    loans_collection,
    insurance_collection,
    investments_collection,
)
from app.services.financial_profile import normalize_income


# ---------------------------------------------------------------------------
# Data gathering
# ---------------------------------------------------------------------------

async def _gather_user_data(user_id: str) -> dict:
    profile = await financial_profiles_collection.find_one({"userId": user_id})
    goals = [g async for g in goals_collection.find({"userId": user_id})]
    loans = [l async for l in loans_collection.find({"userId": user_id})]
    insurance = [i async for i in insurance_collection.find({"userId": user_id})]
    investments = [inv async for inv in investments_collection.find({"userId": user_id})]
    return {
        "profile": profile,
        "goals": goals,
        "loans": loans,
        "insurance": insurance,
        "investments": investments,
    }


# ---------------------------------------------------------------------------
# Base metrics
# ---------------------------------------------------------------------------

def _clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def calculate_income_expense_summary(profile: dict) -> dict:
    monthly_income = normalize_income(profile["income"])
    monthly_expenses = profile.get("expenses", 0)

    if monthly_income <= 0:
        return {
            "monthlyIncome": monthly_income,
            "monthlyExpenses": monthly_expenses,
            "monthlySavings": None,
            "savingsRate": None,
            "status": "unavailable",
        }

    monthly_savings = monthly_income - monthly_expenses
    savings_rate = (monthly_savings / monthly_income) * 100

    if savings_rate < 0:
        status = "deficit"
    elif savings_rate < 10:
        status = "poor"
    elif savings_rate < 20:
        status = "fair"
    elif savings_rate < 30:
        status = "good"
    else:
        status = "excellent"

    return {
        "monthlyIncome": monthly_income,
        "monthlyExpenses": monthly_expenses,
        "monthlySavings": monthly_savings,
        "savingsRate": round(savings_rate, 2),
        "status": status,
    }


def calculate_savings_score(savings_rate: Optional[float]) -> float:
    if savings_rate is None:
        return 0
    if savings_rate < 0:
        return 0
    if savings_rate < 10:
        return 25
    if savings_rate < 20:
        return 50
    if savings_rate < 30:
        return 75
    return 100


def calculate_emergency_fund(profile: dict, monthly_expenses: float) -> dict:
    savings = profile.get("savings", 0)

    if monthly_expenses == 0:
        months_covered = float("inf")
        score = 100
    else:
        months_covered = savings / monthly_expenses
        if months_covered < 1:
            score = 0
        elif months_covered < 3:
            score = 40
        elif months_covered < 6:
            score = 75
        else:
            score = 100

    if months_covered == float("inf") or months_covered >= 6:
        status = "strong"
    elif months_covered >= 3:
        status = "adequate"
    else:
        status = "insufficient"

    return {
        "monthsCovered": None if months_covered == float("inf") else round(months_covered, 2),
        "status": status,
        "_score": score,
    }


def calculate_debt(loans: list[dict], monthly_income: float) -> dict:
    total_monthly_emi = sum(l.get("emiAmount", 0) for l in loans)

    if monthly_income <= 0:
        return {
            "totalMonthlyEMI": total_monthly_emi,
            "emiBurden": None,
            "status": "unavailable",
            "_score": 0,
        }

    emi_burden = (total_monthly_emi / monthly_income) * 100

    if emi_burden < 20:
        status, score = "low", 100
    elif emi_burden < 30:
        status, score = "moderate", 75
    elif emi_burden < 40:
        status, score = "high", 50
    elif emi_burden < 50:
        status, score = "veryHigh", 25
    else:
        status, score = "veryHigh", 0

    return {
        "totalMonthlyEMI": total_monthly_emi,
        "emiBurden": round(emi_burden, 2),
        "status": status,
        "_score": score,
    }


def calculate_insurance_adequacy(insurance: list[dict], profile: dict, monthly_income: float) -> dict:
    has_dependents = len(profile.get("dependents", [])) > 0
    annual_income = monthly_income * 12

    life_coverage = sum(
        i.get("coverageAmount", 0)
        for i in insurance
        if i.get("insuranceType") in ("life", "termLife")
    )
    health_coverage = sum(
        i.get("coverageAmount", 0)
        for i in insurance
        if i.get("insuranceType") == "health"
    )

    if not has_dependents:
        life_status = "notApplicable"
    elif annual_income <= 0:
        life_status = "unavailable"
    elif life_coverage >= annual_income * 10:
        life_status = "adequate"
    elif life_coverage >= annual_income * 5:
        life_status = "partial"
    else:
        life_status = "inadequate"

    health_status = "adequate" if health_coverage >= 500000 else "inadequate"

    return {
        "lifeCoverage": life_coverage,
        "lifeStatus": life_status,
        "healthCoverage": health_coverage,
        "healthStatus": health_status,
        "hasDependents": has_dependents,
    }


def calculate_investment_summary(investments: list[dict]) -> dict:
    total_invested = sum(i.get("amountInvested", 0) for i in investments)
    total_current_value = sum(i.get("currentValue", 0) for i in investments)

    allocation: dict[str, float] = {}
    for inv in investments:
        inv_type = inv.get("investmentType", "other")
        allocation[inv_type] = allocation.get(inv_type, 0) + inv.get("currentValue", 0)

    return {
        "totalInvested": total_invested,
        "totalCurrentValue": total_current_value,
        "gain": total_current_value - total_invested,
        "allocation": allocation,
    }


def _goal_progress_status(goal: dict) -> str:
    target_amount = goal.get("targetAmount", 0)
    current_amount = goal.get("currentAmount", 0)
    target_date = goal.get("targetDate")
    created_at = goal.get("createdAt")

    if target_amount > 0 and current_amount >= target_amount:
        return "completed"

    now = datetime.now(timezone.utc)

    if isinstance(target_date, date) and not isinstance(target_date, datetime):
        target_date = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
    if isinstance(created_at, date) and not isinstance(created_at, datetime):
        created_at = datetime.combine(created_at, datetime.min.time(), tzinfo=timezone.utc)

    if target_date and now > target_date and current_amount < target_amount:
        return "overdue"

    if not target_date or not created_at or target_amount <= 0:
        return "onTrack"

    total_duration = (target_date - created_at).total_seconds()
    elapsed_duration = (now - created_at).total_seconds()

    if total_duration <= 0:
        expected_progress = 100
    else:
        expected_progress = _clamp((elapsed_duration / total_duration) * 100)

    progress_percent = _clamp((current_amount / target_amount) * 100)

    if progress_percent >= expected_progress - 10:
        return "onTrack"
    return "behindSchedule"


def calculate_goal_progress(goals: list[dict]) -> dict:
    active_goals = [g for g in goals]
    results = []
    on_track = 0

    for goal in active_goals:
        status = _goal_progress_status(goal)
        if status in ("onTrack", "completed"):
            on_track += 1
        results.append({
            "goalId": str(goal.get("_id")),
            "goalName": goal.get("goalName"),
            "goalType": goal.get("goalType"),
            "priority": goal.get("priority"),
            "progressPercent": _clamp(
                (goal.get("currentAmount", 0) / goal.get("targetAmount", 1)) * 100
            ) if goal.get("targetAmount", 0) > 0 else 0,
            "status": status,
        })

    if not active_goals:
        score = 100
    else:
        score = (on_track / len(active_goals)) * 100

    return {
        "totalActive": len(active_goals),
        "onTrack": on_track,
        "behindSchedule": len(active_goals) - on_track,
        "goals": results,
        "_score": score,
    }


# ---------------------------------------------------------------------------
# Financial health score
# ---------------------------------------------------------------------------

def calculate_financial_health(
    savings_score: float,
    emergency_score: float,
    debt_score: float,
    goal_score: float,
) -> dict:
    total = (
        savings_score * 0.35
        + emergency_score * 0.25
        + debt_score * 0.25
        + goal_score * 0.15
    )
    score = round(_clamp(total))

    if score >= 85:
        grade, label = "A", "Excellent"
    elif score >= 70:
        grade, label = "B", "Good"
    elif score >= 50:
        grade, label = "C", "Fair"
    else:
        grade, label = "D", "Poor"

    return {"score": score, "grade": grade, "label": label}


# ---------------------------------------------------------------------------
# Insight rules
# ---------------------------------------------------------------------------

def generate_insights(
    income_expense: dict,
    emergency_fund: dict,
    debt: dict,
    insurance: dict,
    goal_progress: dict,
) -> list[dict]:
    insights = []

    savings_rate = income_expense.get("savingsRate")
    monthly_income = income_expense.get("monthlyIncome", 0)
    monthly_expenses = income_expense.get("monthlyExpenses", 0)

    if monthly_income and monthly_expenses > monthly_income:
        insights.append({"type": "incomeExpenseDeficit", "severity": "high"})
    if savings_rate is not None and savings_rate < 0:
        insights.append({"type": "negativeSavings", "severity": "high"})
    elif savings_rate is not None and savings_rate < 10:
        insights.append({"type": "lowSavingsRate", "severity": "medium"})

    months_covered = emergency_fund.get("monthsCovered")
    if months_covered is not None and months_covered < 3:
        insights.append({"type": "insufficientEmergencyFund", "severity": "high"})
    elif emergency_fund.get("status") == "strong":
        insights.append({"type": "strongEmergencyFund", "severity": "positive"})

    emi_burden = debt.get("emiBurden")
    if emi_burden is not None:
        if emi_burden >= 40:
            insights.append({"type": "highEMIBurden", "severity": "high"})
        elif emi_burden >= 20:
            insights.append({"type": "moderateEMIBurden", "severity": "medium"})
        else:
            insights.append({"type": "lowEMIBurden", "severity": "positive"})

    if insurance.get("lifeStatus") == "inadequate":
        insights.append({"type": "inadequateLifeInsurance", "severity": "high"})
    elif insurance.get("lifeStatus") == "partial":
        insights.append({"type": "partialLifeInsurance", "severity": "medium"})
    if insurance.get("healthStatus") == "inadequate":
        insights.append({"type": "inadequateHealthInsurance", "severity": "medium"})

    for goal in goal_progress.get("goals", []):
        if goal["status"] == "overdue":
            insights.append({"type": "goalOverdue", "severity": "high", "goalId": goal["goalId"]})
        elif goal["status"] == "behindSchedule":
            if goal.get("priority") == "high":
                insights.append({
                    "type": "highPriorityGoalAtRisk",
                    "severity": "high",
                    "goalId": goal["goalId"],
                })
            else:
                insights.append({
                    "type": "goalBehindSchedule",
                    "severity": "medium",
                    "goalId": goal["goalId"],
                })

    return insights


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

async def get_intelligence_overview(user_id: str) -> dict:
    data = await _gather_user_data(user_id)
    profile = data["profile"]

    if not profile:
        return {
            "financialHealth": None,
            "message": "No financial profile found. Set one up to see your intelligence overview.",
        }

    income_expense = calculate_income_expense_summary(profile)
    monthly_income = income_expense["monthlyIncome"]
    monthly_expenses = income_expense["monthlyExpenses"]

    emergency_fund = calculate_emergency_fund(profile, monthly_expenses)
    debt = calculate_debt(data["loans"], monthly_income)
    insurance = calculate_insurance_adequacy(data["insurance"], profile, monthly_income)
    investment_summary = calculate_investment_summary(data["investments"])
    goal_progress = calculate_goal_progress(data["goals"])

    savings_score = calculate_savings_score(income_expense.get("savingsRate"))

    financial_health = calculate_financial_health(
        savings_score=savings_score,
        emergency_score=emergency_fund["_score"],
        debt_score=debt["_score"],
        goal_score=goal_progress["_score"],
    )

    insights = generate_insights(income_expense, emergency_fund, debt, insurance, goal_progress)

    emergency_fund = {k: v for k, v in emergency_fund.items() if not k.startswith("_")}
    debt = {k: v for k, v in debt.items() if not k.startswith("_")}
    goal_progress_out = {k: v for k, v in goal_progress.items() if not k.startswith("_")}

    return {
        "financialHealth": financial_health,
        "income": income_expense,
        "emergencyFund": emergency_fund,
        "debt": debt,
        "insurance": insurance,
        "investments": investment_summary,
        "goals": goal_progress_out,
        "insights": insights,
    }