import os
import re
from urllib.parse import urlparse

import requests


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
]

TARGET_TITLE_TERMS = [
    "data analyst",
    "junior data analyst",
    "business data analyst",
    "bi analyst",
    "business intelligence analyst",
    "reporting analyst",
    "hr analytics analyst",
    "people analytics analyst",
    "workforce analytics analyst",
    "analytics analyst",
    "insights analyst",
    "business analyst",
    "operations analyst",
    "statistician",
    "محلل بيانات",
    "محلل ذكاء أعمال",
    "محلل تقارير",
    "محلل تحليلات",
    "إحصائي",
]

DATA_CONTEXT_TERMS = [
    "data",
    "analytics",
    "analysis",
    "business intelligence",
    "bi",
    "reporting",
    "dashboard",
    "power bi",
    "sql",
    "excel",
    "kpi",
    "metrics",
    "insights",
    "visualization",
    "statistical",
    "statistics",
    "تحليل",
    "بيانات",
    "تقارير",
    "لوحات",
    "مؤشرات",
    "إحصاء",
]

ENTRY_TERMS = [
    "junior",
    "entry level",
    "fresh graduate",
    "graduate",
    "tamheer",
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
    "qassim",
    "القصيم",
    "saudi arabia",
    "ksa",
    "السعودية",
]

BAD_TERMS = [
    "senior",
    "lead",
    "manager",
    "director",
    "principal",
    "head of",
    "5+",
    "6+",
    "7+",
    "8+",
    "10+",
    "data engineer",
    "data scientist",
    "machine learning engineer",
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

BLOCKED_DOMAINS = [
    "jooble.org",
    "indeed.com",
    "bayt.com",
    "naukrigulf.com",
    "glassdoor.com",
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
]


COMPANY_LABELS = {
    "stc": "stc (إس تي سي – اتصالات وتقنية)",
    "sabbar": "Sabbar (صبار – منصة توظيف)",
    "linkedin": "LinkedIn (لينكدإن – منصة وظائف وتواصل مهني)",
}


def contains_any(text: str, terms: list[str]) -> bool:
    text = text.lower()
    return any(term.lower() in text for term in terms)


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_url(url: str) -> str:
    return (url or "").split("?")[0].rstrip("/")


def is_blocked_domain(url: str) -> bool:
    domain = urlparse(url).netloc.lower().replace("www.", "")
    return any(blocked in domain for blocked in BLOCKED_DOMAINS)


def is_direct_job_url(url: str) -> bool:
    lower_url = url.lower()

    if is_blocked_domain(lower_url):
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


def extract_company(title: str, url: str, snippet: str) -> str:
    text = f"{title} {snippet}".lower()
    domain = urlparse(url).netloc.lower().replace("www.", "")

    if "stc" in text or "careers.stc.com.sa" in domain:
        return COMPANY_LABELS["stc"]

    if "sabbar.com" in domain:
        return COMPANY_LABELS["sabbar"]

    if "linkedin.com" in domain:
        return COMPANY_LABELS["linkedin"]

    parts = domain.split(".")
    if parts:
        return parts[0]

    return "غير معروف"


def estimate_location(title: str, snippet: str) -> str:
    text = f"{title} {snippet}".lower()

    if "riyadh" in text or "الرياض" in text:
        return "الرياض"
    if "qassim" in text or "القصيم" in text:
        return "القصيم"
    if "dammam" in text or "khobar" in text or "eastern" in text or "الشرقية" in text:
        return "الشرقية"
    if "saudi" in text or "ksa" in text or "السعودية" in text:
        return "السعودية"

    return "غير مذكورة"


def is_good_result(title: str, snippet: str, url: str) -> bool:
    combined = f"{title} {snippet} {url}".lower()

    if not is_direct_job_url(url):
        return False

    if is_generic_search_result(title, url):
        return False

    if contains_any(combined, BAD_TERMS):
        return False

    has_target_title = contains_any(combined, TARGET_TITLE_TERMS)
    has_data_context = contains_any(combined, DATA_CONTEXT_TERMS)
    has_location = contains_any(combined, LOCATION_TERMS)

    if not has_target_title:
        return False

    if not has_data_context:
        return False

    if not has_location:
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
        url = item.get("link", "")

        if not title or not url:
            continue

        if not is_good_result(title, snippet, url):
            continue

        company = extract_company(title, url, snippet)
        location = estimate_location(title, snippet)

        results.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "description": build_description(title, snippet),
                "url": normalize_url(url),
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
        return (
            "محرك البحث مفعّل: SerpApi.\n"
            "إذا لم تظهر فرصة قوية، فهذا يعني أن الفلتر لم يجد إعلانًا مباشرًا مناسبًا اليوم."
        )

    return "محرك البحث غير مفعّل: أضف SERPAPI_KEY في GitHub Secrets."
