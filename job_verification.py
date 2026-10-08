"""Check a job against its original posting before recommending it.

For each job the bot tries to open the employer's own posting (company site
or hiring system), then checks:
- source: employer posting, LinkedIn, job board (repost) or unknown site
- status: open, closed or unknown
- experience: minimum years asked for
- requirements: skills Abdullah has, is learning, or is missing

LinkedIn pages are not opened (LinkedIn doesn't allow automated access), so
a LinkedIn-only job stays "not verified" and the message says to check it.
"""

import re
from datetime import date, datetime
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

from config import (
    ABDULLAH_HAS_SKILLS,
    APPLY_OPEN_SIGNALS,
    FRESH_LINKEDIN_DAYS,
    MAX_LINK_DATE_AGE_DAYS,
    MAX_UNCONFIRMED_POSTING_AGE_DAYS,
    ABDULLAH_LEARNING_SKILLS,
    ATS_DOMAINS,
    JOB_BOARD_DOMAINS,
    MIN_PAGE_TEXT_LENGTH,
    PLATFORM_SKILLS,
    SKILL_TERMS,
)
from opportunity_scoring import ARABIC_DIGITS, contains_any, is_stale_posting, required_experience_years


HEADERS = {"User-Agent": "Mozilla/5.0 AbdullahCareerAgent/2.0"}

# Words in company names that don't identify the company in a web address.
GENERIC_COMPANY_WORDS = {
    "company", "group", "holding", "inc", "ltd", "llc", "co", "the", "and",
    "saudi", "arabia", "ksa", "international", "services", "solutions",
}

SOURCE_ORDER = ["company", "job_board", "unknown", "linkedin"]


# ---------- Where a link points ----------

def get_domain(url: str) -> str:
    return urlparse(url).netloc.lower().replace("www.", "")


def company_matches_domain(company: str, domain: str) -> bool:
    words = [word for word in re.findall(r"[a-z0-9]+", company.lower()) if word not in GENERIC_COMPANY_WORDS]
    if not words:
        return False
    plain_domain = domain.replace("-", "")
    if "".join(words) in plain_domain:
        return True
    return any(len(word) >= 4 and word in plain_domain for word in words)


def classify_source(url: str, company: str) -> str:
    domain = get_domain(url)
    if "linkedin.com" in domain:
        return "linkedin"
    if any(board in domain for board in JOB_BOARD_DOMAINS):
        return "job_board"
    if any(ats in domain for ats in ATS_DOMAINS) or company_matches_domain(company, domain):
        return "company"
    return "unknown"


# ---------- Reading pages ----------

