from opportunity_scoring import Opportunity, score_opportunity
from interview_path import recommend_interview_path
from config import (
    MAX_APPLY_NOW_JOBS,
    MAX_MISSING_SKILLS_PENALTY,
    MAX_QUICK_APPLY_JOBS,
    MEDIUM_SCORE,
    MISSING_PLATFORM_PENALTY,
    MISSING_SKILL_PENALTY,
    STRONG_SCORE,
    TOO_MANY_YEARS,
    WATCH_SCORE,
)
from job_verification import verify_job
from application_log import build_application_record
from manual_opportunities import get_manual_opportunities
from company_career_scanner import scan_company_career_pages
from job_search_engine import get_search_problems, get_search_stats, search_market_opportunities
from interview_strategy import build_interview_strategy


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
    # Title and link only: real job descriptions use words like "support" and "plan".
    text = f'{item.get("title", "")} {item.get("url", "")}'.lower()

    return contains_any(text, BLOCKED_REPORT_TERMS)


def is_low_quality_item(item: dict) -> bool:
    title = item.get("title", "").lower()
    url = item.get("url", "").lower()

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
        "Relevant data-analysis title": "مسمى مناسب لمسارك",
        "Matches Abdullah's current skills or entry-level path": "يناسب مهاراتك أو مسار مبتدئ",
        "Matches Abdullah's entry-level path": "مناسب لمبتدئ / حديث تخرج / تمهير",
        "Matches Abdullah's current skills": "يناسب Excel وPower BI والتقارير",
        "Matches Abdullah's SQL learning path": "SQL مطلوب أو مفيد",
        "Location fits Riyadh priority": "الموقع ممتاز: الرياض",
        "Location fits Eastern Province priority": "الموقع مناسب: الشرقية",
        "Location fits Qassim priority": "الموقع مناسب: القصيم",
        "Location fits Saudi Arabia preferences": "داخل السعودية",
        "Remote option may fit": "عن بعد وقد يناسبك",
        "Has a skill gap Abdullah can prepare for": "فيه مهارة تحتاج تجهيز",
        "Has a clearer path to interview or outreach": "مسار التقديم واضح",
        "May be too senior or outside target path": "قد تكون أعلى من مستواك",
        "Not enough job details to confirm fit": "التفاصيل غير كافية",
        "Posting looks old or closed": "الإعلان قديم أو مغلق",
        "Posted on a job board: apply on the company site if possible": "منشورة في موقع وظائف: دوّرها في موقع الشركة وقدّم من هناك",
    }.get(reason, reason)


def translate_action(action: str) -> str:
    return {
        "Apply officially as soon as possible": "قدّم اليوم",
        "Prepare a personalized LinkedIn message": "بعد التقديم أرسل رسالة قصيرة",
        "Consider a small company-relevant portfolio angle": "اربط التقديم بمشروع من أعمالك",
        "Apply officially": "قدّم رسميًا",
        "Keep in daily report and monitor": "راقب فقط",
        "Do not spend much time unless new signals appear": "لا تصرف وقتًا الآن",
        "Fast apply only, do not customize heavily": "قدّم سريعًا بدون تخصيص كبير",
        "Prepare a short LinkedIn message": "أرسل رسالة LinkedIn قصيرة",
        "Fast apply if it takes less than 5 minutes": "قدّم سريعًا إذا ما يأخذ أكثر من 5 دقائق",
        "Do not customize heavily": "لا تخصص لها وقت كثير",
        "Find the original posting on the company site and apply there": "دوّر الإعلان في موقع الشركة وقدّم منه",
        "Apply on the job board if the company site has no posting": "إذا ما لقيته، قدّم من موقع الوظائف",
    }.get(action, action)


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
    if contains_any(text, ["khobar", "dammam", "dhahran", "eastern", "الخبر", "الدمام", "الظهران", "الشرقية"]):
        return "الشرقية"
    if contains_any(text, ["qassim", "buraydah", "unaizah", "القصيم", "بريدة", "عنيزة"]):
        return "القصيم"
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


