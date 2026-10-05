from opportunity_scoring import Opportunity, score_opportunity
from interview_path import recommend_interview_path
from application_log import build_application_record
from manual_opportunities import get_manual_opportunities
from company_career_scanner import scan_company_career_pages
from manual_visit_strategy import build_manual_visit_radar
from job_search_engine import search_market_opportunities, build_search_engine_status


TITLE_TRANSLATIONS = {
    "HR Analytics Analyst": "محلل تحليلات الموارد البشرية",
    "People Analytics Analyst": "محلل تحليلات الموظفين",
    "Workforce Analytics Analyst": "محلل تحليلات القوى العاملة",
    "Talent Analytics": "تحليلات المواهب",
    "Analytics Analyst": "محلل تحليلات",
    "Junior Data Analyst": "محلل بيانات مبتدئ",
    "Business Data Analyst": "محلل بيانات أعمال",
    "Business Intelligence Analyst": "محلل ذكاء أعمال",
    "BI Analyst": "محلل ذكاء أعمال",
    "Reporting Analyst": "محلل تقارير",
    "Power BI Analyst": "محلل Power BI",
    "Graduate Data Analyst": "محلل بيانات - برنامج خريجين",
    "Data Analyst Intern": "متدرب تحليل بيانات",
    "Data Analyst": "محلل بيانات",
    "Business Analyst": "محلل أعمال",
    "Operations Analyst": "محلل عمليات",
    "Performance Analyst": "محلل أداء",
    "Insights Analyst": "محلل رؤى",
    "Statistician": "إحصائي",
    "Company under monitoring": "شركة تحت المراقبة",
}

BLOCKED_REPORT_TERMS = [
    "international calls",
    "quicknet",
    "mobile data",
    "internet",
    "voice",
    "package",
    "packages",
    "plan",
    "plans",
    "support",
    "contact us",
    "about us",
    "privacy",
    "terms",
    "tel:",
    "mailto:",
    "الباقات",
    "الإنترنت",
    "الخدمات",
    "اتصل بنا",
]

BLOCKED_GENERIC_SOURCES = [
    "jooble.org",
    "indeed.com",
    "bayt.com",
    "naukrigulf.com",
    "glassdoor.com",
]

BLOCKED_GENERIC_TITLE_TERMS = [
    "jobs in",
    "job vacancies",
    "job openings",
    "no experience jobs",
    "analyst jobs",
    "data analyst jobs",
    "وظائف",
    "فرص عمل",
]


def contains_any(text: str, terms: list[str]) -> bool:
    text = text.lower()
    return any(term.lower() in text for term in terms)


def contains_blocked_report_term(item: dict) -> bool:
    text = " ".join(
        [
            item.get("title", ""),
            item.get("company", ""),
            item.get("location", ""),
            item.get("description", ""),
            item.get("url", ""),
        ]
    ).lower()

    return contains_any(text, BLOCKED_REPORT_TERMS)


def is_low_quality_item(item: dict) -> bool:
    title = item.get("title", "").lower()
    company = item.get("company", "").lower()
    url = item.get("url", "").lower()

    if contains_any(url, BLOCKED_GENERIC_SOURCES):
        return True

    if contains_any(company, BLOCKED_GENERIC_SOURCES):
        return True

    if contains_any(title, BLOCKED_GENERIC_TITLE_TERMS):
        return True

    if "linkedin.com/jobs/" in url and "/jobs/view/" not in url:
        return True

    return False


def translate_job_title(title: str) -> str:
    lower_title = title.lower()

    for english_title, arabic_title in TITLE_TRANSLATIONS.items():
        if english_title.lower() in lower_title:
            if arabic_title in title:
                return title
            return f"{title} ({arabic_title})"

    return title


