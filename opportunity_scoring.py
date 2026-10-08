from dataclasses import dataclass
import re
from urllib.parse import urlparse


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
    "statistician",
    "محلل أعمال",
    "محلل أداء",
    "محلل عمليات",
    "محلل موارد بشرية",
    "إحصائي",
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
    "statistical",
    "statistics",
    "تحليل",
    "بيانات",
    "تقارير",
    "لوحات",
    "مؤشرات",
    "ذكاء الأعمال",
    "إحصاء",
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

# Checked against the job TITLE only: descriptions often mention these
# words for other people ("report to the manager", "work with data engineers").
BAD_TITLE_SIGNALS = [
    "senior",
    "lead",
    "manager",
    "director",
    "principal",
    "staff",
    "head of",
    "machine learning engineer",
    "data engineer",
    "database administrator",
    "data scientist",
    "مدير",
    "خبير",
    "رئيس",
]

# A job is too senior when it asks for at least this many years.
TOO_MANY_YEARS = 3
# Bigger numbers next to "years" are usually age limits ("22-35 years old").
MAX_REALISTIC_YEARS = 15

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "ثلاث": 3, "ثلاثة": 3, "أربع": 4, "اربع": 4, "أربعة": 4, "اربعة": 4,
    "خمس": 5, "خمسة": 5, "ست": 6, "ستة": 6, "سبع": 7, "سبعة": 7,
    "ثمان": 8, "ثماني": 8, "ثمانية": 8, "عشر": 10, "عشرة": 10,
}

NUMBER_WORD_PATTERN = re.compile(
    r"(?<![a-z\u0600-\u06FF])("
    + "|".join(sorted(NUMBER_WORDS, key=len, reverse=True))
    + r")(?![a-z\u0600-\u06FF])"
)

YEAR_WORD = r"(?:years?|yrs?|سنوات|سنة|سنين|أعوام|عام)"
RANGE_SEPARATOR = r"(?:-|–|to|إلى|الى|و)"
YEARS_RANGE_PATTERN = re.compile(rf"(\d+)\s*{RANGE_SEPARATOR}\s*(\d+)\s*\+?\s*{YEAR_WORD}")
SINGLE_YEARS_PATTERN = re.compile(rf"(\d+)\s*\+?\s*{YEAR_WORD}")
EXPERIENCE_CONTEXT_PATTERN = re.compile(r"experience|\bexp\b|خبرة|خبره|minimum|at least|لا تقل|\+")
EXPERIENCE_CONTEXT_WINDOW = 60

STALE_SIGNALS = [
    "posted 2 years ago",
    "posted 1 year ago",
    "posted a year ago",
    "months ago",
    "closed",
    "expired",
    "no longer accepting applications",
    "منذ سنة",
    "منذ سنتين",
    "منذ أشهر",
    "مغلق",
    "منتهي",
]

HRIS_HEAVY_SIGNALS = [
    "hris",
    "oracle hcm",
    "workday",
    "sap successfactors",
    "successfactors",
    "gosi",
    "qiwa",
    "mudad",
    "muqeem",
    "absher",
    "nitaqat",
    "saudization",
    "employee master data",
    "hr data integrity",
    "قوى",
    "مدد",
    "مقيم",
    "أبشر",
    "نطاقات",
    "التأمينات",
    "سعودة",
]

PROCESS_ONLY_SIGNALS = [
    "business process documentation",
    "process documentation",
    "workflow diagrams",
    "business process mapping",
    "as-is",
    "to-be",
    "visio",
    "mega",
    "manuals",
]

AGGREGATOR_DOMAINS = [
    "jooble.org",
    "indeed.com",
    "bayt.com",
    "naukrigulf.com",
    "glassdoor.com",
    "bebee.com",
    "trabajo.org",
    "learn4good.com",
    "wzzff.com",
]

INTERVIEW_PATH_SIGNALS = [
    "careers",
    "apply",
    "job",
    "jobs",
    "recruiter",
    "hiring",
    "talent acquisition",
    "linkedin.com/jobs/view",
    "greenhouse",
    "lever",
    "ashby",
    "workdayjobs",
    "oraclecloud",
    "successfactors",
    "smartrecruiters",
    "careers-page",
    "تقديم",
    "توظيف",
    "وظائف",
]

LOCATION_WEIGHTS = [
    (["riyadh", "الرياض"], 20, "Location fits Riyadh priority"),
    (["eastern province", "eastern", "dammam", "khobar", "dhahran", "الشرقية", "الدمام", "الخبر", "الظهران"], 18, "Location fits Eastern Province priority"),
    (["qassim", "buraydah", "unaizah", "القصيم", "بريدة", "عنيزة"], 16, "Location fits Qassim priority"),
    (["saudi arabia", "ksa", "السعودية"], 8, "Location fits Saudi Arabia preferences"),
    (["remote", "hybrid", "عن بعد", "هجين"], 6, "Remote option may fit"),
]


ARABIC_CHARS = re.compile(r"[؀-ۿ]")


def term_in_text(term: str, text: str) -> bool:
    """English: whole-word match. Arabic: plain substring (words often carry "ال")."""
    if ARABIC_CHARS.search(term):
        return term in text
    pattern = r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def contains_any(text: str, terms: list[str]) -> bool:
    text = text.lower()
    return any(term_in_text(term.lower(), text) for term in terms)


def add_reason(reasons: list[str], reason: str | None) -> None:
    if reason and reason not in reasons:
        reasons.append(reason)


def get_domain(url: str) -> str:
    return urlparse(url).netloc.lower().replace("www.", "")


