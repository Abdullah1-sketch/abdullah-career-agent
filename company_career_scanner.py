import re

import requests
from bs4 import BeautifulSoup

from company_career_links import COMPANY_CAREER_TARGETS


KEYWORDS = [
    "data analyst",
    "junior data analyst",
    "business intelligence",
    "bi analyst",
    "reporting analyst",
    "power bi",
    "sql",
    "محلل بيانات",
    "ذكاء الأعمال",
    "تقارير",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 AbdullahCareerAgent/0.2"
}


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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
    page_text = clean_text(soup.get_text(" ")).lower()

    matched_keywords = [
        keyword for keyword in KEYWORDS if keyword.lower() in page_text
    ]

    if not matched_keywords:
        return []

    return [
        {
            "title": "Potential data-related opening or signal",
            "company": target["company"],
            "location": "Saudi Arabia",
            "description": (
                "Detected career-page signals: "
                + ", ".join(matched_keywords)
                + ". Review the official career page manually."
            ),
            "url": target["career_url"],
            "source": "Company career page scanner",
        }
    ]


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
