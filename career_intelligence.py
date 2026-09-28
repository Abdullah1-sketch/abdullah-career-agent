from datetime import date


COMPANY_FIT_MAP = {
    "Foodics": {
        "arabic_label": "فودكس – تقنية المطاعم ونقاط البيع",
        "best_project": "Excel Branch Performance & Profitability",
        "why_it_fits": "مشروع Excel حق الفروع والربحية قريب جدًا من بيئة المطاعم ونقاط البيع.",
        "door_opener": (
            "السلام عليكم، أنا عبدالله خريج رياضيات ومحلل بيانات مبتدئ. "
            "عندي مشروع Excel يحلل أداء الفروع والربحية والمبيعات، وحسيته قريب من بيئة Foodics. "
            "إذا فيه فرصة Junior Data Analyst أو Reporting Analyst أتشرف أرسل لكم ملف الأعمال."
        ),
    },
    "Tamara": {
        "arabic_label": "تمارا – تقنية مالية وخدمات اشتر الآن وادفع لاحقًا",
        "best_project": "SAMA POS Analysis",
        "why_it_fits": "مشروع SAMA POS قريب من المدفوعات والنمو والقطاع المالي.",
        "door_opener": (
            "السلام عليكم، أنا عبدالله خريج رياضيات ومحلل بيانات مبتدئ. "
            "عندي مشروع Power BI على بيانات SAMA POS، وحسيته قريب من مجال المدفوعات والنمو في Tamara. "
            "إذا فيه فرصة Junior Data Analyst أو BI Analyst أتشرف أرسل لكم ملف الأعمال."
        ),
    },
    "Tabby": {
        "arabic_label": "تابي – تقنية مالية وخدمات اشتر الآن وادفع لاحقًا",
        "best_project": "SAMA POS Analysis",
        "why_it_fits": "مشروع SAMA POS مناسب لشركات التقنية المالية والمدفوعات.",
        "door_opener": (
            "السلام عليكم، أنا عبدالله خريج رياضيات ومحلل بيانات مبتدئ. "
            "اشتغلت على مشروع Power BI يحلل بيانات نقاط البيع من SAMA، وأشوفه قريب من قطاع المدفوعات. "
            "إذا فيه فرصة Junior Data Analyst أو Reporting Analyst أتشرف أشارك ملف الأعمال."
        ),
    },
    "Elm": {
        "arabic_label": "علم – حلول رقمية حكومية",
        "best_project": "SAMA POS Analysis",
        "why_it_fits": "مشروع بيانات سعودية مفتوحة مناسب لشركة تعمل في التحول الرقمي الحكومي.",
        "door_opener": (
            "السلام عليكم، أنا عبدالله خريج رياضيات ومحلل بيانات مبتدئ. "
            "عندي مشاريع Power BI وExcel، ومنها مشروع على بيانات سعودية مفتوحة. "
            "أبحث عن فرصة Junior Data Analyst أو BI Analyst وأتشرف أرسل لكم ملف الأعمال."
        ),
    },
    "stc": {
        "arabic_label": "إس تي سي – اتصالات وتقنية",
        "best_project": "SAMA POS Analysis",
        "why_it_fits": "مشروع Power BI يثبت قدرتك على تحليل بيانات كبيرة ومؤشرات أداء.",
        "door_opener": (
            "السلام عليكم، أنا عبدالله خريج رياضيات ومحلل بيانات مبتدئ. "
            "عندي مشاريع Power BI وExcel في التحليل والتقارير، وأبحث عن فرصة Junior Data Analyst أو Reporting Analyst. "
            "أقدر أرسل لكم ملف الأعمال إذا فيه فرصة مناسبة."
        ),
    },
    "Jahez": {
        "arabic_label": "جاهز – توصيل وطلبات",
        "best_project": "Excel Branch Performance & Profitability",
        "why_it_fits": "مشروع Excel مناسب لتحليل الفروع، المبيعات، الأداء التشغيلي، والربحية.",
        "door_opener": (
            "السلام عليكم، أنا عبدالله خريج رياضيات ومحلل بيانات مبتدئ. "
            "عندي مشروع Excel يحلل أداء الفروع والربحية والمبيعات، وأشوفه قريب من تقارير التشغيل والطلبات. "
            "إذا فيه فرصة Junior Reporting Analyst أو Data Analyst أتشرف أرسل لكم ملف الأعمال."
        ),
    },
    "Tahakom": {
        "arabic_label": "تحكم – حلول المدن الذكية والسلامة المرورية",
        "best_project": "SAMA POS Analysis",
        "why_it_fits": "مشاريعك تثبت قدرتك على بناء مؤشرات ولوحات متابعة، وهذا مناسب للبيئات التشغيلية.",
        "door_opener": (
            "السلام عليكم، أنا عبدالله خريج رياضيات ومحلل بيانات مبتدئ. "
            "عندي مشاريع Power BI وExcel في بناء التقارير ولوحات المؤشرات، وأبحث عن فرصة Junior Data Analyst أو BI Analyst. "
            "أقدر أرسل لكم ملف الأعمال إذا فيه فرصة مناسبة."
        ),
    },
    "Lean": {
        "arabic_label": "لين تكنولوجيز – تقنية مالية وخدمات مصرفية مفتوحة",
        "best_project": "SAMA POS Analysis",
        "why_it_fits": "مشروع SAMA POS قريب من التقنية المالية وتحليل المدفوعات.",
        "door_opener": (
            "السلام عليكم، أنا عبدالله خريج رياضيات ومحلل بيانات مبتدئ. "
            "عندي مشروع Power BI على بيانات SAMA POS، وأشوفه قريب من مجال التقنية المالية والخدمات المصرفية المفتوحة. "
            "إذا فيه فرصة Junior Data Analyst أو BI Analyst أتشرف أرسل لكم ملف الأعمال."
        ),
    },
}


