"""
Planning service — roadmap calculators for each planner type.
Deterministic math only, no AI. Pulls the user's financial_profile for
monthly income and applies simple savings-based projections.
"""

from datetime import datetime, date, timezone
from typing import Optional

from app.database import financial_profiles_collection
from app.services.financial_profile import normalize_income


PLANNER_TYPES = [
    {
        "goalType": "vehicle",
        "label": "Vehicle Planner",
        "fields": ["vehicleType", "vehiclePrice", "downPayment", "financingPreference"],
    },
    {
        "goalType": "house",
        "label": "House Planner",
        "fields": ["propertyType", "location", "expectedPropertyValue", "downPayment", "financingPreference"],
    },
    {
        "goalType": "retirement",
        "label": "Retirement Planner",
        "fields": ["currentAge", "retirementAge", "currentRetirementSavings", "expectedMonthlyExpensePostRetirement"],
    },
    {
        "goalType": "education",
        "label": "Education Planner",
        "fields": ["studentName", "courseType", "expectedEducationCost", "targetYear"],
    },
]


def list_planner_types() -> list[dict]:
    return PLANNER_TYPES


def _months_between(start: datetime, end: datetime) -> int:
    months = (end.year - start.year) * 12 + (end.month - start.month)
    return max(months, 0)


async def _get_monthly_income(user_id: str) -> Optional[float]:
    profile = await financial_profiles_collection.find_one({"userId": user_id})
    if not profile:
        return None
    return normalize_income(profile["income"])


def _normalize_date(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)
    return None


async def get_roadmap(goal: dict, user_id: str) -> dict:
    """
    Dispatches to the right calculator based on goalType.
    All planners share the same core projection: how much needs to be
    saved per month to reach targetAmount by targetDate, given
    currentAmount already saved.
    """
    goal_type = goal.get("goalType")
    target_amount = goal.get("targetAmount", 0)
    current_amount = goal.get("currentAmount", 0)
    target_date = _normalize_date(goal.get("targetDate"))
    now = datetime.now(timezone.utc)

    remaining_amount = max(target_amount - current_amount, 0)

    if not target_date or target_date <= now:
        months_remaining = 0
    else:
        months_remaining = _months_between(now, target_date)

    if months_remaining > 0:
        required_monthly_saving = remaining_amount / months_remaining
    else:
        required_monthly_saving = remaining_amount  # due now / overdue

    monthly_income = await _get_monthly_income(user_id)

    affordability = None
    if monthly_income and monthly_income > 0:
        pct_of_income = (required_monthly_saving / monthly_income) * 100
        if pct_of_income <= 20:
            affordability = "comfortable"
        elif pct_of_income <= 40:
            affordability = "moderate"
        else:
            affordability = "stretched"

    base_result = {
        "goalType": goal_type,
        "targetAmount": target_amount,
        "currentAmount": current_amount,
        "remainingAmount": remaining_amount,
        "monthsRemaining": months_remaining,
        "requiredMonthlySaving": round(required_monthly_saving, 2),
        "affordability": affordability,
    }

    if goal_type == "vehicle":
        base_result.update(_vehicle_roadmap(goal))
    elif goal_type == "house":
        base_result.update(_house_roadmap(goal))
    elif goal_type == "retirement":
        base_result.update(_retirement_roadmap(goal))
    elif goal_type == "education":
        base_result.update(_education_roadmap(goal))

    return base_result


def _vehicle_roadmap(goal: dict) -> dict:
    data = goal.get("goalSpecificData", {})
    vehicle_price = data.get("vehiclePrice", goal.get("targetAmount", 0))
    down_payment = data.get("downPayment", 0)
    loan_amount = max(vehicle_price - down_payment, 0)
    return {
        "vehiclePrice": vehicle_price,
        "downPayment": down_payment,
        "estimatedLoanAmount": loan_amount,
    }


def _house_roadmap(goal: dict) -> dict:
    data = goal.get("goalSpecificData", {})
    property_value = data.get("expectedPropertyValue", goal.get("targetAmount", 0))
    down_payment = data.get("downPayment", 0)
    loan_amount = max(property_value - down_payment, 0)
    return {
        "expectedPropertyValue": property_value,
        "downPayment": down_payment,
        "estimatedLoanAmount": loan_amount,
    }


def _retirement_roadmap(goal: dict) -> dict:
    data = goal.get("goalSpecificData", {})
    current_age = data.get("currentAge")
    retirement_age = data.get("retirementAge")
    years_to_retirement = None
    if current_age is not None and retirement_age is not None:
        years_to_retirement = max(retirement_age - current_age, 0)
    return {
        "currentAge": current_age,
        "retirementAge": retirement_age,
        "yearsToRetirement": years_to_retirement,
        "currentRetirementSavings": data.get("currentRetirementSavings", 0),
    }


def _education_roadmap(goal: dict) -> dict:
    data = goal.get("goalSpecificData", {})
    return {
        "studentName": data.get("studentName"),
        "courseType": data.get("courseType"),
        "expectedEducationCost": data.get("expectedEducationCost", goal.get("targetAmount", 0)),
        "targetYear": data.get("targetYear"),
    }