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


if __name__ == "__main__":
    unittest.main()
