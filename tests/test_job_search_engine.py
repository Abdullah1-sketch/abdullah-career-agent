import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import job_search_engine as engine
from config import SEARCHES_PER_RUN


def google_job(
    title="Junior Data Analyst",
    company="Riyadh Pay",
    location="Riyadh Saudi Arabia",
    description="Build Excel and Power BI dashboards. 0-2 years of experience.",
    apply_links=("https://boards.greenhouse.io/riyadhpay/jobs/1",),
    posted="3 days ago",
):
    return {
        "title": title,
        "company_name": company,
        "location": location,
        "description": description,
        "via": "LinkedIn",
        "detected_extensions": {"posted_at": posted} if posted else {},
        "apply_options": [{"title": "Apply", "link": link} for link in apply_links],
        "share_link": "https://www.google.com/search?ibp=htl;jobs#job1",
    }


class FakeResponse:
    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data


def run_search(data=None, env=None, get=None):
    """Run the daily search with a fake SerpApi. Returns (results, request params, printed output)."""
    captured = []

    def fake_get(url, params=None, timeout=None):
        captured.append(params)
        return FakeResponse(data or {"jobs_results": []})

    output = io.StringIO()
    with patch.dict("os.environ", env if env is not None else {"SERPAPI_KEY": "test-key"}, clear=True), \
            patch.object(engine.requests, "get", get or fake_get), redirect_stdout(output):
        results = engine.search_market_opportunities()
    return results, captured, output.getvalue()


class GoogleJobsRequestTests(unittest.TestCase):
    def test_uses_google_jobs_in_saudi_arabia(self):
        _, captured, _ = run_search()
        self.assertEqual(len(captured), SEARCHES_PER_RUN)
        for params in captured:
            self.assertEqual(params["engine"], "google_jobs")
            self.assertEqual(params["gl"], "sa")
            self.assertEqual(params["location"], "Saudi Arabia")
            self.assertIn(params["q"], engine.SEARCH_QUERIES)


class JobConversionTests(unittest.TestCase):
    def test_job_fields_are_kept(self):
        job = engine.to_opportunity(google_job())
        self.assertEqual(job["title"], "Junior Data Analyst")
        self.assertEqual(job["company"], "Riyadh Pay")
        self.assertEqual(job["location"], "Riyadh Saudi Arabia")
        self.assertIn("Power BI", job["description"])
        self.assertIn("Posted 3 days ago", job["description"])

    def test_all_apply_links_are_kept_for_verification(self):
        links = ("https://www.bayt.com/en/saudi-arabia/jobs/data-analyst-1/", "https://careers.riyadhpay.sa/jobs/1")
        job = engine.to_opportunity(google_job(apply_links=links))
        self.assertEqual(job["apply_links"], list(links))

    def test_company_site_link_is_preferred(self):
        job = engine.to_opportunity(google_job(apply_links=(
            "https://www.bayt.com/en/saudi-arabia/jobs/data-analyst-1/",
            "https://www.linkedin.com/jobs/view/4012345678",
            "https://careers.riyadhpay.sa/jobs/1",
        )))
        self.assertEqual(job["url"], "https://careers.riyadhpay.sa/jobs/1")

    def test_linkedin_is_preferred_over_job_boards(self):
        job = engine.to_opportunity(google_job(apply_links=(
            "https://www.bayt.com/en/saudi-arabia/jobs/data-analyst-1/",
            "https://www.linkedin.com/jobs/view/4012345678",
        )))
        self.assertEqual(job["url"], "https://www.linkedin.com/jobs/view/4012345678")

    def test_google_link_when_no_apply_option(self):
        job = engine.to_opportunity(google_job(apply_links=()))
        self.assertEqual(job["url"], "https://www.google.com/search?ibp=htl;jobs#job1")


