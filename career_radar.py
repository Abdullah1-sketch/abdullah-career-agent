from opportunity_scoring import Opportunity, score_opportunity
from interview_path import recommend_interview_path
from application_log import build_application_record
from sources import SOURCES


def build_daily_radar_message() -> str:
    sample_opportunity = {
        "title": "Junior Data Analyst",
        "company": "Example Saudi Company",
        "location": "Riyadh, Saudi Arabia",
        "description": "Entry level role requiring Excel, Power BI, SQL, dashboards, and reporting.",
        "url": "https://example.com/careers/apply",
        "source": "System sample",
    }

    opportunity = Opportunity(
        title=sample_opportunity["title"],
        company=sample_opportunity["company"],
        location=sample_opportunity["location"],
        description=sample_opportunity["description"],
        url=sample_opportunity["url"],
    )

    scoring = score_opportunity(opportunity)
    interview_path = recommend_interview_path(sample_opportunity, scoring)
    record = build_application_record(sample_opportunity, scoring, interview_path)

    high_priority_sources = [
        source["name"] for source in SOURCES if source["priority"] == "high"
    ]

    return f"""Abdullah Career Agent - Daily Career Radar

System status: Working

Sample opportunity:
{record["title"]} - {record["company"]}
Location: {record["location"]}
Score: {record["score"]}/100
Priority: {record["priority"]}

Why:
{chr(10).join("- " + reason for reason in record["reasons"])}

Best path:
{record["interview_path"]}

Actions:
{chr(10).join("- " + action for action in record["recommended_actions"])}

High-priority sources:
{chr(10).join("- " + source for source in high_priority_sources)}

Next build step:
Connect real opportunity sources and remove the sample opportunity.
"""
