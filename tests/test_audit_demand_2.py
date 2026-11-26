"""Session 10214 (chain 710, part D: the demand page audited, docs/reviews/demand-model-audit-2026-11-26.md, finding 1,
the figure). Not for landing: it shows what MISO's 2025 peak would be on MISO's own reports, for the owner's ruling.

MISO's highest hour of 2025 in site/data/demand_growth.json (120,343 MW, the hour from 20:00 UTC on 24 July 2025) is
EIA's estimate in its Adjusted demand: MISO reported nothing that day. On MISO's own reports (EIA's "Demand"), with the
page's screen, the highest hour of 2025 is 118,106 MW (29 July 2025), +1.29 percent on 2019 against the page's +3.21.
Runs where EIA's workbook extract is held (the data machine's warehouse/raw, or a folder named by ERW_AUDIT_RAW).
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


class MisoPeakOnItsOwnReports(unittest.TestCase):
    def test_the_2025_peak_on_misos_own_reports(self):
        path = extract("miso_hours.csv")
        if not path:
            self.skipTest("EIA's workbook extract is not held on this machine")
        import pandas as pd
        import impossible_hours
        x = pd.read_csv(path, comment="#", usecols=["ts_utc", "demand_mwh"])
        x["ts_utc"] = pd.to_datetime(x["ts_utc"], utc=True)
        d = x.drop_duplicates("ts_utc").set_index("ts_utc")["demand_mwh"].sort_index()
        d = d[d.index >= pd.Timestamp("2018-01-01", tz="UTC")]
        used = impossible_hours.screen(d, 0.25)
        local = used.index.tz_convert("America/Chicago")
        y25 = used[local.year == 2025].dropna()
        y19 = used[local.year == 2019].dropna()
        own25, own19 = round(float(y25.max()), 1), round(float(y19.max()), 1)
        site = json.load(open(os.path.join(ROOT, "site", "data", "demand_growth.json"), encoding="utf-8"))
        page25 = site["areas"]["MISO"]["years"]["2025"]["peak_demand_mw"]
        page19 = site["areas"]["MISO"]["years"]["2019"]["peak_demand_mw"]
        self.assertEqual(page25, 120343.0)
        self.assertEqual(own19, page19, "2019's peak is MISO's own report in both")
        self.assertEqual(own25, 118106.0)
        self.assertEqual(y25.idxmax().strftime("%Y-%m-%dT%H:%M:%SZ"), "2025-07-29T21:00:00Z")
        self.assertEqual(round(100 * (own25 - own19) / own19, 2), 1.29)
        self.assertEqual(site["areas"]["MISO"]["years"]["2025"]["peak_demand_growth_since_2019_pct"], 3.21)


if __name__ == "__main__":
    unittest.main()
