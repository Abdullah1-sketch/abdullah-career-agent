from opportunity_scoring import Opportunity, score_opportunity
from interview_path import recommend_interview_path
from application_log import build_application_record
from manual_opportunities import get_manual_opportunities
from company_career_scanner import scan_company_career_pages
from manual_visit_strategy import build_manual_visit_radar
from application_tracker import build_application_tracking_note


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

DAILY_ACTIONS = [
    {
        "title": "قو SQL اليوم",
        "reason": "SQL أكثر مهارة ترفع فرصك في وظائف Data Analyst وBI Analyst.",
        "task": "ذاكر 45 دقيقة: SELECT + WHERE + ORDER BY، ثم طبّق 10 استعلامات بسيطة.",
    },
    {
        "title": "جهز رسالة LinkedIn قصيرة",
        "reason": "التقديم الرسمي وحده ما يكفي دائمًا، الرسالة المختصرة تزيد فرصة الانتباه لك.",
        "task": "اكتب رسالة من 3 أسطر: من أنت، أقرب مشروع للشركة، ونوع الفرصة اللي تبحث عنها.",
    },
    {
        "title": "راجع مشروع SAMA POS",
        "reason": "هذا أقوى مشروع لك للبنوك والفنتك والشركات الحكومية.",
        "task": "اكتب 3 نقاط: مصدر البيانات، أهم المؤشرات، وش اكتشفت.",
    },
    {
        "title": "راجع مشروع Excel",
        "reason": "مشروع الفروع والربحية مناسب لشركات التشغيل والمطاعم والتوصيل.",
        "task": "اكتب 3 نقاط: المشكلة، التحليل، النتيجة.",
    },
]


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

    return any(term.lower() in text for term in BLOCKED_REPORT_TERMS)


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
        "Matches Abdullah's current skills": "يناسب مهاراتك الحالية: Excel وPower BI والتحليل والتقارير",
        "Matches Abdullah's SQL learning path": "SQL مطلوب أو مفيد، وهو ضمن مسارك الحالي",
        "Location fits Riyadh priority": "الموقع ممتاز لأنه في الرياض",
        "Location fits Eastern Province priority": "الموقع يناسب أولوية الشرقية",
        "Location fits Qassim priority": "الموقع يناسب أولوية القصيم",
        "Location fits Saudi Arabia preferences": "الموقع مناسب داخل السعودية",
        "Remote option may fit": "الخيار عن بعد وقد يناسبك",
        "Has a skill gap Abdullah can prepare for": "فيه مهارة تحتاج تجهيز",
        "Has a clearer path to interview or outreach": "يوجد طريق واضح للتقديم أو التواصل",
        "May be too senior or outside target path": "قد تكون أعلى من مستواك الحالي",
        "Not enough job details to confirm fit": "التفاصيل غير كافية لتأكيد التوافق",
    }.get(reason, reason)


def translate_action(action: str) -> str:
    return {
        "Apply officially as soon as possible": "قدّم رسميًا اليوم",
        "Prepare a personalized LinkedIn message": "بعد التقديم جهّز رسالة LinkedIn مخصصة",
        "Consider a small company-relevant portfolio angle": "اربط التقديم بمشروع مناسب من ملف أعمالك",
        "Apply officially": "قدّم رسميًا",
        "Keep in daily report and monitor": "راقبها فقط إذا ظهرت إشارة جديدة",
        "Do not spend much time unless new signals appear": "لا تصرف عليها وقتًا إلا إذا ظهرت إشارة جديدة",
    }.get(action, action)


