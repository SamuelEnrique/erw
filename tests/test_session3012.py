"""Session 3012 (chain 164): the findings hunt, tariffs and policy, the retail side (deep/retail.py).

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
import retail  # noqa: E402


def write(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        frame.to_csv(f, index=False, lineterminator="\n")


def tables(d):
    rng = np.random.default_rng(3012)
    months = pd.date_range("2015-01-01", "2017-12-01", freq="MS").strftime("%Y-%m-%dT00:00:00Z")
    years = [f"{y}-01-01T00:00:00Z" for y in range(2015, 2019)]
    sales, prices = [], []
    for st in ("US", "TX"):
        for sec in ("COM", "RES", "IND"):
            sales.append(pd.DataFrame({"entity": f"eia:retail_sales:{st}:{sec}", "variable": "retail_sales", "ts_utc": months, "value": np.round(rng.uniform(1e6, 9e6, len(months)), 0)}))
            prices.append(pd.DataFrame({"entity": f"eia:retail_price:{st}:{sec}", "variable": "retail_price", "ts_utc": months, "value": np.round(rng.uniform(60, 200, len(months)), 2)}))
    write(d, retail.SALES, pd.concat(sales))
    write(d, retail.PRICES, pd.concat(prices))
    rel = []
    for i, geo in enumerate(["US-TX", "US-TX", "US-NE"]):
        for var, lo, hi in (("ieee_saidi_with_med", 50, 500), ("ieee_customers", 1e4, 1e6)):
            rel.append(pd.DataFrame({"entity": f"eia861_reliability:{i}:{geo[3:]}", "variable": var, "ts_utc": years, "value": np.round(rng.uniform(lo, hi, 4), 2), "geo": geo}))
    write(d, retail.REL, pd.concat(rel))
    met = []
    for st in ("US", "TX"):
        for kind, lo, hi in (("advanced_meter_infrastructure", 1e5, 5e5), ("all_meters", 6e5, 9e5)):
            met.append(pd.DataFrame({"entity": f"eia_meters:{st}:{kind}:TOT", "variable": "meters", "ts_utc": years, "value": np.round(rng.uniform(lo, hi, 4), 0)}))
    write(d, retail.METERS, pd.concat(met))
    write(d, retail.NEM, pd.concat([pd.DataFrame({"entity": f"eia_net_metering:{st}:all_technologies:TOT", "variable": "capacity", "ts_utc": years,
                                                  "value": np.round(rng.uniform(100, 900, 4), 1)}) for st in ("US", "TX")]))


class Retail(unittest.TestCase):
    def test_every_candidate_reproduces_from_the_table(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            hm.clear_cache()
            for P in retail.CANDIDATES:
                got = P["_fn"](d)
                regions = sorted({r["region"] for r in got["rows"]})
                self.assertTrue(regions, P["name"])
                for region in regions:
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                    path = os.path.join(d, f"r_{P['name']}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    table = {"commercial_sales": retail.SALES, "res_price": retail.PRICES, "res_over_ind": retail.PRICES, "saidi": retail.REL,
                             "ami_share": retail.METERS, "net_metered": retail.NEM}[P["name"]]
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
