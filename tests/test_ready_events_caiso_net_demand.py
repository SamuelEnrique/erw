"""Session 11407 (chain 770 part C), readied from session 10225's test of the events audit's finding 4
(wip/audit-events-4, docs/reviews/events-model-audit-2026-11-26.md): /events/caiso-heat-2020 now prints a figure of
net demand, each Pacific day's highest hour of California's demand less solar and wind from the event's region file
(site/lib/countryfiles.ts netDemandPeaks), for 14 to 19 August, and the window's highest day by it: 14 August, the
first outage day, at 54,390 MW against 52,013 on the 18th. CAISO's gross highest hours stay as they were, 46,024 MW on
the 14th and 46,643 on the 18th, 619 MW apart. For the owner's ruling, not for landing alone.
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
    def test_the_page_prints_net_demand(self):
        with open(os.path.join(ROOT, "site", "app", "events", "caiso-heat-2020", "page.tsx"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertIn('import { eventRegionsFile, netDemandPeaks } from "@/lib/countryfiles";', s)
        self.assertIn('netDemandPeaks(file, "CAL", "America/Los_Angeles")', s)
        self.assertIn("<NetDemand />", s)
        self.assertIn("<strong>By demand less solar and wind.</strong>", s)
        self.assertIn('const NET_DAYS = ["2020-08-14", "2020-08-15", "2020-08-16", "2020-08-17", "2020-08-18", "2020-08-19"];', s)
        self.assertIn("is given just below.", s)
        self.assertNotIn("is not on this page.", s)
        self.assertIn('find(rows, E, "demand_max_pct_vs_baseline", "2020-08-14")', s, "the gross comparison stays")
        self.assertNotIn(chr(0x2014), s)

    def test_the_lib_rule(self):
        with open(os.path.join(ROOT, "site", "lib", "countryfiles.ts"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertIn("export function netDemandPeaks(file: EventRegionsFile, code: string, timeZone: string): NetPeak[]", s)
        self.assertIn("a.best && a.n >= 23 && a.held === a.n", s, "a day is given only when the file holds all its hours")
        self.assertIn("d - s - w", s)

    def test_the_note_says_it(self):
        with open(os.path.join(ROOT, "docs", "methods", "events.md"), encoding="utf-8") as fh:
            self.assertIn("the window's highest day by that measure, 14 August at 54,390 MW", fh.read())

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
        best, n, held = {}, {}, {}
        for i, d in enumerate(cal["demand_mw"]):
            day = (t0 + dt.timedelta(hours=i - 7)).strftime("%Y-%m-%d")  # Pacific daylight time all window
            n[day] = n.get(day, 0) + 1
            so, wi = cal["gen"]["solar"][i], cal["gen"]["wind"][i]
            if None not in (d, so, wi):
                held[day] = held.get(day, 0) + 1
                best[day] = max(best.get(day, 0), d - so - wi)
        self.assertEqual([round(best[d]) for d in ("2020-08-14", "2020-08-15", "2020-08-16", "2020-08-17", "2020-08-18", "2020-08-19")],
                         [54390, 52166, 50324, 51456, 52013, 50210])
        window = [d for d in best if "2020-08-10" <= d <= "2020-08-24" and n[d] >= 23 and held.get(d) == n[d]]
        self.assertEqual(len(window), 15, "every day of the window is whole in the file")
        self.assertEqual(max(window, key=best.get), "2020-08-14", "the first outage day is the window's highest by net demand")


if __name__ == "__main__":
    unittest.main()
