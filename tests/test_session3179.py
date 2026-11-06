"""Session 3179 (chain 166): the rest of the US tables (deep/other_us.py).

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
import hunt_measures as hm  # noqa: E402
import other_us as ou  # noqa: E402


def write(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        frame.to_csv(f, index=False, lineterminator="\n")


class OtherUS(unittest.TestCase):
    def test_every_candidate_reproduces_from_its_table(self):
        rng = np.random.default_rng(3179)
        months = pd.date_range("2015-01-01", "2017-12-01", freq="MS").strftime("%Y-%m-%dT00:00:00Z")
        years = [f"{y}-01-01T00:00:00Z" for y in range(2015, 2019)]
        with tempfile.TemporaryDirectory() as d:
            write(d, ou.PE, pd.concat([pd.DataFrame({"entity": e, "variable": "production", "ts_utc": months, "value": np.round(rng.uniform(lo, hi, len(months)), 3)})
                                       for e, lo, hi in (("eia:REPRBUS", 100, 900), ("eia:TEPRBUS", 5000, 9000))]))
            write(d, ou.SEDS, pd.concat([pd.DataFrame({"entity": f"eia_seds_res:{s}:{st}", "variable": "expenditures", "ts_utc": years, "value": np.round(rng.uniform(lo, hi, 4), 0)})
                                         for s, lo, hi in (("ESRCV", 1e8, 5e8), ("TERCV", 6e8, 9e8)) for st in ("US", "TX")]))
            write(d, ou.REG, pd.concat([pd.DataFrame({"entity": f"afdc_reg:{st}", "variable": f"registrations_{f}", "ts_utc": years, "value": rng.integers(10, 9000, 4)})
                                        for f in ("ev", "gasoline", "hev") for st in ("US", "CA")]))
            write(d, ou.EV, pd.concat([pd.DataFrame({"entity": f"afdc_ev:{st}", "variable": "ev_dcfast_ports", "ts_utc": years, "value": rng.integers(1, 900, 4)})
                                       for st in ("ca", "tx", "pr")]))
            hm.clear_cache()
            for P in ou.CANDIDATES:
                got = P["_fn"](d)
                for region in sorted({r["region"] for r in got["rows"]}):
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                    path = os.path.join(d, f"r_{P['name']}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    r = subprocess.run([sys.executable, "-I", path, os.path.join(d, ou.TABLE[P["name"]] + ".csv")], capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, (P["name"], r.stderr))
                    printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                    self.assertEqual(sorted(printed), sorted(want), (P["name"], region))
                    for y in want:
                        self.assertAlmostEqual(printed[y], want[y], places=5, msg=(P["name"], region, y))
            hm.clear_cache()


if __name__ == "__main__":
    unittest.main()
