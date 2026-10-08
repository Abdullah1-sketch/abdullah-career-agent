import unittest

from company_career_scanner import classify_link


class ScannerLinkTests(unittest.TestCase):
    def test_graduate_leadership_program_link_is_kept(self):
        self.assertEqual(
            classify_link("Graduate Leadership Program - Data Analyst", "https://x.sa/careers/job/123"),
            "apply_now",
        )

    def test_senior_link_is_dropped(self):
        self.assertIsNone(classify_link("Senior Data Analyst", "https://x.sa/careers/job/124"))

    def test_mobile_package_page_is_not_a_bi_job(self):
        self.assertIsNone(classify_link("Mobile packages", "https://x.sa/jobs/mobile"))


if __name__ == "__main__":
    unittest.main()
