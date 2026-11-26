"""Session 10225 (chain 710, the events audit, finding 8): /events/uri-2021 prints ERCOT's hub price and the event study
estimates its effect (+2,293.84 USD/MWh a day, with an interval), and says nothing of the ceiling it sat at: on 16 to
18 February 2021 the hub's daily mean real-time price stood within 0.6 percent of the day's highest 15-minute price.
Words only: the page's caveat and docs/methods/events.md say the price sat at the market's ceiling and what that does
to its figures; no figure moves (the count of intervals near the ceiling is the ruling alternative wip/alt-events-4).
docs/reviews/events-model-audit-2026-11-26.md.
"""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROWS = os.path.join(ROOT, "replication", "events", "window_rows.csv")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class ThePriceSatAtTheCeiling(unittest.TestCase):
    def test_the_page_says_it(self):
        s = src("site", "app", "events", "uri-2021", "page.tsx")
        self.assertIn('<span data-uri-ceiling="1">{CEILING_WORDS}</span>', s)
        for w in ["stood within one percent of the day's highest 15-minute price", "held at the market's ceiling",
                  "measure the ceiling's reach as much as the scarcity"]:
            self.assertIn(w, s)

    def test_the_note_says_it(self):
        self.assertIn("**The price sat at the ceiling (session 10225, 26 November 2026).**", src("docs", "methods", "events.md"))

    @unittest.skipUnless(os.path.exists(ROWS), "the replication's public rows are not in this checkout")
    def test_three_days_within_one_percent(self):
        with open(ROWS, encoding="utf-8") as fh:
            rows = [r for r in csv.DictReader(l for l in fh if not l.startswith("#")) if r["event"] == "uri_2021" and r["entity"] == "ercot:HB_HUBAVG"]
        v = {(r["variable"], r["ts_utc"][:10]): float(r["value"]) for r in rows}
        for d in ("2021-02-16", "2021-02-17", "2021-02-18"):
            with self.subTest(d):
                self.assertGreater(v[("rt_mean", d)] / v[("rt_max", d)], 0.99)
                self.assertGreater(v[("rt_max", d)], 8900)
        self.assertLess(v[("rt_mean", "2021-02-15")] / v[("rt_max", "2021-02-15")], 0.99, "the first outage day moved")


if __name__ == "__main__":
    unittest.main()
