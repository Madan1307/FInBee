"""
Report endpoints — generated on demand, nothing persisted:
- GET /reports/financial-health
- GET /reports/goals
- GET /reports/summary
- GET /reports/summary/pdf — same data, rendered as a downloadable PDF
"""

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.middleware.auth import get_current_user
from app.services.reports import (
    build_financial_health_report,
    build_goals_report,
    build_summary_report,
    render_summary_pdf,
)

router = APIRouter()


@router.get("/financial-health")
async def get_financial_health_report(current_user: dict = Depends(get_current_user)):
    return await build_financial_health_report(str(current_user["_id"]))


@router.get("/goals")
async def get_goals_report(current_user: dict = Depends(get_current_user)):
    return await build_goals_report(str(current_user["_id"]))


@router.get("/summary")
async def get_summary_report(current_user: dict = Depends(get_current_user)):
    return await build_summary_report(str(current_user["_id"]))


@router.get("/summary/pdf")
async def get_summary_report_pdf(current_user: dict = Depends(get_current_user)):
    report = await build_summary_report(str(current_user["_id"]))
    pdf_bytes = render_summary_pdf(report)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=finbee-summary-report.pdf"},
    )

