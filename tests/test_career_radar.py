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


def verification_result(verified=True, source="company", status="open", years=1, missing=(), platforms=()):
    return {
        "source": source,
        "source_url": "https://careers.example-employer.sa/jobs/1",
        "status": status,
        "verified": verified,
        "experience_years": years,
        "requirements": {
            "have": ["Excel", "Power BI"],
            "learning": [],
            "missing": list(missing),
            "missing_platforms": list(platforms),
        },
    }


def patch_verification(**kwargs):
    return patch.object(career_radar, "verify_job", return_value=verification_result(**kwargs))


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

        with patch_verification():
            scores = [career_radar.get_score(item) for item in items]
        self.assertTrue(all(score >= 80 for score in scores[:4]), scores)
        self.assertTrue(all(60 <= score < 80 for score in scores[4:]), scores)

        with patch.object(career_radar, "get_current_opportunities", return_value=items), patch_verification():
            job_search_engine.SEARCH_PROBLEMS.clear()
            message = career_radar.build_daily_radar_message()

        for item in items:
            self.assertIn(item["title"], message)


class CheckSummaryTests(unittest.TestCase):
    def test_message_shows_what_was_checked_and_why_rejected(self):
        job_search_engine.SEARCH_PROBLEMS.clear()
        job_search_engine.SEARCH_STATS.clear()
        job_search_engine.SEARCH_STATS.update(
            {"found": 9, "kept": 1, f"rejected:{job_search_engine.REJECT_SENIOR_TITLE}": 5,
             f"rejected:{job_search_engine.REJECT_NOT_DATA}": 3}
        )
        items = [make_item("Reporting Analyst 1", "Excel reporting.", 1, location="Jeddah")]
        with patch.object(career_radar, "get_current_opportunities", return_value=items), patch_verification():
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


STRONG_JOB = ("Junior Data Analyst", "Fresh graduates. Excel, Power BI dashboards and reporting.")


def message_for(item, **verification):
    job_search_engine.SEARCH_PROBLEMS.clear()
    with patch.object(career_radar, "get_current_opportunities", return_value=[item]), \
            patch_verification(**verification):
        return career_radar.build_daily_radar_message()


class VerifiedRecommendationTests(unittest.TestCase):
    def test_green_needs_a_verified_original_posting(self):
        message = message_for(make_item(*STRONG_JOB, 1))
        self.assertIn("🟢 قدّم الآن", message)
        self.assertIn("✅", message)
        self.assertIn("https://careers.example-employer.sa/jobs/1", message)

    def test_strong_but_unverified_job_is_not_green(self):
        message = message_for(make_item(*STRONG_JOB, 1), verified=False, source="linkedin", status="unknown")
        self.assertNotIn("🟢 قدّم الآن", message)
        self.assertIn("تحقق قبل التقديم", message)
        self.assertIn("⚠️", message)

    def test_no_outreach_advice_for_unverified_job(self):
        message = message_for(make_item(*STRONG_JOB, 1), verified=False, source="job_board", status="unknown")
        self.assertNotIn("رسالة جاهزة", message)
        self.assertNotIn("تحرك يدوي", message)

    def test_closed_job_is_not_recommended(self):
        item = make_item(*STRONG_JOB, 1)
        message = message_for(item, verified=False, status="closed")
        self.assertNotIn(item["url"], message)
        self.assertNotIn("https://careers.example-employer.sa/jobs/1", message)
        self.assertIn("مغلقة 1", message)

    def test_job_asking_three_plus_years_on_original_page_is_not_recommended(self):
        message = message_for(make_item(*STRONG_JOB, 1), years=3)
        self.assertNotIn("قدّم", message.split("📊")[0].replace("لا توجد فرصة قوية اليوم", ""))
        self.assertIn("تطلب خبرة 3+ 1", message)

    def test_missing_platform_skill_is_not_green(self):
        item = make_item("Business & Data Analyst - ServiceNow HRSD", "Excel and Power BI reporting.", 1)
        message = message_for(item, missing=["ServiceNow"], platforms=["ServiceNow"])
        self.assertNotIn("🟢 قدّم الآن", message)
        self.assertIn("ServiceNow", message)

    def test_required_experience_is_shown_from_the_posting(self):
        message = message_for(make_item(*STRONG_JOB, 1), years=1)
        self.assertIn("الخبرة المطلوبة: سنة على الأقل", message)

    def test_ready_message_never_claims_sql(self):
        item = make_item("Junior Data Analyst", "Fresh graduates. SQL, Excel, Power BI dashboards.", 1)
        message = message_for(item)
        ready = message.split("رسالة جاهزة:")[1]
        self.assertNotIn("SQL", ready)


if __name__ == "__main__":
    unittest.main()
