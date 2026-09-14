"""
Search service — simple keyword-based feature/service discovery.
Not financial-data search. No AI, no semantic search — matches the
user's query against a static catalog of FinBee's features.
"""

FEATURE_CATALOG = [
    {
        "type": "planner",
        "name": "Vehicle Planner",
        "description": "Plan and track savings for buying a vehicle.",
        "route": "/planning/vehicle",
        "keywords": ["car", "vehicle", "bike", "buy car", "vehicle planning", "auto loan"],
    },
    {
        "type": "planner",
        "name": "House Planner",
        "description": "Plan and track savings for buying a house.",
        "route": "/planning/house",
        "keywords": ["house", "home", "property", "flat", "apartment", "buy house"],
    },
    {
        "type": "planner",
        "name": "Retirement Planner",
        "description": "Plan your retirement savings and timeline.",
        "route": "/planning/retirement",
        "keywords": ["retirement", "retire", "pension", "old age"],
    },
    {
        "type": "planner",
        "name": "Education Planner",
        "description": "Plan and track savings for education expenses.",
        "route": "/planning/education",
        "keywords": ["education", "college", "school", "study", "tuition", "course"],
    },
    {
        "type": "service",
        "name": "Purchase Decision",
        "description": "Check whether a purchase may create financial burden.",
        "route": "/decisions/purchase",
        "keywords": ["afford", "can i afford", "purchase", "buy", "buying"],
    },
    {
        "type": "service",
        "name": "Loan Decision",
        "description": "Check whether taking a loan is financially sustainable.",
        "route": "/decisions/loan",
        "keywords": ["loan", "borrow", "emi", "take a loan"],
    },
    {
        "type": "service",
        "name": "Investment Decision",
        "description": "Evaluate whether a new investment fits your financial picture.",
        "route": "/decisions/investment",
        "keywords": ["invest", "investment", "should i invest"],
    },
    {
        "type": "feature",
        "name": "Financial Health",
        "description": "See your overall financial health score and insights.",
        "route": "/intelligence",
        "keywords": ["financial health", "how am i doing", "health score", "insights"],
    },
    {
        "type": "feature",
        "name": "Debt & EMI Analysis",
        "description": "See your current EMI burden and debt analysis.",
        "route": "/intelligence",
        "keywords": ["debt", "emi", "burden", "loans overview"],
    },
    {
        "type": "feature",
        "name": "Goal Progress",
        "description": "Track progress on all your financial goals.",
        "route": "/intelligence",
        "keywords": ["goal progress", "my goals", "goals"],
    },
    {
        "type": "feature",
        "name": "Reports",
        "description": "Generate and download financial reports.",
        "route": "/reports",
        "keywords": ["report", "summary", "pdf", "download report"],
    },
    {
        "type": "feature",
        "name": "AI Assistant",
        "description": "Ask questions and get personalized financial guidance.",
        "route": "/ai",
        "keywords": ["ai", "assistant", "chat", "ask", "help"],
    },
]


def match_query_to_features(query: str) -> list[dict]:
    """
    Simple keyword matching: scores each catalog entry by how many
    of its keywords appear as substrings in the query, returns matches
    sorted by score descending. No AI/semantic matching involved.
    """
    query_lower = query.lower()
    results = []

    for feature in FEATURE_CATALOG:
        score = sum(1 for kw in feature["keywords"] if kw in query_lower)
        if score > 0:
            results.append({**feature, "matchScore": score})

    results.sort(key=lambda f: f["matchScore"], reverse=True)
    return [{k: v for k, v in r.items() if k != "keywords"} for r in results]