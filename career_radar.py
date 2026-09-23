from opportunity_scoring import Opportunity, score_opportunity
from interview_path import recommend_interview_path
from application_log import build_application_record
from sources import SOURCES
from company_watchlist import build_company_watchlist_summary
from search_queries import build_search_links_summary
from company_career_links import build_career_targets_summary
from manual_opportunities import get_manual_opportunities
from company_career_scanner import scan_company_career_pages


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
        "Location fits Saudi Arabia preferences": "الموقع مناسب لتفضيلاتك داخل السعودية",
        "Has a clearer path to interview or outreach": "يوجد طريق أوضح للتقديم أو التواصل",
        "May be too senior or outside target path": "قد تكون الفرصة أعلى من مستواك الحالي أو خارج المسار",
    }.get(reason, reason)


def translate_action(action: str) -> str:
    return {
        "Apply officially as soon as possible": "قدّم رسميًا بأسرع وقت",
        "Prepare a personalized LinkedIn message": "جهّز رسالة LinkedIn مخصصة",
        "Consider a small company-relevant portfolio angle": "فكّر بزاوية مشروع مصغر مناسب للشركة",
        "Apply officially": "قدّم رسميًا",
        "Keep in daily report and monitor": "احتفظ بها في التقرير اليومي وراقبها",
        "Do not spend much time unless new signals appear": "لا تصرف عليها وقتًا كبيرًا إلا إذا ظهرت إشارات جديدة",
    }.get(action, action)


def translate_path(path: str) -> str:
    return {
        "High-effort interview push": "دفع قوي للوصول إلى مقابلة",
        "Standard application": "تقديم رسمي عادي",
        "Monitor only": "مراقبة فقط",
    }.get(path, path)


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

    translated_reasons = [translate_reason(reason) for reason in record["reasons"]]
    translated_actions = [translate_action(action) for action in record["recommended_actions"]]

    return f"""فرصة / إشارة:
{record["title"]} - {record["company"]}

الموقع: {record["location"]}
المصدر: {record["source"]}
درجة التوافق: {record["score"]}/100
الأولوية: {translate_priority(record["priority"])}

سبب الترشيح:
{chr(10).join("- " + reason for reason in translated_reasons)}

أفضل مسار:
{translate_path(record["interview_path"])}

الخطوات المقترحة:
{chr(10).join("- " + action for action in translated_actions)}

الرابط:
{record["url"]}
"""


def get_current_opportunities() -> list[dict]:
    scanned = scan_company_career_pages(limit=10)
    manual = get_manual_opportunities()

    if scanned:
        return scanned + manual

    return manual


def build_daily_radar_message() -> str:
    opportunities = get_current_opportunities()
    opportunity_sections = [
        build_opportunity_section(opportunity) for opportunity in opportunities[:3]
    ]

    high_priority_sources = [
        source["name"] for source in SOURCES if source["priority"] == "high"
    ]

    return f"""رادار عبدالله المهني

الحالة: يعمل

أفضل الفرص / الإشارات الحالية:
{chr(10).join(opportunity_sections)}

المصادر عالية الأولوية:
{chr(10).join("- " + source for source in high_priority_sources)}

شركات تستحق تركيز خاص:
{build_company_watchlist_summary(8)}

روابط بحث ذكية:
{build_search_links_summary(6)}

أفضل أهداف توظيف مباشرة:
{build_career_targets_summary(4)}

ملاحظة:
إذا ظهرت إشارة من صفحة شركة، راجع الرابط يدويًا ثم نقرر: تقديم رسمي، رسالة مخصصة، أو مشروع مصغر.

الخطوة القادمة:
تحسين السحب من ATS وربط فرص أكثر دقة من الشركات.
"""
