"""Session 11408 (chain 770, part C): /demand, the other choice of the demand audit's finding 5
(docs/reviews/demand-model-audit-2026-11-26.md; its test branch wip/audit-demand-6, carried over here and turned to the
new rule). Not for landing until the owner rules.

The rule on this branch: the hours left out ("Hours left out for ERCOT: ... 48 blank") are counted from 2019 to the
newest hour used, not to the workbook's last row, so EIA's unfilled last day is not counted. Measured by running the
builder on this machine's EIA workbooks of 4 October 2026 (written only into the worktree): blank hours ERCOT 48 to 24,
CAISO 48 to 24, PJM 27 to 3, MISO, SPP, NYISO, ISO-NE and the Lower 48 24 to 0; no other figure of the file moves (0 of
every year's and peak's figures differ). The site file is rebuilt at landing by the desk; it then records
counted_to "newest hour used".

1. warehouse/derived/demand_growth.py counted_hours on a small series: an hour after the newest used is not counted.
2. The replication counts the same window.
3. Once the site file is rebuilt, the printed count holds no hour after the newest month (the audit's measure, turned)."""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))


class BlankHoursToTheNewestUsed(unittest.TestCase):
    def test_counted_hours_stop_at_the_newest_hour_used(self):
        import numpy as np
        import pandas as pd
        import demand_growth as dg
        idx = pd.date_range("2019-01-01T06:00:00Z", periods=8, freq="h")
        raw = pd.Series([100.0, np.nan, 102.0, 101.0, 100.0, np.nan, np.nan, np.nan], index=idx)
        used = raw.copy()
        used.iloc[1] = np.nan
        used = used.dropna()
        got = dg.counted_hours(raw, used, "America/Chicago")
        self.assertEqual(got.index.max(), idx[4])            # the three blank hours after the newest used are not counted
        self.assertEqual(int(got.isna().sum()), 1)           # the blank inside the record is

    def test_the_replication_counts_the_same_window(self):
        with open(os.path.join(ROOT, "replication", "demand", "replicate.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("counts = screen(hours, first, max(used) + dt.timedelta(hours=1))[1]", s)

    def test_the_site_file_once_rebuilt(self):
        with open(os.path.join(ROOT, "site", "data", "demand_growth.json"), encoding="utf-8") as f:
            site = json.load(f)
        if site.get("counted_to") != "newest hour used":
            self.skipTest("the site file is rebuilt at landing by the desk")
        for ba, a in site["areas"].items():
            ys = a["years"]
            inside = sum(r["hours_in_year"] - r["hours_used"] for r in ys.values() if "hours_used" in r)
            newest = ys[max(ys)]
            inside += newest["ytd_hours_in_window"] - newest["ytd_hours_used"]
            printed = a["screened"]["blank"] + a["screened"]["not_positive"] + a["screened"]["jumps"]
            self.assertLessEqual(printed - inside, 1, ba)


if __name__ == "__main__":
    unittest.main()
