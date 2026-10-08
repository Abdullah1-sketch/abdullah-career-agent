import unittest
from unittest.mock import patch

import job_search_engine as engine

LINKEDIN_URL = "https://www.linkedin.com/jobs/view/4012345678"


def check_result(title, snippet, page_text, url=LINKEDIN_URL):
    with patch.object(engine, "fetch_page_text", return_value=page_text.lower()):
        return engine.is_good_result(title, snippet, url)


class ResultFilterTests(unittest.TestCase):
    """The search filter must use the same rules as the scorer."""

    def test_junior_job_page_mentioning_senior_jobs_elsewhere_is_kept(self):
        page = (
            "Junior Data Analyst. Riyadh. 0-2 years of experience. Excel, Power BI. "
            "You will report to the analytics manager. "
            "Similar jobs: Senior Data Analyst, Lead BI Developer"
        )
        self.assertTrue(check_result("Junior Data Analyst", "Riyadh, Saudi Arabia. Excel and Power BI.", page))

    def test_one_to_three_years_is_kept(self):
        page = "Data Analyst. Riyadh. 1-3 years of experience in data analysis. Excel, Power BI."
        self.assertTrue(check_result("Data Analyst", "Riyadh, Saudi Arabia. Data analysis.", page))

    def test_three_plus_years_is_dropped(self):
        page = "Data Analyst. Riyadh. 3+ years of experience in data analysis."
        self.assertFalse(check_result("Data Analyst", "Riyadh, Saudi Arabia. Data analysis.", page))

    def test_senior_title_is_dropped(self):
        self.assertFalse(check_result("Senior Data Analyst", "Riyadh, Saudi Arabia. Data analysis.", ""))

    def test_old_jobs_in_similar_jobs_section_do_not_make_it_stale(self):
        page = "Data Analyst. Riyadh. Excel reporting. Similar jobs: BI Analyst, posted 3 months ago"
        self.assertTrue(check_result("Data Analyst", "Riyadh, Saudi Arabia. 1 week ago. Excel.", page))

    def test_closed_job_page_is_dropped(self):
        page = "Data Analyst. Riyadh. No longer accepting applications."
        self.assertFalse(check_result("Data Analyst", "Riyadh, Saudi Arabia. Excel reporting.", page))

    def test_rejection_reasons_are_specific(self):
        with patch.object(engine, "fetch_page_text", return_value=""):
            reason = engine.result_rejection_reason
            self.assertEqual(reason("Senior Data Analyst", "Riyadh. Data.", LINKEDIN_URL), engine.REJECT_SENIOR_TITLE)
            self.assertEqual(reason("Data Analyst", "Riyadh. 3+ years of experience. Data.", LINKEDIN_URL),
                             engine.REJECT_HIGH_EXPERIENCE)
            self.assertEqual(reason("Sales Executive", "Riyadh. Sales targets.", LINKEDIN_URL), engine.REJECT_NOT_DATA)
            self.assertEqual(reason("Data Analyst", "Dubai. Excel reporting.", LINKEDIN_URL), engine.REJECT_LOCATION)
            self.assertIsNone(reason("Data Analyst", "Riyadh. Excel reporting.", LINKEDIN_URL))


class LinkedInTitleTests(unittest.TestCase):
    def test_hiring_format(self):
        parsed = engine.parse_linkedin_title(
            "Riyadh Pay hiring Junior Data Analyst in Riyadh, Riyadh, Saudi Arabia | LinkedIn"
        )
        self.assertEqual(parsed, ("Junior Data Analyst", "Riyadh Pay", "Riyadh, Riyadh, Saudi Arabia"))

    def test_dash_format(self):
        parsed = engine.parse_linkedin_title("BI Analyst - Eastern Health Services - LinkedIn")
        self.assertEqual(parsed, ("BI Analyst", "Eastern Health Services", ""))

    def test_unknown_format_returns_none(self):
        self.assertIsNone(engine.parse_linkedin_title("Data Analyst"))


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


