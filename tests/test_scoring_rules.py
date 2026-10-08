import unittest

from opportunity_scoring import Opportunity, score_opportunity

SENIOR_REASON = "May be too senior or outside target path"


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


if __name__ == "__main__":
    unittest.main()
