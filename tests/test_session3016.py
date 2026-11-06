"""Session 3016 (chain 164): findings across two families (deep/cross.py).

Energy Research Warehouse (ERW). Small tables written here; no warehouse file, no network, no database.
"""

import os
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings", "deep"))
import cross  # noqa: E402
import hunt_measures as hm  # noqa: E402


def write(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        frame.to_csv(f, index=False, lineterminator="\n")


def tables(d):
    rng = np.random.default_rng(3016)
    months = pd.date_range("2019-01-01", "2021-12-01", freq="MS").strftime("%Y-%m-%dT00:00:00Z")
    sb = []
    for sbe, ba, _ in cross.GRIDS.values():
        for var in ("battery_operating_mw", "battery_mwh_per_solar_mw"):
            sb.append(pd.DataFrame({"entity": sbe, "variable": var, "ts_utc": months, "value": np.round(rng.uniform(0.1, 900, len(months)), 3)}))
    write(d, cross.SB, pd.concat(sb))
    days = pd.date_range("2019-01-01", "2021-12-31", freq="D").strftime("%Y-%m-%dT00:00:00Z")
    write(d, cross.DD, pd.concat([pd.DataFrame({"entity": ba, "variable": "demand_mwh", "ts_utc": days, "value": np.round(rng.uniform(4e5, 9e5, len(days)), 0)})
                                  for _, ba, _ in cross.GRIDS.values()]))
    write(d, cross.OP, pd.DataFrame({"technology": rng.choice(["Solar Photovoltaic", "Batteries"], 300), "nameplate_mw": np.round(rng.uniform(5, 300, 300), 1),
                                     "operating_year": rng.integers(2010, 2025, 300)}))
    write(d, cross.LQ, pd.DataFrame({"type_clean": rng.choice(["Solar", "Battery"], 400), "mw_1": np.round(rng.uniform(5, 500, 400), 1),
                                     "q_year": rng.integers(2010, 2025, 400)}))


ARGS = {"battery_per_peak": [cross.SB, cross.DD], "built_per_asked": [cross.OP, cross.LQ], "storage_per_solar": [cross.SB]}


class Cross(unittest.TestCase):
    def test_every_candidate_reproduces_from_the_tables(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            hm.clear_cache()
            for P in cross.CANDIDATES:
                got = P["_fn"](d)
                for region in sorted({r["region"] for r in got["rows"]}):
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                    path = os.path.join(d, f"r_{P['name']}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    r = subprocess.run([sys.executable, "-I", path] + [os.path.join(d, t + ".csv") for t in ARGS[P["name"]]], capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, (P["name"], r.stderr))
                    printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                    self.assertEqual(sorted(printed), sorted(want), (P["name"], region))
                    for y in want:
                        self.assertAlmostEqual(printed[y], want[y], places=5, msg=(P["name"], region, y))
                    self.assertTrue(all("\n" not in b for b in P["reproduce"](region)["do"].strip("\n").split("\n\n")), P["name"])
            hm.clear_cache()


if __name__ == "__main__":
    unittest.main()
