import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from company_career_links import COMPANY_CAREER_TARGETS
from opportunity_scoring import contains_any


JOB_TITLE_KEYWORDS = [
    "data analyst",
    "junior data analyst",
    "graduate data analyst",
    "business data analyst",
    "bi analyst",
    "business intelligence analyst",
    "reporting analyst",
    "data reporting",
    "power bi analyst",
    "analytics analyst",
    "hr analytics analyst",
    "people analytics",
    "people analytics analyst",
    "workforce analytics",
    "workforce analytics analyst",
    "talent analytics",
    "performance analyst",
    "insights analyst",
    "business analyst",
    "operations analyst",
    "commercial analyst",
    "محلل بيانات",
    "محلل ذكاء أعمال",
    "محلل تقارير",
    "محلل تحليلات",
    "تحليلات الموارد البشرية",
    "تحليلات الموظفين",
    "تحليلات القوى العاملة",
]

ENTRY_LEVEL_KEYWORDS = [
    "junior",
    "entry level",
    "fresh graduate",
    "graduate",
    "tamheer",
    "coop",
    "intern",
    "internship",
    "trainee",
    "0-1",
    "0-2",
    "0-3",
    "حديث تخرج",
    "خريج",
    "تمهير",
    "تدريب",
    "متدرب",
]

DATA_CONTEXT_KEYWORDS = [
    "data",
    "analytics",
    "analysis",
    "bi",
    "business intelligence",
    "reporting",
    "dashboard",
    "power bi",
    "sql",
    "excel",
    "insights",
    "metrics",
    "kpi",
    "visualization",
    "تحليل",
    "بيانات",
    "تقارير",
    "لوحات",
    "مؤشرات",
]

STRONG_JOB_URL_HINTS = [
    "/job/",
    "/jobs/",
    "/jobdetails",
    "/job-detail",
    "/jobsearch",
    "careers.stc.com.sa/job",
    "greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "workdayjobs.com",
    "oraclecloud.com",
    "successfactors",
    "smartrecruiters.com",
    "bamboohr.com",
    "jobvite.com",
]

WEAK_JOB_URL_HINTS = [
    "/career",
    "/careers",
    "/position",
    "/positions",
    "/opening",
    "/openings",
    "/vacancy",
    "/vacancies",
    "careers.",
    "jobs.",
]

BLOCKED_URL_HINTS = [
    "/personal/",
    "/business/connect/",
    "/mobile/",
    "/international-calls",
    "/internet",
    "/voice",
    "/packages",
    "/plans",
    "/shop",
    "/store",
    "/support",
    "/help",
    "/contact",
    "/news",
    "/blog",
    "/media",
    "/privacy",
    "/terms",
    "/about",
    "/investor",
    "/products",
    "/services",
    "tel:",
    "mailto:",
    "whatsapp",
    "facebook",
    "instagram",
    "twitter",
    "x.com",
    "youtube",
]

BLOCKED_TEXT_HINTS = [
    "international calls",
    "quicknet",
    "mobile data",
    "package",
    "packages",
    "plan",
    "plans",
    "internet",
    "voice",
    "support",
    "contact us",
    "about us",
    "privacy",
    "terms",
    "media center",
    "investor relations",
    "product",
    "service",
    "المساعدة",
    "اتصل بنا",
    "الباقات",
    "الإنترنت",
    "الخدمات",
    "المنتجات",
]

SENIOR_KEYWORDS = [
    "senior",
    "lead",
    "manager",
    "director",
    "principal",
    "head of",
    "5+",
    "7+",
    "10+",
    "مدير",
    "رئيس",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 AbdullahCareerAgent/0.7"
}


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)

    if parsed.scheme not in ["http", "https"]:
        return False

    normalized_url = url.lower()

    if contains_any(normalized_url, BLOCKED_URL_HINTS):
        return False

    return True


def is_noise_text(text: str) -> bool:
    cleaned = re.sub(r"[\s\-\+\(\)]", "", text)

    if cleaned.isdigit():
        return True

    if len(text.strip()) < 4:
        return True

    if contains_any(text, BLOCKED_TEXT_HINTS):
        return True

    return False


def build_company_label(target: dict) -> str:
    arabic_label = target.get("arabic_label") or target.get("arabic_description")

    if arabic_label:
        return f'{target["company"]} ({arabic_label})'

    return target["company"]


def looks_like_job_url(url: str) -> bool:
    normalized_url = url.lower()
    return contains_any(normalized_url, STRONG_JOB_URL_HINTS) or contains_any(
        normalized_url,
        WEAK_JOB_URL_HINTS,
    )


def classify_link(text: str, url: str) -> str | None:
    combined = f"{text} {url}".lower()

    if contains_any(combined, BLOCKED_TEXT_HINTS):
        return None

    if contains_any(combined, SENIOR_KEYWORDS):
        return None

    has_job_title = contains_any(combined, JOB_TITLE_KEYWORDS)
    has_entry_signal = contains_any(combined, ENTRY_LEVEL_KEYWORDS)
    has_data_context = contains_any(combined, DATA_CONTEXT_KEYWORDS)
    has_strong_job_url = contains_any(combined, STRONG_JOB_URL_HINTS)
    has_any_job_url = looks_like_job_url(url)

    if has_job_title and has_data_context and has_any_job_url:
        return "apply_now"

    if has_job_title and has_strong_job_url:
        return "apply_now"

    if has_entry_signal and has_data_context and has_strong_job_url:
        return "apply_now"

    return None


def extract_job_links(soup: BeautifulSoup, base_url: str) -> list[dict]:
    job_links = []

    for link in soup.find_all("a"):
        text = clean_text(link.get_text(" "))
        href = link.get("href")

        if not text or not href:
            continue

        full_url = urljoin(base_url, href)

        if not is_valid_url(full_url):
            continue

        if is_noise_text(text):
            continue

        signal_type = classify_link(text, full_url)

        if signal_type:
            job_links.append(
                {
                    "title": text,
                    "url": full_url,
                    "signal_type": signal_type,
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
        opportunities.append(
            {
                "title": job["title"],
                "company": company_label,
                "location": "Saudi Arabia",
                "description": (
                    "تم العثور على رابط شاغر رسمي أو مسمى قريب من تحليل البيانات/التحليلات. "
                    "راجع المتطلبات ثم قدّم إذا كانت مناسبة."
                ),
                "url": job["url"],
                "source": "Company career page scanner",
                "category": "🟢 قدّم الآن",
                "is_real_job": True,
            }
        )

    return opportunities


def scan_company_career_pages(limit: int = 12) -> list[dict]:
    opportunities = []

    targets = [
        target
        for target in COMPANY_CAREER_TARGETS
        if target.get("priority") == "high"
    ][:limit]

    for target in targets:
        opportunities.extend(scan_company_page(target))

    return opportunities
