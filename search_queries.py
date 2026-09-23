from urllib.parse import quote_plus


SEARCH_QUERIES = [
    {
        "category": "Direct jobs",
        "priority": "high",
        "query": "Data Analyst Saudi Arabia entry level OR junior",
    },
    {
        "category": "Direct jobs",
        "priority": "high",
        "query": "محلل بيانات مبتدئ السعودية",
    },
    {
        "category": "Adjacent titles",
        "priority": "high",
        "query": "BI Analyst OR Reporting Analyst Saudi Arabia entry level",
    },
    {
        "category": "Adjacent titles",
        "priority": "medium",
        "query": "Power BI Analyst Saudi Arabia",
    },
    {
        "category": "Tamheer and training",
        "priority": "high",
        "query": "محلل بيانات تمهير",
    },
    {
        "category": "Tamheer and training",
        "priority": "medium",
        "query": "Data Analyst Tamheer Saudi Arabia",
    },
    {
        "category": "Government and semi-government",
        "priority": "high",
        "query": "محلل بيانات جدارات الرياض",
    },
    {
        "category": "Early signals",
        "priority": "high",
        "query": "نبحث عن محلل بيانات الرياض",
    },
    {
        "category": "Early signals",
        "priority": "high",
        "query": "hiring data analyst Riyadh Saudi Arabia recruiter",
    },
    {
        "category": "Company-targeted",
        "priority": "high",
        "query": "site:greenhouse.io Saudi Data Analyst Riyadh",
    },
    {
        "category": "Company-targeted",
        "priority": "high",
        "query": "site:lever.co Saudi Data Analyst Riyadh",
    },
    {
        "category": "Company-targeted",
        "priority": "high",
        "query": "site:ashbyhq.com Saudi Data Analyst Riyadh",
    },
]


SEARCH_SOURCES = [
    {
        "name": "LinkedIn",
        "url_template": "https://www.linkedin.com/jobs/search/?keywords={query}",
        "best_for": "job listings and recruiter activity",
    },
    {
        "name": "Indeed",
        "url_template": "https://sa.indeed.com/jobs?q={query}",
        "best_for": "public job listings",
    },
    {
        "name": "Google",
        "url_template": "https://www.google.com/search?q={query}",
        "best_for": "company career pages and ATS boards",
    },
    {
        "name": "X Search",
        "url_template": "https://x.com/search?q={query}&src=typed_query&f=live",
        "best_for": "early hiring posts and recruiter signals",
    },
]


def build_search_links(priority: str | None = None) -> list[dict]:
    links = []

    queries = SEARCH_QUERIES
    if priority:
        queries = [query for query in SEARCH_QUERIES if query["priority"] == priority]

    for query in queries:
        encoded_query = quote_plus(query["query"])

        for source in SEARCH_SOURCES:
            links.append(
                {
                    "category": query["category"],
                    "priority": query["priority"],
                    "query": query["query"],
                    "source": source["name"],
                    "best_for": source["best_for"],
                    "url": source["url_template"].format(query=encoded_query),
                }
            )

    return links


def build_search_links_summary(limit: int = 12) -> str:
    links = build_search_links(priority="high")[:limit]

    lines = []
    for link in links:
        lines.append(
            f'- [{link["category"]}] {link["source"]}: {link["query"]}\n  {link["url"]}'
        )

    return "\n".join(lines)