APPLY_NOW = "🟢 قدّم الآن"
VERIFY_FIRST = "🟡 قوية، تحقق قبل التقديم"
QUICK_APPLY = "🟡 قدّم سريع"
WATCH = "🟡 راقب"
LOW = "⚪ راقب"
EXCLUDED = "⛔ مستبعدة"

EXCLUDED_CLOSED = "مغلقة"
EXCLUDED_HIGH_EXPERIENCE = "تطلب خبرة 3+"


def skill_gap_penalty(requirements: dict) -> int:
    platforms = len(requirements["missing_platforms"])
    others = len(requirements["missing"]) - platforms
    return platforms * MISSING_PLATFORM_PENALTY + min(others * MISSING_SKILL_PENALTY, MAX_MISSING_SKILLS_PENALTY)


def choose_category(opportunity_data: dict, score: int, verification: dict | None, excluded: str | None) -> str:
    if opportunity_data.get("is_real_job") is False:
        return LOW
    if excluded:
        return EXCLUDED
    if score >= STRONG_SCORE:
        return APPLY_NOW if verification and verification["verified"] else VERIFY_FIRST
    if score >= MEDIUM_SCORE:
        return QUICK_APPLY
    if score >= WATCH_SCORE:
        return WATCH
    return LOW


def assess(opportunity_data: dict) -> dict:
    """Keyword score, then a check of the original posting for promising jobs.

    Cached on the item so each posting is opened once per run.
    """
    if "assessment" in opportunity_data:
        return opportunity_data["assessment"]

    scoring = score_opportunity(build_opportunity(opportunity_data))
    score = scoring["score"]
    verification = None
    excluded = None

    if opportunity_data.get("is_real_job") is not False and score >= MEDIUM_SCORE:
        verification = verify_job(opportunity_data)
        years = verification["experience_years"]
        if verification["status"] == "closed":
            excluded = EXCLUDED_CLOSED
        elif years is not None and years >= TOO_MANY_YEARS:
            excluded = EXCLUDED_HIGH_EXPERIENCE
        else:
            score = max(0, score - skill_gap_penalty(verification["requirements"]))

    assessment = {
        "scoring": scoring,
        "score": score,
        "verification": verification,
        "excluded": excluded,
        "category": choose_category(opportunity_data, score, verification, excluded),
    }
    opportunity_data["assessment"] = assessment
    return assessment


def get_score(opportunity_data: dict) -> int:
    return assess(opportunity_data)["score"]


def get_category(opportunity_data: dict, score: int | None = None) -> str:
    return assess(opportunity_data)["category"]


def best_link(opportunity_data: dict) -> str:
    verification = assess(opportunity_data)["verification"]
    if verification and verification["source_url"]:
        return verification["source_url"]
    return opportunity_data["url"]


def describe_experience(years: int | None) -> str:
    if years is None:
        return "غير مذكورة في الإعلان"
    if years == 0:
        return "بدون خبرة"
    if years == 1:
        return "سنة على الأقل"
    if years == 2:
        return "سنتين على الأقل"
    return f"{years} سنوات على الأقل"


def describe_verification(verification: dict | None) -> str:
    if verification is None:
        return "⚠️ ما تم التحقق"
    if verification["verified"]:
        return "✅ من إعلان الشركة الأصلي، والتقديم مفتوح"
    source = verification["source"]
    if source == "linkedin":
        return "⚠️ إعلان LinkedIn ما أقدر أفتحه: تأكد بنفسك إنه مفتوح ومن الخبرة المطلوبة"
    if source == "job_board":
        return "⚠️ منشور في موقع تجميع وما لقيت إعلان الشركة الأصلي"
    if source == "company":
        return "⚠️ صفحة الشركة ما انفتحت أو ما فيها تفاصيل كافية"
    return "⚠️ مصدر غير معروف"


