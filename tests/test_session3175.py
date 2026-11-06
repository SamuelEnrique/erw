"""Session 3175 (chain 166): coal and uranium (deep/coal.py).

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
import coal  # noqa: E402
import hunt_measures as hm  # noqa: E402


class Coal(unittest.TestCase):
    def test_every_candidate_reproduces_from_its_table(self):
        rng = np.random.default_rng(3175)
        years = [f"{y}-01-01T00:00:00Z" for y in range(2003, 2010)]
        with tempfile.TemporaryDirectory() as d:
            frames = {}
            for name, (table, kind, num, den, scale) in coal.SPEC.items():
                for ent, var in [num] + ([den] if den else []):
                    ts = years if (ent, var) != ("eia_uranium:us", "purchased_us_origin") else years[1:]
                    frames.setdefault(table, []).append(pd.DataFrame({"entity": ent, "variable": var, "ts_utc": ts, "value": np.round(rng.uniform(10, 900, len(ts)), 3)}))
            for table, parts in frames.items():
                with open(os.path.join(d, table + ".csv"), "w", encoding="utf-8", newline="\n") as f:
                    f.write("# a test table\n")
                    pd.concat(parts).drop_duplicates(["entity", "variable", "ts_utc"]).to_csv(f, index=False, lineterminator="\n")
            hm.clear_cache()
            for P in coal.CANDIDATES:
                got = P["_fn"](d)
                region = got["rows"][0]["region"]
                want = {r["year"]: r["value"] for r in got["rows"]}
                path = os.path.join(d, f"r_{P['name']}.py")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(P["reproduce"](region)["py"])
                r = subprocess.run([sys.executable, "-I", path, os.path.join(d, coal.SPEC[P["name"]][0] + ".csv")], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, (P["name"], r.stderr))
                printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                self.assertEqual(sorted(printed), sorted(want), P["name"])
                for y in want:
                    self.assertAlmostEqual(printed[y], want[y], places=5, msg=(P["name"], y))
                self.assertTrue(all("\n" not in b for b in P["reproduce"](region)["do"].strip("\n").split("\n\n")), P["name"])
            hm.clear_cache()


if __name__ == "__main__":
    unittest.main()