def estimate_experience(opportunity_data: dict) -> str:
    text = " ".join(
        [
            opportunity_data.get("title", ""),
            opportunity_data.get("description", ""),
        ]
    ).lower()

    if any(word in text for word in ["tamheer", "تمهير"]):
        return "تمهير / حديث تخرج"
    if any(word in text for word in ["intern", "internship", "coop", "trainee", "تدريب"]):
        return "تدريب / حديث تخرج"
    if any(word in text for word in ["fresh graduate", "graduate", "حديث تخرج", "خريج"]):
        return "حديث تخرج"
    if any(word in text for word in ["junior", "entry level", "0-1", "0-2", "0-3", "1-2 years", "2 years"]):
        return "0-3 سنوات"
    if any(word in text for word in ["senior", "lead", "manager", "5+", "7+"]):
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

    if any(word in text for word in ["riyadh", "الرياض"]):
        return "الرياض"
    if any(word in text for word in ["qassim", "buraydah", "unaizah", "القصيم", "بريدة", "عنيزة"]):
        return "القصيم"
    if any(word in text for word in ["khobar", "dammam", "dhahran", "eastern", "الخبر", "الدمام", "الظهران", "الشرقية"]):
        return "الشرقية"
    if any(word in text for word in ["saudi", "ksa", "السعودية"]):
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

    if score >= 70:
        return "🟢 قدّم الآن"

    if score >= 50:
        return "🟡 راقب"

    return "⚪ شركة تحت المراقبة"


def build_missing_items(opportunity_data: dict) -> list[str]:
    text = " ".join(
        [
            opportunity_data.get("title", ""),
            opportunity_data.get("description", ""),
        ]
    ).lower()

    missing = []

    if "python" in text:
        missing.append("Python")
    if "sql" in text:
        missing.append("راجع SQL قبل التقديم أو المقابلة")
    if any(word in text for word in ["tableau", "looker"]):
        missing.append("أداة BI إضافية مثل Tableau أو Looker")
    if any(word in text for word in ["statistics", "statistical", "إحصاء"]):
        missing.append("أساسيات الإحصاء")

    if not missing:
        missing.append("لا يظهر نقص واضح من الوصف المتاح")

    return missing


def build_strong_extra_move(opportunity_data: dict, score: int) -> str:
    if score < 80 or opportunity_data.get("is_real_job") is False:
        return ""

    company = opportunity_data.get("company", "الشركة")

    return (
        "\n\nخطوة السبق:\n"
        f"- قدّم رسميًا، ثم أرسل رسالة قصيرة لمسؤول توظيف أو شخص من فريق البيانات في {company}.\n"
        "- اربط الرسالة بأقرب مشروع من ملف أعمالك."
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
    missing_items = build_missing_items(opportunity_data)

    return f"""{category}

{translate_job_title(record["title"])}
الشركة: {record["company"]}
المدينة: {estimate_city(opportunity_data)}
الخبرة: {estimate_experience(opportunity_data)}
التوافق: {score}/100

ليش تستحق؟
{chr(10).join("- " + reason for reason in reasons)}

ينقصك:
{chr(10).join("- " + item for item in missing_items[:1])}

الإجراء:
{chr(10).join("- " + action for action in actions)}

الرابط:
{record["url"]}{build_strong_extra_move(opportunity_data, score)}
"""


def get_current_opportunities() -> list[dict]:
    scanned = scan_company_career_pages(limit=12)
    manual = get_manual_opportunities()
    all_items = scanned + manual

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


def build_daily_action_brief() -> str:
    action = DAILY_ACTIONS[0]

    return f"""وش تسوي اليوم؟

لا توجد فرصة قوية جديدة تستحق التقديم.

أقوى حركة اليوم:
{action["title"]}

ليش؟
{action["reason"]}

المهمة:
{action["task"]}"""


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
        sections.append("فرص تستحق التقديم اليوم:")
        sections.extend(build_opportunity_section(item) for item in apply_now[:3])
        sections.append(
            "\nتحرك يدوي إذا كان يزيد فرصة المقابلة:\n"
            + build_manual_visit_radar(limit=2)
        )
        sections.append(build_application_tracking_note())
    else:
        sections.append(build_daily_action_brief())

    if early_signals:
        sections.append("\nإشارات مختصرة:")
        sections.extend(build_opportunity_section(item) for item in early_signals[:1])

    return "\n\n".join(sections)
