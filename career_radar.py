from opportunity_scoring import Opportunity, score_opportunity
from interview_path import recommend_interview_path
from application_log import build_application_record
from sources import SOURCES
from company_watchlist import build_company_watchlist_summary
from search_queries import build_search_links_summary


def build_daily_radar_message() -> str:
    sample_opportunity = {
        "title": "محلل بيانات مبتدئ",
        "company": "شركة سعودية تجريبية",
        "location": "الرياض، السعودية",
        "description": "فرصة مبتدئة تتطلب Excel و Power BI و SQL ولوحات معلومات وتقارير.",
        "url": "https://example.com/careers/apply",
        "source": "اختبار النظام",
    }

    opportunity = Opportunity(
        title=sample_opportunity["title"],
        company=sample_opportunity["company"],
        location=sample_opportunity["location"],
        description=sample_opportunity["description"],
        url=sample_opportunity["url"],
    )

    scoring = score_opportunity(opportunity)
    interview_path = recommend_interview_path(sample_opportunity, scoring)
    record = build_application_record(sample_opportunity, scoring, interview_path)

    high_priority_sources = [
        source["name"] for source in SOURCES if source["priority"] == "high"
    ]

    priority_ar = {
        "Strong": "قوية",
        "Medium": "متوسطة",
        "Low": "منخفضة",
    }

    reasons_ar = {
        "Relevant data-analysis title": "المسمى قريب من تحليل البيانات",
        "Matches Abdullah's current skills or entry-level path": "يناسب مهاراتك الحالية أو مسار المبتدئين",
        "Location fits Saudi Arabia preferences": "الموقع مناسب لتفضيلاتك داخل السعودية",
        "Has a clearer path to interview or outreach": "يوجد طريق أوضح للتقديم أو التواصل",
        "May be too senior or outside target path": "قد تكون الفرصة أعلى من مستواك الحالي أو خارج المسار",
    }

    actions_ar = {
        "Apply officially as soon as possible": "قدّم رسميًا بأسرع وقت",
        "Prepare a personalized LinkedIn message": "جهّز رسالة LinkedIn مخصصة",
        "Consider a small company-relevant portfolio angle": "فكّر بزاوية مشروع مصغر مناسب للشركة",
        "Apply officially": "قدّم رسميًا",
        "Keep in daily report and monitor": "احتفظ بها في التقرير اليومي وراقبها",
        "Do not spend much time unless new signals appear": "لا تصرف عليها وقتًا كبيرًا إلا إذا ظهرت إشارات جديدة",
    }

    path_ar = {
        "High-effort interview push": "دفع قوي للوصول إلى مقابلة",
        "Standard application": "تقديم رسمي عادي",
        "Monitor only": "مراقبة فقط",
    }

    translated_reasons = [
        reasons_ar.get(reason, reason) for reason in record["reasons"]
    ]
    translated_actions = [
        actions_ar.get(action, action) for action in record["recommended_actions"]
    ]

    translated_priority = priority_ar.get(record["priority"], record["priority"])
    translated_path = path_ar.get(record["interview_path"], record["interview_path"])

    return f"""رادار عبدالله المهني

الحالة: يعمل

فرصة تجريبية:
{record["title"]} - {record["company"]}

الموقع: {record["location"]}
درجة التوافق: {record["score"]}/100
الأولوية: {translated_priority}

سبب الترشيح:
{chr(10).join("- " + reason for reason in translated_reasons)}

أفضل مسار:
{translated_path}

الخطوات المقترحة:
{chr(10).join("- " + action for action in translated_actions)}

المصادر عالية الأولوية:
{chr(10).join("- " + source for source in high_priority_sources)}

شركات تستحق تركيز خاص:
{build_company_watchlist_summary(10)}

روابط بحث ذكية:
{build_search_links_summary(8)}

الخطوة القادمة:
ربط مصادر الفرص الحقيقية وإزالة الفرصة التجريبية.
"""
