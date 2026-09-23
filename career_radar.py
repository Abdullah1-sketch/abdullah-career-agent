from opportunity_scoring import Opportunity, score_opportunity
from interview_path import recommend_interview_path
from application_log import build_application_record
from manual_opportunities import get_manual_opportunities
from company_career_scanner import scan_company_career_pages


TITLE_TRANSLATIONS = {
    "Data Analyst": "محلل بيانات",
    "Junior Data Analyst": "محلل بيانات مبتدئ",
    "Business Data Analyst": "محلل بيانات أعمال",
    "BI Analyst": "محلل ذكاء أعمال",
    "Business Intelligence Analyst": "محلل ذكاء أعمال",
    "Reporting Analyst": "محلل تقارير",
    "Power BI Analyst": "محلل Power BI",
    "Graduate Data Analyst": "محلل بيانات - برنامج خريجين",
    "Data Analyst Intern": "متدرب تحليل بيانات",
    "Tamheer Data Analyst": "تمهير تحليل بيانات",
    "Company under monitoring": "شركة تحت المراقبة",
}


def translate_job_title(title: str) -> str:
    lower_title = title.lower()

    for english_title, arabic_title in TITLE_TRANSLATIONS.items():
        if english_title.lower() in lower_title:
            if arabic_title in title:
                return title
            return f"{title} ({arabic_title})"

    return title


def translate_priority(priority: str) -> str:
    return {
        "Strong": "قوية",
        "Medium": "متوسطة",
        "Low": "منخفضة",
    }.get(priority, priority)


def translate_reason(reason: str) -> str:
    return {
        "Relevant data-analysis title": "المسمى قريب من تحليل البيانات",
        "Matches Abdullah's current skills or entry-level path": "يناسب مهاراتك الحالية أو مسار المبتدئين",
        "Matches Abdullah's entry-level path": "مناسب لمسار مبتدئ / حديث تخرج / تمهير",
        "Matches Abdullah's current skills": "يناسب مهاراتك الحالية: Excel وPower BI والتحليل والتقارير",
        "Matches Abdullah's SQL learning path": "SQL مطلوب أو مفيد، وهو ضمن مسارك الحالي",
        "Location fits Riyadh priority": "الموقع يناسب أولوية الرياض",
        "Location fits Eastern Province priority": "الموقع يناسب أولوية الشرقية",
        "Location fits Qassim priority": "الموقع يناسب أولوية القصيم",
        "Location fits Saudi Arabia preferences": "الموقع مناسب لتفضيلاتك داخل السعودية",
        "Remote option may fit": "الخيار عن بعد وقد يناسبك",
        "Has a skill gap Abdullah can prepare for": "فيه مهارة تحتاج تجهيز قبل التقديم أو المقابلة",
        "Has a clearer path to interview or outreach": "يوجد طريق أوضح للتقديم أو التواصل",
        "May be too senior or outside target path": "قد تكون الفرصة أعلى من مستواك الحالي أو خارج المسار",
        "Not enough job details to confirm fit": "التفاصيل غير كافية لتأكيد التوافق",
    }.get(reason, reason)


def translate_action(action: str) -> str:
    return {
        "Apply officially as soon as possible": "قدّم رسميًا بأسرع وقت",
        "Prepare a personalized LinkedIn message": "جهّز رسالة LinkedIn مخصصة",
        "Consider a small company-relevant portfolio angle": "فكّر بزاوية مشروع مصغر مناسب للشركة",
        "Apply officially": "قدّم رسميًا",
        "Keep in daily report and monitor": "راقبها فقط إذا ظهرت إشارة جديدة",
        "Do not spend much time unless new signals appear": "لا تصرف عليها وقتًا كبيرًا إلا إذا ظهرت إشارات جديدة",
    }.get(action, action)


def translate_path(path: str) -> str:
    return {
        "High-effort interview push": "دفع قوي للوصول إلى مقابلة",
        "Standard application": "تقديم رسمي عادي",
        "Monitor only": "مراقبة فقط",
    }.get(path, path)


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

    if any(word in text for word in ["junior", "entry level", "0-1", "0-2", "0-3"]):
        return "0-3 سنوات"

    if any(word in text for word in ["senior", "lead", "manager", "5+", "7+"]):
        return "قد تكون أعلى من المستوى المستهدف"

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

    if any(word in text for word in ["khobar", "dammam", "dhahran", "eastern", "الخبر", "الدمام", "الظهران", "الشرقية"]):
        return "الشرقية"

    if any(word in text for word in ["qassim", "buraydah", "unaizah", "القصيم", "بريدة", "عنيزة"]):
        return "القصيم"

    if any(word in text for word in ["saudi", "ksa", "السعودية"]):
        return "السعودية"

    return opportunity_data.get("location", "غير مذكورة")


def get_category(opportunity_data: dict, score: int) -> str:
    if opportunity_data.get("category"):
        return opportunity_data["category"]

    if opportunity_data.get("is_real_job") is False:
        return "⚪ شركة تحت المراقبة"

    if score >= 70:
        return "🟢 قدّم الآن"

    if score >= 45:
        return "🟡 إشارة مبكرة / راقب"

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
        missing.append("Python يحتاج تقوية إذا كان مطلوبًا")

    if "sql" in text:
        missing.append("SQL يحتاج ممارسة أكثر قبل المقابلة")

    if any(word in text for word in ["tableau", "looker"]):
        missing.append("أداة BI إضافية مذكورة؛ Power BI يغطي جزءًا من الفكرة لكن تحتاج تعرف الأساسيات")

    if any(word in text for word in ["statistics", "statistical", "إحصاء"]):
        missing.append("راجع أساسيات الإحصاء والتحليل الوصفي")

    if not missing:
        missing.append("لا يظهر نقص واضح من الوصف المتاح، راجع المتطلبات في الرابط")

    return missing


