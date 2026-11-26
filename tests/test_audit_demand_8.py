"""Session 10214 (chain 710, part D: the demand page audited, docs/reviews/demand-model-audit-2026-11-26.md, finding 7).
Not for landing: it shows a figure for the owner's ruling.

Every growth on /demand is against one year, 2019 ("the last whole year before the pandemic in the file"). The same
EIA workbooks hold 2018 whole, and the builder reads it (for the screen's median) and writes nothing of it. On 2018,
CAISO's and MISO's average demand of 2025 is below the base, where on 2019 it is above. Runs where EIA's workbook
extract is held (the data machine's warehouse/raw, or a folder named by ERW_AUDIT_RAW). The extract is EIA's "Demand"
column; the page reads "Adjusted demand", which differs in a few hours (finding 1), not in the sign.
"""
import glob
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))


def extract(name):
    roots = [os.path.join(ROOT, "warehouse", "raw", "eia930_emissions")]
    if os.environ.get("ERW_AUDIT_RAW"):
        roots.insert(0, os.environ["ERW_AUDIT_RAW"])
    for r in roots:
        hits = sorted(glob.glob(os.path.join(r, "*", name)))
        if hits:
            return hits[-1]
    return None


class OneBaseYear(unittest.TestCase):
    def test_on_2018_caiso_and_miso_fell(self):
        hist = None
        for d0 in (os.environ.get("ERW_AUDIT_TABLES"), os.path.join(ROOT, "warehouse", "output")):
            if d0 and os.path.exists(os.path.join(d0, "eia930_all_history.csv")):
                hist = os.path.join(d0, "eia930_all_history.csv")
        if not extract("ciso_hours.csv") or not hist:
            self.skipTest("EIA's workbook extract or the six-month file of 2018 is not held on this machine")
        import pandas as pd
        import impossible_hours
        site = json.load(open(os.path.join(ROOT, "site", "data", "demand_growth.json"), encoding="utf-8"))
        h = pd.read_csv(hist, comment="#", usecols=["entity", "variable", "ts_utc", "value"])
        h = h[h["variable"] == "demand_mw"]
        for ba, tz in (("ciso", "America/Los_Angeles"), ("miso", "America/Chicago")):
            x = pd.read_csv(extract(f"{ba}_hours.csv"), comment="#", usecols=["ts_utc", "demand_mwh"])
            first = h[h["entity"] == f"eia930:{ba.upper()}"].rename(columns={"value": "demand_mwh"})[["ts_utc", "demand_mwh"]]
            x = pd.concat([first, x])   # January to June 2018 from EIA's six-month file, then the workbook's extract
            x["ts_utc"] = pd.to_datetime(x["ts_utc"], utc=True)
            d = x.drop_duplicates("ts_utc", keep="last").set_index("ts_utc")["demand_mwh"].sort_index()
            d = d.reindex(pd.date_range(d.index.min(), d.index.max(), freq="h"))
            used = impossible_hours.screen(d, 0.25)
            y18 = used[used.index.tz_convert(tz).year == 2018]
            self.assertGreaterEqual(y18.notna().sum(), 0.95 * 8760, f"{ba}: 2018 is a whole year in EIA's file")
            a18 = float(y18.mean())
            page = site["areas"][ba.upper()]["years"]
            self.assertLess(page["2025"]["avg_demand_mw"], a18, f"{ba}: 2025 is below 2018")
            self.assertGreater(page["2025"]["avg_demand_growth_since_2019_pct"], 2.0, f"{ba}: and well above 2019")


if __name__ == "__main__":
    unittest.main()
