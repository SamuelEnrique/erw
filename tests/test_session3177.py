"""Session 3177 (chain 166): the grids' stress (deep/stress.py).

Energy Research Warehouse (ERW). A small table written here; no warehouse file, no network, no database.
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
import hunt_measures as hm  # noqa: E402
import stress  # noqa: E402


class Stress(unittest.TestCase):
    def test_every_candidate_reproduces_from_the_table(self):
        rng = np.random.default_rng(3177)
        years = [f"{y}-01-01T00:00:00Z" for y in range(2019, 2026)]
        rows = []
        for ent in ("iso:ercot", "iso:caiso"):
            for num, den, _ in stress.SPEC.values():
                for v in [num] + ([den] if den else []):
                    rows.append(pd.DataFrame({"entity": ent, "variable": v, "ts_utc": years, "value": np.round(rng.uniform(1, 900, len(years)), 3)}))
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, stress.T + ".csv"), "w", encoding="utf-8", newline="\n") as f:
                f.write("# a test table\n")
                pd.concat(rows).drop_duplicates(["entity", "variable", "ts_utc"]).to_csv(f, index=False, lineterminator="\n")
            hm.clear_cache()
            for P in stress.CANDIDATES:
                got = P["_fn"](d)
                for region in sorted({r["region"] for r in got["rows"]}):
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                    path = os.path.join(d, f"r_{P['name']}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    r = subprocess.run([sys.executable, "-I", path, os.path.join(d, stress.T + ".csv")], capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, (P["name"], r.stderr))
                    printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                    self.assertEqual(sorted(printed), sorted(want), (P["name"], region))
                    for y in want:
                        self.assertAlmostEqual(printed[y], want[y], places=5, msg=(P["name"], region, y))
            hm.clear_cache()


if __name__ == "__main__":
    unittest.main()
