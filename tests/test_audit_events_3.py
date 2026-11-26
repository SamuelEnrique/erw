"""Session 10225 (chain 710, the events audit, finding 3): /events/caiso-heat-2020 says in bold "Not on the outage days":
CAISO's highest hour against its baseline was higher on 18 August than on the outage days of 14 and 15 August. That
compares each day's highest hour of demand served; the Stage 3 emergencies came in the evening as solar fell (CAISO's
notices: 18:36 to 20:38 on the 14th, 18:27 to 18:48 on the 15th), and the shed load is not in demand served. By
California's demand less solar and wind (the event's region file), 14 August was the highest of 14 to 19 August.
Words only: the page and docs/methods/events.md say what the comparison measures; no figure moves (a figure of net
demand is finding 4, the owner's ruling). docs/reviews/events-model-audit-2026-11-26.md.
"""
import datetime as dt
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILE = os.path.join(ROOT, "site", "data", "regions", "events", "caiso_heat_2020.json")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class WhatTheOutageDaysComparisonMeasures(unittest.TestCase):
    def test_the_page_says_it(self):
        s = src("site", "app", "events", "caiso-heat-2020", "page.tsx")
        self.assertIn('<span data-outage-hours="1">{OUTAGE_HOURS_WORDS}</span>', s)
        for w in ["each day's highest hour of demand served against its own baseline days", "demand served leaves that load out",
                  "18:36 to 20:38 on the 14th and 18:27 to 18:48 on the 15th", "do not show that the grid was less stretched on the outage days"]:
            self.assertIn(w, s)
        self.assertIn("<strong>Not on the outage days.</strong>", s, "the page's own sentence stands")

    def test_the_note_says_it(self):
        self.assertIn("not of the hours the outages came in", src("docs", "methods", "events.md"))

    @unittest.skipUnless(os.path.exists(FILE), "the region file is not in this checkout")
    def test_by_net_demand_the_first_outage_day_is_the_highest(self):
        with open(FILE, encoding="utf-8") as fh:
            f = json.load(fh)
        cal = f["regions"]["CAL"]
        t0 = dt.datetime.fromisoformat(f["hours"]["start"].replace("Z", "+00:00"))
        best = {}
        for i, d in enumerate(cal["demand_mw"]):
            so, wi = cal["gen"]["solar"][i], cal["gen"]["wind"][i]
            if None in (d, so, wi):
                continue
            day = (t0 + dt.timedelta(hours=i - 7)).strftime("%Y-%m-%d")  # Pacific daylight time
            best[day] = max(best.get(day, 0), d - so - wi)
        days = ["2020-08-14", "2020-08-15", "2020-08-17", "2020-08-18", "2020-08-19"]
        self.assertEqual(max(days, key=lambda x: best[x]), "2020-08-14")
        self.assertEqual(round(best["2020-08-14"]), 54390)
        self.assertEqual(round(best["2020-08-18"]), 52013)


if __name__ == "__main__":
    unittest.main()
