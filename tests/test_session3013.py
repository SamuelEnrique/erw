"""Session 3013 (chain 164): the findings hunt, oil and products (deep/oil.py).

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
import oil  # noqa: E402


def write(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        frame.to_csv(f, index=False, lineterminator="\n")


def tables(d):
    rng = np.random.default_rng(3013)
    days = pd.bdate_range("2014-01-01", "2016-12-31").strftime("%Y-%m-%dT00:00:00Z")
    weeks = pd.date_range("2014-01-06", "2016-12-26", freq="7D").strftime("%Y-%m-%dT00:00:00Z")
    months = pd.date_range("2014-01-01", "2016-12-01", freq="MS").strftime("%Y-%m-%dT00:00:00Z")
    write(d, oil.FUEL, pd.DataFrame({"entity": "eia:wti_cushing", "variable": "spot_price", "ts_utc": days, "value": np.round(rng.uniform(40, 90, len(days)), 2)}))
    write(d, oil.PROD, pd.concat([pd.DataFrame({"entity": e, "variable": "spot_price", "ts_utc": days[5:], "value": np.round(rng.uniform(1.2, 2.8, len(days) - 5), 3)})
                                  for e, _ in oil.PRODUCTS.values()]))
    write(d, oil.RETAIL, pd.DataFrame({"entity": oil.RETAIL_GAS, "variable": "retail_price", "ts_utc": weeks, "value": np.round(rng.uniform(2.0, 3.8, len(weeks)), 3)}))
    write(d, oil.NET, pd.DataFrame({"entity": "eia_net_imports:MTTNTUS2", "variable": "net_imports_crude_and_products", "ts_utc": months,
                                     "value": np.round(rng.uniform(-3000, 5000, len(months)), 1)}))
    imp = [pd.DataFrame({"entity": "eia:MCRIMUS2", "variable": "imports", "ts_utc": months, "value": np.round(rng.uniform(6000, 8000, len(months)), 1)})]
    for c in ("CA", "SA"):
        imp.append(pd.DataFrame({"entity": f"eia:MCRIMUS{c}2", "variable": "imports", "ts_utc": months, "value": np.round(rng.uniform(500, 3000, len(months)), 1)}))
    write(d, oil.IMP, pd.concat(imp))
    write(d, oil.CRUDE, pd.concat([pd.DataFrame({"entity": e, "variable": "field_production_per_day", "ts_utc": months, "value": np.round(rng.uniform(lo, hi, len(months)), 1)})
                                   for e, lo, hi in (("eia_crude_production:NUS:MCRFPUS", 9000, 12000), ("eia_crude_production:STX:MCRFPTX", 3000, 5000),
                                                     ("eia_crude_production:SND:MCRFPND", 900, 1200))]))


ARGS = {"gasoline_crack": [oil.PROD, oil.FUEL], "diesel_crack": [oil.PROD, oil.FUEL], "jet_crack": [oil.PROD, oil.FUEL],
        "crude_share_of_pump": [oil.RETAIL, oil.FUEL], "pump_over_spot": [oil.RETAIL, oil.PROD], "net_imports": [oil.NET],
        "import_share": [oil.IMP], "state_crude_share": [oil.CRUDE]}


class Oil(unittest.TestCase):
    def test_every_candidate_reproduces_from_the_tables(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            hm.clear_cache()
            for P in oil.CANDIDATES:
                got = P["_fn"](d)
                regions = sorted({r["region"] for r in got["rows"]})
                self.assertTrue(regions, P["name"])
                for region in regions:
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
                    do = P["reproduce"](region)["do"]
                    self.assertNotIn("///", do)
                    self.assertTrue(all("\n" not in b for b in do.strip("\n").split("\n\n")), P["name"])
            hm.clear_cache()


if __name__ == "__main__":
    unittest.main()
