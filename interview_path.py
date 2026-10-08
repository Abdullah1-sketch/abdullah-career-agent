from config import MEDIUM_SCORE, STRONG_SCORE, WATCH_SCORE


AGGREGATOR_DOMAINS = [
    "jooble.org",
    "indeed.com",
    "bayt.com",
    "naukrigulf.com",
    "glassdoor.com",
    "bebee.com",
    "trabajo.org",
    "learn4good.com",
]

FAST_APPLY_SIGNALS = [
    "3+ years",
    "minimum 3 years",
    "minimum of 3 years",
    "at least 3 years",
    "3 years of experience",
    "three years of experience",
    "٣ سنوات",
    "ثلاث سنوات",
]

OFFICIAL_APPLY_SIGNALS = [
    "careers",
    "apply",
    "workday",
    "greenhouse",
    "lever",
    "ashby",
    "oraclecloud",
    "successfactors",
    "smartrecruiters",
    "careers-page",
    "linkedin.com/jobs/view",
    "sabbar.com",
    "تقديم",
]

RECRUITER_SIGNALS = [
    "recruiter",
    "hiring",
    "talent acquisition",
    "linkedin",
    "توظيف",
]

PORTFOLIO_SIGNALS = [
    "analytics",
    "data team",
    "business intelligence",
    "growth",
    "operations",
    "finance",
    "dashboard",
    "power bi",
    "reporting",
]


def contains_any(text: str, terms: list[str]) -> bool:
    text = text.lower()
    return any(term.lower() in text for term in terms)


def is_aggregator_link(text: str) -> bool:
    return contains_any(text, AGGREGATOR_DOMAINS)


def recommend_interview_path(opportunity: dict, scoring: dict) -> dict:
    text = " ".join(
        [
            opportunity.get("title", ""),
            opportunity.get("company", ""),
            opportunity.get("location", ""),
            opportunity.get("description", ""),
            opportunity.get("url", ""),
        ]
    ).lower()

    score = scoring.get("score", 0)
    priority = scoring.get("priority", "Low")

    has_official_apply = contains_any(text, OFFICIAL_APPLY_SIGNALS)
    has_recruiter_signal = contains_any(text, RECRUITER_SIGNALS)
    has_portfolio_signal = contains_any(text, PORTFOLIO_SIGNALS)
    has_fast_apply_signal = contains_any(text, FAST_APPLY_SIGNALS)
    is_aggregator = is_aggregator_link(text)

    actions = []

    if score >= MEDIUM_SCORE and is_aggregator:
        actions.append("Find the original posting on the company site and apply there")
        actions.append("Apply on the job board if the company site has no posting")

        path = "Find original posting"

    elif score >= STRONG_SCORE and not is_aggregator:
        actions.append("Apply officially as soon as possible")
        actions.append("Prepare a personalized LinkedIn message")

        if has_portfolio_signal:
            actions.append("Consider a small company-relevant portfolio angle")

        path = "High-effort interview push"

    elif score >= MEDIUM_SCORE and not is_aggregator:
        actions.append("Apply officially")

        if has_fast_apply_signal:
            actions.append("Fast apply only, do not customize heavily")
        elif has_recruiter_signal:
            actions.append("Prepare a short LinkedIn message")

        path = "Standard application"

    elif score >= WATCH_SCORE and has_official_apply and not is_aggregator:
        actions.append("Fast apply if it takes less than 5 minutes")
        actions.append("Do not customize heavily")

        path = "Fast application"

    else:
        actions.append("Do not spend much time unless new signals appear")

        path = "Monitor only"

    return {
        "path": path,
        "actions": actions,
    }
