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
    "graduate data analyst",
    "business data analyst",
    "business intelligence analyst",
    "bi analyst",
    "reporting analyst",
    "data reporting analyst",
    "power bi analyst",
    "data specialist",
    "محلل بيانات",
    "محلل ذكاء أعمال",
    "محلل تقارير",
    "أخصائي بيانات",
]

ADJACENT_ANALYTICS_TITLES = [
    "analytics analyst",
    "hr analytics analyst",
    "people analytics",
    "people analytics analyst",
    "workforce analytics",
    "workforce analytics analyst",
    "talent analytics",
    "performance analyst",
    "insights analyst",
    "business analyst",
    "operations analyst",
    "commercial analyst",
    "product analyst",
    "محلل أعمال",
    "محلل أداء",
    "محلل عمليات",
    "محلل موارد بشرية",
]

DATA_CONTEXT_SIGNALS = [
    "data",
    "analytics",
    "analysis",
    "business intelligence",
    "bi",
    "reporting",
    "reports",
    "dashboard",
    "dashboards",
    "power bi",
    "sql",
    "excel",
    "kpi",
    "metrics",
    "insights",
    "visualization",
    "data quality",
    "predictive",
    "تحليل",
    "بيانات",
    "تقارير",
    "لوحات",
    "مؤشرات",
    "ذكاء الأعمال",
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
    "1-2 years",
    "2 years",
    "حديث تخرج",
    "خريج",
    "تمهير",
    "تدريب",
    "متدرب",
]

ABDULLAH_CURRENT_SKILLS = [
    "excel",
    "power bi",
    "dashboard",
    "dashboards",
    "reporting",
    "reports",
    "analysis",
    "analytics",
    "business intelligence",
    "bi",
    "data visualization",
    "visualization",
    "metrics",
    "kpi",
    "insights",
    "تحليل",
    "تقارير",
    "لوحات",
    "مؤشرات",
    "تصور البيانات",
]

ABDULLAH_GROWING_SKILLS = [
    "sql",
    "database",
    "query",
    "queries",
    "data quality",
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
    "predictive",
    "بايثون",
    "إحصاء",
]

BAD_SIGNALS = [
    "senior",
    "lead",
    "manager",
    "director",
    "principal",
    "staff",
    "head of",
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
    "رئيس",
]

INTERVIEW_PATH_SIGNALS = [
    "careers",
    "apply",
    "job",
    "jobs",
    "recruiter",
    "hiring",
    "talent acquisition",
    "linkedin.com/jobs",
    "greenhouse",
    "lever",
    "ashby",
    "workday",
    "oraclecloud",
    "successfactors",
    "smartrecruiters",
    "تقديم",
    "توظيف",
    "وظائف",
]

LOCATION_WEIGHTS = [
    (["riyadh", "الرياض"], 20, "Location fits Riyadh priority"),
    (["qassim", "buraydah", "unaizah", "القصيم", "بريدة", "عنيزة"], 16, "Location fits Qassim priority"),
    (["eastern province", "eastern", "dammam", "khobar", "dhahran", "الشرقية", "الدمام", "الخبر", "الظهران"], 12, "Location fits Eastern Province priority"),
    (["saudi arabia", "ksa", "السعودية"], 8, "Location fits Saudi Arabia preferences"),
    (["remote", "hybrid", "عن بعد", "هجين"], 6, "Remote option may fit"),
]


def contains_any(text: str, terms: list[str]) -> bool:
    return any(term.lower() in text for term in terms)


def add_reason(reasons: list[str], reason: str | None) -> None:
    if reason and reason not in reasons:
        reasons.append(reason)


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
            opportunity.company,
            opportunity.location,
            opportunity.description,
            opportunity.url,
        ]
    ).lower()

    score = 0
    reasons = []

    has_direct_title = contains_any(title_text, TARGET_TITLES)
    has_direct_title_in_text = contains_any(full_text, TARGET_TITLES)
    has_adjacent_title = contains_any(title_text, ADJACENT_ANALYTICS_TITLES)
    has_adjacent_title_in_text = contains_any(full_text, ADJACENT_ANALYTICS_TITLES)
    has_data_context = contains_any(full_text, DATA_CONTEXT_SIGNALS)

    if has_direct_title:
        score += 40
        add_reason(reasons, "Relevant data-analysis title")
    elif has_adjacent_title and has_data_context:
        score += 35
        add_reason(reasons, "Relevant data-analysis title")
    elif has_direct_title_in_text:
        score += 25
        add_reason(reasons, "Relevant data-analysis title")
    elif has_adjacent_title_in_text and has_data_context:
        score += 22
        add_reason(reasons, "Relevant data-analysis title")

    if contains_any(full_text, ENTRY_LEVEL_SIGNALS):
        score += 15
        add_reason(reasons, "Matches Abdullah's entry-level path")

    if contains_any(full_text, ABDULLAH_CURRENT_SKILLS):
        score += 25
        add_reason(reasons, "Matches Abdullah's current skills")

    if contains_any(full_text, ABDULLAH_GROWING_SKILLS):
        score += 10
        add_reason(reasons, "Matches Abdullah's SQL learning path")

    location_score, location_reason = score_location(full_text)
    if location_score:
        score += location_score
        add_reason(reasons, location_reason)

    if contains_any(full_text, INTERVIEW_PATH_SIGNALS):
        score += 10
        add_reason(reasons, "Has a clearer path to interview or outreach")

    if contains_any(full_text, MISSING_BUT_ACCEPTABLE_SKILLS):
        score -= 5
        add_reason(reasons, "Has a skill gap Abdullah can prepare for")

    if contains_any(full_text, BAD_SIGNALS):
        score -= 35
        add_reason(reasons, "May be too senior or outside target path")

    if not has_data_context:
        score -= 15
        add_reason(reasons, "Not enough job details to confirm fit")

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
