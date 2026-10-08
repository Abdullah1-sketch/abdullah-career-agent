"""How well a job fits Abdullah, from what the posting actually asks for.

The fit score has four parts (role, experience, skills, location) and caps:
a job can't score high when experience is unmet, required tools are missing
or still being learned, the role is finance/another specialty, or the
posting doesn't say what it needs. Reliability of the posting is scored
separately (see job_verification).
"""

from config import (
    ABDULLAH_EXPERIENCE_YEARS,
    ADJACENT_ANALYTICS_TITLES,
    DATA_CONTEXT_SIGNALS,
    ENTRY_LEVEL_SIGNALS,
    FINANCE_TITLE_SIGNALS,
    FIT_CAPS,
    FIT_WEIGHTS,
    LEARNING_SKILL_CREDIT,
    LOCATION_WEIGHTS,
    ROLE_SHARE,
    SPECIALTY_TITLE_SIGNALS,
    TARGET_TITLES,
)
from opportunity_scoring import contains_any

ROLE_LABELS = {
    "data": "تحليل بيانات",
    "adjacent": "قريب من تحليل البيانات",
    "finance": "وظيفة مالية، مو تحليل بيانات",
    "specialty": "تخصص آخر يحتاج مهارات غير البيانات",
    "other": "مو تحليل بيانات",
}


ANALYST_WORDS = ["analyst", "analysis", "analytics", "محلل", "تحليل"]


def role_type(title: str, description: str) -> str:
    title = title.lower()
    is_analyst_role = (
        contains_any(title, ANALYST_WORDS)
        or contains_any(title, TARGET_TITLES)
        or contains_any(title, ADJACENT_ANALYTICS_TITLES)
    )
    if not is_analyst_role:
        return "other"
    if contains_any(title, SPECIALTY_TITLE_SIGNALS):
        return "specialty"
    if contains_any(title, FINANCE_TITLE_SIGNALS):
        return "finance"
    if contains_any(title, TARGET_TITLES):
        return "data"
    if contains_any(title, ADJACENT_ANALYTICS_TITLES):
        return "adjacent"
    if contains_any(title, ["analyst", "محلل"]) and contains_any(description, DATA_CONTEXT_SIGNALS):
        return "adjacent"
    return "other"


def experience_points(years: int | None, says_entry_level: bool) -> int:
    best = FIT_WEIGHTS["experience"]
    if years is None:
        return round(best * (0.88 if says_entry_level else 0.6))
    if years == 0:
        return best
    if years <= ABDULLAH_EXPERIENCE_YEARS:
        return round(best * 0.88)
    return round(best * 0.4)


def skills_points(requirements: dict) -> int:
    asked = len(requirements["have"]) + len(requirements["learning"]) + len(requirements["missing"])
    best = FIT_WEIGHTS["skills"]
    if not asked:
        return round(best * 0.6)
    credit = len(requirements["have"]) + LEARNING_SKILL_CREDIT * len(requirements["learning"])
    return round(best * credit / asked)


def location_points(location: str) -> int:
    best_raw = max(points for _, points, _ in LOCATION_WEIGHTS)
    for terms, points, _ in LOCATION_WEIGHTS:
        if contains_any(location, terms):
            return round(FIT_WEIGHTS["location"] * points / best_raw)
    return 0


def applicable_caps(role: str, years: int | None, requirements: dict) -> list[str]:
    caps = []
    if requirements["missing_platforms"]:
        caps.append("missing_platform")
    if role in ("finance", "specialty", "other"):
        caps.append("role_not_data")
    if years is not None and years > ABDULLAH_EXPERIENCE_YEARS:
        caps.append("experience_unmet")
    if len(requirements["missing"]) > len(requirements["missing_platforms"]):
        caps.append("missing_skill")
    if requirements["learning"]:
        caps.append("learning_skill")
    asked = requirements["have"] or requirements["learning"] or requirements["missing"]
    if years is None or not asked:
        caps.append("unknown_details")
    return caps


def compute_fit(job: dict, years: int | None, requirements: dict) -> dict:
    title, description = job.get("title", ""), job.get("description", "")
    role = role_type(title, description)
    says_entry_level = contains_any(f"{title} {description}", ENTRY_LEVEL_SIGNALS)

    parts = {
        "role": round(FIT_WEIGHTS["role"] * ROLE_SHARE[role]),
        "experience": experience_points(years, says_entry_level),
        "skills": skills_points(requirements),
        "location": location_points(job.get("location", "")),
    }
    caps = applicable_caps(role, years, requirements)
    score = min([sum(parts.values())] + [FIT_CAPS[cap] for cap in caps])

    return {
        "score": score,
        "parts": parts,
        "caps": caps,
        "role": role,
        "experience_unmet": "experience_unmet" in caps,
    }
