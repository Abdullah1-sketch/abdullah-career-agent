import os
import re
from urllib.parse import urlparse

import requests


SERPAPI_URL = "https://serpapi.com/search.json"


TARGET_QUERIES = [
    '("Data Analyst" OR "Junior Data Analyst") ("Riyadh" OR "Saudi Arabia") ("0-2" OR "0-3" OR junior OR graduate OR Tamheer)',
    '("BI Analyst" OR "Business Intelligence Analyst" OR "Reporting Analyst") ("Riyadh" OR "Saudi Arabia") (junior OR graduate OR "0-2" OR "0-3")',
    '("HR Analytics Analyst" OR "People Analytics Analyst" OR "Workforce Analytics Analyst") ("Riyadh" OR "Saudi Arabia")',
    '("Business Data Analyst" OR "Analytics Analyst" OR "Insights Analyst") ("Riyadh" OR "Saudi Arabia") (junior OR graduate OR "0-2" OR "0-3")',
    '("محلل بيانات" OR "محلل ذكاء أعمال" OR "محلل تقارير") ("الرياض" OR "السعودية")',
    '("تمهير" OR "برنامج خريجين") ("تحليل بيانات" OR "ذكاء أعمال" OR "Power BI" OR "SQL")',
]

TARGET_TITLE_TERMS = [
    "data analyst",
    "junior data analyst",
    "business data analyst",
    "bi analyst",
    "business intelligence analyst",
    "reporting analyst",
    "analytics analyst",
    "hr analytics analyst",
    "people analytics",
    "workforce analytics",
    "insights analyst",
    "محلل بيانات",
    "محلل ذكاء أعمال",
    "محلل تقارير",
]

ENTRY_LEVEL_TERMS = [
    "junior",
    "graduate",
    "fresh graduate",
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

GOOD_SKILL_TERMS = [
    "excel",
    "power bi",
    "sql",
    "dashboard",
    "reporting",
    "analytics",
    "analysis",
    "business intelligence",
    "kpi",
    "metrics",
    "تحليل",
    "تقارير",
    "لوحات",
    "مؤشرات",
]

TARGET_LOCATIONS = [
    "riyadh",
    "الرياض",
    "qassim",
    "القصيم",
    "dammam",
    "khobar",
    "eastern",
    "السعودية",
    "saudi arabia",
]

BAD_TERMS = [
    "senior",
    "lead",
    "manager",
    "director",
    "principal",
    "5+",
    "7+",
    "10+",
    "data engineer",
    "data scientist",
    "machine learning engineer",
    "مدير",
    "رئيس",
    "خبير",
]

BAD_URL_TERMS = [
    "/blog",
    "/news",
    "/media",
    "/about",
    "/privacy",
    "/terms",
    "/support",
    "/contact",
    "/products",
    "/services",
    "facebook.com",
    "instagram.com",
    "youtube.com",
]

PREFERRED_DOMAINS = [
    "linkedin.com/jobs",
    "careers.",
    "jobs.",
    "greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "workdayjobs.com",
    "oraclecloud.com",
    "successfactors",
    "smartrecruiters.com",
    "myworkdayjobs.com",
    "bayt.com",
    "indeed.com",
    "sa.indeed.com",
]


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def contains_any(text: str, terms: list[str]) -> bool:
    text = text.lower()
    return any(term.lower() in text for term in terms)


def get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except ValueError:
        return ""


def is_bad_result(title: str, snippet: str, url: str) -> bool:
    combined = f"{title} {snippet} {url}".lower()

    if contains_any(combined, BAD_TERMS):
        return True

    if contains_any(url.lower(), BAD_URL_TERMS):
        return True

    return False


def looks_like_job_source(url: str) -> bool:
    url = url.lower()
    return contains_any(url, PREFERRED_DOMAINS)


def score_search_result(title: str, snippet: str, url: str) -> int:
    combined = f"{title} {snippet} {url}".lower()

    score = 0

    if contains_any(combined, TARGET_TITLE_TERMS):
        score += 40

    if contains_any(combined, ENTRY_LEVEL_TERMS):
        score += 20

    if contains_any(combined, GOOD_SKILL_TERMS):
        score += 20

    if contains_any(combined, TARGET_LOCATIONS):
        score += 15

    if looks_like_job_source(url):
        score += 15

    if contains_any(combined, BAD_TERMS):
        score -= 40

    return max(0, min(score, 100))


def infer_location(text: str) -> str:
    text = text.lower()

    if "riyadh" in text or "الرياض" in text:
        return "الرياض"
    if "qassim" in text or "القصيم" in text:
        return "القصيم"
    if any(word in text for word in ["dammam", "khobar", "eastern", "الدمام", "الخبر", "الشرقية"]):
        return "الشرقية"
    if "saudi" in text or "السعودية" in text:
        return "السعودية"

    return "غير مذكورة"


def infer_company(title: str, snippet: str, url: str) -> str:
    domain = get_domain(url)

    known_companies = {
        "stc": "stc (إس تي سي – اتصالات وتقنية)",
        "elm": "Elm (علم – حلول رقمية حكومية)",
        "tamara": "Tamara (تمارا – تقنية مالية)",
        "tabby": "Tabby (تابي – تقنية مالية)",
        "foodics": "Foodics (فودكس – تقنية المطاعم ونقاط البيع)",
        "tahakom": "Tahakom (تحكم – حلول المدن الذكية والسلامة المرورية)",
        "sdaia": "SDAIA (سدايا – البيانات والذكاء الاصطناعي)",
        "moz": "Mozn (مزن – ذكاء اصطناعي ومخاطر مالية)",
    }

    combined = f"{title} {snippet} {domain}".lower()

    for key, company in known_companies.items():
        if key in combined:
            return company

    if domain:
        return domain.replace("www.", "")

    return "غير مذكورة"


def search_serpapi(query: str, limit: int = 5) -> list[dict]:
    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        return []

    params = {
        "engine": "google",
        "q": query,
        "hl": "en",
        "gl": "sa",
        "num": limit,
        "api_key": api_key,
    }

    try:
        response = requests.get(SERPAPI_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return []

    results = []

    for result in data.get("organic_results", []):
        title = clean_text(result.get("title", ""))
        snippet = clean_text(result.get("snippet", ""))
        url = result.get("link", "")

        if not title or not url:
            continue

        if is_bad_result(title, snippet, url):
            continue

        score = score_search_result(title, snippet, url)

        if score < 65:
            continue

        combined = f"{title} {snippet}"

        results.append(
            {
                "title": title,
                "company": infer_company(title, snippet, url),
                "location": infer_location(combined),
                "description": snippet or "فرصة ظهرت من بحث ويب مخصص لمسار تحليل البيانات.",
                "url": url,
                "source": "Web job search",
                "category": "🟢 قدّم الآن" if score >= 75 else "🟡 راقب",
                "is_real_job": True,
                "search_score": score,
            }
        )

    return results


def search_market_opportunities(limit_per_query: int = 5) -> list[dict]:
    all_results = []

    for query in TARGET_QUERIES:
        all_results.extend(search_serpapi(query, limit=limit_per_query))

    unique_results = {}

    for item in all_results:
        url = item.get("url", "")
        if not url:
            continue
        unique_results[url] = item

    sorted_results = sorted(
        unique_results.values(),
        key=lambda item: item.get("search_score", 0),
        reverse=True,
    )

    return sorted_results[:8]


def build_search_engine_status() -> str:
    if os.getenv("SERPAPI_KEY"):
        return "محرك البحث مفعّل."
    return "محرك البحث غير مفعّل: أضف SERPAPI_KEY في GitHub Secrets."
