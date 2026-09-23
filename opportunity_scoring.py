from dataclasses import dataclass


@dataclass(frozen=True)
class Opportunity:
    title: str
    company: str
    location: str
    description: str
    url: str


TARGET_TITLES = [
    "data analyst",
    "junior data analyst",
    "business intelligence analyst",
    "bi analyst",
    "reporting analyst",
    "data specialist",
    "محلل بيانات",
    "ذكاء الأعمال",
]

GOOD_SIGNALS = [
    "excel",
    "power bi",
    "sql",
    "dashboard",
    "reporting",
    "analysis",
    "تحليل",
    "تقارير",
    "لوحات",
    "تمهير",
    "fresh graduate",
    "entry level",
    "junior",
]

INTERVIEW_PATH_SIGNALS = [
    "careers",
    "apply",
    "recruiter",
    "hiring",
    "talent acquisition",
    "linkedin.com/jobs",
    "greenhouse",
    "lever",
    "ashby",
    "workday",
    "oraclecloud",
    "تقديم",
    "توظيف",
    "وظائف",
]

BAD_SIGNALS = [
    "senior",
    "lead",
    "manager",
    "5+ years",
    "7+ years",
    "machine learning engineer",
    "data engineer",
    "database administrator",
]

PREFERRED_LOCATIONS = [
    "riyadh",
    "الرياض",
    "eastern province",
    "الشرقية",
    "dammam",
    "الدمام",
    "khobar",
    "الخبر",
    "qassim",
    "القصيم",
    "remote",
    "عن بعد",
    "saudi arabia",
    "السعودية",
]


def score_opportunity(opportunity: Opportunity) -> dict:
    text = " ".join(
        [
            opportunity.title,
            opportunity.company,
            opportunity.location,
            opportunity.description,
            opportunity.url,
        ]
    ).lower()

    score = 0
    reasons = []

    if any(term in text for term in TARGET_TITLES):
        score += 35
        reasons.append("Relevant data-analysis title")

    if any(term in text for term in GOOD_SIGNALS):
        score += 30
        reasons.append("Matches Abdullah's current skills or entry-level path")

    if any(term in text for term in PREFERRED_LOCATIONS):
        score += 20
        reasons.append("Location fits Saudi Arabia preferences")

    if opportunity.company.strip() and any(term in text for term in INTERVIEW_PATH_SIGNALS):
        score += 15
        reasons.append("Has a clearer path to interview or outreach")

    if any(term in text for term in BAD_SIGNALS):
        score -= 25
        reasons.append("May be too senior or outside target path")

    final_score = max(0, min(score, 100))

    if final_score >= 75:
        priority = "Strong"
    elif final_score >= 50:
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "score": final_score,
        "priority": priority,
        "reasons": reasons,
    }
