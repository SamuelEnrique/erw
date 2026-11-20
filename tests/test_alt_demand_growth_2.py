"""Ruling alternative 2 of /explore/demand-growth (session 7709, 17 November 2026, branch wip/alt-demand-growth-2; not a
default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-demand-growth-2026-11-17.md, line 2): write a
growth for the newest year's months (March 2026 shows its MW and no growth)? On this branch the builder writes
growth_mw_mMM and growth_pct_mMM on the newest year's row for each whole month it holds (warehouse/derived/
demand_growth.py newest_month_growth), and the page reads a month at the newest year when that growth is held
(site/lib/explore/demandgrowth.ts latestOf). Pinned with the builder's own function on the rows the page reads
(replication/demand_growth/table_rows.csv, public, 16 November 2026), and with the page drawn by its own code on those
rows plus the rows the function writes (site/scripts/demand-growth-figures.mjs): ERCOT March +24.79 to +36.34 percent,
September +17.85 to +34.94, February +32.93 to +27.20; CAISO October +4.99 to +18.33, July -2.01 to +8.82; SPP September
+1.45 to +17.28.

    python -m unittest tests.test_alt_demand_growth_2 -v
"""

import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
ROWS = os.path.join(ROOT, "replication", "demand_growth", "table_rows.csv")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import demand_growth as dg  # noqa: E402


def tables():
    """{entity: {year: {variable: value}}} from the rows the page reads."""
    out = defaultdict(lambda: defaultdict(dict))
    with open(ROWS, encoding="utf-8") as f:
        for r in csv.DictReader(line for line in f if not line.startswith("#")):
            out[r["entity"]][int(r["ts_utc"][:4])][r["variable"]] = float(r["value"])
    return out


def added_rows():
    """The rows newest_month_growth writes on each area's newest year, as table rows."""
    rows = []
    for entity, years in tables().items():
        out = {y: dict(v) for y, v in years.items()}
        newest = max(out)
        before = set(out[newest])
        dg.newest_month_growth(out, newest)
        for k in sorted(set(out[newest]) - before):
            rows.append([entity, k, f"{newest}-01-01T00:00:00Z", repr(out[newest][k]), "pct" if k.startswith("growth_pct_") else "MW", ""])
    return rows


class TheBuilder(unittest.TestCase):
    def test_the_newest_years_months(self):
        out = {2019: {"avg_demand_mw_m03": 100.0, "avg_demand_mw_m04": 200.0}, 2025: {"avg_demand_mw": 1.0}, 2026: {"avg_demand_mw_m03": 125.0, "ytd_avg_demand_mw": 1.0}}
        dg.newest_month_growth(out, 2026)
        self.assertEqual((out[2026]["growth_pct_m03"], out[2026]["growth_mw_m03"]), (25.0, 25.0))
        self.assertNotIn("growth_pct_m04", out[2026])    # a month the newest year does not hold
        self.assertNotIn("growth_pct_m03", out[2025])

    def test_a_whole_newest_year_is_left_as_it_is(self):
        out = {2019: {"avg_demand_mw_m03": 100.0}, 2025: {"avg_demand_mw": 1.0, "avg_demand_mw_m03": 110.0}}
        dg.newest_month_growth(out, 2025)
        self.assertNotIn("growth_pct_m03", out[2025])

    def test_on_the_rows_the_page_reads(self):
        got = {(r[0], r[1]): round(float(r[3]), 2) for r in added_rows()}
        self.assertEqual(got[("eia930:ERCO", "growth_pct_m03")], 36.34)
        self.assertEqual(got[("eia930:ERCO", "growth_pct_m09")], 34.94)
        self.assertEqual(got[("eia930:ERCO", "growth_pct_m02")], 27.20)
        self.assertEqual(got[("eia930:CISO", "growth_pct_m10")], 18.33)
        self.assertEqual(got[("eia930:SWPP", "growth_pct_m09")], 17.28)
        self.assertEqual(got[("eia930:NYIS", "growth_pct_m07")], -10.49)
        self.assertEqual(got[("eia930:US48", "growth_pct_m08")], 12.16)
        self.assertEqual(len([k for k in got if k[1].startswith("growth_pct_")]), 80)   # 8 grids by 10 months


@unittest.skipUnless(shutil.which("node"), "node is not on this machine")
class ThePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        rows = os.path.join(cls.tmp, "eia930_demand_growth.csv")
        with open(ROWS, encoding="utf-8") as f:
            text = f.read()
        with open(rows, "w", encoding="utf-8", newline="") as f:
            f.write(text if text.endswith("\n") else text + "\n")
            csv.writer(f, lineterminator="\n").writerows(added_rows())
        out = os.path.join(cls.tmp, "drawn.json")
        p = subprocess.run(["node", "--no-warnings", "--import", "./scripts/tsx-register.mjs", "scripts/demand-growth-figures.mjs", rows, out, "--grids=ercot,caiso,spp"],
                           cwd=SITE, capture_output=True, text=True, timeout=600)
        if p.returncode != 0:
            raise AssertionError(p.stdout[-1500:] + p.stderr[-1500:])
        with open(out, encoding="utf-8") as f:
            cls.views = json.load(f)["views"]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def first(self, grid, window):
        v = next(v for v in self.views if v["q"].get("grid") == grid and v["q"].get("window") == window)
        return v["slots"]["h1.value"]

    def test_the_first_headline_at_the_newest_year(self):
        self.assertEqual(self.first("ercot", "m03"), "+36.34")
        self.assertEqual(self.first("ercot", "m09"), "+34.94")
        self.assertEqual(self.first("caiso", "m07"), "+8.82")
        self.assertEqual(self.first("spp", "m09"), "+17.28")

    def test_a_month_the_newest_year_does_not_hold_stays_at_the_last_whole_year(self):
        v = next(v for v in self.views if v["q"].get("grid") == "ercot" and v["q"].get("window") == "m12")
        self.assertIn("2025", v["slots"]["h1.label"])


if __name__ == "__main__":
    unittest.main()
