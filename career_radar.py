import re

from opportunity_scoring import Opportunity, score_opportunity
from interview_path import recommend_interview_path
from config import (
    MAX_APPLY_NOW_JOBS,
    MAX_MISSING_SKILLS_PENALTY,
    MAX_QUICK_APPLY_JOBS,
    FIT_WEIGHTS,
    MEDIUM_SCORE,
    MISSING_PLATFORM_PENALTY,
    MISSING_SKILL_PENALTY,
    STRONG_SCORE,
    TOO_MANY_YEARS,
    WATCH_SCORE,
)
from job_fit import ROLE_LABELS, compute_fit
from job_verification import (
    is_old_and_unconfirmed,
    link_date_age_days,
    posted_age_days,
    reliability,
    verify_job,
)
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
OTHER_FIELD = "🔵 خارج تحليل البيانات"
LOW = "⚪ راقب"
EXCLUDED = "⛔ مستبعدة"

EXCLUDED_CLOSED = "مغلقة"
EXCLUDED_HIGH_EXPERIENCE = "تطلب خبرة 3+"
EXCLUDED_OLD = "قديمة وغير مؤكدة"

RELIABILITY_LABELS = {"high": "✅ عالية", "medium": "⚠️ متوسطة", "low": "⚠️ منخفضة"}
PART_LABELS = {"role": "الدور", "experience": "الخبرة", "skills": "المهارات", "location": "الموقع"}


def choose_category(
    opportunity_data: dict, fit_score: int, reliability_level: str | None, excluded: str | None, role: str | None
) -> str:
    if opportunity_data.get("is_real_job") is False:
        return LOW
    if excluded:
        return EXCLUDED
    if role in ("finance", "specialty"):
        return OTHER_FIELD if fit_score >= WATCH_SCORE else LOW
    if fit_score >= STRONG_SCORE:
        return APPLY_NOW if reliability_level == "high" else VERIFY_FIRST
    if fit_score >= MEDIUM_SCORE:
        return QUICK_APPLY
    if fit_score >= WATCH_SCORE:
        return WATCH
    return LOW


def exclusion_reason(opportunity_data: dict, verification: dict, posted_days: int | None) -> str | None:
    years = verification["experience_years"]
    links = f'{opportunity_data.get("url", "")} {verification["source_url"]}'
    if verification["status"] == "closed":
        return EXCLUDED_CLOSED
    if years is not None and years >= TOO_MANY_YEARS:
        return EXCLUDED_HIGH_EXPERIENCE
    if is_old_and_unconfirmed(verification, posted_days, link_date_age_days(links)):
        return EXCLUDED_OLD
    return None