def describe_requirements(verification: dict | None) -> str:
    if verification is None:
        return "غير معروفة"
    requirements = verification["requirements"]
    parts = []
    if requirements["have"]:
        parts.append("عندك: " + "، ".join(requirements["have"]))
    if requirements["learning"]:
        parts.append("تتعلمها: " + "، ".join(requirements["learning"]))
    if requirements["missing"]:
        parts.append("ناقصك: " + "، ".join(requirements["missing"]))
    return " | ".join(parts) if parts else "ما ذكر أدوات محددة"


def build_extra_push(opportunity_data: dict) -> str:
    city = estimate_city(opportunity_data)

    if city not in ["الرياض", "الشرقية", "القصيم"]:
        return ""

    return (
        "\n\nزيادة فرصتك:\n"
        "- قدّم من الرابط.\n"
        "- أرسل رسالة LinkedIn قصيرة لمسؤول توظيف أو شخص من فريق البيانات.\n"
        f"- إذا تقدر: تحرك يدوي في {city}."
    )


def build_opportunity_section(opportunity_data: dict) -> str:
    assessment = assess(opportunity_data)
    scoring = dict(assessment["scoring"], score=assessment["score"])
    verification = assessment["verification"]
    category = assessment["category"]
    score = assessment["score"]

    reasons = [translate_reason(reason) for reason in scoring["reasons"][:2]]

    if category == APPLY_NOW:
        interview_path = recommend_interview_path(opportunity_data, scoring)
        actions = [translate_action(action) for action in interview_path["actions"][:2]]
        extras = build_extra_push(opportunity_data) + build_interview_strategy(opportunity_data, score)
    else:
        actions = ["افتح الرابط وتأكد إن التقديم مفتوح والخبرة المطلوبة قبل ما تقدّم"]
        extras = ""

    years = verification["experience_years"] if verification else None

    return f"""{category}

{translate_job_title(opportunity_data["title"])}
الشركة: {opportunity_data["company"]}
المدينة: {estimate_city(opportunity_data)}
الخبرة المطلوبة: {describe_experience(years)}
التوافق: {score}/100
التحقق: {describe_verification(verification)}
المتطلبات: {describe_requirements(verification)}

ليش؟
{chr(10).join("- " + reason for reason in reasons)}

الإجراء:
{chr(10).join("- " + action for action in actions)}

الرابط:
{best_link(opportunity_data)}{extras}"""


def search_market_safely() -> list[dict]:
    try:
        return search_market_opportunities(limit=15)
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
    category_ranks = {APPLY_NOW: 0, VERIFY_FIRST: 1, QUICK_APPLY: 2, WATCH: 3}

    def sort_key(item: dict) -> tuple[int, int, int]:
        assessment = assess(item)
        category_rank = category_ranks.get(assessment["category"], 4)
        city_rank = {"الرياض": 0, "الشرقية": 1, "القصيم": 2, "السعودية": 3}.get(estimate_city(item), 4)
        return (category_rank, city_rank, -assessment["score"])

    return sorted(opportunities, key=sort_key)


def build_quick_apply_line(opportunity_data: dict) -> str:
    assessment = assess(opportunity_data)
    verification = assessment["verification"]
    badge = "✅" if verification and verification["verified"] else "⚠️ تحقق منها"
    years = verification["experience_years"] if verification else None
    line = (
        f"- {translate_job_title(opportunity_data['title'])} | {opportunity_data['company']} | "
        f"{estimate_city(opportunity_data)} | {assessment['score']}/100 | {badge}\n"
        f"  الخبرة: {describe_experience(years)}"
    )
    if verification and verification["requirements"]["missing"]:
        line += " | ناقصك: " + "، ".join(verification["requirements"]["missing"])
    return line + f"\n  {best_link(opportunity_data)}"


def build_quick_apply_list(opportunities: list[dict]) -> str:
    lines = ["🟡 تستحق تقديم سريع (بدون تخصيص كبير):"]
    lines.extend(build_quick_apply_line(item) for item in opportunities)
    return "\n".join(lines)