def fetch_page(url: str) -> tuple[str, list[str]]:
    """Visible text and absolute links of a page, or ("", []) if it can't be opened."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException:
        return "", []

    soup = BeautifulSoup(response.text, "html.parser")
    text = re.sub(r"\s+", " ", soup.get_text(" ")).strip()
    links = [urljoin(url, anchor["href"]) for anchor in soup.find_all("a", href=True)]
    return text, links


def has_content(text: str) -> bool:
    return len(text) >= MIN_PAGE_TEXT_LENGTH


def find_employer_posting(links: list[str], company: str) -> tuple[str, str]:
    """Open the first employer posting among `links`. Returns (url, text) or ("", "")."""
    for link in links:
        if classify_source(link, company) != "company":
            continue
        text, _ = fetch_page(link)
        if has_content(text):
            return link, text
    return "", ""


# ---------- Requirements ----------

def analyze_requirements(text: str) -> dict:
    asked = [skill for skill, terms in SKILL_TERMS.items() if contains_any(text, terms)]
    missing = [skill for skill in asked if skill not in ABDULLAH_HAS_SKILLS + ABDULLAH_LEARNING_SKILLS]
    return {
        "have": [skill for skill in asked if skill in ABDULLAH_HAS_SKILLS],
        "learning": [skill for skill in asked if skill in ABDULLAH_LEARNING_SKILLS],
        "missing": missing,
        "missing_platforms": [skill for skill in missing if skill in PLATFORM_SKILLS],
    }


# ---------- Verification ----------

def verify_job(job: dict) -> dict:
    company = job.get("company", "")
    links = job.get("apply_links") or [job.get("url", "")]
    links = sorted(links, key=lambda link: SOURCE_ORDER.index(classify_source(link, company)))

    source, source_url, page_text = "", "", ""

    # 1. The employer's own posting among the apply links.
    source_url, page_text = find_employer_posting(links, company)
    if source_url:
        source = "company"

    # 2. A job board page that links to the employer's posting.
    if not source:
        for link in links:
            if classify_source(link, company) not in ("job_board", "unknown"):
                continue
            board_text, board_links = fetch_page(link)
            employer_url, employer_text = find_employer_posting(board_links, company)
            if employer_url:
                source, source_url, page_text = "company", employer_url, employer_text
                break
            if has_content(board_text) and not source:
                source, source_url, page_text = classify_source(link, company), link, board_text

    # 3. Nothing could be opened: keep the best link we have.
    if not source:
        source_url = links[0] if links else ""
        source = classify_source(source_url, company) if source_url else "unknown"

    all_text = f"{job.get('description', '')} {page_text}"
    read_employer_page = source == "company" and has_content(page_text)

    if is_stale_posting(all_text):
        status = "closed"
    elif read_employer_page and contains_any(page_text, APPLY_OPEN_SIGNALS):
        status = "open_confirmed"
    elif read_employer_page:
        status = "page_seen"
    else:
        status = "unknown"

    return {
        "source": source,
        "source_url": source_url,
        "status": status,
        "verified": status == "open_confirmed",
        "checked_at": datetime.now(ZoneInfo("Asia/Riyadh")).strftime("%Y-%m-%d %H:%M"),
        "experience_years": required_experience_years(all_text),
        "requirements": analyze_requirements(all_text),
    }


# ---------- Dates ----------

ENGLISH_AGE_PATTERN = re.compile(r"(\d+|an|a|one)\+?\s*(hour|day|week|month|year)s?\s+ago")
ARABIC_AGE_PATTERN = re.compile(
    r"منذ\s+(\d+)?\s*(ساعات|ساعة|يومين|أيام|يوم|أسبوعين|أسابيع|أسبوع|شهرين|أشهر|شهور|شهر|سنتين|سنوات|سنة)"
)
UNIT_DAYS = {"hour": 0, "day": 1, "week": 7, "month": 30, "year": 365}
ARABIC_UNIT_DAYS = {
    "ساعة": 0, "ساعات": 0, "يوم": 1, "أيام": 1, "أسبوع": 7, "أسابيع": 7,
    "شهر": 30, "أشهر": 30, "شهور": 30, "سنة": 365, "سنوات": 365,
}
ARABIC_DUAL_DAYS = {"يومين": 2, "أسبوعين": 14, "شهرين": 60, "سنتين": 730}
LINK_DATE_PATTERN = re.compile(r"(?<!\d)(20\d{2})[-_/]?(0[1-9]|1[0-2])[-_/]?(0[1-9]|[12]\d|3[01])(?!\d)")


def posted_age_days(text: str) -> int | None:
    """Days since posting from text like "3 days ago", "30+ days ago" or "منذ 5 أيام"."""
    text = (text or "").lower().translate(ARABIC_DIGITS)

    match = ENGLISH_AGE_PATTERN.search(text)
    if match:
        count = 1 if match.group(1) in ("an", "a", "one") else int(match.group(1))
        return count * UNIT_DAYS[match.group(2)]

    match = ARABIC_AGE_PATTERN.search(text)
    if match:
        number, unit = match.group(1), match.group(2)
        if unit in ARABIC_DUAL_DAYS:
            return ARABIC_DUAL_DAYS[unit]
        return (int(number) if number else 1) * ARABIC_UNIT_DAYS[unit]

    return None


def link_date_age_days(url: str, today: date | None = None) -> int | None:
    """Age of a date written inside a link, e.g. ".../accenture-analyst-20250221"."""
    today = today or date.today()
    for year, month, day in LINK_DATE_PATTERN.findall(url):
        try:
            found = date(int(year), int(month), int(day))
        except ValueError:
            continue
        if found <= today:
            return (today - found).days
    return None


def is_old_and_unconfirmed(result: dict, posted_days: int | None, link_days: int | None) -> bool:
    if result["status"] == "open_confirmed":
        return False
    too_old_posting = posted_days is not None and posted_days >= MAX_UNCONFIRMED_POSTING_AGE_DAYS
    too_old_link = link_days is not None and link_days > MAX_LINK_DATE_AGE_DAYS
    return too_old_posting or too_old_link


# ---------- Reliability ----------

def reliability(result: dict, posted_days: int | None) -> tuple[str, str]:
    """(level, reason): how sure we are the posting is real, current and open."""
    source, status = result["source"], result["status"]
    if source == "company" and status == "open_confirmed":
        return "high", "إعلان الشركة الأصلي وفيه زر تقديم"
    if source == "company" and status == "page_seen":
        return "medium", "صفحة الشركة موجودة، بس ما تأكدت إن التقديم مفتوح"
    if source == "linkedin" and posted_days is not None and posted_days <= FRESH_LINKEDIN_DAYS:
        return "medium", "إعلان LinkedIn حديث، ما أقدر أفتحه وأتأكد"
    if source == "linkedin":
        return "low", "إعلان LinkedIn بدون تاريخ واضح، ما أقدر أفتحه"
    if source == "job_board":
        return "low", "منشور في موقع تجميع وما لقيت إعلان الشركة"
    if source == "company":
        return "low", "صفحة الشركة ما انفتحت"
    return "low", "مصدر غير معروف"
