"""Audit of the Grid tool, finding 5 (session 10205, docs/reviews/grid-model-audit-2026-11-26.md): what "now" is. The
Now sentence names four hours in one paragraph (demand, the mix, the exchange, carbon); carbon comes from EIA's CO2
workbooks, days behind the demand hour, and the sentence did not say so. The Clean tab's "Carbon intensity now, ranked"
ranks each ISO at its own latest hour, which can be days apart.

1. Against the warehouse (passes on main, skipped where the table is not on the machine): carbon_intensity_hourly's
   newest hour is more than a day before the table's own retrieval time, and the ISOs' newest hours are not all one.
2. The fix on this branch (fails on main): the sentence says the carbon hour is older than the demand hour, and the
   ranked table's title says each ISO is at its latest hour."""
import datetime as dt
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.environ.get("ERW_AUDIT_OUTPUT_DIR", os.path.join(ROOT, "warehouse", "output"))
ISOS = [f"eia930:{c}" for c in ("CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP")]


class WhatNowIs(unittest.TestCase):
    def test_carbon_is_days_behind_and_uneven(self):
        path = os.path.join(OUT, "carbon_intensity_hourly.csv")
        if not os.path.exists(path):
            self.skipTest("carbon_intensity_hourly is not on this machine")
        import pandas as pd
        n, retrieved = 0, None
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                n += 1
                if retrieved is None and "Retrieved: " in line:
                    retrieved = dt.datetime.strptime(line.split("Retrieved: ")[1][:16], "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc)
        self.assertIsNotNone(retrieved)
        newest = {}
        cut = (retrieved - dt.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        for c in pd.read_csv(path, skiprows=n, usecols=["entity", "variable", "ts_utc"], chunksize=400_000):
            c = c[(c["variable"] == "intensity_generation") & c["entity"].isin(ISOS) & (c["ts_utc"] >= cut)]
            for e, t in c.groupby("entity")["ts_utc"].max().items():
                newest[e] = max(newest.get(e, ""), t)
        self.assertEqual(len(newest), 7)
        latest = dt.datetime.strptime(max(newest.values()), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
        self.assertGreater(retrieved - latest, dt.timedelta(hours=24))
        self.assertGreater(len(set(newest.values())), 1)

    def test_the_words_say_how_old(self):
        with open(os.path.join(ROOT, "site", "components", "grid", "NowView.tsx"), encoding="utf-8") as f:
            self.assertIn("its CO2 estimates come days after the hour, so this hour is older than the hour of demand named first", f.read())
        with open(os.path.join(ROOT, "site", "components", "grid", "Emissions.tsx"), encoding="utf-8") as f:
            t = f.read()
        self.assertNotIn('title="Carbon intensity now, ranked"', t)
        self.assertIn("each ISO's latest hour, ranked", t)


if __name__ == "__main__":
    unittest.main()
