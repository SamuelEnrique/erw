"""Session 2252: PSE's power balance of Poland, a quarter hour.

Energy Research Warehouse (ERW). Tests warehouse/connectors/pse_poland.py on answers built here in PSE's form (figures
made up for the test, not PSE's): a quarter hour keyed by its UTC start, a blank figure with no row, the day in progress
left out; a field not in the map, an empty field that holds a figure, a UTC period given twice and a full page each
stopping the run; the year's address; the sector rule and the hold. No network.

    python -m unittest tests.test_session2252 -v
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import pse_poland as P  # noqa: E402
import build_coverage as B  # noqa: E402


def row(day="2025-03-30", utc="2025-03-30 01:15:00", period="01:00 - 01:15", **more):
    r = {k: 1.0 for k in P.FIELDS}
    r.update({k: None for k in P.EMPTY})
    r.update({"jgw2": None, "dtime": "x", "dtime_utc": utc, "period": "x", "period_utc": period, "business_date": day,
              "publication_ts": "x", "publication_ts_utc": "x", "demand": 15000.5})
    r.update(more)
    return r


def answer(rows):
    return json.dumps({"value": rows}).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        out = P.parse(answer([row(), row(day="2025-03-31", utc="2025-03-31 00:15:00", period="00:00 - 00:15")]), 2025, {}, "2025-03-31", counts)
        got = {(r["variable"], r["ts_utc"]): r for r in out}
        d = got[("demand", "2025-03-30T01:00:00Z")]
        self.assertEqual((d["value"], d["unit"], d["freq"], d["geo"], d["x_field"], d["x_business_date"]),
                         (15000.5, "MW", "PT15M", "PL", "demand", "2025-03-30"))
        self.assertNotIn(("generation_jgw2", "2025-03-30T01:00:00Z"), got)
        self.assertEqual((counts["day in progress"], counts["jgw2 blank"]), (1, 1))
        self.assertEqual(len(out), len(P.FIELDS) - 1)

    def test_stops(self):
        for content, words in [(answer([row(newfield=3)]), "not in the map"),
                               (answer([row(jgo=2.0)]), "now holds a figure"),
                               (answer([row(), row()]), "given twice"),
                               (answer([row(period="01:15 - 01:30")]), "unlike its stamp")]:
            with self.assertRaises(RuntimeError) as c:
                P.parse(content, 2025, {}, "2026-01-01", {})
            self.assertIn(words, str(c.exception))
        old = P.PAGE_ROWS
        try:
            P.PAGE_ROWS = 1
            with self.assertRaises(RuntimeError) as c:
                P.parse(answer([row()]), 2025, {}, "2026-01-01", {})
            self.assertIn("fills its page", str(c.exception))
        finally:
            P.PAGE_ROWS = old

    def test_url(self):
        self.assertEqual(P.url_of(2025), "https://api.raporty.pse.pl/api/his-wlk-cal?%24filter=business_date%20ge%20%272025-01-01%27"
                                         "%20and%20business_date%20le%20%272025-12-31%27&%24first=40000")


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(P.TABLE), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {P.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
