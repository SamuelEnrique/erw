"""Ready branch for /forecast (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.5, "the day's peak table
for the chosen places only, not in 'Every place': keep, or add"). Not the default: it waits for Samuel's ruling.

The other choice: under the table of every place, with demand, a table of the day's peak for every place (AllPlacesPeak
in site/app/forecast/view.tsx): one row a place, the days scored and each method's error of its highest hour over the
last two years, keyed to the place file. On the files now on main: on main no such table; here 64 rows (64 places shown,
each with a peak), 320 keyed figures with percent error. site/scripts/test-forecast-peak.mjs draws it from its fixture
(it runs under tests/test_session10405_forecast_peak.py). The page reads every place's file to draw it."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class ThePeakInEveryPlace(unittest.TestCase):
    def test_the_table(self):
        view = src("site", "app", "forecast", "view.tsx")
        self.assertIn("function AllPlacesPeak(", view)
        self.assertIn('{q.s === "demand" ? <AllPlacesPeak index={index} scores={scores} metric={metric}', view)
        block = view[view.index("function AllPlacesPeak("):view.index("/** How /demand's country view")]
        self.assertIn('pfKey(file, ["series", "demand", "peak", "last_2_years", "methods", m, metric])', block)
        self.assertNotIn(".sort(", block)                                  # the index's own order, as the table above

    def test_the_drawn_page_and_the_note(self):
        self.assertIn("ready branch wip/ready-forecast-peak-every-place", src("site", "scripts", "test-forecast-peak.mjs"))
        self.assertIn("a second\ntable gives the day's peak for every place", src("docs", "methods", "predict.md"))


if __name__ == "__main__":
    unittest.main()