def build_no_opportunity_message() -> str:
    return """لا توجد فرصة قوية اليوم.

تم فحص المصادر بدون إعلان مباشر مناسب.
لا تضيع وقتك على تقديم ضعيف."""


def add_search_warning(message: str) -> str:
    problems = get_search_problems()
    if not problems:
        return message
    return message + "\n\n⚠️ تنبيه: " + " ".join(problems)


def build_google_summary() -> str:
    stats = get_search_stats()
    line = f"- Google: {stats['found']} نتيجة، المناسب منها {stats['kept']}"
    if stats["rejected"]:
        reasons = sorted(stats["rejected"].items(), key=lambda pair: -pair[1])
        line += "\n  المستبعد: " + "، ".join(f"{reason} {count}" for reason, count in reasons)
    return line


def build_company_pages_summary(opportunities: list[dict]) -> str:
    from_pages = [item for item in opportunities if item.get("source") == "Company career page scanner"]
    jobs = [item for item in from_pages if item.get("is_real_job") is not False]
    watched = len(from_pages) - len(jobs)
    return f"- مواقع الشركات: {len(jobs)} رابط وظيفة، {watched} شركة بدون إعلان بيانات اليوم"


def build_score_summary(opportunities: list[dict]) -> str:
    counts = {APPLY_NOW: 0, VERIFY_FIRST: 0, QUICK_APPLY: 0, "other": 0}
    excluded = {}
    for item in opportunities:
        if item.get("is_real_job") is False:
            continue
        assessment = assess(item)
        if assessment["excluded"]:
            excluded[assessment["excluded"]] = excluded.get(assessment["excluded"], 0) + 1
        elif assessment["category"] in counts:
            counts[assessment["category"]] += 1
        else:
            counts["other"] += 1

    line = (
        f"- التقييم: قدّم الآن {counts[APPLY_NOW]}، تحقق قبل التقديم {counts[VERIFY_FIRST]}، "
        f"تقديم سريع {counts[QUICK_APPLY]}، ضعيفة {counts['other']}"
    )
    if excluded:
        line += "\n  استبعدتها بعد فتح الإعلان: " + "، ".join(f"{reason} {count}" for reason, count in excluded.items())
    return line


def build_check_summary(opportunities: list[dict]) -> str:
    return "\n".join([
        "📊 فحص اليوم:",
        build_google_summary(),
        build_company_pages_summary(opportunities),
        build_score_summary(opportunities),
    ])


def build_daily_radar_message() -> str:
    opportunities = sort_opportunities(get_current_opportunities())
    message = build_opportunities_message(opportunities)
    return add_search_warning(message + "\n\n" + build_check_summary(opportunities))


def build_opportunities_message(opportunities: list[dict]) -> str:
    def in_category(category: str) -> list[dict]:
        return [item for item in opportunities if assess(item)["category"] == category]

    apply_now = in_category(APPLY_NOW)
    verify_first = in_category(VERIFY_FIRST)
    quick_apply = in_category(QUICK_APPLY)
    watch = in_category(WATCH)

    if not (apply_now or verify_first or quick_apply):
        if watch:
            return "لا توجد فرصة قوية اليوم.\n\nإشارة للمراقبة فقط:\n\n" + build_opportunity_section(watch[0])
        return build_no_opportunity_message()

    sections = []
    if apply_now:
        sections.append("فرص اليوم (متحقق منها):")
        sections.extend(build_opportunity_section(item) for item in apply_now[:MAX_APPLY_NOW_JOBS])
    else:
        sections.append("لا توجد فرصة متحقق منها 100% اليوم.")
    if verify_first:
        sections.extend(build_opportunity_section(item) for item in verify_first[:MAX_APPLY_NOW_JOBS])
    if quick_apply:
        sections.append(build_quick_apply_list(quick_apply[:MAX_QUICK_APPLY_JOBS]))
    return "\n\n".join(sections)
