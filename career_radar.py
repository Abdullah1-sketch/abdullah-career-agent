import re

from opportunity_scoring import Opportunity, score_opportunity
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
from job_fit import compute_fit
from job_verification import (
    is_old_and_unconfirmed,
    link_date_age_days,
    posted_age_days,
    reliability,
    verify_job,
)
from manual_opportunities import get_manual_opportunities
from company_career_scanner import scan_company_career_pages
from job_search_engine import get_search_problems, get_search_stats, search_market_opportunities


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
VERIFY_FIRST = "🟡 تحقق أول"
QUICK_APPLY = "🟡 تقديم سريع"
WATCH = "🟡 راقب"
OTHER_FIELD = "🔵 خارج البيانات"
LOW = "⚪ راقب"
EXCLUDED = "⛔ مستبعدة"

EXCLUDED_CLOSED = "مغلقة"
EXCLUDED_HIGH_EXPERIENCE = "تطلب خبرة 3+"
EXCLUDED_OLD = "قديمة وغير مؤكدة"

RELIABILITY_LABELS = {"high": "✅", "medium": "⚠️ متوسطة", "low": "⚠️ ضعيفة"}

# One short next step per category.
ACTIONS = {
    APPLY_NOW: "قدّم اليوم وراسل شخص من فريق البيانات",
    VERIFY_FIRST: "تأكد إن التقديم مفتوح وبعدها قدّم",
    QUICK_APPLY: "قدّم سريع بدون تخصيص",
    WATCH: "راقبها بس",
}
SHORT_ROLE_LABELS = {"finance": "مالية", "specialty": "تخصص آخر"}


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
        return "غير مذكورة"
    if years == 0:
        return "بدون"
    if years == 1:
        return "سنة"
    if years == 2:
        return "سنتين"
    return f"{years}+ سنوات"


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


def describe_gaps(verification: dict | None) -> str:
    if not verification:
        return ""
    requirements = verification["requirements"]
    parts = []
    if requirements["missing"]:
        parts.append("ناقص: " + "، ".join(requirements["missing"]))
    if requirements["learning"]:
        parts.append("تتعلم: " + "، ".join(requirements["learning"]))
    return " | " + " | ".join(parts) if parts else ""


def build_card(opportunity_data: dict) -> str:
    """Five or six short lines per job."""
    assessment = assess(opportunity_data)
    verification = assessment["verification"]
    years = verification["experience_years"] if verification else None
    reliability_label = RELIABILITY_LABELS.get(assessment["reliability"], "⚠️ ما تحققت")
    lines = [
        f"{assessment['category']}: {opportunity_data['title']} | {opportunity_data['company']} | "
        f"{estimate_city(opportunity_data)}",
        f"توافق {assessment['score']} | موثوقية {reliability_label} | نُشرت {describe_posted(assessment['posted_days'])}",
        f"خبرة: {describe_experience(years)}{describe_gaps(verification)}",
        f"👈 {ACTIONS.get(assessment['category'], ACTIONS[WATCH])}",
        best_link(opportunity_data),
    ]
    related = opportunity_data.get("related", [])
    if related:
        lines.append("+ نفس الشركة: " + "، ".join(item["title"] for item in related))
    return "\n".join(lines)


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


def build_no_opportunity_message() -> str:
    return "ما فيه فرصة مناسبة اليوم."


def add_search_warning(message: str) -> str:
    problems = get_search_problems()
    if not problems:
        return message
    return message + "\n⚠️ " + " ".join(problems)


def build_summary(opportunities: list[dict], shown: int) -> str:
    """One line: how many were checked, sent and dropped (with reasons)."""
    stats = get_search_stats()
    dropped = dict(stats["rejected"])

    for item in opportunities:
        if item.get("is_real_job") is False:
            continue
        assessment = assess(item)
        if item.get("grouped"):
            reason = "نفس الشركة"
        elif assessment["excluded"]:
            reason = assessment["excluded"]
        elif assessment["category"] == LOW:
            reason = "ضعيفة"
        else:
            continue
        dropped[reason] = dropped.get(reason, 0) + 1

    line = f"📊 فحصت {stats['found']} | أرسلت {shown} | استبعدت {sum(dropped.values())}"
    if dropped:
        reasons = sorted(dropped.items(), key=lambda pair: -pair[1])
        line += ": " + "، ".join(f"{reason} {count}" for reason, count in reasons)

    checked = [assess(item)["verification"]["checked_at"] for item in opportunities if assess(item)["verification"]]
    if checked:
        line += f"\nآخر تحقق {max(checked)}"
    return line


def build_daily_radar_message() -> str:
    opportunities = sort_opportunities(get_current_opportunities())
    message, shown = build_opportunities_message(opportunities)
    return add_search_warning(message + "\n\n" + build_summary(opportunities, shown))


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


MAX_OTHER_FIELD_JOBS = 3


def build_other_field_lines(opportunities: list[dict]) -> list[str]:
    lines = []
    for item in opportunities[:MAX_OTHER_FIELD_JOBS]:
        role = SHORT_ROLE_LABELS[assess(item)["fit"]["role"]]
        lines.append(f"- {item['title']} | {item['company']} ({role})\n  {best_link(item)}")
    return lines


def build_opportunities_message(opportunities: list[dict]) -> tuple[str, int]:
    """The job part of the message, and how many jobs it shows."""
    opportunities = group_same_company(opportunities)

    def in_category(category: str) -> list[dict]:
        return [item for item in opportunities if assess(item)["category"] == category]

    main_jobs = (
        in_category(APPLY_NOW)[:MAX_APPLY_NOW_JOBS]
        + in_category(VERIFY_FIRST)[:MAX_APPLY_NOW_JOBS]
        + in_category(QUICK_APPLY)[:MAX_QUICK_APPLY_JOBS]
    )
    if not main_jobs:
        main_jobs = in_category(WATCH)[:1]
    other_field = in_category(OTHER_FIELD)[:MAX_OTHER_FIELD_JOBS]

    sections = [build_card(item) for item in main_jobs] or [build_no_opportunity_message()]
    if other_field:
        sections.append(f"{OTHER_FIELD} (للعلم):\n" + "\n".join(build_other_field_lines(other_field)))

    shown = len(main_jobs) + len(other_field)
    return "\n\n".join(sections), shown
