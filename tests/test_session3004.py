"""Session 3004 (chain 164): the findings hunt, family demand (deep/demand.py), and the builder's ranking by change.

Energy Research Warehouse (ERW). Small tables written here; no warehouse file, no network, no database.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings", "deep"))
sys.path.insert(0, os.path.dirname(__file__))
import builder  # noqa: E402
import demand  # noqa: E402
import hunt  # noqa: E402
import hunt_measures as hm  # noqa: E402
from test_session3001 import synthetic  # noqa: E402


def write(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        frame.to_csv(f, index=False, lineterminator="\n")


def tables(d):
    rng = np.random.default_rng(3004)
    days = pd.date_range("2019-01-01", "2020-12-31", freq="D").strftime("%Y-%m-%dT00:00:00Z")
    rows = []
    for ba in ("ERCO", "SOCO"):
        v = rng.uniform(800, 1600, len(days)) * 1000
        v[5] = 1.0                                       # a fault: a day far under a third of the year's median
        rows.append(pd.DataFrame({"entity": f"eia930:{ba}", "variable": "demand_mwh", "ts_utc": days, "value": np.round(v, 1)}))
    write(d, "eia930_daily_demand", pd.concat(rows))
    for y in (2019, 2020):
        hours = pd.date_range(f"{y}-01-01T00:00:00Z", f"{y}-12-31T23:00:00Z", freq="h").strftime("%Y-%m-%dT%H:%M:%SZ")
        parts = []
        for ent, node in (("eia930_subba:PJM:DOM", "Dominion Virginia Power zone (PJM)"), ("eia930_subba:ERCO:FWES", "Far West (ERCO)")):
            v = rng.uniform(3000, 9000, len(hours))
            v[10] = 90000.0                              # a fault: over three times the year's median
            parts.append(pd.DataFrame({"entity": ent, "variable": "demand_mw", "ts_utc": hours, "value": np.round(v, 0), "node": node}))
        write(d, f"eia930_subba_demand_hourly_{y}", pd.concat(parts))


class Reproduce(unittest.TestCase):
    def test_every_candidate_reproduces_from_the_tables(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            hm.clear_cache()
            for P in demand.CANDIDATES:
                got = P["_fn"](d)
                for region in sorted({r["region"] for r in got["rows"] if r["value"] is not None}):
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region and r["value"] is not None}
                    path = os.path.join(d, f"r_{P['name']}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    files = ([os.path.join(d, "eia930_daily_demand.csv")] if P["name"] in demand.PY_DAILY_BODY
                             else [os.path.join(d, f"eia930_subba_demand_hourly_{y}.csv") for y in (2019, 2020)])
                    r = subprocess.run([sys.executable, "-I", path] + files, capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, (P["name"], r.stderr))
                    printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                    self.assertEqual(sorted(printed), sorted(want), (P["name"], region))
                    for y in want:
                        self.assertAlmostEqual(printed[y], want[y], places=5, msg=(P["name"], region, y))
                    do = P["reproduce"](region)["do"]
                    self.assertNotIn("///", do)
                    self.assertIn("destring value, replace force", do)
                    self.assertTrue(all("\n" not in b for b in do.strip("\n").split("\n\n")), P["name"])
            hm.clear_cache()

    def test_the_faults_are_dropped(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            hm.clear_cache()
            n = {(r["region"], r["year"]): r["n"] for r in demand.mean_day(d)["rows"]}
            m = {(r["region"], r["year"]): r["n"] for r in demand.sub_mean(d)["rows"]}
            hm.clear_cache()
        self.assertEqual(n[("ercot_ba", 2019)], 364)
        self.assertEqual(m[("pjm_sub_DOM", 2020)], 8778)     # Eastern 2020: 8,784 hours less the 5 that fall in UTC 2021 (no table here), less the fault


class Rank(unittest.TestCase):
    def test_a_candidate_ranked_by_change_keeps_the_largest_region(self):
        P = builder.candidate("t", "testfam", synthetic([("ba_small", 1.0), ("ba_big", 50.0)]), "MW", 0, 8000, 1.0, "T", "t", lambda w: w,
                              "Limits.", lambda region: {"py": '"""x"""\n', "do": "* x\n"}, consequence=2)
        P["rank"] = lambda c: abs(c["change"])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(builder, "DOCS", os.path.join(d, "docs")), \
                mock.patch.object(hunt, "blocked_grids", lambda meta_dir=None: set()), mock.patch.object(builder, "MAX_PER_CANDIDATE", 1):
            s = builder.run("testfam", [P], d, dry_run=True, log=lambda m: None, out_root=os.path.join(d, "runs"))
        self.assertEqual([r["region"] for r in s["results"] if r["drafted"]], ["ba_big"])


if __name__ == "__main__":
    unittest.main()
