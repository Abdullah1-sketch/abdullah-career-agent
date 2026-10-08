import unittest

from career_radar import is_low_quality_item
from interview_path import recommend_interview_path
from opportunity_scoring import ENTRY_LEVEL_BONUS, Opportunity, is_stale_posting, score_opportunity

SENIOR_REASON = "May be too senior or outside target path"
AGGREGATOR_REASON = "Posted on a job board: apply on the company site if possible"


def make_job(title="Data Analyst", description="", location="Riyadh, Saudi Arabia",
             url="https://careers.example-company.sa/jobs/123", company="Example Co"):
    return Opportunity(title=title, company=company, location=location,
                       description=description, url=url)


def score(**kwargs) -> dict:
    return score_opportunity(make_job(**kwargs))


class SeniorityInTitleOnlyTests(unittest.TestCase):
    def test_manager_in_description_does_not_reject_junior(self):
        result = score(
            title="Junior Data Analyst",
            description="You will build Power BI dashboards and report to the analytics manager.",
        )
        self.assertNotIn(SENIOR_REASON, result["reasons"])
        self.assertGreater(result["score"], 0)

    def test_working_with_data_engineers_does_not_reject(self):
        result = score(
            description="Work with the data engineer and data scientist on SQL reporting.",
        )
        self.assertNotIn(SENIOR_REASON, result["reasons"])

    def test_senior_in_title_is_rejected(self):
        result = score(title="Senior Data Analyst", description="Excel and Power BI reporting.")
        self.assertEqual(result["reasons"], [SENIOR_REASON])

    def test_off_track_title_is_rejected(self):
        result = score(title="Data Engineer", description="Build pipelines and SQL reporting.")
        self.assertEqual(result["reasons"], [SENIOR_REASON])

    def test_arabic_manager_title_is_rejected(self):
        result = score(title="مدير تحليل البيانات", description="تحليل البيانات وإعداد التقارير")
        self.assertEqual(result["reasons"], [SENIOR_REASON])


class ExperienceRangeTests(unittest.TestCase):
    def assert_not_too_experienced(self, description):
        result = score(description=description)
        self.assertNotIn(SENIOR_REASON, result["reasons"], description)

    def assert_too_experienced(self, description):
        result = score(description=description)
        self.assertEqual(result["reasons"], [SENIOR_REASON], description)

    def test_low_minimum_ranges_are_accepted(self):
        self.assert_not_too_experienced("1-3 years of experience in data analysis.")
        self.assert_not_too_experienced("0-3 years experience with Excel and Power BI.")
        self.assert_not_too_experienced("2 to 4 years of experience in reporting.")
        self.assert_not_too_experienced("خبرة من 1 إلى 3 سنوات في تحليل البيانات")
        self.assert_not_too_experienced("خبرة من ١ إلى ٣ سنوات في تحليل البيانات")

    def test_high_minimum_is_rejected(self):
        self.assert_too_experienced("3+ years of experience in data analysis.")
        self.assert_too_experienced("Minimum of 5 years experience in BI.")
        self.assert_too_experienced("3-5 years of experience in reporting.")
        self.assert_too_experienced("at least three years of experience with SQL.")
        self.assert_too_experienced("خبرة عملية تتراوح بين 3 إلى 10 سنوات")
        self.assert_too_experienced("خبرة لا تقل عن ٣ سنوات")
        self.assert_too_experienced("خبرة لا تقل عن خمس سنوات")

    def test_years_unrelated_to_experience_are_ignored(self):
        self.assert_not_too_experienced("Join a company growing for 10 years in Riyadh. Excel reporting.")


class AggregatorLinkTests(unittest.TestCase):
    JOB_BOARD_URL = "https://www.bayt.com/en/saudi-arabia/jobs/junior-data-analyst-4812345/"

    def test_job_board_link_is_scored_not_rejected(self):
        result = score(
            title="Junior Data Analyst",
            description="Fresh graduates. Excel, Power BI dashboards and SQL.",
            url=self.JOB_BOARD_URL,
        )
        self.assertGreaterEqual(result["score"], 60)
        self.assertIn(AGGREGATOR_REASON, result["reasons"])

    def test_job_board_item_passes_daily_report_filter(self):
        item = {"title": "Junior Data Analyst", "company": "Example Co", "url": self.JOB_BOARD_URL}
        self.assertFalse(is_low_quality_item(item))

    def test_job_board_listing_page_is_still_filtered(self):
        item = {"title": "Data Analyst jobs in Riyadh", "company": "Bayt",
                "url": "https://www.bayt.com/en/saudi-arabia/jobs/data-analyst-jobs-in-riyadh/"}
        self.assertTrue(is_low_quality_item(item))

    def test_good_job_board_match_gets_find_original_action(self):
        opportunity = {"title": "Junior Data Analyst", "url": self.JOB_BOARD_URL}
        path = recommend_interview_path(opportunity, {"score": 82, "priority": "Strong"})
        self.assertIn("Find the original posting on the company site and apply there", path["actions"])


class MissingLevelWordTests(unittest.TestCase):
    def test_no_level_words_is_neutral(self):
        plain = dict(title="Data Analyst", location="", url="https://example-company.sa/123")
        without_level = score(description="Excel reporting.", **plain)["score"]
        with_junior = score(description="Junior role. Excel reporting.", **plain)["score"]
        self.assertEqual(with_junior - without_level, ENTRY_LEVEL_BONUS)


class StaleJobTests(unittest.TestCase):
    def assert_stale(self, description):
        self.assertTrue(is_stale_posting(description), description)

    def assert_fresh(self, description):
        self.assertFalse(is_stale_posting(description), description)

    def test_normal_words_are_not_stale(self):
        self.assert_fresh("Track closed deals and enclosed reports in Power BI.")
        self.assert_fresh("Prepare monthly reports; dashboards refreshed every 3 months.")
        self.assert_fresh("Posted 1 month ago")
        self.assert_fresh("Posted 2 weeks ago")
        self.assert_fresh("نُشرت منذ شهر")

    def test_old_or_closed_postings_are_stale(self):
        self.assert_stale("Posted 3 months ago")
        self.assert_stale("Posted 2 years ago")
        self.assert_stale("No longer accepting applications")
        self.assert_stale("This job has expired")
        self.assert_stale("نُشرت منذ شهرين")
        self.assert_stale("منذ 4 أشهر")
        self.assert_stale("منذ سنة")
        self.assert_stale("انتهى التقديم")

    def test_stale_job_gets_clear_reason(self):
        result = score(description="Excel reporting. No longer accepting applications.")
        self.assertEqual(result["reasons"], ["Posting looks old or closed"])


class GraduateProgramTests(unittest.TestCase):
    def test_data_graduate_program_is_strong(self):
        result = score(
            title="Graduate Development Program - Data & Analytics",
            description="12-month program for fresh graduates. Rotations in reporting and BI. Excel, Power BI.",
        )
        self.assertGreaterEqual(result["score"], 80, result)

    def test_data_analytics_intern_is_strong(self):
        result = score(
            title="Data Analytics Intern",
            description="Open to fresh graduates. Excel reporting and Power BI dashboards.",
        )
        self.assertGreaterEqual(result["score"], 80, result)


if __name__ == "__main__":
    unittest.main()
