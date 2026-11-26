"""Audit of the Grid tool, finding 6 (session 10205, docs/reviews/grid-model-audit-2026-11-26.md): the network snapshot the
Grid tool's exchange figures come from (warehouse/derived/grid_network.py, daily, and network_hourly.py, hourly) takes
every interchange report as filed, with no test that a value is one a tie could carry. The twelve months' figures
(warehouse/derived/ba_supply.py) set aside a pair-day further than impossible_hours.MADS median absolute deviations from
its pair's median. In the table's hours (13 September to 3 November 2026) two reports are above 20,000 MW, both SPP's
of its MISO tie (4 and 6 October); the pair rule reads MISO's report of that tie, so neither reached a figure. Adding a
screen would move a figure only in an hour such a report is read: the owner's ruling. This branch only shows it.

1. In the code (passes on main): ba_supply.py screens; neither snapshot builder does.
2. In the warehouse (passes on main, skipped without eia930_all_interchange): reports above 20,000 MW exist."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.environ.get("ERW_AUDIT_OUTPUT_DIR", os.path.join(ROOT, "warehouse", "output"))
DERIVED = os.path.join(ROOT, "warehouse", "derived")


class NoScreen(unittest.TestCase):
    def test_the_snapshot_builders_take_every_report(self):
        with open(os.path.join(DERIVED, "ba_supply.py"), encoding="utf-8") as f:
            self.assertIn("def screen(", f.read())
        for name in ("grid_network.py", "network_hourly.py"):
            with open(os.path.join(DERIVED, name), encoding="utf-8") as f:
                t = f.read()
            self.assertIsNone(re.search(r"MADS|def screen|impossible_hours|screen_", t), name)

    def test_reports_no_tie_carries(self):
        path = os.path.join(OUT, "eia930_all_interchange.csv")
        if not os.path.exists(path):
            self.skipTest("eia930_all_interchange is not on this machine")
        import pandas as pd
        n = 0
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                n += 1
        big = 0
        for c in pd.read_csv(path, skiprows=n, usecols=["value"], chunksize=400_000):
            big += int((c["value"].abs() > 20000).sum())
        self.assertGreater(big, 0)


if __name__ == "__main__":
    unittest.main()