class SerpApiSearchTests(unittest.TestCase):
    def search(self, data):
        with patch.dict("os.environ", {"SERPAPI_KEY": "test-key"}), \
                patch.object(engine.requests, "get", return_value=FakeResponse(data)), \
                patch.object(engine, "fetch_page_text", return_value="excel and power bi reporting"):
            return engine.serpapi_search("any query")

    def test_linkedin_result_uses_real_company_and_title(self):
        results = self.search({"organic_results": [{
            "title": "Riyadh Pay hiring Junior Data Analyst in Riyadh, Saudi Arabia | LinkedIn",
            "snippet": "Excel, Power BI and SQL reporting. 0-2 years.",
            "link": LINKEDIN_URL,
        }]})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Junior Data Analyst")
        self.assertEqual(results[0]["company"], "Riyadh Pay")
        self.assertEqual(results[0]["location"], "الرياض")

    def test_search_counts_found_and_rejected_results(self):
        engine.SEARCH_STATS.clear()
        self.search({"organic_results": [
            {"title": "Riyadh Pay hiring Junior Data Analyst in Riyadh, Saudi Arabia | LinkedIn",
             "snippet": "Excel and Power BI.", "link": LINKEDIN_URL},
            {"title": "Riyadh Pay hiring Senior Data Analyst in Riyadh, Saudi Arabia | LinkedIn",
             "snippet": "Excel and Power BI.", "link": "https://www.linkedin.com/jobs/view/4000000001"},
        ]})
        stats = engine.get_search_stats()
        self.assertEqual(stats["found"], 2)
        self.assertEqual(stats["kept"], 1)
        self.assertEqual(stats["rejected"], {engine.REJECT_SENIOR_TITLE: 1})

    def test_each_result_is_logged_with_its_decision(self):
        import io
        from contextlib import redirect_stdout

        output = io.StringIO()
        with redirect_stdout(output):
            self.search({"organic_results": [
                {"title": "Data Analyst Jobs in Dammam (25 new)", "snippet": "Data analyst jobs.",
                 "link": "https://sa.linkedin.com/jobs/data-analyst-jobs-dammam"},
            ]})
        log = output.getvalue()
        self.assertIn(engine.REJECT_NOT_JOB_PAGE, log)
        self.assertIn("https://sa.linkedin.com/jobs/data-analyst-jobs-dammam", log)

    def test_serpapi_error_is_reported(self):
        engine.SEARCH_PROBLEMS.clear()
        self.search({"error": "Your account has run out of searches."})
        self.assertIn("SerpApi: Your account has run out of searches.", engine.get_search_problems())

    def test_missing_key_is_reported(self):
        engine.SEARCH_PROBLEMS.clear()
        with patch.dict("os.environ", {}, clear=True):
            engine.serpapi_search("any query")
        self.assertTrue(any("SERPAPI_KEY" in problem for problem in engine.get_search_problems()))

    def run_with_get(self, get_mock):
        engine.SEARCH_PROBLEMS.clear()
        with patch.dict("os.environ", {"SERPAPI_KEY": "secret-key-123"}), \
                patch.object(engine.requests, "get", get_mock):
            engine.serpapi_search("any query")
        return " ".join(engine.get_search_problems())

    def test_timeout_reason_is_reported_without_the_key(self):
        def raise_timeout(*args, **kwargs):
            raise engine.requests.Timeout(
                "Read timed out: https://serpapi.com/search.json?api_key=secret-key-123"
            )
        problems = self.run_with_get(raise_timeout)
        self.assertIn("Timeout", problems)
        self.assertNotIn("secret-key-123", problems)

    def test_non_json_reply_reports_status_code(self):
        class HtmlResponse:
            status_code = 502
            text = "<html>Bad Gateway</html>"

            def json(self):
                raise ValueError("not json")

        problems = self.run_with_get(lambda *args, **kwargs: HtmlResponse())
        self.assertIn("502", problems)

    def test_daily_search_asks_for_ten_results_per_query(self):
        captured = []

        def fake_get(url, params=None, timeout=None):
            captured.append(params)
            return FakeResponse({"organic_results": []})

        with patch.dict("os.environ", {"SERPAPI_KEY": "test-key"}), \
                patch.object(engine.requests, "get", fake_get):
            engine.search_market_opportunities()
        self.assertTrue(captured)
        self.assertTrue(all(params["num"] == 10 for params in captured))

    def test_github_actions_gets_one_notice_with_all_results(self):
        import io
        from contextlib import redirect_stdout

        def fake_get(url, params=None, timeout=None):
            return FakeResponse({"organic_results": [
                {"title": "Data Analyst Jobs in Dammam (25 new)", "snippet": "Jobs.",
                 "link": "https://sa.linkedin.com/jobs/data-analyst-jobs-dammam"},
            ]})

        output = io.StringIO()
        with patch.dict("os.environ", {"SERPAPI_KEY": "k", "GITHUB_ACTIONS": "true"}), \
                patch.object(engine.requests, "get", fake_get), redirect_stdout(output):
            engine.search_market_opportunities()
        notices = [line for line in output.getvalue().splitlines() if line.startswith("::notice")]
        self.assertEqual(len(notices), 1)
        self.assertIn("data-analyst-jobs-dammam", notices[0])


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
