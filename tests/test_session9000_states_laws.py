"""Session 9000, data request 563: /states says what the large-load research did for a state with no law in the table."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


class ResearchStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import states_page
        cls.sp = states_page

    def test_texas_is_withheld_not_lawless(self):
        status, words = self.sp.research_status("TX")
        self.assertEqual(status, "withheld")
        self.assertIn("S.B. 6", words)
        self.assertNotIn("holds no state law", words)

    def test_a_searched_state_says_none_found(self):
        self.assertEqual(self.sp.research_status("NC")[0], "none found")

    def test_an_unreadable_legislature_says_not_read(self):
        self.assertEqual(self.sp.research_status("GA")[0], "not read")

    def test_a_state_not_covered_says_not_yet_read(self):
        status, words = self.sp.research_status("AK")
        self.assertEqual(status, "not yet read")
        self.assertIn("Alaska", words)


if __name__ == "__main__":
    unittest.main()
