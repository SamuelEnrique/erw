"""Session 3002 (chain 164): the findings hunt, family prices, second part (deep/prices_markets.py).

Energy Research Warehouse (ERW). Each candidate's reproduce.py, run on small tables written here, prints the value the
module computed; each do-file keeps the owner's rules. No warehouse file, no network, no database.
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
sys.path.insert(0, os.path.dirname(__file__))
import hunt_measures as hm  # noqa: E402
import prices_markets as pm  # noqa: E402
from test_session3001 import write_tables  # noqa: E402


def write_more(d):
    """Day-ahead rows beside the real-time ones, the ancillary service table and a longer Henry Hub."""
    rng = np.random.default_rng(3002)
    hubs = pd.read_csv(os.path.join(d, "ercot_all_hub_prices_history.csv"), skiprows=1)
    hours = pd.date_range("2015-01-01T06:00:00Z", periods=4 * 24, freq="h")
    da = []
    for node in hubs["node"].unique():
        da.append(pd.DataFrame({"entity": "ercot:" + node, "variable": "price", "ts_utc": hours.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "value": np.round(25 + rng.normal(0, 5, len(hours)), 2), "market": "ercot_dam", "node": node}))
    with open(os.path.join(d, "ercot_all_hub_prices_history.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        pd.concat([hubs] + da, ignore_index=True).to_csv(f, index=False, lineterminator="\n")
    a = pd.DataFrame({"entity": [f"ercot:{s}" for s in ("REGUP", "RRS") for _ in hours], "variable": "mcpc_dam",
                      "ts_utc": list(hours.strftime("%Y-%m-%dT%H:%M:%SZ")) * 2, "value": np.round(rng.uniform(1, 20, 2 * len(hours)), 2)})
    with open(os.path.join(d, "ercot_as_prices.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        a.to_csv(f, index=False, lineterminator="\n")
    days = pd.bdate_range("2014-12-01", "2015-02-27")
    g = pd.DataFrame({"entity": "eia:henry_hub", "variable": "spot_price", "ts_utc": days.strftime("%Y-%m-%dT00:00:00Z"),
                      "value": np.round(3 + np.cumsum(rng.normal(0, 0.05, len(days))), 3)})
    with open(os.path.join(d, "eia_fuel_spot_prices.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        g.to_csv(f, index=False, lineterminator="\n")


class Reproduce(unittest.TestCase):
    def test_every_candidate_reproduces_from_the_table(self):
        with tempfile.TemporaryDirectory() as d:
            write_tables(d)
            write_more(d)
            hm.clear_cache()
            for P in pm.CANDIDATES:
                got = P["_fn"](d)
                regions = sorted({r["region"] for r in got["rows"] if r["value"] is not None})
                self.assertTrue(regions, P["name"])
                for region in regions[:1] + [r for r in regions if "LZ_" in r][:1]:
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region and r["value"] is not None}
                    path = os.path.join(d, f"r_{P['name']}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    if P["name"] == "as_price_mean":
                        table = "ercot_as_prices"
                    elif P["name"] == "henry_hub_volatility":
                        table = "eia_fuel_spot_prices"
                    else:
                        table = "ercot_zone_prices_history" if "LZ_" in region else "ercot_all_hub_prices_history"
                    r = subprocess.run([sys.executable, "-I", path, os.path.join(d, table + ".csv")], capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, (P["name"], r.stderr))
                    printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                    self.assertEqual(sorted(printed), sorted(want), (P["name"], region))
                    for y in want:
                        self.assertAlmostEqual(printed[y], want[y], places=5, msg=(P["name"], region, y))
            hm.clear_cache()

    def test_every_do_file_keeps_the_owners_rules(self):
        for P in pm.CANDIDATES:
            region = {"as_price_mean": "ercot_as_RRS", "henry_hub_volatility": "us_henry_hub"}.get(P["name"], "ercot_HB_WEST")
            do = P["reproduce"](region)["do"]
            self.assertNotIn("///", do)
            self.assertNotIn("/*", do)
            self.assertIn("destring value, replace force", do)
            self.assertIn("list year measure n, noobs", do)
            self.assertTrue(all("\n" not in b for b in do.strip("\n").split("\n\n")), P["name"])

    def test_the_areas(self):
        self.assertEqual(pm.area("ercot_as_RRS"), "ercot_as_RRS")
        self.assertEqual(pm.area("us_henry_hub"), "us_henry_hub")
        self.assertEqual(pm.area("ercot_LZ_WEST"), "WEST")


if __name__ == "__main__":
    unittest.main()