def translate_reason(reason: str) -> str:
    return {
        "Relevant data-analysis title": "المسمى قريب من تحليل البيانات أو التحليلات",
        "Matches Abdullah's current skills or entry-level path": "يناسب مهاراتك الحالية أو مسار المبتدئين",
        "Matches Abdullah's entry-level path": "مناسب لمسار مبتدئ / حديث تخرج / تمهير",
        "Matches Abdullah's current skills": "يناسب مهاراتك الحالية: Excel وPower BI والتقارير",
        "Matches Abdullah's SQL learning path": "SQL مطلوب أو مفيد",
        "Location fits Riyadh priority": "الموقع ممتاز لأنه في الرياض",
        "Location fits Eastern Province priority": "الموقع يناسب الشرقية",
        "Location fits Qassim priority": "الموقع يناسب القصيم",
        "Location fits Saudi Arabia preferences": "الموقع داخل السعودية",
        "Remote option may fit": "الخيار عن بعد وقد يناسبك",
        "Has a skill gap Abdullah can prepare for": "فيه مهارة تحتاج تجهيز",
        "Has a clearer path to interview or outreach": "يوجد رابط أو مسار تقديم واضح",
        "May be too senior or outside target path": "قد تكون أعلى من مستواك الحالي",
        "Not enough job details to confirm fit": "التفاصيل غير كافية لتأكيد التوافق",
    }.get(reason, reason)


def translate_action(action: str) -> str:
    return {
        "Apply officially as soon as possible": "قدّم رسميًا اليوم",
        "Prepare a personalized LinkedIn message": "بعد التقديم أرسل رسالة LinkedIn قصيرة",
        "Consider a small company-relevant portfolio angle": "اربط التقديم بمشروع مناسب من أعمالك",
        "Apply officially": "قدّم رسميًا",
        "Keep in daily report and monitor": "راقبها فقط",
        "Do not spend much time unless new signals appear": "لا تصرف عليها وقتًا الآن",
    }.get(action, action)


def estimate_experience(opportunity_data: dict) -> str:
    text = " ".join(
        [
            opportunity_data.get("title", ""),
            opportunity_data.get("description", ""),
        ]
    ).lower()

    if contains_any(text, ["tamheer", "تمهير"]):
        return "تمهير / حديث تخرج"
    if contains_any(text, ["intern", "internship", "coop", "trainee", "تدريب"]):
        return "تدريب / حديث تخرج"
    if contains_any(text, ["fresh graduate", "graduate", "حديث تخرج", "خريج"]):
        return "حديث تخرج"
    if contains_any(text, ["junior", "entry level", "0-1", "0-2", "0-3", "1-2 years", "2 years"]):
        return "0-3 سنوات"
    if contains_any(text, ["senior", "lead", "manager", "5+", "7+"]):
        return "أعلى من المستوى المستهدف غالبًا"

    return "غير مذكورة"


def estimate_city(opportunity_data: dict) -> str:
    text = " ".join(
        [
            opportunity_data.get("location", ""),
            opportunity_data.get("description", ""),
            opportunity_data.get("title", ""),
        ]
    ).lower()

    if contains_any(text, ["riyadh", "الرياض"]):
        return "الرياض"
    if contains_any(text, ["qassim", "buraydah", "unaizah", "القصيم", "بريدة", "عنيزة"]):
        return "القصيم"
    if contains_any(text, ["khobar", "dammam", "dhahran", "eastern", "الخبر", "الدمام", "الظهران", "الشرقية"]):
        return "الشرقية"
    if contains_any(text, ["saudi", "ksa", "السعودية"]):
        return "السعودية"

    return opportunity_data.get("location", "غير مذكورة")


def build_opportunity(opportunity_data: dict) -> Opportunity:
    return Opportunity(
        title=opportunity_data["title"],
        company=opportunity_data["company"],
        location=opportunity_data["location"],
        description=opportunity_data["description"],
        url=opportunity_data["url"],
    )


def get_score(opportunity_data: dict) -> int:
    return score_opportunity(build_opportunity(opportunity_data))["score"]


def get_category(opportunity_data: dict, score: int) -> str:
    if opportunity_data.get("is_real_job") is False:
        return "⚪ شركة تحت المراقبة"

    if score >= 75:
        return "🟢 قدّم الآن"

    if score >= 55:
        return "🟡 راقب"

    return "⚪ شركة تحت المراقبة"


def build_missing_items(opportunity_data: dict) -> str:
    text = " ".join(
        [
            opportunity_data.get("title", ""),
            opportunity_data.get("description", ""),
        ]
    ).lower()

    missing = []

    if "sql" in text:
        missing.append("راجع SQL قبل التقديم أو المقابلة")
    if "python" in text:
        missing.append("Python قد يكون مطلوبًا")
    if contains_any(text, ["tableau", "looker"]):
        missing.append("قد تحتاج أداة BI إضافية")
    if contains_any(text, ["statistics", "statistical", "إحصاء"]):
        missing.append("راجع أساسيات الإحصاء")

    if not missing:
        return "لا يظهر نقص واضح من الوصف المتاح"

    return "، ".join(missing[:2])


