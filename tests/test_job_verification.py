import unittest
from datetime import date
from unittest.mock import patch

import job_verification as verification


def job(url, description="Excel and Power BI reporting.", company="Riyadh Pay", apply_links=None):
    return {
        "title": "Junior Data Analyst",
        "company": company,
        "location": "Riyadh",
        "description": description,
        "url": url,
        "apply_links": apply_links if apply_links is not None else [url],
    }


LONG_TEXT = " Build Excel and Power BI dashboards for the finance team." * 12
APPLY = " Apply now."


def fake_pages(pages: dict):
    """pages: url -> (text, links). Missing url = fetch failed."""
    def fetch(url):
        return pages.get(url, ("", []))
    return patch.object(verification, "fetch_page", side_effect=fetch)


class SourceTests(unittest.TestCase):
    def test_source_types(self):
        cases = [
            ("https://boards.greenhouse.io/riyadhpay/jobs/1", "Riyadh Pay", "company"),
            ("https://careers.riyadhpay.sa/jobs/1", "Riyadh Pay", "company"),
            ("https://www.linkedin.com/jobs/view/4012345678", "Riyadh Pay", "linkedin"),
            ("https://www.bayt.com/en/saudi-arabia/jobs/data-analyst-1/", "Riyadh Pay", "job_board"),
            ("https://www.jobleads.com/sa/job/junior-mis-data", "JASARA", "job_board"),
            ("https://www.directoryksa.com/jobs/business-data-analyst", "Tawantech", "job_board"),
            ("https://gyhuvlae.strivehischools.org/remote-jobs/x", "Virtucruit", "unknown"),
        ]
        for url, company, expected in cases:
            with self.subTest(url):
                self.assertEqual(verification.classify_source(url, company), expected)


