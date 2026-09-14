"""
Reports service — generates reports from already-computed data.
No new calculations here; reuses Intelligence, Decisions and Planning
services. Nothing is persisted — reports are generated on demand.
"""

import io
from datetime import datetime, timezone

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

from app.services.intelligence import get_intelligence_overview
from app.database import goals_collection


async def build_financial_health_report(user_id: str) -> dict:
    overview = await get_intelligence_overview(user_id)
    return {
        "reportType": "financialHealth",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "financialHealth": overview.get("financialHealth"),
        "income": overview.get("income"),
        "emergencyFund": overview.get("emergencyFund"),
        "debt": overview.get("debt"),
        "insurance": overview.get("insurance"),
        "insights": overview.get("insights"),
    }


async def build_goals_report(user_id: str) -> dict:
    overview = await get_intelligence_overview(user_id)
    return {
        "reportType": "goals",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "goals": overview.get("goals"),
    }


async def build_summary_report(user_id: str) -> dict:
    overview = await get_intelligence_overview(user_id)
    return {
        "reportType": "summary",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        **overview,
    }


def _insight_label(insight_type: str) -> str:
    """Turns camelCase insight flags into readable labels for the PDF."""
    labels = {
        "incomeExpenseDeficit": "Income-Expense Deficit",
        "negativeSavings": "Negative Savings",
        "lowSavingsRate": "Low Savings Rate",
        "insufficientEmergencyFund": "Insufficient Emergency Fund",
        "strongEmergencyFund": "Strong Emergency Fund",
        "highEMIBurden": "High EMI Burden",
        "moderateEMIBurden": "Moderate EMI Burden",
        "lowEMIBurden": "Low EMI Burden",
        "inadequateLifeInsurance": "Inadequate Life Insurance",
        "partialLifeInsurance": "Partial Life Insurance Coverage",
        "inadequateHealthInsurance": "Inadequate Health Insurance",
        "goalBehindSchedule": "Goal Behind Schedule",
        "highPriorityGoalAtRisk": "High-Priority Goal At Risk",
        "goalOverdue": "Goal Overdue",
    }
    return labels.get(insight_type, insight_type)


def render_summary_pdf(report: dict) -> bytes:
    """Renders the summary report as a PDF, returned as raw bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("FinBee Financial Summary Report", styles["Title"]))
    story.append(Spacer(1, 12))

    health = report.get("financialHealth") or {}
    story.append(Paragraph(
        f"Financial Health: {health.get('score', 'N/A')} "
        f"({health.get('grade', '')} - {health.get('label', '')})",
        styles["Heading2"],
    ))
    story.append(Spacer(1, 8))

    income = report.get("income") or {}
    income_rows = [
        ["Monthly Income", str(income.get("monthlyIncome", "N/A"))],
        ["Monthly Expenses", str(income.get("monthlyExpenses", "N/A"))],
        ["Monthly Savings", str(income.get("monthlySavings", "N/A"))],
        ["Savings Rate", f"{income.get('savingsRate', 'N/A')}%"],
    ]
    income_table = Table(income_rows, colWidths=[2.5 * inch, 2.5 * inch])
    income_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(income_table)
    story.append(Spacer(1, 16))

    debt = report.get("debt") or {}
    story.append(Paragraph(
        f"Debt: EMI burden {debt.get('emiBurden', 'N/A')}% ({debt.get('status', 'N/A')})",
        styles["Normal"],
    ))

    emergency = report.get("emergencyFund") or {}
    story.append(Paragraph(
        f"Emergency Fund: {emergency.get('monthsCovered', 'N/A')} months covered "
        f"({emergency.get('status', 'N/A')})",
        styles["Normal"],
    ))
    story.append(Spacer(1, 16))

    insights = report.get("insights") or []
    if insights:
        story.append(Paragraph("Insights", styles["Heading2"]))
        for insight in insights:
            story.append(Paragraph(
                f"- {_insight_label(insight.get('type', ''))} ({insight.get('severity', '')})",
                styles["Normal"],
            ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