def is_aggregator_url(url: str) -> bool:
    domain = get_domain(url)
    return any(blocked in domain for blocked in AGGREGATOR_DOMAINS)


def normalize_numbers(text: str) -> str:
    text = text.lower().translate(ARABIC_DIGITS)
    return NUMBER_WORD_PATTERN.sub(lambda match: str(NUMBER_WORDS[match.group(1)]), text)


def is_experience_mention(text: str, start: int, end: int) -> bool:
    window = text[max(0, start - EXPERIENCE_CONTEXT_WINDOW): end + EXPERIENCE_CONTEXT_WINDOW]
    return EXPERIENCE_CONTEXT_PATTERN.search(window) is not None


def required_experience_years(text: str) -> int | None:
    """Minimum years of experience the job asks for, or None if not stated.

    "1-3 years" -> 1, "3+ years" -> 3. If several are stated, the highest wins.
    """
    text = normalize_numbers(text)
    minimums = []

    for match in YEARS_RANGE_PATTERN.finditer(text):
        if is_experience_mention(text, match.start(), match.end()):
            minimums.append(int(match.group(1)))
    text = YEARS_RANGE_PATTERN.sub(" ", text)

    for match in SINGLE_YEARS_PATTERN.finditer(text):
        if is_experience_mention(text, match.start(), match.end()):
            minimums.append(int(match.group(1)))

    realistic = [years for years in minimums if years <= MAX_REALISTIC_YEARS]
    return max(realistic) if realistic else None


def has_high_experience(text: str) -> bool:
    years = required_experience_years(text)
    return years is not None and years >= TOO_MANY_YEARS


def is_hris_heavy_role(title: str, text: str) -> bool:
    title_lower = title.lower()

    is_hr_role = any(
        term in title_lower
        for term in ["hr data", "hr analytics", "people analytics", "workforce analytics", "محلل موارد بشرية"]
    )

    return is_hr_role and contains_any(text, HRIS_HEAVY_SIGNALS)


def is_process_only_business_role(title: str, text: str) -> bool:
    title_lower = title.lower()

    if "business analyst" not in title_lower and "محلل أعمال" not in title_lower:
        return False

    has_process_only = contains_any(text, PROCESS_ONLY_SIGNALS)
    has_data_context = contains_any(text, DATA_CONTEXT_SIGNALS)

    return has_process_only and not has_data_context


def score_location(text: str) -> tuple[int, str | None]:
    for terms, points, reason in LOCATION_WEIGHTS:
        if contains_any(text, terms):
            return points, reason
    return 0, None


def hard_reject_reason(opportunity: Opportunity, full_text: str) -> str | None:
    if contains_any(full_text, STALE_SIGNALS):
        return "Not enough job details to confirm fit"

    if contains_any(opportunity.title, BAD_TITLE_SIGNALS) or has_high_experience(full_text):
        return "May be too senior or outside target path"

    if is_hris_heavy_role(opportunity.title, full_text):
        return "May be too senior or outside target path"

    if is_process_only_business_role(opportunity.title, full_text):
        return "Not enough job details to confirm fit"

    return None


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

    reject_reason = hard_reject_reason(opportunity, full_text)

    if reject_reason:
        return {
            "score": 0,
            "priority": "Low",
            "reasons": [reject_reason],
        }

    score = 0
    reasons = []

    has_direct_title = contains_any(title_text, TARGET_TITLES)
    has_direct_title_in_text = contains_any(full_text, TARGET_TITLES)
    has_adjacent_title = contains_any(title_text, ADJACENT_ANALYTICS_TITLES)
    has_adjacent_title_in_text = contains_any(full_text, ADJACENT_ANALYTICS_TITLES)
    has_data_context = contains_any(full_text, DATA_CONTEXT_SIGNALS)

    if has_direct_title:
        score += 38
        add_reason(reasons, "Relevant data-analysis title")
    elif has_adjacent_title and has_data_context:
        score += 30
        add_reason(reasons, "Relevant data-analysis title")
    elif has_direct_title_in_text:
        score += 24
        add_reason(reasons, "Relevant data-analysis title")
    elif has_adjacent_title_in_text and has_data_context:
        score += 18
        add_reason(reasons, "Relevant data-analysis title")

    if contains_any(full_text, ENTRY_LEVEL_SIGNALS):
        score += 18
        add_reason(reasons, "Matches Abdullah's entry-level path")
    else:
        score -= 8

    if contains_any(full_text, ABDULLAH_CURRENT_SKILLS):
        score += 22
        add_reason(reasons, "Matches Abdullah's current skills")

    if contains_any(full_text, ABDULLAH_GROWING_SKILLS):
        score += 8
        add_reason(reasons, "Matches Abdullah's SQL learning path")

    location_score, location_reason = score_location(full_text)
    if location_score:
        score += location_score
        add_reason(reasons, location_reason)

    if opportunity.url and is_aggregator_url(opportunity.url):
        score -= 5
        add_reason(reasons, "Posted on a job board: apply on the company site if possible")
    elif contains_any(full_text, INTERVIEW_PATH_SIGNALS):
        score += 8
        add_reason(reasons, "Has a clearer path to interview or outreach")

    if contains_any(full_text, MISSING_BUT_ACCEPTABLE_SKILLS):
        score -= 5
        add_reason(reasons, "Has a skill gap Abdullah can prepare for")

    if not has_data_context:
        score -= 25
        add_reason(reasons, "Not enough job details to confirm fit")

    if opportunity.url and not opportunity.url.startswith("http"):
        score -= 15
        add_reason(reasons, "Not enough job details to confirm fit")

    final_score = max(0, min(score, 100))

    if final_score >= 80:
        priority = "Strong"
    elif final_score >= 60:
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
