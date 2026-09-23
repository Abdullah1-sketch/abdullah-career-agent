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
    "business data analyst",
    "business intelligence analyst",
    "bi analyst",
    "reporting analyst",
    "power bi analyst",
    "data reporting",
    "محلل بيانات",
    "محلل ذكاء أعمال",
    "محلل تقارير",
]

ENTRY_LEVEL_SIGNALS = [
    "junior",
    "entry level",
    "fresh graduate",
    "graduate",
    "tamheer",
    "intern",
    "internship",
    "coop",
    "trainee",
    "0-1",
    "0-2",
    "0-3",
    "حديث تخرج",
    "خريج",
    "تمهير",
    "تدريب",
]

ABDULLAH_CURRENT_SKILLS = [
    "excel",
    "power bi",
    "dashboard",
    "reporting",
    "reports",
    "analysis",
    "data visualization",
    "تحليل",
    "تقارير",
    "لوحات",
    "تصور البيانات",
]

ABDULLAH_GROWING_SKILLS = [
    "sql",
    "database",
    "query",
    "queries",
    "قواعد بيانات",
    "استعلامات",
]

MISSING_BUT_ACCEPTABLE_SKILLS = [
    "python",
    "tableau",
    "looker",
    "statistics",
    "statistical",
    "machine learning",
    "بايثون",
    "إحصاء",
]

BAD_SIGNALS = [
    "senior",
    "lead",
    "manager",
    "principal",
    "staff",
    "5+ years",
    "6+ years",
    "7+ years",
    "8+ years",
    "10+ years",
    "machine learning engineer",
    "data engineer",
    "database administrator",
    "data scientist",
    "مدير",
    "خبير",
]

LOCATION_WEIGHTS = [
    (["riyadh", "الرياض"], 15, "Location fits Riyadh priority"),
    (["eastern province", "eastern", "dammam", "khobar", "dhahran", "الشرقية", "الدمام", "الخبر", "الظهران"], 12, "Location fits Eastern Province priority"),
    (["qassim", "buraydah", "unaizah", "القصيم", "بريدة", "عنيزة"], 10, "Location fits Qassim priority"),
    (["saudi arabia", "ksa", "السعودية"], 7, "Location fits Saudi Arabia preferences"),
    (["remote", "عن بعد"], 6, "Remote option may fit"),
]


def contains_any(text: str, terms: list[str]) -> bool:
    return any(term.lower() in text for term in terms)


def score_location(text: str) -> tuple[int, str | None]:
    for terms, points, reason in LOCATION_WEIGHTS:
        if contains_any(text, terms):
            return points, reason
    return 0, None


def score_opportunity(opportunity: Opportunity) -> dict:
    title_text = opportunity.title.lower()
    full_text = " ".join(
        [
            opportunity.title,
            opportunity.location,
            opportunity.description,
            opportunity.url,
        ]
    ).lower()

    score = 0
    reasons = []

    if contains_any(title_text, TARGET_TITLES):
        score += 35
        reasons.append("Relevant data-analysis title")
    elif contains_any(full_text, TARGET_TITLES):
        score += 20
        reasons.append("Relevant data-analysis title")

    if contains_any(full_text, ENTRY_LEVEL_SIGNALS):
        score += 25
        reasons.append("Matches Abdullah's entry-level path")

    if contains_any(full_text, ABDULLAH_CURRENT_SKILLS):
        score += 20
        reasons.append("Matches Abdullah's current skills")

    if contains_any(full_text, ABDULLAH_GROWING_SKILLS):
        score += 10
        reasons.append("Matches Abdullah's SQL learning path")

    location_score, location_reason = score_location(full_text)
    if location_score:
        score += location_score
        reasons.append(location_reason)

    if contains_any(full_text, MISSING_BUT_ACCEPTABLE_SKILLS):
        score -= 5
        reasons.append("Has a skill gap Abdullah can prepare for")

    if contains_any(full_text, BAD_SIGNALS):
        score -= 35
        reasons.append("May be too senior or outside target path")

    if opportunity.url and not opportunity.url.startswith("http"):
        score -= 10

    final_score = max(0, min(score, 100))

    if final_score >= 75:
        priority = "Strong"
    elif final_score >= 50:
        priority = "Medium"
    else:
        priority = "Low"

    if not reasons:
        reasons.append("Not enough job details to confirm fit")

    return {
        "score": final_score,
        "priority": priority,
        "reasons": reasons,
    }
