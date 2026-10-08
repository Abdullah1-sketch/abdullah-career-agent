PROJECTS = {
    "fintech": {
        "project": "SAMA POS Power BI",
        "why": "قريب من المدفوعات، مؤشرات النمو، وسلوك العملاء.",
    },
    "operations": {
        "project": "Excel Branch Performance & Profitability",
        "why": "قريب من تحليل الفروع، الأداء، المبيعات، والربحية.",
    },
    "government": {
        "project": "SAMA POS Power BI",
        "why": "مشروع مبني على بيانات سعودية مفتوحة ويناسب بيئات التحول الرقمي.",
    },
    "telecom": {
        "project": "SAMA POS Power BI",
        "why": "يثبت قدرتك على تحليل مؤشرات كبيرة وبناء Dashboard واضح.",
    },
    "hr": {
        "project": "SAMA POS Power BI أو Excel Branch Performance",
        "why": "يثبت قدرتك على بناء مؤشرات وتقارير تساعد في اتخاذ القرار.",
    },
    "default": {
        "project": "SAMA POS Power BI أو Excel Branch Performance",
        "why": "اربط التقديم بأقرب مشروع يثبت Excel وPower BI والتحليل.",
    },
}


COMPANY_HINTS = {
    "stc": ("telecom", "إس تي سي – اتصالات وتقنية"),
    "mobily": ("telecom", "موبايلي – اتصالات وتقنية"),
    "zain": ("telecom", "زين – اتصالات وتقنية"),
    "tamara": ("fintech", "تمارا – تقنية مالية"),
    "tabby": ("fintech", "تابي – تقنية مالية"),
    "lean": ("fintech", "لين – تقنية مالية وخدمات مصرفية مفتوحة"),
    "rajhi": ("fintech", "مصرف الراجحي – قطاع مصرفي"),
    "snb": ("fintech", "البنك الأهلي السعودي – قطاع مصرفي"),
    "riyad bank": ("fintech", "بنك الرياض – قطاع مصرفي"),
    "foodics": ("operations", "فودكس – تقنية المطاعم ونقاط البيع"),
    "jahez": ("operations", "جاهز – توصيل وطلبات"),
    "hungerstation": ("operations", "هنقرستيشن – توصيل وطلبات"),
    "elm": ("government", "علم – حلول رقمية حكومية"),
    "sdaia": ("government", "سدايا – بيانات وذكاء اصطناعي"),
    "tahakom": ("government", "تحكم – مدن ذكية وسلامة مرورية"),
}


def contains_any(text: str, terms: list[str]) -> bool:
    text = text.lower()
    return any(term.lower() in text for term in terms)


def detect_company_context(company_name: str, description: str) -> tuple[str, str | None]:
    text = f"{company_name} {description}".lower()

    for company_key, (sector, arabic_label) in COMPANY_HINTS.items():
        if company_key in text:
            return sector, arabic_label

    if contains_any(text, ["bank", "fintech", "payment", "payments", "finance", "pos", "مدفوعات", "بنك"]):
        return "fintech", None

    if contains_any(text, ["restaurant", "retail", "sales", "branch", "operations", "delivery", "طلبات", "مبيعات", "تشغيل"]):
        return "operations", None

    if contains_any(text, ["government", "public sector", "digital government", "حكومي", "تحول رقمي"]):
        return "government", None

    if contains_any(text, ["telecom", "customer", "network", "اتصالات", "عملاء"]):
        return "telecom", None

    if contains_any(text, ["hr analytics", "people analytics", "workforce", "human resources", "موارد بشرية"]):
        return "hr", None

    return "default", None


def detect_target_people(title: str, description: str) -> str:
    text = f"{title} {description}".lower()

    if contains_any(text, ["hr analytics", "people analytics", "workforce"]):
        return "Talent Acquisition أو HR Analytics أو People Analytics"

    if contains_any(text, ["bi", "business intelligence", "power bi", "dashboard"]):
        return "Talent Acquisition أو BI Analyst أو Data Team"

    if contains_any(text, ["operations", "reporting", "performance"]):
        return "Talent Acquisition أو Operations Analyst أو Reporting Team"

    if contains_any(text, ["finance", "payment", "risk", "growth"]):
        return "Talent Acquisition أو Growth/Data Analyst أو Finance Analytics"

    return "Talent Acquisition أو مسؤول توظيف أو شخص من فريق البيانات"


def detect_message_focus(title: str, description: str) -> str:
    text = f"{title} {description}".lower()

    focus = []

    if contains_any(text, ["power bi", "dashboard", "dashboards", "bi"]):
        focus.append("Power BI")
    if contains_any(text, ["excel", "reporting", "reports"]):
        focus.append("Excel والتقارير")
    if contains_any(text, ["kpi", "metrics", "performance"]):
        focus.append("مؤشرات الأداء")
    if contains_any(text, ["data quality", "cleaning"]):
        focus.append("تنظيف وجودة البيانات")

    if not focus:
        return "التحليل والتقارير"

    return "، ".join(focus[:3])


def build_linkedin_message(opportunity_data: dict, project: str, focus: str) -> str:
    company = opportunity_data.get("company", "الشركة")
    title = opportunity_data.get("title", "فرصة مناسبة")

    return (
        f"السلام عليكم، أنا عبدالله خريج رياضيات ومحلل بيانات مبتدئ. "
        f"قدمت على فرصة {title} لدى {company}. "
        f"عندي مشروع {project} يوضح شغلي في {focus}. "
        f"يسعدني مشاركة ملف الأعمال إذا كان مناسب."
    )


def build_interview_strategy(opportunity_data: dict, score: int) -> str:
    if score < 80:
        return ""

    title = opportunity_data.get("title", "")
    company = opportunity_data.get("company", "")
    location = opportunity_data.get("location", "")
    description = opportunity_data.get("description", "")

    sector, arabic_label = detect_company_context(company, description)
    project_data = PROJECTS.get(sector, PROJECTS["default"])
    people = detect_target_people(title, description)
    focus = detect_message_focus(title, description)
    message = build_linkedin_message(opportunity_data, project_data["project"], focus)

    company_line = company
    if arabic_label and arabic_label not in company:
        company_line = f"{company} ({arabic_label})"

    return f"""
خطة الوصول للمقابلة:
- الشركة: {company_line}
- المدينة: {location or "غير مذكورة"}
- قدّم من الرابط أولًا.
- ابحث في LinkedIn عن: {people}.
- المشروع الأنسب: {project_data["project"]}.
- سبب الربط: {project_data["why"]}

رسالة جاهزة:
{message}"""
