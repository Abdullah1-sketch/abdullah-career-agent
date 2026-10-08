"""Fit score tests built from real postings in the 2026-10-08 report."""

import unittest

from job_fit import compute_fit, role_type


def requirements(have=(), learning=(), missing=(), platforms=()):
    return {"have": list(have), "learning": list(learning), "missing": list(missing),
            "missing_platforms": list(platforms)}


def fit(title, description="", location="Riyadh", years=None, reqs=None):
    job = {"title": title, "description": description, "location": location}
    return compute_fit(job, years, reqs if reqs is not None else requirements())


class RoleTypeTests(unittest.TestCase):
    def test_roles_from_real_report(self):
        cases = {
            "Junior MIS Data & Reporting Analyst": "data",
            "Junior Data Analyst": "data",
            "Junior MIS & Dashboards Analyst": "adjacent",
            "Strategic FP&A & Financial Reporting Analyst": "finance",
            "Control & Reporting Asst Analyst": "finance",
            "Junior Analyst, Valuation": "finance",
            "GIS Data Analyst": "specialty",
            "Sales Executive": "other",
        }
        for title, expected in cases.items():
            with self.subTest(title):
                self.assertEqual(role_type(title, "Excel and Power BI reports."), expected)


class FitScoreTests(unittest.TestCase):
    def test_everything_known_and_met_can_be_high(self):
        result = fit("Junior MIS Data & Reporting Analyst", years=1,
                     reqs=requirements(have=["Excel", "Power BI"]))
        self.assertGreaterEqual(result["score"], 90)

    def test_no_100_when_experience_unknown(self):
        result = fit("Junior Data Analyst", "Fresh graduates.", years=None,
                     reqs=requirements(have=["Excel", "Power BI"]))
        self.assertLess(result["score"], 100)

    def test_unmet_experience_caps_the_score(self):
        result = fit("Junior Data Analyst", years=2, reqs=requirements(have=["Excel", "Power BI"]))
        self.assertLessEqual(result["score"], 75)
        self.assertTrue(result["experience_unmet"])

    def test_missing_core_skills_cap_the_score(self):
        result = fit("Junior Data Analyst", years=0,
                     reqs=requirements(have=["Power BI"], learning=["SQL"],
                                       missing=["Python", "Tableau", "SAS", "Azure", "AWS"]))
        self.assertLess(result["score"], 80)

    def test_learning_skill_is_not_counted_as_mastered(self):
        mastered = fit("Junior Data Analyst", years=0, reqs=requirements(have=["Excel", "SQL"]))
        learning = fit("Junior Data Analyst", years=0, reqs=requirements(have=["Excel"], learning=["SQL"]))
        self.assertLess(learning["score"], mastered["score"])
        self.assertLessEqual(learning["score"], 90)

    def test_missing_platform_skill_is_not_strong(self):
        result = fit("Business & Data Analyst - ServiceNow", years=None,
                     reqs=requirements(have=["Excel"], missing=["ServiceNow"], platforms=["ServiceNow"]))
        self.assertLess(result["score"], 60)

    def test_finance_role_is_labelled_and_capped(self):
        result = fit("Strategic FP&A & Financial Reporting Analyst",
                     reqs=requirements(have=["Excel", "Power BI"]))
        self.assertEqual(result["role"], "finance")
        self.assertLessEqual(result["score"], 60)

    def test_parts_add_up_and_are_reported(self):
        result = fit("Junior Data Analyst", years=1, reqs=requirements(have=["Excel"]))
        self.assertEqual(set(result["parts"]), {"role", "experience", "skills", "location"})


if __name__ == "__main__":
    unittest.main()
