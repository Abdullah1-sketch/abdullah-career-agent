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


if __name__ == "__main__":
    unittest.main()
