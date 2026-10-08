import os
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config import BAD_TITLE_SIGNALS
from opportunity_scoring import (
    CLOSED_POSTING_SIGNALS,
    contains_any,
    has_high_experience,
    is_hris_heavy_role,
    is_process_only_business_role,
    is_stale_posting,
)


SERPAPI_URL = "https://serpapi.com/search.json"

SEARCH_QUERIES = [
    "site:linkedin.com/jobs/view Saudi Arabia Riyadh \"Data Analyst\" \"0-2\"",
    "site:linkedin.com/jobs/view Saudi Arabia Riyadh \"Junior Data Analyst\"",
    "site:linkedin.com/jobs/view Saudi Arabia Riyadh \"BI Analyst\"",
    "site:linkedin.com/jobs/view Saudi Arabia Riyadh \"Reporting Analyst\"",
    "site:linkedin.com/jobs/view Saudi Arabia Riyadh \"HR Analytics Analyst\"",
    "site:linkedin.com/jobs/view Saudi Arabia Riyadh \"Business Analyst\" \"Power BI\"",
    "site:sabbar.com Saudi Arabia Riyadh \"Data Analyst\" fresh graduate",
    "site:sabbar.com Saudi Arabia Riyadh \"محلل بيانات\"",
    "site:careers.stc.com.sa Riyadh analytics analyst",
    "site:careers.stc.com.sa Riyadh data analyst",
    "site:jobs.lever.co Saudi Arabia Riyadh data analyst",
    "site:boards.greenhouse.io Saudi Arabia Riyadh data analyst",
    "site:jobs.ashbyhq.com Saudi Arabia Riyadh data analyst",
    "site:*.careers-page.com Riyadh \"Data Analyst\"",
    "site:*.careers-page.com Riyadh \"Business Intelligence\"",
]

TARGET_TITLE_TERMS = [
    "data analyst",
    "junior data analyst",
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
    "statistician",
    "محلل بيانات",
    "محلل ذكاء أعمال",
    "محلل تقارير",
    "محلل تحليلات",
    "تحليلات الموارد البشرية",
    "تحليلات الموظفين",
    "تحليلات القوى العاملة",
    "إحصائي",
]

DATA_CONTEXT_TERMS = [
    "data",
    "analytics",
    "analysis",
    "bi",
    "business intelligence",
    "reporting",
    "dashboard",
    "dashboards",
    "power bi",
    "sql",
    "excel",
    "insights",
    "metrics",
    "kpi",
    "visualization",
    "statistics",
    "statistical",
    "تحليل",
    "بيانات",
    "تقارير",
    "لوحات",
    "مؤشرات",
    "إحصاء",
]

ENTRY_LEVEL_TERMS = [
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

LOCATION_TERMS = [
    "riyadh",
    "الرياض",
    "eastern",
    "dammam",
    "khobar",
    "dhahran",
    "الشرقية",
    "الدمام",
    "الخبر",
    "الظهران",
    "qassim",
    "القصيم",
    "saudi arabia",
    "ksa",
    "السعودية",
]

GENERIC_TITLE_TERMS = [
    "jobs in",
    "job in",
    "job vacancies",
    "job openings",
    "no experience jobs",
    "analyst jobs",
    "data analyst jobs",
    "وظائف",
    "فرص عمل",
]

AGGREGATOR_DOMAINS = [
    "jooble.org",
    "indeed.com",
    "bayt.com",
    "naukrigulf.com",
    "glassdoor.com",
    "bebee.com",
    "trabajo.org",
    "learn4good.com",
    "wzzff.com",
]

BLOCKED_URL_PARTS = [
    "/jobs/search",
    "/jobs?q=",
    "/job-search",
    "/search",
    "/salary",
    "/career-advice",
    "/companies",
]

DIRECT_JOB_URL_HINTS = [
    "/jobs/view/",
    "/job/",
    "/jobs/",
    "greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "workdayjobs.com",
    "oraclecloud.com",
    "successfactors",
    "smartrecruiters",
    "sabbar.com",
    "careers.stc.com.sa",
    "careers-page.com",
]

COMPANY_LABELS = {
    "stc": "stc (إس تي سي – اتصالات وتقنية)",
    "sabbar": "Sabbar (صبار – منصة توظيف)",
    "linkedin": "LinkedIn (لينكدإن – منصة وظائف وتواصل مهني)",
    "sgr": "Saudi Gold Refinery (مصفاة الذهب السعودية – تعدين ومعادن ثمينة)",
}


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_url(url: str) -> str:
    return (url or "").split("?")[0].rstrip("/")


def get_domain(url: str) -> str:
    return urlparse(url).netloc.lower().replace("www.", "")


def is_aggregator_url(url: str) -> bool:
    domain = get_domain(url)
    return any(blocked in domain for blocked in AGGREGATOR_DOMAINS)


def is_direct_job_url(url: str) -> bool:
    lower_url = url.lower()

    if is_aggregator_url(lower_url):
        return False

    if contains_any(lower_url, BLOCKED_URL_PARTS):
        if "/jobs/view/" not in lower_url:
            return False

    return contains_any(lower_url, DIRECT_JOB_URL_HINTS)


def is_generic_search_result(title: str, url: str) -> bool:
    title_lower = title.lower()
    url_lower = url.lower()

    if contains_any(title_lower, GENERIC_TITLE_TERMS):
        return True

    if re.search(r"\b\d{2,5}\s+.*jobs\b", title_lower):
        return True

    if "linkedin.com/jobs/" in url_lower and "/jobs/view/" not in url_lower:
        return True

    return False


def fetch_page_html(url: str) -> str:
    try:
        response = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 AbdullahCareerAgent/1.1"},
        )
        response.raise_for_status()
    except requests.RequestException:
        return ""

    return response.text


