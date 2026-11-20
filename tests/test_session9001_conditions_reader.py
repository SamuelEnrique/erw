"""Session 9001, chain 601 part H, row H3: read on production, /conditions opened on ERCOT drew its two scarcity strips
as empty charts with every axis label "01-01" and its alerts as a header with no row, because the newest 35 days hold
no figure for them (ERCOT's adder table ends on 2025-12-04, the alerts table on 2026-10-15). A strip with no figure in
its window now says so in words, with the last day the file holds; the alerts have a visible heading and a "none" line.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "site", "app", "conditions", "page.tsx")
DATA = os.path.join(ROOT, "site", "data", "conditions")


def page():
    with open(PAGE, encoding="utf-8") as f:
        return f.read()


class StripsSayWhenNothingIsHeld(unittest.TestCase):
    def test_every_chart_is_drawn_only_from_lines_that_hold_points(self):
        s = page()
        # the charts take the lines computed once, and each has its words for an empty window
        for name in ["hDemand", "hOut", "hCons", "hAdder", "dDemand", "dOut", "dCons", "dAdder"]:
            self.assertIn(f"{name}.length ?", s, name)
        self.assertNotIn("<LineChart lines={hourlyLines(", s)
        self.assertNotIn("<TimeChart series={dailySeries(", s)
        for k in ["-demand`", "-out`", "-cons`", "-scar`", "-demand-d`", "-out-d`", "-cons-d`", "-scar-d`"]:
            self.assertIn(f'w={{w}} k={{`${{tag}}{k}}} />', s, k)

    def test_the_alerts_have_a_visible_heading_and_a_none_line(self):
        s = page()
        self.assertIn("data-alerts-heading={tag}", s)
        self.assertIn("None held in this window.", s)

    def test_the_case_found_is_one_the_words_cover(self):
        path = os.path.join(DATA, "ercot.json")
        if not os.path.exists(path):
            self.skipTest("the page files are not in this checkout")
        with open(path, encoding="utf-8") as f:
            F = json.load(f)
        i = F["hourly_columns"].index("adder")
        recent = F["hourly"]["recent"]
        self.assertTrue(recent)
        self.assertTrue(all(r[i] is None for r in recent), "the newest 35 days hold no adder: the words, not a chart")
        j = F["daily_columns"].index("adder_hours")
        held = [r[0] for r in F["daily"] if r[j] is not None]
        self.assertTrue(held, "the file holds earlier adder days, so the words name the last")


if __name__ == "__main__":
    unittest.main()