class RejectionReasonTests(unittest.TestCase):
    def reason(self, **kwargs):
        return engine.job_rejection_reason(engine.to_opportunity(google_job(**kwargs)))

    def test_good_junior_job_is_kept(self):
        self.assertIsNone(self.reason())

    def test_reasons_are_specific(self):
        self.assertEqual(self.reason(title="Senior Data Analyst"), engine.REJECT_SENIOR_TITLE)
        self.assertEqual(self.reason(description="Excel reporting. 3+ years of experience."),
                         engine.REJECT_HIGH_EXPERIENCE)
        self.assertEqual(self.reason(title="Sales Executive", description="Meet sales targets."),
                         engine.REJECT_NOT_DATA)
        self.assertEqual(self.reason(location="Dubai - United Arab Emirates"), engine.REJECT_LOCATION)
        self.assertEqual(self.reason(posted="2 months ago"), engine.REJECT_OLD)

    def test_real_junior_titles_from_google_jobs_are_kept(self):
        for title in ["Data Analysis - Tamheer", "Junior MIS & Dashboards Analyst", "Data & AI Analyst"]:
            with self.subTest(title):
                self.assertIsNone(self.reason(title=title, description="Excel and Power BI dashboards and reports."))

    def test_manager_in_description_is_fine(self):
        self.assertIsNone(self.reason(description="Excel and Power BI reports for the finance manager."))


class SearchRunTests(unittest.TestCase):
    def test_counts_found_kept_and_rejected(self):
        data = {"jobs_results": [google_job(), google_job(title="Senior Data Analyst")]}
        results, _, _ = run_search(data)
        stats = engine.get_search_stats()
        self.assertEqual(stats["found"], 2 * SEARCHES_PER_RUN)
        self.assertEqual(stats["kept"], SEARCHES_PER_RUN)
        self.assertEqual(stats["rejected"], {engine.REJECT_SENIOR_TITLE: SEARCHES_PER_RUN})
        self.assertEqual(len(results), 1)  # same job from every query is kept once

    def test_github_actions_gets_one_notice_with_all_results(self):
        data = {"jobs_results": [google_job()]}
        _, _, output = run_search(data, env={"SERPAPI_KEY": "k", "GITHUB_ACTIONS": "true"})
        notices = [line for line in output.splitlines() if line.startswith("::notice")]
        self.assertEqual(len(notices), 1)
        self.assertIn("Junior Data Analyst", notices[0])


class SearchProblemTests(unittest.TestCase):
    def test_missing_key_is_reported(self):
        run_search(env={})
        self.assertTrue(any("SERPAPI_KEY" in problem for problem in engine.get_search_problems()))

    def test_serpapi_error_is_reported(self):
        run_search({"error": "Your account has run out of searches."})
        self.assertIn("SerpApi: Your account has run out of searches.", engine.get_search_problems())

    def test_no_jobs_reply_is_not_a_problem(self):
        run_search({"error": "Google hasn't returned any results for this query."})
        self.assertEqual(engine.get_search_problems(), [])

    def test_timeout_reason_is_reported_without_the_key(self):
        def raise_timeout(*args, **kwargs):
            raise engine.requests.Timeout("Read timed out: https://serpapi.com/search.json?api_key=test-key")

        run_search(get=raise_timeout)
        problems = " ".join(engine.get_search_problems())
        self.assertIn("Timeout", problems)
        self.assertNotIn("test-key", problems)

    def test_non_json_reply_reports_status_code(self):
        class HtmlResponse:
            status_code = 502

            def json(self):
                raise ValueError("not json")

        run_search(get=lambda *args, **kwargs: HtmlResponse())
        self.assertIn("502", " ".join(engine.get_search_problems()))


class QueryPlanTests(unittest.TestCase):
    def test_each_run_uses_a_limited_number_of_queries(self):
        self.assertEqual(len(engine.choose_queries_for_day(day_number=1, per_run=6)), 6)

    def test_rotation_covers_every_query_within_a_few_days(self):
        per_run = 6
        days_needed = -(-len(engine.SEARCH_QUERIES) // per_run)
        used = set()
        for day in range(days_needed):
            used.update(engine.choose_queries_for_day(day_number=day, per_run=per_run))
        self.assertEqual(used, set(engine.SEARCH_QUERIES))

    def test_queries_cover_priority_regions_and_graduate_programs(self):
        all_queries = " ".join(engine.SEARCH_QUERIES).lower()
        for term in ["riyadh", "dammam", "khobar", "qassim", "graduate", "tamheer", "محلل بيانات"]:
            self.assertIn(term, all_queries)


if __name__ == "__main__":
    unittest.main()
