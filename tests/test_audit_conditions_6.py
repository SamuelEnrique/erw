"""Session 10219 (chain 710, the conditions audit, finding 6): /conditions counts "hours the adder was above zero", and
an hour counts at any amount above zero: from July 2018 to the adder's end, 5,799 of ERCOT's 10,492 hours above zero
were under 5 cents per MWh (the median 1.6 cents), and the page's own hourly chart, kept to 0.1, draws them as 0.0.
Words only: the glance and the chart say "however small", and both adder charts' hovers say what the count holds; the
count is unchanged (a level is finding 7, the owner's ruling). docs/reviews/conditions-model-audit-2026-11-26.md.
"""
import json
import os
import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "conditions")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheWordsSayHoweverSmall(unittest.TestCase):
    def test_the_glance_and_the_chart_say_it(self):
        s = src("site", "app", "conditions", "page.tsx")
        self.assertIn('words: "Most hours with the adder above zero, however small, in a day"', s)
        self.assertIn('title="Hours the adder was above zero, however small, a day"', s)
        self.assertEqual(s.count("${ADDER_WORDS}`} />}>"), 2, "both adder charts carry the words")
        for w in ["above zero, however small", "more than half were under 5 cents per MWh (the median 1.6 cents)", "draw as 0.0 on the hourly chart"]:
            self.assertIn(w, s)
        self.assertNotIn("export const ADDER_WORDS", s)

    def test_the_note_says_it(self):
        self.assertIn("the day's hours above zero, however small", src("docs", "methods", "grid_conditions.md"))

    @unittest.skipUnless(os.path.exists(os.path.join(DIR, "ercot.json")), "the conditions files are not in this checkout")
    def test_the_daily_count_holds_hours_the_chart_draws_as_zero(self):
        with open(os.path.join(DIR, "ercot.json"), encoding="utf-8") as fh:
            f = json.load(fh)
        k = f["hourly_columns"].index("adder")
        ct = ZoneInfo("America/Chicago")
        by = {}
        for rows in f["hourly"].values():
            for r in rows:
                if r[k] is not None:
                    d = datetime.strptime(r[0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(ct).strftime("%Y-%m-%d")
                    by.setdefault(d, {})[r[0]] = r[k]
        i = f["daily_columns"].index("adder_hours")
        more = sum(r[i] - sum(1 for v in by[r[0]].values() if v > 0) for r in f["daily"] if r[i] is not None and r[0] in by and len(by[r[0]]) >= 23)
        self.assertGreater(more, 300, "hours counted above zero whose hourly value the file keeps as 0.0")


if __name__ == "__main__":
    unittest.main()
