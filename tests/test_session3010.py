"""Session 3010 (chain 164): the findings hunt, datacenters (deep/datacenters.py).

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
import datacenters as dc  # noqa: E402
import hunt_measures as hm  # noqa: E402


def write(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        frame.to_csv(f, index=False, lineterminator="\n")


def tables(d):
    rng = np.random.default_rng(3010)
    months = pd.date_range("2014-01-01", "2016-12-01", freq="MS").strftime("%Y-%m-%dT00:00:00Z")
    write(d, dc.C30, pd.concat([pd.DataFrame({"entity": e, "variable": "value_put_in_place", "ts_utc": months, "value": np.round(rng.uniform(1e8, 9e9, len(months)), 0)})
                                for e in ("census_c30:private:data_center", "census_c30:private:nonresidential", "census_c30:private:electric")]))
    cbp = []
    for st in ("ca", "ny", "va"):
        for var, lo, hi in (("employment", 1000, 90000), ("establishments", 50, 3000), ("annual_payroll", 1e8, 9e9)):
            cbp.append(pd.DataFrame({"entity": f"census_cbp_518210:{st}", "variable": var, "ts_utc": [f"{y}-01-01T00:00:00Z" for y in range(2012, 2016)],
                                     "value": np.round(rng.uniform(lo, hi, 4), 0)}))
    write(d, dc.CBP, pd.concat(cbp))
    q = pd.date_range("2004-01-01", "2006-10-01", freq="QS").strftime("%Y-%m-%dT00:00:00Z")
    write(d, dc.QSS, pd.DataFrame({"entity": "census_qss:518", "variable": "total_revenue", "ts_utc": q, "value": np.round(rng.uniform(1e10, 3e10, len(q)), 0)}))


class Datacenters(unittest.TestCase):
    def test_every_candidate_reproduces_from_the_table(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            hm.clear_cache()
            for P in dc.CANDIDATES:
                got = P["_fn"](d)
                regions = sorted({r["region"] for r in got["rows"]})
                self.assertTrue(regions, P["name"])
                for region in [r for r in regions if r.startswith("us_") or r.endswith("_US") or r.endswith("_VA")][:2]:
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                    path = os.path.join(d, f"r_{P['name']}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    table = {"dc_construction": dc.C30, "power_construction": dc.C30, "dc_share": dc.C30, "hosting_revenue": dc.QSS}.get(P["name"], dc.CBP)
                    r = subprocess.run([sys.executable, "-I", path, os.path.join(d, table + ".csv")], capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, (P["name"], r.stderr))
                    printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                    self.assertEqual(sorted(printed), sorted(want), (P["name"], region))
                    for y in want:
                        self.assertAlmostEqual(printed[y], want[y], places=5, msg=(P["name"], region, y))
                    do = P["reproduce"](region)["do"]
                    self.assertNotIn("///", do)
                    self.assertTrue(all("\n" not in b for b in do.strip("\n").split("\n\n")), P["name"])
            hm.clear_cache()


if __name__ == "__main__":
    unittest.main()
