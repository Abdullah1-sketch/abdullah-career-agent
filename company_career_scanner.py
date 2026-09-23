import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from company_career_links import COMPANY_CAREER_TARGETS


JOB_TITLE_KEYWORDS = [
    "data analyst",
    "junior data analyst",
    "business data analyst",
    "bi analyst",
    "business intelligence analyst",
    "reporting analyst",
    "data reporting",
    "power bi analyst",
    "محلل بيانات",
    "محلل ذكاء أعمال",
    "محلل تقارير",
]

ENTRY_LEVEL_KEYWORDS = [
    "junior",
    "entry level",
    "fresh graduate",
    "graduate",
    "tamheer",
    "coop",
    "intern",
    "trainee",
    "0-1",
    "0-2",
    "0-3",
    "حديث تخرج",
    "خريج",
    "تمهير",
    "تدريب",
]

GENERIC_CAREER_WORDS = [
    "careers",
    "career",
    "jobs",
    "join us",
    "work with us",
    "الوظائف",
    "التوظيف",
    "انضم",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 AbdullahCareerAgent/0.3"
}


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def contains_any(text: str, keywords: list[str]) -> bool:
    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)


def classify_signal(title_text: str, url: str) -> str:
    combined = f"{title_text} {url}".lower()

    if contains_any(combined, JOB_TITLE_KEYWORDS):
        return "apply_now"

    if contains_any(combined, ENTRY_LEVEL_KEYWORDS) and contains_any(
        combined, ["data", "bi", "analytics", "تحليل", "بيانات"]
    ):
        return "apply_now"

    return "monitor_company"


def build_company_label(target: dict) -> str:
    arabic_label = target.get("arabic_label") or target.get("arabic_description")
    if arabic_label:
        return f'{target["company"]} ({arabic_label})'
    return target["company"]


def extract_job_links(soup: BeautifulSoup, base_url: str) -> list[dict]:
    job_links = []

    for link in soup.find_all("a"):
        text = clean_text(link.get_text(" "))
        href = link.get("href")

        if not text or not href:
            continue

        full_url = urljoin(base_url, href)
        combined = f"{text} {full_url}"

        if contains_any(combined, JOB_TITLE_KEYWORDS + ENTRY_LEVEL_KEYWORDS):
            job_links.append(
                {
                    "title": text,
                    "url": full_url,
                    "signal_type": classify_signal(text, full_url),
                }
            )

    unique_links = {}
    for item in job_links:
        unique_links[item["url"]] = item

    return list(unique_links.values())


def scan_company_page(target: dict) -> list[dict]:
    try:
        response = requests.get(
            target["career_url"],
            headers=HEADERS,
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    company_label = build_company_label(target)
    job_links = extract_job_links(soup, target["career_url"])

    if not job_links:
        return [
            {
                "title": "Company under monitoring",
                "company": company_label,
                "location": "Saudi Arabia",
                "description": (
                    "صفحة وظائف عامة. لم يتم العثور على شاغر بيانات واضح اليوم، "
                    "لذلك تُصنف كشركة تحت المراقبة وليست فرصة تقديم."
                ),
                "url": target["career_url"],
                "source": "Company career page scanner",
                "category": "⚪ شركة تحت المراقبة",
                "is_real_job": False,
            }
        ]

    opportunities = []

    for job in job_links:
        if job["signal_type"] == "apply_now":
            opportunities.append(
                {
                    "title": job["title"],
                    "company": company_label,
                    "location": "Saudi Arabia",
                    "description": (
                        "تم العثور على رابط شاغر أو برنامج قريب من مسار تحليل البيانات. "
                        "راجع المتطلبات ثم قدّم إذا كانت مناسبة."
                    ),
                    "url": job["url"],
                    "source": "Company career page scanner",
                    "category": "🟢 قدّم الآن",
                    "is_real_job": True,
                }
            )
        else:
            opportunities.append(
                {
                    "title": job["title"],
                    "company": company_label,
                    "location": "Saudi Arabia",
                    "description": (
                        "إشارة محتملة من صفحة التوظيف، لكنها تحتاج مراجعة قبل اعتبارها فرصة تقديم."
                    ),
                    "url": job["url"],
                    "source": "Company career page scanner",
                    "category": "🟡 إشارة مبكرة / راقب",
                    "is_real_job": False,
                }
            )

    return opportunities


def scan_company_career_pages(limit: int = 8) -> list[dict]:
    opportunities = []

    targets = [
        target
        for target in COMPANY_CAREER_TARGETS
        if target.get("priority") == "high"
    ][:limit]

    for target in targets:
        opportunities.extend(scan_company_page(target))

    return opportunities
