"""
Decisions service — deterministic financial burden/affordability assessment.
No AI involved. Reuses the exact EMI burden thresholds from Intelligence
(services/intelligence.py) for consistency between the two features.
"""

from app.database import (
    financial_profiles_collection,
    loans_collection,
)
from app.services.financial_profile import normalize_income


async def gather_decision_context(user_id: str) -> dict:
    profile = await financial_profiles_collection.find_one({"userId": user_id})
    loans = [l async for l in loans_collection.find({"userId": user_id})]
    return {"profile": profile, "loans": loans}


def _emi_burden_status(emi_burden: float) -> str:
    """Same thresholds as Intelligence's debt analysis — kept identical
    on purpose so a user sees one consistent definition of 'burden'."""
    if emi_burden < 20:
        return "low"
    if emi_burden < 30:
        return "moderate"
    if emi_burden < 40:
        return "high"
    return "veryHigh"


def calculate_monthly_surplus(profile: dict) -> float:
    monthly_income = normalize_income(profile["income"])
    monthly_expenses = profile.get("expenses", 0)
    return monthly_income - monthly_expenses


def calculate_projected_emi_impact(context: dict, decision: dict) -> dict:
    profile = context["profile"]
    loans = context["loans"]

    monthly_income = normalize_income(profile["income"])
    existing_emi = sum(l.get("emiAmount", 0) for l in loans)
    new_emi = decision.get("newEmiAmount", 0)
    projected_emi = existing_emi + new_emi

    if monthly_income <= 0:
        return {
            "existingEMI": existing_emi,
            "newEMI": new_emi,
            "projectedEMI": projected_emi,
            "projectedEMIBurden": None,
            "status": "unavailable",
        }

    projected_burden = (projected_emi / monthly_income) * 100

    return {
        "existingEMI": existing_emi,
        "newEMI": new_emi,
        "projectedEMI": projected_emi,
        "projectedEMIBurden": round(projected_burden, 2),
        "status": _emi_burden_status(projected_burden),
    }


def calculate_emergency_fund_impact(profile: dict, decision: dict) -> dict:
    savings = profile.get("savings", 0)
    down_payment = decision.get("downPayment", 0)
    monthly_expenses = profile.get("expenses", 0)

    remaining_savings = savings - down_payment

    if monthly_expenses > 0:
        months_after = remaining_savings / monthly_expenses
    else:
        months_after = None

    return {
        "savingsBefore": savings,
        "savingsAfter": remaining_savings,
        "emergencyFundMonthsAfter": round(months_after, 2) if months_after is not None else None,
        "depleted": remaining_savings < 0,
    }


def calculate_savings_impact(profile: dict, decision: dict) -> dict:
    monthly_surplus = calculate_monthly_surplus(profile)
    new_emi = decision.get("newEmiAmount", 0)
    surplus_after = monthly_surplus - new_emi

    return {
        "monthlySurplusBefore": round(monthly_surplus, 2),
        "monthlySurplusAfter": round(surplus_after, 2),
        "goesNegative": surplus_after < 0,
    }


def assess_burden(
    emi_impact: dict,
    emergency_impact: dict,
    savings_impact: dict,
) -> str:
    """
    Combines the three factors into one overall burden level.
    EMI burden status is the primary driver; emergency fund depletion
    or negative surplus escalates the result.
    """
    emi_status = emi_impact.get("status", "unavailable")

    order = ["low", "moderate", "high", "veryHigh"]
    base_index = order.index(emi_status) if emi_status in order else 1

    if emergency_impact.get("depleted") or savings_impact.get("goesNegative"):
        base_index = min(base_index + 1, len(order) - 1)

    return order[base_index]


def build_reasons_and_recommendations(
    emi_impact: dict,
    emergency_impact: dict,
    savings_impact: dict,
    assessment: str,
) -> tuple[list[str], list[str]]:
    reasons = []
    recommendations = []

    if emi_impact.get("projectedEMIBurden") is not None:
        reasons.append(
            f"Projected EMI burden would be {emi_impact['projectedEMIBurden']}% of monthly income "
            f"({emi_impact['status']})."
        )

    if emergency_impact.get("depleted"):
        reasons.append("This decision would fully deplete your available savings.")
        recommendations.append("Consider a smaller down payment or delaying this decision.")
    elif emergency_impact.get("emergencyFundMonthsAfter") is not None and emergency_impact["emergencyFundMonthsAfter"] < 3:
        reasons.append(
            f"Your emergency fund would cover only {emergency_impact['emergencyFundMonthsAfter']} months of expenses afterward."
        )
        recommendations.append("Aim to keep at least 3 months of expenses in savings after this decision.")

    if savings_impact.get("goesNegative"):
        reasons.append("This decision would push your monthly surplus into deficit.")
        recommendations.append("Reduce the loan amount or increase the down payment to keep a positive monthly surplus.")

    if assessment in ("high", "veryHigh"):
        recommendations.append("Consider increasing the down payment or extending the tenure to lower the EMI.")
    elif assessment == "low" and not recommendations:
        recommendations.append("This decision looks financially comfortable based on your current profile.")

    if not reasons:
        reasons.append("This decision has minimal impact on your current financial position.")

    return reasons, recommendations


async def build_decision_result(user_id: str, decision: dict) -> dict:
    context = await gather_decision_context(user_id)
    profile = context["profile"]

    if not profile:
        return {
            "assessment": "unavailable",
            "financialImpact": {},
            "reasons": ["No financial profile found. Please set one up first."],
            "recommendations": [],
        }

    emi_impact = calculate_projected_emi_impact(context, decision)
    emergency_impact = calculate_emergency_fund_impact(profile, decision)
    savings_impact = calculate_savings_impact(profile, decision)

    assessment = assess_burden(emi_impact, emergency_impact, savings_impact)
    reasons, recommendations = build_reasons_and_recommendations(
        emi_impact, emergency_impact, savings_impact, assessment
    )

    return {
        "assessment": assessment,
        "financialImpact": {
            "emi": emi_impact,
            "emergencyFund": emergency_impact,
            "savings": savings_impact,
        },
        "reasons": reasons,
        "recommendations": recommendations,
    }