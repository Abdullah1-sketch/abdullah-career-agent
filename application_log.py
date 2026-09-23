from datetime import datetime, timezone


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
