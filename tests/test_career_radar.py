import unittest
from unittest.mock import patch

import career_radar
import job_search_engine


class SearchWarningTests(unittest.TestCase):
    def test_daily_message_warns_when_search_failed(self):
        job_search_engine.SEARCH_PROBLEMS.clear()
        job_search_engine.SEARCH_PROBLEMS.append("SerpApi: Your account has run out of searches.")
        with patch.object(career_radar, "get_current_opportunities", return_value=[]):
            message = career_radar.build_daily_radar_message()
        self.assertIn("Your account has run out of searches.", message)


def make_item(title, description, url_id, location="Riyadh"):
    return {
        "title": title,
        "company": f"Company {url_id}",
        "location": location,
        "description": description,
        "url": f"https://boards.greenhouse.io/company{url_id}/jobs/{url_id}",
        "source": "test",
        "is_real_job": True,
    }


class DailyMessageTests(unittest.TestCase):
    def test_october_message_lists_all_strong_and_quick_apply_jobs(self):
        strong = "Fresh graduates. Excel, Power BI dashboards, SQL reporting."
        quick = "Excel reporting."  # outside priority cities -> quick apply
        items = [make_item(f"Junior Data Analyst {i}", strong, i) for i in range(1, 5)]
        items += [make_item(f"Reporting Analyst {i}", quick, i, location="Jeddah") for i in range(5, 7)]

        scores = [career_radar.get_score(item) for item in items]
        self.assertTrue(all(score >= 80 for score in scores[:4]), scores)
        self.assertTrue(all(60 <= score < 80 for score in scores[4:]), scores)

        with patch.object(career_radar, "get_current_opportunities", return_value=items):
            job_search_engine.SEARCH_PROBLEMS.clear()
            message = career_radar.build_daily_radar_message()

        for item in items:
            self.assertIn(item["url"], message)


class CheckSummaryTests(unittest.TestCase):
    def test_message_shows_what_was_checked_and_why_rejected(self):
        job_search_engine.SEARCH_PROBLEMS.clear()
        job_search_engine.SEARCH_STATS.clear()
        job_search_engine.SEARCH_STATS.update(
            {"found": 9, "kept": 1, f"rejected:{job_search_engine.REJECT_SENIOR_TITLE}": 5,
             f"rejected:{job_search_engine.REJECT_NOT_DATA}": 3}
        )
        items = [make_item("Reporting Analyst 1", "Excel reporting.", 1, location="Jeddah")]
        with patch.object(career_radar, "get_current_opportunities", return_value=items):
            message = career_radar.build_daily_radar_message()

        self.assertIn("📊", message)
        self.assertIn("9 نتيجة", message)
        self.assertIn(f"{job_search_engine.REJECT_SENIOR_TITLE} 5", message)


class CurrentOpportunitiesTests(unittest.TestCase):
    def test_real_job_descriptions_with_common_words_are_kept(self):
        job = make_item(
            "Junior Data Analyst", "Support the team, plan reports, follow privacy terms. Excel and Power BI.", 1
        )
        with patch.object(career_radar, "search_market_safely", return_value=[job]), \
                patch.object(career_radar, "scan_company_career_pages", return_value=[]):
            self.assertEqual(career_radar.get_current_opportunities(), [job])

    def test_telecom_package_page_from_scanner_is_still_dropped(self):
        page = make_item("Mobile data packages", "Internet plans", 2)
        with patch.object(career_radar, "search_market_safely", return_value=[]), \
                patch.object(career_radar, "scan_company_career_pages", return_value=[page]):
            self.assertEqual(career_radar.get_current_opportunities(), [])


if __name__ == "__main__":
    unittest.main()
