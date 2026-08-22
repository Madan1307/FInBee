# FinBee Backend

FastAPI + MongoDB Atlas backend for FinBee — an AI-powered financial planning
and decision-support platform. Deterministic financial calculations live in
the backend; AI is used only for explanation and conversation.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in real values
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/health` — should return `{"status": "ok", ...}`
once MONGODB_URI is set correctly.

## Structure

```
app/
├── main.py          # FastAPI entrypoint, CORS, health check
├── config.py         # env-driven settings
├── database.py        # MongoDB Atlas connection + collections
├── models/            # Pydantic schemas (user, financial_profile, goal, ...)
├── routes/            # API endpoints per resource/feature
├── services/           # business logic per feature
└── middleware/          # auth middleware, etc.
```

## Roadmap

1. Foundation (this) — FastAPI + Mongo + health check
2. Auth — Google OAuth + JWT
3. Core CRUD — users, financial_profiles, goals, loans, insurance, investments
4. Intelligence
5. Planning
6. Decisions
7. Reports
8. Search
9. AI integration
10. Frontend integration + E2E testing
