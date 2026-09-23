from urllib.parse import quote_plus


COMPANY_CAREER_TARGETS = [
    {
        "company": "Elm",
        "arabic_label": "علم – حلول رقمية حكومية",
        "priority": "high",
        "sector": "Digital government",
        "sector_ar": "حكومة رقمية",
        "career_url": "https://www.elm.sa/en/careers",
        "why": "شركة قوية جدًا في التحول الرقمي الحكومي، وفرص البيانات فيها مناسبة لمسار BI والتحليل.",
        "mini_project_angle": "تحليل مؤشرات الخدمات الرقمية الحكومية أو تجربة المستخدم للخدمات الإلكترونية من بيانات عامة.",
        "best_move": "تابع صفحة الوظائف + ابحث عن موظفي Talent Acquisition وData/BI في LinkedIn.",
    },
    {
        "company": "stc",
        "arabic_label": "إس تي سي – اتصالات وتقنية",
        "priority": "high",
        "sector": "Telecom",
        "sector_ar": "اتصالات",
        "career_url": "https://www.stc.com.sa/content/stc/sa/en/about-stc/careers.html",
        "why": "شركة ضخمة واحتياجها للتحليلات والتقارير مستمر في العملاء، الشبكات، المبيعات، وتجربة المستخدم.",
        "mini_project_angle": "تحليل بيانات استخدام الاتصالات أو رضا العملاء من مصادر عامة، مع Dashboard بسيط.",
        "best_move": "قدّم رسميًا + جهز رسالة مختصرة لمسؤول توظيف أو فريق BI.",
    },
    {
        "company": "SDAIA",
        "arabic_label": "سدايا – الهيئة السعودية للبيانات والذكاء الاصطناعي",
        "priority": "high",
        "sector": "Data and AI",
        "sector_ar": "بيانات وذكاء اصطناعي",
        "career_url": "https://sdaia.gov.sa",
        "why": "أقوى جهة مرتبطة بالبيانات والذكاء الاصطناعي في السعودية.",
        "mini_project_angle": "مشروع يستخدم بيانات حكومية مفتوحة ويعرض جودة التحليل والتنظيف والتصور.",
        "best_move": "راقب الإعلانات والبرامج، وابنِ مشروعًا قويًا ببيانات سعودية مفتوحة.",
    },
    {
        "company": "Tahakom",
        "arabic_label": "تحكم – حلول المدن الذكية والسلامة المرورية",
        "priority": "high",
        "sector": "Smart mobility",
        "sector_ar": "تنقل ذكي",
        "career_url": "https://www.tahakom.com/careers",
        "why": "بيئة تشغيلية تعتمد على البيانات، التقارير، الأداء، والتحليلات.",
        "mini_project_angle": "تحليل مؤشرات السلامة المرورية أو الحوادث من بيانات عامة إن توفرت.",
        "best_move": "قدّم رسميًا وابحث عن Analytics/BI/Data team في LinkedIn.",
    },
    {
        "company": "Mozn",
        "arabic_label": "مزن – ذكاء اصطناعي ومخاطر مالية",
        "priority": "high",
        "sector": "AI and fintech risk",
        "sector_ar": "ذكاء اصطناعي ومخاطر مالية",
        "career_url": "https://www.mozn.sa/careers",
        "why": "شركة Data/AI قوية، وقد تكون مناسبة للأدوار التحليلية القريبة من المخاطر والتقارير.",
        "mini_project_angle": "تحليل بسيط لمؤشرات الاحتيال أو المخاطر في المدفوعات من بيانات عامة/مصطنعة بوضوح.",
        "best_move": "ركز على Portfolio يثبت تنظيف بيانات وتحليل أنماط وتقرير واضح.",
    },
    {
        "company": "Tamara",
        "arabic_label": "تمارا – تقنية مالية وخدمات اشتر الآن وادفع لاحقًا",
        "priority": "high",
        "sector": "Fintech",
        "sector_ar": "تقنية مالية",
        "career_url": "https://www.tamara.co/careers",
        "why": "فنتك سريع النمو، والتحليلات مهمة في المخاطر، النمو، المنتج، والمدفوعات.",
        "mini_project_angle": "تحليل مؤشرات المدفوعات الإلكترونية في السعودية باستخدام بيانات SAMA المفتوحة.",
        "best_move": "قدّم + رسالة LinkedIn مخصصة تربط مشروع SAMA POS بالشركة.",
    },
    {
        "company": "Tabby",
        "arabic_label": "تابي – تقنية مالية وخدمات اشتر الآن وادفع لاحقًا",
        "priority": "high",
        "sector": "Fintech",
        "sector_ar": "تقنية مالية",
        "career_url": "https://tabby.ai/en-SA/careers",
        "why": "فنتك إقليمي يحتاج تحليلات نمو، مخاطر، عملاء، وتقارير.",
        "mini_project_angle": "Dashboard عن نمو المدفوعات ونقاط البيع في السعودية من SAMA.",
        "best_move": "قدّم رسميًا واذكر مشروع SAMA إذا كان مناسبًا.",
    },
    {
        "company": "Foodics",
        "arabic_label": "فودكس – تقنية المطاعم ونقاط البيع",
        "priority": "high",
        "sector": "SaaS",
        "sector_ar": "برمجيات كخدمة",
        "career_url": "https://www.foodics.com/careers/",
        "why": "SaaS سعودي، وتحليلات المطاعم والمبيعات والعملاء مناسبة جدًا لمحلل بيانات مبتدئ.",
        "mini_project_angle": "تحليل مبيعات مطاعم افتراضية: الفروع، المنتجات، الربحية، وساعات الذروة.",
        "best_move": "استخدم مشروع Excel حق الفروع والربحية كزاوية تواصل.",
    },
    {
        "company": "HungerStation",
        "arabic_label": "هنقرستيشن – توصيل وماركت بليس للمطاعم",
        "priority": "high",
        "sector": "Delivery marketplace",
        "sector_ar": "توصيل وطلبات",
        "career_url": "https://www.hungerstation.com/sa-en/careers",
        "why": "شركات التوصيل تعتمد بقوة على operations analytics وgrowth analytics.",
        "mini_project_angle": "تحليل طلبات توصيل افتراضية حسب الوقت والمنطقة ومعدل الإلغاء.",
        "best_move": "قدّم + جهز رسالة تبين فهمك لمؤشرات التشغيل.",
    },
    {
        "company": "Jahez",
        "arabic_label": "جاهز – توصيل وطلبات",
        "priority": "high",
        "sector": "Delivery marketplace",
        "sector_ar": "توصيل وطلبات",
        "career_url": "https://www.jahez.net/careers",
        "why": "شركة سعودية مدرجة، واحتياجها للتقارير والتحليلات التشغيلية كبير.",
        "mini_project_angle": "Dashboard تشغيلي عن الطلبات، المناطق، أوقات الذروة، والأداء.",
        "best_move": "قدّم رسميًا وراقب وظائف Operations/BI/Reporting.",
    },
    {
        "company": "Al Rajhi Bank",
        "arabic_label": "مصرف الراجحي – قطاع مصرفي",
        "priority": "high",
        "sector": "Banking",
        "sector_ar": "مصرفية",
        "career_url": "https://www.alrajhibank.com.sa/About-alrajhi-bank/Careers",
        "why": "البنوك فيها فرص BI وتقارير ومخاطر ومالية بشكل مستمر.",
        "mini_project_angle": "تحليل مؤشرات المدفوعات أو نقاط البيع من SAMA وربطها بسلوك العملاء.",
        "best_move": "قدّم رسميًا وركز على Power BI + Excel + SQL.",
    },
    {
        "company": "SNB",
        "arabic_label": "البنك الأهلي السعودي – قطاع مصرفي",
        "priority": "high",
        "sector": "Banking",
        "sector_ar": "مصرفية",
        "career_url": "https://www.alahli.com/en-us/about-us/careers",
        "why": "بنك كبير وفرص التحليل فيه تكون في المالية، المخاطر، العمليات، والعملاء.",
        "mini_project_angle": "تحليل سوق المدفوعات أو POS بزاوية مصرفية.",
        "best_move": "قدّم رسميًا وابحث عن Business Intelligence / Reporting Analyst.",
    },
    {
        "company": "Riyad Bank",
        "arabic_label": "بنك الرياض – قطاع مصرفي",
        "priority": "high",
        "sector": "Banking",
        "sector_ar": "مصرفية",
        "career_url": "https://www.riyadbank.com/careers",
        "why": "بنك مناسب لمهارات Power BI والتقارير وتحليل الأداء.",
        "mini_project_angle": "تحليل مؤشرات قطاع المدفوعات أو القنوات الرقمية.",
        "best_move": "قدّم رسميًا وخصص رسالة قصيرة تربط مشروع SAMA بالبنوك.",
    },
    {
        "company": "PwC Middle East",
        "arabic_label": "برايس ووترهاوس كوبرز الشرق الأوسط – استشارات",
        "priority": "high",
        "sector": "Consulting",
        "sector_ar": "استشارات",
        "career_url": "https://www.pwc.com/m1/en/careers.html",
        "why": "الاستشارات تعطي خبرة قوية، وفيها احتياج لتحليل بيانات وتقارير ومشاريع عملاء.",
        "mini_project_angle": "Case study صغير: تحليل أداء فروع أو قطاع باستخدام Excel/Power BI.",
        "best_move": "ابحث عن Graduate / Analyst / Data Analytics roles.",
    },
    {
        "company": "Deloitte",
        "arabic_label": "ديلويت – استشارات ومراجعة",
        "priority": "high",
        "sector": "Consulting",
        "sector_ar": "استشارات",
        "career_url": "https://www.deloitte.com/middle-east/en/careers.html",
        "why": "مشاريع التحول والبيانات مناسبة للمبتدئ إذا دخل Analyst أو Graduate.",
        "mini_project_angle": "تقرير تحليلي قصير عن قطاع سعودي مع Dashboard.",
        "best_move": "ركز على أدوار Analyst وGraduate وBusiness Intelligence.",
    },
    {
        "company": "Accenture",
        "arabic_label": "أكسنتشر – استشارات وتقنية",
        "priority": "high",
        "sector": "Consulting and technology",
        "sector_ar": "استشارات وتقنية",
        "career_url": "https://www.accenture.com/sa-en/careers",
        "why": "شركة تقنية واستشارات، وفرص analytics والتحول الرقمي فيها قوية.",
        "mini_project_angle": "تحليل رقمي لخدمة أو قطاع مع توصيات تنفيذية.",
        "best_move": "قدّم على أدوار Entry-level Analyst أو Technology Analyst.",
    },
    {
        "company": "Tadawul Group",
        "arabic_label": "مجموعة تداول السعودية – الأسواق المالية",
        "priority": "high",
        "sector": "Capital markets",
        "sector_ar": "أسواق مالية",
        "career_url": "https://www.saudiexchange.sa",
        "why": "بيانات مالية وسوقية، وفرص التقارير والتحليل قوية.",
        "mini_project_angle": "تحليل بسيط لحركة قطاعات السوق أو قيم التداول من بيانات عامة.",
        "best_move": "راقب وظائف Data/BI/Reporting والبرامج.",
    },
]


def get_company_label(target: dict) -> str:
    return f'{target["company"]} ({target["arabic_label"]})'


def build_official_search_url(company: str) -> str:
    query = quote_plus(f"{company} careers Saudi Arabia data analyst OR BI analyst")
    return f"https://www.google.com/search?q={query}"


def get_high_priority_career_targets(limit: int = 12) -> list[dict]:
    high_priority = [
        target for target in COMPANY_CAREER_TARGETS if target["priority"] == "high"
    ]
    return high_priority[:limit]


def build_career_targets_summary(limit: int = 5, include_search_links: bool = False) -> str:
    targets = get_high_priority_career_targets(limit)

    lines = []
    for target in targets:
        block = [
            f'- {get_company_label(target)} | القطاع: {target["sector_ar"]}',
            f'  لماذا تهمك: {target["why"]}',
            f'  مشروع مصغر مناسب: {target["mini_project_angle"]}',
            f'  أفضل تحرك: {target["best_move"]}',
            f'  رابط التوظيف: {target["career_url"]}',
        ]

        if include_search_links:
            official_search = build_official_search_url(target["company"])
            block.append(f"  بحث احتياطي: {official_search}")

        lines.append("\n".join(block))

    return "\n\n".join(lines)
