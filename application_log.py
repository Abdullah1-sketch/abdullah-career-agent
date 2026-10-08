import csv
from datetime import datetime, timezone

from config import MEDIUM_SCORE, STRONG_SCORE
from opportunity_scoring import Opportunity, score_opportunity


APPLICATION_STATUSES = [
    "found",
    "recommended",
    "applied",
    "no_response",
    "rejected",
    "contacted",
    "interview",
]


def build_application_record(opportunity: dict, scoring: dict, interview_path: dict) -> dict:
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "company": opportunity.get("company", ""),
        "title": opportunity.get("title", ""),
        "location": opportunity.get("location", ""),
        "source": opportunity.get("source", ""),
        "url": opportunity.get("url", ""),
        "score": scoring.get("score", 0),
        "priority": scoring.get("priority", "Low"),
        "reasons": scoring.get("reasons", []),
        "interview_path": interview_path.get("path", ""),
        "recommended_actions": interview_path.get("actions", []),
        "status": "found",
        "notes": "",
    }


def update_status(record: dict, status: str, notes: str = "") -> dict:
    if status not in APPLICATION_STATUSES:
        raise ValueError(f"Invalid status: {status}")

    updated = dict(record)
    updated["status"] = status
    updated["updated_at"] = datetime.now(timezone.utc).isoformat()

    if notes:
        updated["notes"] = notes

    return updated


# ---------- Comparing the bot's scores with real replies ----------

RESPONSE_STATUSES = {"interview", "contacted", "مقابلة", "اتصال"}
NO_RESPONSE_STATUSES = {"rejected", "no_response", "رفض", "لا رد"}

STRONG_BAND = f"قدّم الآن ({STRONG_SCORE}+)"
MEDIUM_BAND = f"قدّم سريع ({MEDIUM_SCORE}-{STRONG_SCORE - 1})"
LOW_BAND = f"لا تقدم (<{MEDIUM_SCORE})"


def outcome_of(status: str) -> str:
    status = status.strip().lower()
    if status in RESPONSE_STATUSES:
        return "response"
    if status in NO_RESPONSE_STATUSES:
        return "no_response"
    return "pending"


def score_band(score: int) -> str:
    if score >= STRONG_SCORE:
        return STRONG_BAND
    if score >= MEDIUM_SCORE:
        return MEDIUM_BAND
    return LOW_BAND


def compute_bot_score(row: dict) -> int:
    opportunity = Opportunity(
        title=row.get("title", ""),
        company=row.get("company", ""),
        location=row.get("location", ""),
        description=row.get("description", ""),
        url=row.get("url", ""),
    )
    return score_opportunity(opportunity)["score"]


def load_applications(path: str) -> list[dict]:
    """Read applications.csv. An empty bot_score is filled by scoring the row now."""
    with open(path, encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    records = []
    for row in rows:
        row = {key: (value or "").strip() for key, value in row.items()}
        score_text = row.get("bot_score", "")
        row["bot_score"] = int(score_text) if score_text.isdigit() else compute_bot_score(row)
        records.append(row)
    return records


def summarize_by_band(records: list[dict]) -> dict:
    bands = {band: {"decided": 0, "responses": 0} for band in (STRONG_BAND, MEDIUM_BAND, LOW_BAND)}
    for record in records:
        outcome = outcome_of(record["status"])
        if outcome == "pending":
            continue
        band = bands[score_band(record["bot_score"])]
        band["decided"] += 1
        if outcome == "response":
            band["responses"] += 1
    return bands


def build_score_vs_outcome_report(records: list[dict]) -> str:
    if not records:
        return "ما فيه تقديمات مسجلة بعد. سجّلها في applications.csv."

    pending = sum(1 for record in records if outcome_of(record["status"]) == "pending")
    lines = [f"تقرير التقديمات: {len(records)} تقديم ({pending} بانتظار رد)", ""]

    lines.append("نسبة الرد حسب تقييم البوت:")
    for band, counts in summarize_by_band(records).items():
        decided, responses = counts["decided"], counts["responses"]
        rate = f"{round(100 * responses / decided)}%" if decided else "-"
        lines.append(f"- {band}: {responses} رد من {decided} ({rate})")

    missed = [
        record for record in records
        if outcome_of(record["status"]) == "response" and record["bot_score"] < MEDIUM_SCORE
    ]
    if missed:
        lines += ["", "البوت قال لا تقدم وجاك رد (راجع ليش قيمها منخفض):"]
        lines += [f"- {r['title']} | {r['company']} | {r['bot_score']}/100" for r in missed]

    return "\n".join(lines)
