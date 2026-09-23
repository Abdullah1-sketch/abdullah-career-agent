from target_companies import TARGET_COMPANIES


SECTOR_WEIGHTS = {
    "Banking": 25,
    "Fintech": 25,
    "Consulting": 25,
    "Consulting and technology": 25,
    "Digital government and technology": 25,
    "Data and AI government authority": 25,
    "Financial regulator": 25,
    "Delivery and marketplace": 20,
    "SaaS and restaurant technology": 20,
    "Telecom and digital services": 20,
    "Smart mobility and public safety technology": 20,
    "Capital markets": 20,
    "Airline": 15,
    "Insurance": 15,
    "Insurance and healthcare": 15,
    "Retail": 10,
    "Logistics": 10,
}


PROJECT_FIT_KEYWORDS = [
    "sama",
    "financial",
    "bank",
    "fintech",
    "delivery",
    "marketplace",
    "retail",
    "operations",
    "tourism",
    "airline",
    "public-data",
    "reporting",
]


def calculate_company_focus_score(company: dict) -> dict:
    score = 0
    reasons = []

    if company.get("priority") == "high":
        score += 35
        reasons.append("High-priority target")
    elif company.get("priority") == "medium":
        score += 20
        reasons.append("Medium-priority target")

    sector = company.get("sector", "")
    sector_score = SECTOR_WEIGHTS.get(sector, 5)
    score += sector_score
    reasons.append(f"Sector fit score: {sector_score}")

    searchable_text = " ".join(
        [
            company.get("name", ""),
            company.get("sector", ""),
            company.get("why", ""),
        ]
    ).lower()

    if any(keyword in searchable_text for keyword in PROJECT_FIT_KEYWORDS):
        score += 25
        reasons.append("Good mini-project or portfolio angle")

    final_score = max(0, min(score, 100))

    return {
        **company,
        "focus_score": final_score,
        "focus_reasons": reasons,
    }


def get_top_focus_companies(limit: int = 10) -> list[dict]:
    scored = [calculate_company_focus_score(company) for company in TARGET_COMPANIES]
    return sorted(scored, key=lambda company: company["focus_score"], reverse=True)[:limit]


def build_company_watchlist_summary(limit: int = 10) -> str:
    companies = get_top_focus_companies(limit)

    if not companies:
        return "لا توجد شركات للمراقبة حاليًا."

    lines = []
    for company in companies:
        lines.append(
            f'- {company["name"]} ({company["sector"]}) | درجة التركيز: {company["focus_score"]}/100'
        )

    return "\n".join(lines)
