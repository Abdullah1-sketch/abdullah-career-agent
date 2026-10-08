import unittest

from opportunity_scoring import contains_any


class EnglishWholeWordMatchTests(unittest.TestCase):
    def test_bi_does_not_match_inside_ability(self):
        self.assertFalse(contains_any("strong ability to learn", ["bi"]))

    def test_intern_does_not_match_internal(self):
        self.assertFalse(contains_any("internal audit team", ["intern"]))

    def test_range_does_not_match_inside_bigger_range(self):
        self.assertFalse(contains_any("10-15 years of experience", ["0-1"]))

    def test_lead_does_not_match_leadership(self):
        self.assertFalse(contains_any("support leadership with reports", ["lead"]))

    def test_whole_word_still_matches(self):
        self.assertTrue(contains_any("Power BI and Excel", ["bi"]))
        self.assertTrue(contains_any("Data Analyst Intern", ["intern"]))
        self.assertTrue(contains_any("0-1 years", ["0-1"]))

    def test_matches_next_to_punctuation(self):
        self.assertTrue(contains_any("tools: excel, power bi.", ["bi"]))
        self.assertTrue(contains_any("https://x.com/careers/123", ["careers"]))

    def test_terms_with_special_characters(self):
        self.assertTrue(contains_any("needs 3+ years", ["3+ years"]))
        self.assertTrue(contains_any("https://linkedin.com/jobs/view/1", ["linkedin.com/jobs/view"]))

    def test_terms_with_punctuation_edges_match_inside_urls(self):
        self.assertTrue(contains_any("https://www.linkedin.com/jobs/view/4012345678", ["/jobs/view/"]))
        self.assertTrue(contains_any("https://x.sa/job/77", ["/job/"]))

    def test_case_insensitive(self):
        self.assertTrue(contains_any("JUNIOR Data Analyst", ["junior"]))


class ArabicSubstringMatchTests(unittest.TestCase):
    def test_arabic_matches_with_al_prefix(self):
        self.assertTrue(contains_any("خبرة في البيانات والتقارير", ["بيانات"]))
        self.assertTrue(contains_any("الرياض", ["رياض"]))

    def test_arabic_term_not_present(self):
        self.assertFalse(contains_any("محاسب", ["محلل بيانات"]))


if __name__ == "__main__":
    unittest.main()
