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