def fetch_page_text(url: str) -> str:
    html = fetch_page_html(url)

    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    return clean_text(soup.get_text(" ")[:9000]).lower()


def extract_original_job_url(url: str) -> str:
    if is_direct_job_url(url):
        return normalize_url(url)

    if not is_aggregator_url(url):
        return ""

    html = fetch_page_html(url)

    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    candidates = []

    for link in soup.find_all("a"):
        href = link.get("href")

        if not href:
            continue

        full_url = urljoin(url, href)

        if is_direct_job_url(full_url):
            candidates.append(normalize_url(full_url))

    if not candidates:
        return ""

    platform_priority = [
        "careers-page.com",
        "careers.stc.com.sa",
        "linkedin.com/jobs/view",
        "greenhouse.io",
        "lever.co",
        "ashbyhq.com",
        "workdayjobs.com",
        "oraclecloud.com",
        "successfactors",
        "smartrecruiters",
    ]

    for platform in platform_priority:
        for candidate in candidates:
            if platform in candidate.lower():
                return candidate

    return candidates[0]


def extract_company(title: str, url: str, snippet: str) -> str:
    text = f"{title} {snippet}".lower()
    domain = get_domain(url)

    if "stc" in text or "careers.stc.com.sa" in domain:
        return COMPANY_LABELS["stc"]

    if "sabbar.com" in domain:
        return COMPANY_LABELS["sabbar"]

    if "linkedin.com" in domain:
        return COMPANY_LABELS["linkedin"]

    if domain.startswith("sgr.") or "saudi gold refinery" in text:
        return COMPANY_LABELS["sgr"]

    parts = domain.split(".")
    if parts:
        return parts[0]

    return "غير معروف"


def estimate_location(title: str, snippet: str) -> str:
    text = f"{title} {snippet}".lower()

    if "riyadh" in text or "الرياض" in text:
        return "الرياض"
    if "khobar" in text or "dammam" in text or "dhahran" in text or "eastern" in text or "الشرقية" in text:
        return "الشرقية"
    if "qassim" in text or "القصيم" in text:
        return "القصيم"
    if "saudi" in text or "ksa" in text or "السعودية" in text:
        return "السعودية"

    return "غير مذكورة"


def is_good_result(title: str, snippet: str, url: str) -> bool:
    combined = f"{title} {snippet} {url}".lower()

    if not is_direct_job_url(url):
        return False

    if is_generic_search_result(title, url):
        return False

    if contains_any(title, BAD_TITLE_SIGNALS):
        return False

    if is_stale_posting(combined) or has_high_experience(combined):
        return False

    has_target_title = contains_any(combined, TARGET_TITLE_TERMS)
    has_data_context = contains_any(combined, DATA_CONTEXT_TERMS)
    has_location = contains_any(combined, LOCATION_TERMS)

    if not (has_target_title and has_data_context and has_location):
        return False

    # The job page can also list other jobs ("Similar jobs"), so only explicit
    # closure and experience requirements are read from it, not titles or ages.
    page_text = fetch_page_text(url)
    full_text = f"{combined} {page_text}"

    if contains_any(page_text, CLOSED_POSTING_SIGNALS):
        return False

    if has_high_experience(full_text):
        return False

    if is_hris_heavy_role(title, full_text):
        return False

    if is_process_only_business_role(title, full_text):
        return False

    return True


def build_description(title: str, snippet: str) -> str:
    text = clean_text(f"{title}. {snippet}")

    if not text:
        return "إعلان وظيفة محتمل في مجال تحليل البيانات."

    return text[:900]


def serpapi_search(query: str, limit: int = 5) -> list[dict]:
    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        return []

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "hl": "en",
        "gl": "sa",
        "num": limit,
        "tbs": "qdr:m",
    }

    try:
        response = requests.get(SERPAPI_URL, params=params, timeout=25)
        response.raise_for_status()
    except requests.RequestException:
        return []

    data = response.json()
    results = []

    for item in data.get("organic_results", []):
        title = clean_text(item.get("title", ""))
        snippet = clean_text(item.get("snippet", ""))
        raw_url = item.get("link", "")

        if not title or not raw_url:
            continue

        final_url = extract_original_job_url(raw_url)

        if not final_url:
            continue

        if not is_good_result(title, snippet, final_url):
            continue

        company = extract_company(title, final_url, snippet)
        location = estimate_location(title, snippet)

        results.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "description": build_description(title, snippet),
                "url": normalize_url(final_url),
                "source": "SerpApi Google Search",
                "category": "🟢 قدّم الآن",
                "is_real_job": True,
            }
        )

    return results


def deduplicate(items: list[dict]) -> list[dict]:
    unique = {}

    for item in items:
        key = normalize_url(item.get("url", "")) or f'{item.get("title", "")}-{item.get("company", "")}'
        unique[key] = item

    return list(unique.values())


def search_market_opportunities(limit: int = 8) -> list[dict]:
    all_results = []

    for query in SEARCH_QUERIES:
        all_results.extend(serpapi_search(query, limit=5))

        if len(all_results) >= limit * 2:
            break

    unique_results = deduplicate(all_results)

    return unique_results[:limit]


def build_search_engine_status() -> str:
    if os.getenv("SERPAPI_KEY"):
        return "محرك البحث مفعّل: SerpApi."

    return "محرك البحث غير مفعّل: أضف SERPAPI_KEY في GitHub Secrets."