class VerifyTests(unittest.TestCase):
    def test_open_company_posting_is_verified(self):
        url = "https://boards.greenhouse.io/riyadhpay/jobs/1"
        with fake_pages({url: ("1-2 years of experience." + LONG_TEXT + APPLY, [])}):
            result = verification.verify_job(job(url))
        self.assertTrue(result["verified"])
        self.assertEqual(result["status"], "open_confirmed")
        self.assertEqual(result["experience_years"], 1)
        self.assertEqual(result["source_url"], url)

    def test_closed_company_posting(self):
        url = "https://boards.greenhouse.io/riyadhpay/jobs/1"
        with fake_pages({url: ("No longer accepting applications." + LONG_TEXT, [])}):
            result = verification.verify_job(job(url))
        self.assertEqual(result["status"], "closed")
        self.assertFalse(result["verified"])

    def test_experience_found_only_on_original_page(self):
        url = "https://boards.greenhouse.io/riyadhpay/jobs/1"
        with fake_pages({url: ("Requirements: 3-5 years of experience in BI." + LONG_TEXT, [])}):
            result = verification.verify_job(job(url, description="Excel reporting."))
        self.assertEqual(result["experience_years"], 3)

    def test_job_board_leads_to_original_posting(self):
        board = "https://www.bayt.com/en/saudi-arabia/jobs/data-analyst-1/"
        original = "https://boards.greenhouse.io/riyadhpay/jobs/1"
        pages = {board: ("Apply on company site", [original]), original: (LONG_TEXT + APPLY, [])}
        with fake_pages(pages):
            result = verification.verify_job(job(board))
        self.assertTrue(result["verified"])
        self.assertEqual(result["source"], "company")
        self.assertEqual(result["source_url"], original)

    def test_company_link_among_apply_options_is_used(self):
        board = "https://www.bayt.com/en/saudi-arabia/jobs/data-analyst-1/"
        original = "https://careers.riyadhpay.sa/jobs/1"
        with fake_pages({original: (LONG_TEXT + APPLY, [])}):
            result = verification.verify_job(job(board, apply_links=[board, original]))
        self.assertEqual(result["source_url"], original)
        self.assertTrue(result["verified"])

    def test_job_board_without_original_is_not_verified(self):
        board = "https://www.bayt.com/en/saudi-arabia/jobs/data-analyst-1/"
        with fake_pages({board: (LONG_TEXT, [])}):
            result = verification.verify_job(job(board))
        self.assertFalse(result["verified"])
        self.assertEqual(result["source"], "job_board")

    def test_second_job_board_does_not_erase_the_first(self):
        first = "https://www.bayt.com/en/saudi-arabia/jobs/data-analyst-1/"
        second = "https://www.jobleads.com/sa/job/data-analyst-2"
        with fake_pages({first: ("1-2 years of experience." + LONG_TEXT, [])}):
            result = verification.verify_job(job(first, apply_links=[first, second]))
        self.assertEqual(result["source_url"], first)
        self.assertEqual(result["experience_years"], 1)

    def test_official_page_without_apply_button_is_only_seen(self):
        url = "https://www.pepsicojobs.com/main/jobs/466519"
        with fake_pages({url: (LONG_TEXT, [])}):
            result = verification.verify_job(job(url, company="PepsiCo"))
        self.assertEqual(result["source"], "company")
        self.assertEqual(result["status"], "page_seen")
        self.assertFalse(result["verified"])

    def test_check_time_is_recorded(self):
        url = "https://boards.greenhouse.io/riyadhpay/jobs/1"
        with fake_pages({url: (LONG_TEXT + APPLY, [])}):
            result = verification.verify_job(job(url))
        self.assertRegex(result["checked_at"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")

    def test_page_that_cannot_be_opened(self):
        url = "https://careers.riyadhpay.sa/jobs/1"
        with fake_pages({}):
            result = verification.verify_job(job(url))
        self.assertEqual(result["status"], "unknown")
        self.assertFalse(result["verified"])

    def test_linkedin_is_not_fetched(self):
        url = "https://www.linkedin.com/jobs/view/4012345678"
        with fake_pages({}) as fetch:
            result = verification.verify_job(job(url))
        fetch.assert_not_called()
        self.assertEqual(result["source"], "linkedin")
        self.assertFalse(result["verified"])


class PostingDateTests(unittest.TestCase):
    TODAY = date(2026, 10, 8)

    def test_google_posted_at_values(self):
        cases = {"3 days ago": 3, "an hour ago": 0, "30+ days ago": 30, "a month ago": 30,
                 "2 weeks ago": 14, "منذ 5 أيام": 5}
        for text, days in cases.items():
            with self.subTest(text):
                self.assertEqual(verification.posted_age_days(text), days)

    def test_unknown_posted_at(self):
        self.assertIsNone(verification.posted_age_days(""))

    def test_old_date_inside_link(self):
        url = "https://ai-search.io/job-board/accenture-data-ai-analyst-riyadh-sa-20250221"
        self.assertEqual(verification.link_date_age_days(url, today=self.TODAY), 594)
        self.assertIsNone(verification.link_date_age_days("https://x.sa/jobs/4012345678", today=self.TODAY))

    def test_old_unconfirmed_posting_is_excluded(self):
        result = {"status": "unknown", "source": "job_board"}
        self.assertTrue(verification.is_old_and_unconfirmed(result, posted_days=45, link_days=None))
        self.assertTrue(verification.is_old_and_unconfirmed(result, posted_days=None, link_days=594))
        self.assertFalse(verification.is_old_and_unconfirmed(result, posted_days=3, link_days=None))
        confirmed = {"status": "open_confirmed", "source": "company"}
        self.assertFalse(verification.is_old_and_unconfirmed(confirmed, posted_days=45, link_days=None))


class ReliabilityTests(unittest.TestCase):
    def level(self, source, status, posted_days=None):
        return verification.reliability({"source": source, "status": status}, posted_days)[0]

    def test_levels(self):
        self.assertEqual(self.level("company", "open_confirmed"), "high")
        self.assertEqual(self.level("company", "page_seen"), "medium")
        self.assertEqual(self.level("linkedin", "unknown", posted_days=3), "medium")
        self.assertEqual(self.level("linkedin", "unknown", posted_days=None), "low")
        self.assertEqual(self.level("job_board", "unknown", posted_days=1), "low")


class RequirementTests(unittest.TestCase):
    def test_requirements_split_by_what_abdullah_has(self):
        text = "Excel, SQL and Python required. Experience with ServiceNow HRSD."
        requirements = verification.analyze_requirements(text)
        self.assertEqual(requirements["have"], ["Excel"])
        self.assertEqual(requirements["learning"], ["SQL"])
        self.assertEqual(requirements["missing"], ["Python", "ServiceNow"])
        self.assertEqual(requirements["missing_platforms"], ["ServiceNow"])


if __name__ == "__main__":
    unittest.main()