DAILY_ACTIONS = [
    {
        "title": "قو SQL اليوم",
        "reason": "SQL أكثر مهارة ترفع فرصك في وظائف Data Analyst وBI Analyst.",
        "task": "ذاكر 45 دقيقة: SELECT + WHERE + ORDER BY، ثم طبّق 10 استعلامات بسيطة.",
    },
    {
        "title": "جهز رسالة LinkedIn قصيرة",
        "reason": "التقديم الرسمي وحده أحيانًا ما يكفي، الرسالة المختصرة تزيد فرصة الانتباه لك.",
        "task": "اكتب رسالة من 3 أسطر لمسؤول توظيف: من أنت، وش مشروعك الأقرب، وش نوع الفرصة اللي تبحث عنها.",
    },
    {
        "title": "راجع مشروع Excel",
        "reason": "مشروع Excel حق الفروع والربحية مناسب لشركات التشغيل والمطاعم والتوصيل.",
        "task": "اكتب 3 نقاط قصيرة تشرح: المشكلة، التحليل، النتيجة.",
    },
    {
        "title": "راجع مشروع SAMA POS",
        "reason": "هذا أفضل مشروع تبرزه للبنوك والفنتك والشركات الحكومية.",
        "task": "اكتب 3 نقاط قصيرة تشرح: مصدر البيانات، أهم المؤشرات، وش اكتشفت.",
    },
    {
        "title": "حسّن عنوان LinkedIn",
        "reason": "العنوان يساعد مسؤولي التوظيف يفهمون مسارك بسرعة.",
        "task": "استخدم عنوان واضح: Junior Data Analyst | Power BI | Excel | SQL Learner.",
    },
    {
        "title": "جهز رد المقابلة الأول",
        "reason": "أول سؤال غالبًا: تكلم عن نفسك. جاهزية الجواب تفرق.",
        "task": "اكتب جواب 45 ثانية: خريج رياضيات، مهتم بتحليل البيانات، عندك Power BI وExcel، وتتعلم SQL.",
    },
    {
        "title": "ابحث يدويًا عن شركة واحدة",
        "reason": "أحيانًا أفضل فرصة تجي من صفحة الشركة أو مسؤول توظيف قبل ما تنتشر.",
        "task": "اختر شركة واحدة في الرياض أو القصيم، وافتح صفحة الوظائف وابحث عن Data / BI / Reporting.",
    },
]


def get_company_fit(company_name: str) -> dict | None:
    company_name_lower = company_name.lower()

    for company, fit in COMPANY_FIT_MAP.items():
        if company.lower() in company_name_lower:
            return {
                "company": company,
                **fit,
            }

    return None


def get_today_action() -> dict:
    index = date.today().toordinal() % len(DAILY_ACTIONS)
    return DAILY_ACTIONS[index]


def build_daily_action_brief() -> str:
    action = get_today_action()

    return f"""وش تسوي اليوم؟

لا توجد فرصة قوية جديدة تستحق التقديم.

أقوى حركة اليوم:
{action["title"]}

ليش؟
{action["reason"]}

المهمة:
{action["task"]}
"""


def build_interview_door_opener(company_name: str) -> str:
    fit = get_company_fit(company_name)

    if not fit:
        return ""

    return f"""سبب تواصل مخصص:
الشركة: {fit["company"]} ({fit["arabic_label"]})
المشروع المناسب: {fit["best_project"]}

ليش هذا مدخل جيد؟
{fit["why_it_fits"]}

نص رسالة مقترح:
{fit["door_opener"]}
"""


def build_opportunity_battle_card(opportunity_data: dict, score: int) -> str:
    company_name = opportunity_data.get("company", "")
    title = opportunity_data.get("title", "")
    url = opportunity_data.get("url", "")

    door_opener = build_interview_door_opener(company_name)

    decision = "قدّم اليوم"
    if score < 75:
        decision = "قدّم إذا كانت المتطلبات مناسبة بعد قراءة الإعلان"

    parts = [
        "بطاقة التقديم:",
        "",
        f"الفرصة: {title}",
        f"الشركة: {company_name}",
        f"قرار البوت: {decision}",
        "",
        "خطوة السبق:",
        "- قدّم رسميًا أولًا.",
        "- بعدها أرسل رسالة مخصصة لمسؤول توظيف أو شخص من فريق البيانات.",
        "- اربط الرسالة بمشروع مناسب من ملف أعمالك.",
        "",
        f"الرابط: {url}",
    ]

    if door_opener:
        parts.extend(["", door_opener])

    return "\n".join(parts)


def build_weekly_market_radar() -> str:
    return """تقرير السوق الأسبوعي:

أهم فجوة الآن:
SQL

ليش؟
أغلب وظائف Data Analyst وBI Analyst تطلب SQL أو تعتبرها ميزة قوية.

خطة 3 أيام:
اليوم 1: SELECT + WHERE + ORDER BY
اليوم 2: JOIN
اليوم 3: GROUP BY + CASE

هدف الأسبوع:
تقدر تقول بثقة: أقدر أطلع البيانات بـ SQL وأعرضها في Power BI.
"""
