"""Find jobs with SerpApi's Google Jobs engine.

Google Jobs returns real postings (title, company, location, full
description, apply links), so no web pages are scraped. Each search costs
one SerpApi credit and returns up to 10 jobs.
"""

import os
from collections import Counter
from datetime import date
from urllib.parse import urlparse

import requests

from config import BAD_TITLE_SIGNALS, SEARCHES_PER_RUN
from opportunity_scoring import (
    contains_any,
    has_high_experience,
    is_hris_heavy_role,
    is_process_only_business_role,
    is_stale_posting,
)


SERPAPI_URL = "https://serpapi.com/search.json"

# Google Jobs searches inside Saudi Arabia; the city goes in the query.
SEARCH_LOCATION = "Saudi Arabia"

SEARCH_QUERIES = [
    "Data Analyst Riyadh",
    "Junior Data Analyst Saudi Arabia",
    "Data Analyst Dammam",
    "Data Analyst Khobar",
    "BI Analyst Riyadh",
    "Power BI Analyst Saudi Arabia",
    "Reporting Analyst Riyadh",
    "Data Analyst Qassim Buraydah",
    "Graduate Development Program data Saudi Arabia",
    "Fresh graduate data analyst Saudi Arabia",
    "محلل بيانات",
    "Business Intelligence Analyst Eastern Province",
    "Tamheer data analysis",
    "Data Analyst intern Riyadh",
    "Business Analyst Power BI Riyadh",
    "Operations Analyst Riyadh",
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
    "buraydah",
    "unaizah",
    "القصيم",
    "بريدة",
    "عنيزة",
    "saudi arabia",
    "ksa",
    "السعودية",
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


REJECT_SENIOR_TITLE = "مسمى أعلى من مستواك"
REJECT_OLD = "قديمة أو مغلقة"
REJECT_HIGH_EXPERIENCE = "تطلب خبرة 3+"
REJECT_NOT_DATA = "مو تحليل بيانات"
REJECT_LOCATION = "خارج السعودية"
REJECT_HR_SYSTEMS = "أنظمة موارد بشرية"
REJECT_PROCESS_ONLY = "توثيق عمليات بدون بيانات"

# Error text SerpApi returns when a query simply has no jobs (not a problem).
NO_RESULTS_ERROR = "hasn't returned any results"


# ---------- Turning a Google Jobs result into an opportunity ----------

def get_domain(url: str) -> str:
    return urlparse(url).netloc.lower().replace("www.", "")


def is_aggregator_url(url: str) -> bool:
    domain = get_domain(url)
    return any(blocked in domain for blocked in AGGREGATOR_DOMAINS)


def choose_apply_link(job: dict) -> str:
    """Company site first, then LinkedIn, then job boards, then the Google listing."""
    links = [option.get("link", "") for option in job.get("apply_options", []) if option.get("link")]

    company_sites = [link for link in links if not is_aggregator_url(link) and "linkedin.com" not in link]
    linkedin = [link for link in links if "linkedin.com" in link]

    for group in (company_sites, linkedin, links):
        if group:
            return group[0]
    return job.get("share_link", "")


def to_opportunity(job: dict) -> dict:
    description = job.get("description", "")
    posted_at = job.get("detected_extensions", {}).get("posted_at")
    if posted_at:
        description = f"Posted {posted_at}. {description}"

    return {
        "title": job.get("title", ""),
        "company": job.get("company_name", ""),
        "location": job.get("location", ""),
        "description": description,
        "url": choose_apply_link(job),
        "source": f"Google Jobs (via {job.get('via', '').replace('via ', '')})",
        "is_real_job": True,
    }


def job_rejection_reason(opportunity: dict) -> str | None:
    """Why a job is not worth showing, or None if it is. Same rules as the scorer."""
    title = opportunity["title"]
    text = f"{title} {opportunity['location']} {opportunity['description']}".lower()

    if contains_any(title, BAD_TITLE_SIGNALS):
        return REJECT_SENIOR_TITLE
    if is_stale_posting(text):
        return REJECT_OLD
    if has_high_experience(text):
        return REJECT_HIGH_EXPERIENCE
    if not (contains_any(text, TARGET_TITLE_TERMS) and contains_any(text, DATA_CONTEXT_TERMS)):
        return REJECT_NOT_DATA
    if not contains_any(opportunity["location"], LOCATION_TERMS):
        return REJECT_LOCATION
    if is_hris_heavy_role(title, text):
        return REJECT_HR_SYSTEMS
    if is_process_only_business_role(title, text):
        return REJECT_PROCESS_ONLY
    return None


# ---------- What happened in the last run (shown in the daily message) ----------

SEARCH_PROBLEMS: list[str] = []
SEARCH_STATS: Counter = Counter()  # "found", "kept", "rejected:<reason>"
SEARCH_LOG: list[str] = []


def record_search_problem(problem: str) -> None:
    if problem not in SEARCH_PROBLEMS:
        SEARCH_PROBLEMS.append(problem)


def get_search_problems() -> list[str]:
    return list(SEARCH_PROBLEMS)


def get_search_stats() -> dict:
    rejected = {
        key.split(":", 1)[1]: count
        for key, count in SEARCH_STATS.items()
        if key.startswith("rejected:")
    }
    return {"found": SEARCH_STATS["found"], "kept": SEARCH_STATS["kept"], "rejected": rejected}


def log_result(decision: str, title: str, company: str, url: str) -> None:
    line = f"{decision} | {title} | {company} | {url}"
    SEARCH_LOG.append(line)
    print(f"[search] {line}")


def publish_search_log_notice() -> None:
    """Put all result lines in one GitHub Actions notice (readable through the API)."""
    if os.getenv("GITHUB_ACTIONS") != "true" or not SEARCH_LOG:
        return
    text = "\n".join(SEARCH_LOG)
    escaped = text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    print(f"::notice title=Search results::{escaped}")


# ---------- Searching ----------

def fetch_google_jobs(query: str, api_key: str) -> list[dict]:
    params = {
        "engine": "google_jobs",
        "q": query,
        "location": SEARCH_LOCATION,
        "gl": "sa",
        "hl": "en",
        "api_key": api_key,
    }

    try:
        response = requests.get(SERPAPI_URL, params=params, timeout=40)
    except requests.RequestException as error:
        reason = str(error).replace(api_key, "***")[:150]
        record_search_problem(f"تعذر الاتصال بـ SerpApi ({type(error).__name__}: {reason}).")
        return []

    try:
        data = response.json()
    except ValueError:
        record_search_problem(f"رد SerpApi غير مفهوم (HTTP {response.status_code}).")
        return []

    error = data.get("error")
    if error:
        if NO_RESULTS_ERROR not in error:
            record_search_problem(f"SerpApi: {error}")
        return []

    return data.get("jobs_results", [])


def search_jobs(query: str, api_key: str) -> list[dict]:
    kept = []
    for job in fetch_google_jobs(query, api_key):
        SEARCH_STATS["found"] += 1
        opportunity = to_opportunity(job)
        reason = job_rejection_reason(opportunity)
        if reason:
            SEARCH_STATS[f"rejected:{reason}"] += 1
            log_result(reason, opportunity["title"], opportunity["company"], opportunity["url"])
            continue
        SEARCH_STATS["kept"] += 1
        log_result("kept", opportunity["title"], opportunity["company"], opportunity["url"])
        kept.append(opportunity)
    return kept


def deduplicate(items: list[dict]) -> list[dict]:
    """The same job often appears in several searches; keep it once."""
    unique = {}
    for item in items:
        key = (item["title"].lower().strip(), item["company"].lower().strip())
        unique.setdefault(key, item)
    return list(unique.values())


def choose_queries_for_day(day_number: int, per_run: int) -> list[str]:
    """Rotate through the queries so each day searches a different slice.

    Keeps paid search usage at `per_run` searches a day while still covering
    every query every few days.
    """
    start = (day_number * per_run) % len(SEARCH_QUERIES)
    rotated = SEARCH_QUERIES[start:] + SEARCH_QUERIES[:start]
    return rotated[:per_run]


def search_market_opportunities(limit: int = 15) -> list[dict]:
    SEARCH_PROBLEMS.clear()
    SEARCH_STATS.clear()
    SEARCH_LOG.clear()

    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        record_search_problem("البحث في Google متوقف: مفتاح SERPAPI_KEY غير موجود في GitHub Secrets.")
        return []

    all_results = []
    for query in choose_queries_for_day(date.today().toordinal(), SEARCHES_PER_RUN):
        print(f"[search] query: {query}")
        SEARCH_LOG.append(f"QUERY: {query}")
        all_results.extend(search_jobs(query, api_key))

    publish_search_log_notice()
    return deduplicate(all_results)[:limit]


def build_search_engine_status() -> str:
    if os.getenv("SERPAPI_KEY"):
        return "محرك البحث مفعّل: SerpApi Google Jobs."

    return "محرك البحث غير مفعّل: أضف SERPAPI_KEY في GitHub Secrets."
