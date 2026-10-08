import os
import tempfile
import unittest

from application_log import (
    build_score_vs_outcome_report,
    load_applications,
    outcome_of,
    summarize_by_band,
)


def record(score, status, title="Data Analyst", company="Co"):
    return {"title": title, "company": company, "bot_score": score, "status": status}


class OutcomeTests(unittest.TestCase):
    def test_statuses_in_both_languages(self):
        self.assertEqual(outcome_of("interview"), "response")
        self.assertEqual(outcome_of("مقابلة"), "response")
        self.assertEqual(outcome_of("اتصال"), "response")
        self.assertEqual(outcome_of("rejected"), "no_response")
        self.assertEqual(outcome_of("لا رد"), "no_response")
        self.assertEqual(outcome_of("تم التقديم"), "pending")


class LoadApplicationsTests(unittest.TestCase):
    def test_missing_score_is_computed_by_the_bot(self):
        csv_text = (
            "date,company,title,location,url,description,bot_score,status\n"
            "2026-10-01,Riyadh Pay,Junior Data Analyst,Riyadh,"
            "https://boards.greenhouse.io/x/jobs/1,Excel and Power BI dashboards,,مقابلة\n"
            "2026-10-02,Najd,Data Analyst,Riyadh,https://x.sa/careers/jobs/2,,72,لا رد\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as file:
            file.write(csv_text)
        try:
            records = load_applications(file.name)
        finally:
            os.remove(file.name)

        self.assertEqual(len(records), 2)
        self.assertGreaterEqual(records[0]["bot_score"], 80)
        self.assertEqual(records[1]["bot_score"], 72)


class ReportTests(unittest.TestCase):
    def test_response_rate_per_score_band(self):
        records = [
            record(90, "interview"), record(85, "no_response"),
            record(70, "rejected"), record(65, "rejected"),
            record(40, "contacted"),
            record(88, "applied"),
        ]
        bands = summarize_by_band(records)
        self.assertEqual(bands["قدّم الآن (80+)"], {"decided": 2, "responses": 1})
        self.assertEqual(bands["قدّم سريع (60-79)"], {"decided": 2, "responses": 0})
        self.assertEqual(bands["لا تقدم (<60)"], {"decided": 1, "responses": 1})

    def test_report_flags_jobs_the_bot_said_to_skip_that_replied(self):
        report = build_score_vs_outcome_report([
            record(90, "interview"),
            record(40, "مقابلة", title="Operations Analyst", company="Eastern Ports"),
        ])
        self.assertIn("Operations Analyst", report)
        self.assertIn("Eastern Ports", report)

    def test_report_with_no_records(self):
        self.assertIn("ما فيه تقديمات", build_score_vs_outcome_report([]))


class CommandLineTests(unittest.TestCase):
    def test_review_command_prints_report_for_example_file(self):
        import subprocess
        import sys

        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output = subprocess.run(
            [sys.executable, "main.py", "--review-applications", "applications.example.csv"],
            cwd=repo_root, capture_output=True, text=True, check=True,
        ).stdout
        self.assertIn("تقرير التقديمات: 3 تقديم", output)


if __name__ == "__main__":
    unittest.main()
