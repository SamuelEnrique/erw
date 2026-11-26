"""Session 10225 (chain 710, the events audit, finding 4): /events/caiso-heat-2020 measures the outage days by each
day's highest hour of CAISO's demand served against its baseline, and prints no figure of demand less solar and wind,
the evening measure the rotating outages of 14 and 15 August came in. By that measure (California, the event's region
file) 14 August was the highest of 14 to 19 August, 54,390 MW against 52,013 on the 18th; CAISO's gross highest hours
were 46,024 MW on the 14th and 46,643 on the 18th, 619 MW apart, a gap the shed load (not held) may exceed. Not fixed:
a net-demand figure on the page is a figure added, so the ruling is the owner's (docs/reviews/events-model-audit-2026-11-26.md).
These tests pass on main: they show the finding, not a fix.
"""
import csv
import datetime as dt
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROWS = os.path.join(ROOT, "replication", "events", "window_rows.csv")
FILE = os.path.join(ROOT, "site", "data", "regions", "events", "caiso_heat_2020.json")


class TheOutageDaysByNetDemand(unittest.TestCase):
    def test_the_page_prints_no_net_demand(self):
        with open(os.path.join(ROOT, "site", "app", "events", "caiso-heat-2020", "page.tsx"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertNotIn("net demand", s.lower().replace("demand less solar and wind", ""))
        self.assertIn('find(rows, E, "demand_max_pct_vs_baseline", "2020-08-14")', s)

    @unittest.skipUnless(os.path.exists(ROWS), "the replication's public rows are not in this checkout")
    def test_the_gross_peaks_are_619_mw_apart(self):
        with open(ROWS, encoding="utf-8") as fh:
            rows = {r["ts_utc"][:10]: float(r["value"]) for r in csv.DictReader(l for l in fh if not l.startswith("#"))
                    if r["event"] == "caiso_heat_2020" and r["entity"] == "eia930:CISO" and r["variable"] == "demand_max_mw"}
        self.assertEqual((rows["2020-08-14"], rows["2020-08-18"]), (46024.0, 46643.0))

    @unittest.skipUnless(os.path.exists(FILE), "the region file is not in this checkout")
    def test_by_net_demand_the_14th_leads(self):
        with open(FILE, encoding="utf-8") as fh:
            f = json.load(fh)
        cal = f["regions"]["CAL"]
        t0 = dt.datetime.fromisoformat(f["hours"]["start"].replace("Z", "+00:00"))
        best = {}
        for i, d in enumerate(cal["demand_mw"]):
            so, wi = cal["gen"]["solar"][i], cal["gen"]["wind"][i]
            if None not in (d, so, wi):
                day = (t0 + dt.timedelta(hours=i - 7)).strftime("%Y-%m-%d")
                best[day] = max(best.get(day, 0), d - so - wi)
        self.assertEqual([round(best[d]) for d in ("2020-08-14", "2020-08-15", "2020-08-17", "2020-08-18", "2020-08-19")],
                         [54390, 52166, 51456, 52013, 50210])


if __name__ == "__main__":
    unittest.main()
