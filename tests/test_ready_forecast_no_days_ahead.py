"""Ready branch for /forecast (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.5, "the days after
tomorrow under Tomorrow: keep, or remove"). Not the default: it waits for Samuel's ruling.

The other choice: the days after tomorrow are not drawn under "Tomorrow" and not offered among the downloads
(DAYS_AHEAD_SHOWN in site/app/forecast/view.tsx); site/data/predict/ahead.json is still written and /forecast/ahead still
answers. On the files now on main: Texas draws 5 days after tomorrow (ahead.json holds 29 places) on main, none here.
site/scripts/test-forecast-peak.mjs and tests/test_session10405_forecast_peak.py are turned to the same rule."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheDaysAfterTomorrowAreNotDrawn(unittest.TestCase):
    def test_the_switch(self):
        view = src("site", "app", "forecast", "view.tsx")
        self.assertIn("const DAYS_AHEAD_SHOWN = false;", view)
        self.assertEqual(len(re.findall(r'\{DAYS_AHEAD_SHOWN && q\.s === "demand" && ahead \? \(', view)), 2)
        self.assertNotRegex(view, r'\{q\.s === "demand" && ahead \? \(')

    def test_the_file_and_its_address_stay(self):
        self.assertTrue(os.path.isfile(os.path.join(ROOT, "site", "app", "forecast", "ahead", "route.ts")))
        self.assertIn('"/forecast/ahead": ["./data/predict/ahead.json"]', src("site", "next.config.ts"))

    def test_the_note(self):
        self.assertIn("`/forecast` does not draw the days after tomorrow under \"Tomorrow\"", src("docs", "methods", "predict.md"))

    def test_the_drawn_page_says_so(self):
        self.assertIn("ready branch wip/ready-forecast-no-days-ahead", src("site", "scripts", "test-forecast-peak.mjs"))


if __name__ == "__main__":
    unittest.main()
