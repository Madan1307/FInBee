"""
FinBee backend entrypoint.
Phase 1: app setup, CORS, health check. Feature routers get included here
as each phase is implemented (auth, users, financial_profile, goals, ...).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import ping_database
from app.routes import auth
from app.routes import financial_profile
from app.routes import goals
from app.routes import insurance
from app.routes import loans
from app.routes import investment
from app.routes import intelligence
from app.routes import planning
from app.routes import decisions
from app.routes import reports
from app.routes import search


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "FinBee backend is running", "env": settings.ENV}


@app.get("/health")
async def health_check():
    db_ok = await ping_database()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
    }


# --- Routers get registered here as each phase is built ---
# from app.routes import auth, users, financial_profile, goals, loans, insurance, investments
# from app.routes import intelligence, planning, decisions, ai, reports, search
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(financial_profile.router, prefix="/financial-profile", tags=["financial-profile"])
app.include_router(goals.router, prefix="/goals", tags=["goals"])
app.include_router(insurance.router, prefix="/insurance", tags=["insurance"])
app.include_router(loans.router, prefix="/loans", tags=["loans"])
app.include_router(investment.router, prefix="/investments", tags=["investments"])
app.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
app.include_router(planning.router, prefix="/planning", tags=["planning"])
app.include_router(decisions.router, prefix="/decisions", tags=["decisions"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(search.router, prefix="/search", tags=["search"])
# app.include_router(users.router, prefix="/users", tags=["users"])
# ... etc, added incrementally per phase