def build_strong_extra_move(opportunity_data: dict, score: int) -> str:
    if score < 80 or opportunity_data.get("is_real_job") is False:
        return ""

    company = opportunity_data.get("company", "الشركة")

    return (
        "\nحركة إضافية لزيادة فرصة المقابلة:\n"
        f"- قدّم رسميًا، ثم جهّز رسالة قصيرة لمسؤول توظيف أو شخص من فريق البيانات في {company}.\n"
        "- اربط الرسالة بمشروع واحد من أعمالك: SAMA POS إذا كانت الشركة مالية/تقنية، أو مشروع Excel للفروع والربحية إذا كانت تشغيلية/مطاعم/توصيل.\n"
        "- إذا الشركة تستحق مجهود خاص، جهّز Mini Project صغير من بيانات عامة ولا تدّعي أنها بيانات الشركة."
    )


def build_opportunity_section(opportunity_data: dict) -> str:
    opportunity = Opportunity(
        title=opportunity_data["title"],
        company=opportunity_data["company"],
        location=opportunity_data["location"],
        description=opportunity_data["description"],
        url=opportunity_data["url"],
    )

    scoring = score_opportunity(opportunity)
    interview_path = recommend_interview_path(opportunity_data, scoring)
    record = build_application_record(opportunity_data, scoring, interview_path)

    score = record["score"]
    category = get_category(opportunity_data, score)
    translated_reasons = [translate_reason(reason) for reason in record["reasons"]]
    translated_actions = [translate_action(action) for action in record["recommended_actions"]]
    missing_items = build_missing_items(opportunity_data)

    return f"""{category}

المسمى: {translate_job_title(record["title"])}
الشركة: {record["company"]}
المدينة: {estimate_city(opportunity_data)}
الخبرة المطلوبة: {estimate_experience(opportunity_data)}
تاريخ النشر: غير متوفر
درجة التوافق: {score}/100
الأولوية: {translate_priority(record["priority"])}

لماذا تناسبك:
{chr(10).join("- " + reason for reason in translated_reasons)}

ما الذي ينقصك:
{chr(10).join("- " + item for item in missing_items)}

الإجراء المقترح:
{chr(10).join("- " + action for action in translated_actions)}

أفضل مسار:
{translate_path(record["interview_path"])}

رابط التقديم / المتابعة:
{record["url"]}{build_strong_extra_move(opportunity_data, score)}
"""


def get_current_opportunities() -> list[dict]:
    scanned = scan_company_career_pages(limit=12)
    manual = get_manual_opportunities()

    all_items = scanned + manual

    unique_items = {}
    for item in all_items:
        url = item.get("url")
        title = item.get("title", "")
        company = item.get("company", "")
        key = url or f"{title}-{company}"

        if "example.com" in key.lower():
            continue

        if "manual sample" in item.get("source", "").lower():
            continue

        unique_items[key] = item

    return list(unique_items.values())


def sort_opportunities(opportunities: list[dict]) -> list[dict]:
    def sort_key(item: dict) -> tuple[int, int]:
        category = item.get("category", "")

        if category.startswith("🟢"):
            category_rank = 0
        elif category.startswith("🟡"):
            category_rank = 1
        else:
            category_rank = 2

        city = estimate_city(item)
        city_rank = {
            "الرياض": 0,
            "الشرقية": 1,
            "القصيم": 2,
            "السعودية": 3,
        }.get(city, 4)

        return (category_rank, city_rank)

    return sorted(opportunities, key=sort_key)


def build_daily_radar_message() -> str:
    opportunities = sort_opportunities(get_current_opportunities())

    apply_now = [
        opportunity for opportunity in opportunities
        if get_category(opportunity, 0).startswith("🟢")
    ]

    early_signals = [
        opportunity for opportunity in opportunities
        if get_category(opportunity, 0).startswith("🟡")
    ]

    monitored_companies = [
        opportunity for opportunity in opportunities
        if get_category(opportunity, 0).startswith("⚪")
    ]

    sections = []

    if apply_now:
        sections.extend(build_opportunity_section(item) for item in apply_now[:5])
    else:
        sections.append("لا توجد اليوم فرصة جديدة تستحق التقديم")

    if early_signals:
        sections.append("\nإشارات مبكرة تستحق المراقبة:")
        sections.extend(build_opportunity_section(item) for item in early_signals[:3])

    if monitored_companies:
        monitored_lines = [
            f'- {item["company"]}: {item["url"]}'
            for item in monitored_companies[:5]
        ]
        sections.append(
            "\nشركات تحت المراقبة اليوم:\n"
            + "\n".join(monitored_lines)
        )

    return f"""رادار عبدالله المهني

الحالة: يعمل

{chr(10).join(sections)}

ملاحظة:
التقرير يركز على الشواغر الحقيقية المناسبة لمسارك. صفحات Careers العامة لا تُحسب كفرص تقديم إلا إذا ظهر شاغر واضح.

الخطوة القادمة:
تحسين منع التكرار بين الأيام وتتبع الفرص التي قدمت عليها.
"""