def build_strong_extra_move(opportunity_data: dict, score: int) -> str:
    if score < 85 or opportunity_data.get("is_real_job") is False:
        return ""

    company = opportunity_data.get("company", "الشركة")

    return (
        "\nخطوة السبق:\n"
        f"- بعد التقديم، أرسل رسالة قصيرة لمسؤول توظيف أو شخص من فريق البيانات في {company}.\n"
        "- اربط الرسالة بمشروع مناسب من ملف أعمالك."
    )


def build_opportunity_section(opportunity_data: dict) -> str:
    opportunity = build_opportunity(opportunity_data)
    scoring = score_opportunity(opportunity)
    interview_path = recommend_interview_path(opportunity_data, scoring)
    record = build_application_record(opportunity_data, scoring, interview_path)

    score = record["score"]
    category = get_category(opportunity_data, score)
    reasons = [translate_reason(reason) for reason in record["reasons"][:2]]
    actions = [translate_action(action) for action in record["recommended_actions"][:2]]

    return f"""{category}

{translate_job_title(record["title"])}
الشركة: {record["company"]}
المدينة: {estimate_city(opportunity_data)}
الخبرة: {estimate_experience(opportunity_data)}
التوافق: {score}/100

ليش؟
{chr(10).join("- " + reason for reason in reasons)}

ينقصك:
- {build_missing_items(opportunity_data)}

الإجراء:
{chr(10).join("- " + action for action in actions)}

الرابط:
{record["url"]}
{build_strong_extra_move(opportunity_data, score)}"""


def search_market_safely() -> list[dict]:
    try:
        return search_market_opportunities(limit=8)
    except TypeError:
        return search_market_opportunities()


def get_current_opportunities() -> list[dict]:
    market = search_market_safely()
    scanned = scan_company_career_pages(limit=12)
    manual = get_manual_opportunities()

    all_items = market + scanned + manual
    unique_items = {}

    for item in all_items:
        url = item.get("url", "")
        title = item.get("title", "")
        company = item.get("company", "")
        key = url or f"{title}-{company}"

        if "example.com" in key.lower():
            continue
        if "manual sample" in item.get("source", "").lower():
            continue
        if contains_blocked_report_term(item):
            continue
        if is_low_quality_item(item):
            continue

        unique_items[key] = item

    return list(unique_items.values())


def sort_opportunities(opportunities: list[dict]) -> list[dict]:
    def sort_key(item: dict) -> tuple[int, int, int]:
        score = get_score(item)
        category = get_category(item, score)

        if category.startswith("🟢"):
            category_rank = 0
        elif category.startswith("🟡"):
            category_rank = 1
        else:
            category_rank = 2

        city = estimate_city(item)
        city_rank = {
            "الرياض": 0,
            "القصيم": 1,
            "الشرقية": 2,
            "السعودية": 3,
        }.get(city, 4)

        return (category_rank, city_rank, -score)

    return sorted(opportunities, key=sort_key)


def build_no_opportunity_message() -> str:
    return f"""لا توجد فرصة قوية جديدة تستحق التقديم اليوم.

{build_search_engine_status()}

قرار اليوم:
لا تقدم على فرص ضعيفة. ننتظر فرصة مباشرة أو نبحث يدويًا عن شركة محددة."""


def build_daily_radar_message() -> str:
    opportunities = sort_opportunities(get_current_opportunities())

    apply_now = [
        opportunity for opportunity in opportunities
        if get_category(opportunity, get_score(opportunity)).startswith("🟢")
    ]

    early_signals = [
        opportunity for opportunity in opportunities
        if get_category(opportunity, get_score(opportunity)).startswith("🟡")
    ]

    sections = []

    if apply_now:
        sections.append("فرص اليوم:")
        sections.extend(build_opportunity_section(item) for item in apply_now[:2])

        strongest_score = get_score(apply_now[0])
        if strongest_score >= 85:
            sections.append(
                "تحرك يدوي محتمل إذا كنت بالرياض أو القصيم:\n"
                + build_manual_visit_radar(limit=1)
            )
    else:
        sections.append(build_no_opportunity_message())

    if early_signals and not apply_now:
        sections.append("إشارة واحدة للمراقبة فقط:")
        sections.append(build_opportunity_section(early_signals[0]))

    return "\n\n".join(sections)
