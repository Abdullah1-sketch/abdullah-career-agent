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

    has_official_apply = any(
        term in text
        for term in ["careers", "apply", "workday", "greenhouse", "lever", "ashby", "oraclecloud", "تقديم"]
    )
    has_recruiter_signal = any(
        term in text
        for term in ["recruiter", "hiring", "talent acquisition", "linkedin", "توظيف"]
    )
    strong_company_signal = any(
        term in text
        for term in ["analytics", "data team", "business intelligence", "growth", "operations", "finance"]
    )

    actions = []

    if priority == "Strong":
        actions.append("Apply officially as soon as possible")
        if has_recruiter_signal:
            actions.append("Prepare a personalized LinkedIn message")
        if strong_company_signal:
            actions.append("Consider a small company-relevant portfolio angle")
    elif priority == "Medium":
        if has_official_apply:
            actions.append("Apply officially")
        actions.append("Keep in daily report and monitor")
    else:
        actions.append("Do not spend much time unless new signals appear")

    if score >= 80 and has_official_apply and has_recruiter_signal:
        path = "High-effort interview push"
    elif score >= 60:
        path = "Standard application"
    else:
        path = "Monitor only"

    return {
        "path": path,
        "actions": actions,
    }