def assess(opportunity_data: dict) -> dict:
    """Fit (does the job match Abdullah?) and reliability (is the posting real and open?).

    Jobs that pass a quick keyword check get their original posting opened;
    their fit is then computed from what the posting actually asks for.
    Cached on the item so each posting is opened once per run.
    """
    if "assessment" in opportunity_data:
        return opportunity_data["assessment"]

    keyword_score = score_opportunity(build_opportunity(opportunity_data))["score"]
    verification = fit = excluded = None
    reliability_level = reliability_reason = None
    score = keyword_score
    posted_days = posted_age_days(opportunity_data.get("posted_at") or opportunity_data.get("description", ""))

    if opportunity_data.get("is_real_job") is not False and keyword_score >= WATCH_SCORE:
        verification = verify_job(opportunity_data)
        excluded = exclusion_reason(opportunity_data, verification, posted_days)
        fit = compute_fit(opportunity_data, verification["experience_years"], verification["requirements"])
        score = fit["score"]
        reliability_level, reliability_reason = reliability(verification, posted_days)

    assessment = {
        "score": score,
        "fit": fit,
        "verification": verification,
        "reliability": reliability_level,
        "reliability_reason": reliability_reason,
        "posted_days": posted_days,
        "excluded": excluded,
        "category": choose_category(
            opportunity_data, score, reliability_level, excluded, fit["role"] if fit else None
        ),
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


def describe_posted(days: int | None) -> str:
    if days is None:
        return "غير معروف"
    if days == 0:
        return "اليوم"
    if days == 1:
        return "أمس"
    if days == 2:
        return "قبل يومين"
    if days <= 10:
        return f"قبل {days} أيام"
    return f"قبل {days} يوم"


def describe_fit(fit: dict) -> str:
    parts = "، ".join(
        f"{PART_LABELS[name]} {points}/{FIT_WEIGHTS[name]}" for name, points in fit["parts"].items()
    )
    return f"{fit['score']}/100 ({parts})"


def describe_reliability(assessment: dict) -> str:
    if not assessment["reliability"]:
        return "⚠️ ما تم التحقق"
    return f"{RELIABILITY_LABELS[assessment['reliability']]}: {assessment['reliability_reason']}"


def describe_requirements(verification: dict | None) -> str:
    if verification is None:
        return "غير معروفة"
    requirements = verification["requirements"]
    parts = []
    if requirements["have"]:
        parts.append("عندك: " + "، ".join(requirements["have"]))
    if requirements["learning"]:
        parts.append("تتعلمها (مو متقنها): " + "، ".join(requirements["learning"]))
    if requirements["missing"]:
        parts.append("ناقصك: " + "، ".join(requirements["missing"]))
    return " | ".join(parts) if parts else "ما ذكر أدوات محددة"


def role_warning(assessment: dict) -> str:
    fit = assessment["fit"]
    if not fit or fit["role"] in ("data", "adjacent"):
        return ""
    return f"\nتنبيه: {ROLE_LABELS[fit['role']]}"


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


def build_related_jobs(opportunity_data: dict) -> str:
    related = opportunity_data.get("related", [])
    if not related:
        return ""
    lines = [f"- {item['title']}: {best_link(item)}" for item in related]
    return "\n\nوظائف ثانية في نفس الشركة:\n" + "\n".join(lines)


def build_opportunity_section(opportunity_data: dict) -> str:
    assessment = assess(opportunity_data)
    verification = assessment["verification"]
    category = assessment["category"]

    if category == APPLY_NOW:
        scoring = {"score": assessment["score"], "priority": "Strong"}
        interview_path = recommend_interview_path(opportunity_data, scoring)
        actions = [translate_action(action) for action in interview_path["actions"][:2]]
        extras = build_extra_push(opportunity_data) + build_interview_strategy(opportunity_data, assessment["score"])
    else:
        actions = ["افتح الرابط وتأكد إن التقديم مفتوح والخبرة المطلوبة قبل ما تقدّم"]
        extras = ""

    years = verification["experience_years"] if verification else None
    checked = verification["checked_at"] if verification else "لا"
    fit_line = describe_fit(assessment["fit"]) if assessment["fit"] else f"{assessment['score']}/100"

    return f"""{category}

{translate_job_title(opportunity_data["title"])}
الشركة: {opportunity_data["company"]}
المدينة: {estimate_city(opportunity_data)}
التوافق: {fit_line}
الموثوقية: {describe_reliability(assessment)}
نُشرت: {describe_posted(assessment["posted_days"])} | آخر تحقق: {checked}
الخبرة المطلوبة: {describe_experience(years)}
المهارات: {describe_requirements(verification)}{role_warning(assessment)}

الإجراء:
{chr(10).join("- " + action for action in actions)}

الرابط:
{best_link(opportunity_data)}{build_related_jobs(opportunity_data)}{extras}"""


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
    years = verification["experience_years"] if verification else None
    reliability_label = RELIABILITY_LABELS.get(assessment["reliability"], "⚠️ ما تم التحقق")
    line = (
        f"- {translate_job_title(opportunity_data['title'])} | {opportunity_data['company']} | "
        f"{estimate_city(opportunity_data)}\n"
        f"  التوافق {assessment['score']}/100 | الموثوقية {reliability_label} | "
        f"نُشرت {describe_posted(assessment['posted_days'])}\n"
        f"  الخبرة: {describe_experience(years)}"
    )
    if verification and (verification["requirements"]["missing"] or verification["requirements"]["learning"]):
        gaps = verification["requirements"]["missing"] + verification["requirements"]["learning"]
        line += " | تحتاج تجهز: " + "، ".join(gaps)
    line += role_warning(assessment).replace("\n", "\n  ")
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
    counts = {APPLY_NOW: 0, VERIFY_FIRST: 0, QUICK_APPLY: 0, OTHER_FIELD: 0, "other": 0, "grouped": 0}
    excluded = {}
    for item in opportunities:
        if item.get("is_real_job") is False:
            continue
        assessment = assess(item)
        if item.get("grouped"):
            counts["grouped"] += 1
        elif assessment["excluded"]:
            excluded[assessment["excluded"]] = excluded.get(assessment["excluded"], 0) + 1
        elif assessment["category"] in counts:
            counts[assessment["category"]] += 1
        else:
            counts["other"] += 1

    line = (
        f"- التقييم: قدّم الآن {counts[APPLY_NOW]}، قوية تحتاج تحقق {counts[VERIFY_FIRST]}، "
        f"تقديم سريع {counts[QUICK_APPLY]}، خارج البيانات {counts[OTHER_FIELD]}، ضعيفة {counts['other']}، "
        f"نفس الشركة {counts['grouped']}"
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


COMPANY_FILLER_WORDS = {
    "company", "group", "holding", "inc", "ltd", "llc", "co", "the", "and", "pmc",
    "program", "management", "saudi", "arabia", "ksa", "international",
}


def company_key(company: str) -> str:
    words = [word for word in re.findall(r"[a-z0-9]+", company.lower()) if word not in COMPANY_FILLER_WORDS]
    return words[0] if words else company.strip().lower()


def group_same_company(opportunities: list[dict]) -> list[dict]:
    """Keep the best job per company; others are listed under it ("related")."""
    primary_by_company = {}
    grouped = []
    for item in opportunities:
        key = company_key(item.get("company", ""))
        primary = primary_by_company.get(key)
        if primary is None or assess(item)["category"] in (EXCLUDED, LOW):
            primary_by_company.setdefault(key, item)
            grouped.append(item)
            continue
        primary.setdefault("related", []).append(item)
        item["grouped"] = True
    return grouped


def build_opportunities_message(opportunities: list[dict]) -> str:
    opportunities = group_same_company(opportunities)

    def in_category(category: str) -> list[dict]:
        return [item for item in opportunities if assess(item)["category"] == category]

    apply_now = in_category(APPLY_NOW)
    verify_first = in_category(VERIFY_FIRST)
    quick_apply = in_category(QUICK_APPLY)
    other_field = in_category(OTHER_FIELD)
    watch = in_category(WATCH)

    if not (apply_now or verify_first or quick_apply):
        if other_field:
            return build_no_opportunity_message() + "\n\n" + build_other_field_list(other_field)
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
    if other_field:
        sections.append(build_other_field_list(other_field))
    return "\n\n".join(sections)


MAX_OTHER_FIELD_JOBS = 3


def build_other_field_list(opportunities: list[dict]) -> str:
    lines = [f"{OTHER_FIELD} (تحتاج مهارات غير البيانات، للعلم):"]
    for item in opportunities[:MAX_OTHER_FIELD_JOBS]:
        role = ROLE_LABELS[assess(item)["fit"]["role"]]
        lines.append(f"- {item['title']} | {item['company']} | {estimate_city(item)} | {role}\n  {best_link(item)}")
    return "\n".join(lines)
