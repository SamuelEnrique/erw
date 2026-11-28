"""Session 11408, readied for the owner's ruling (weekend page part 3.4, generator choice 7; the generator audit of 20
November, finding 7, docs/reviews/generator-model-audit-2026-11-20.md, carried from wip/audit-generator-7): output per
MW over the month's mid-point nameplate, the mean of this month's start and the next month's.

1. warehouse/derived/merchant_revenue.py, mid_capacity: on a small fleet table, a plant that starts on the 1st of the
   next month counts half in this one; a plant retired then likewise.
2. Measured from the page's public hourly file (ERCOT solar, last twelve months October 2025 to September 2026, the
   file's month-start nameplates): USD 59.5086 per kW at the mid-point nameplate, against 59.8523. The site's snapshot
   is rebuilt at landing by the desk."""
import csv
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import merchant_revenue as mr  # noqa: E402

CSV = os.path.join(ROOT, "site", "public", "seller", "erw_2026_generator_hourly.csv")


class MidNameplate(unittest.TestCase):
    def test_mid_capacity(self):
        gens = pd.DataFrame({"balancing_authority": ["ERCO"] * 3, "energy_source": ["SUN"] * 3, "nameplate_mw": [100.0, 50.0, 20.0],
                             "start": pd.to_datetime(["2020-01-01", "2026-10-01", "2020-01-01"]),
                             "ret": pd.to_datetime([None, None, "2026-10-01"])})
        self.assertEqual(mr.next_month("2026-12"), "2027-01")
        self.assertAlmostEqual(mr.capacity(gens, "ERCO", "SUN", "2026-09"), 120.0)
        self.assertAlmostEqual(mr.mid_capacity(gens, "ERCO", "SUN", "2026-09"), (120.0 + 150.0) / 2)

    def test_the_default_case_measured(self):
        with open(CSV, encoding="utf-8") as f:
            rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
        ix = {c: i for i, c in enumerate(rows[0])}
        h = [dict(m=r[ix["local_month"]], p=float(r[ix["price_usd_mwh"]]), mwh=float(r[ix["solar_mwh"]]), cap=float(r[ix["nameplate_mw"]]),
                  l12=r[ix["in_last_twelve"]] == "1") for r in rows[1:] if r[ix["solar_mwh"]] != "-99999"]
        cap = {}
        for x in h:
            cap.setdefault(x["m"], x["cap"])
        ms = sorted(cap)
        mid = {m: (cap[m] + cap[ms[i + 1]]) / 2 for i, m in enumerate(ms[:-1])}
        l12 = [x for x in h if x["l12"]]
        self.assertAlmostEqual(sum(x["mwh"] / x["cap"] * x["p"] for x in l12) / 1000, 59.8523, places=3)
        self.assertAlmostEqual(sum(x["mwh"] / mid[x["m"]] * x["p"] for x in l12) / 1000, 59.5086, places=3)

    def test_the_note(self):
        with open(os.path.join(ROOT, "docs", "methods", "generator_earns_algorithm.md"), encoding="utf-8") as f:
            self.assertIn("the mean of this month's first day and the next month's (`mid_capacity`)", f.read())


if __name__ == "__main__":
    unittest.main()
