"""Session 3003 (chain 164): the findings hunt, family prices, the fuels and carbon (deep/fuels_carbon.py).

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
import builder  # noqa: E402
import fuels_carbon as fc  # noqa: E402
import hunt_measures as hm  # noqa: E402


def write(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        frame.to_csv(f, index=False, lineterminator="\n")


def tables(d):
    rng = np.random.default_rng(3003)
    months = pd.date_range("1999-01-01", "2003-12-01", freq="MS").strftime("%Y-%m-%dT00:00:00Z")
    pink = pd.concat([pd.DataFrame({"entity": f"wb_pink:{e}", "variable": "price", "ts_utc": months, "value": np.round(rng.uniform(2, 9, len(months)), 2)})
                      for e in ("natural_gas_us", "natural_gas_europe", "liquefied_natural_gas_japan")])
    write(d, "wb_commodity_prices_monthly", pink)
    st = []
    for geo in ("US-TX", "US-CA"):
        for var in ("price_citygate", "price_residential", "price_electric_power", "price_industrial"):
            st.append(pd.DataFrame({"entity": f"eia_gas_price:x:{geo}", "variable": var, "ts_utc": months, "value": np.round(rng.uniform(2, 15, len(months)), 2),
                                    "geo": geo, "market": "", "node": "a state"}))
    write(d, "eia_gas_prices_state_monthly", pd.concat(st))
    q = pd.date_range("2013-02-01", "2016-11-01", freq="QS-FEB").strftime("%Y-%m-%dT00:00:00Z")
    write(d, "carb_auction_allowance_prices", pd.DataFrame({"entity": "carb:current_auction", "variable": "settlement_price", "ts_utc": q,
                                                            "value": np.round(rng.uniform(10, 20, len(q)), 2)}))
    w = pd.date_range("2019-01-07", "2021-12-27", freq="7D").strftime("%Y-%m-%dT00:00:00Z")
    write(d, "carb_lcfs_credit_prices", pd.DataFrame({"entity": "carb:lcfs_credit", "variable": "credit_price_weekly_avg", "ts_utc": w,
                                                      "value": np.round(rng.uniform(50, 200, len(w)), 2)}))
    days = pd.bdate_range("2001-01-01", "2003-12-31").strftime("%Y-%m-%dT00:00:00Z")
    write(d, "eia_fuel_spot_prices", pd.concat([pd.DataFrame({"entity": e, "variable": "spot_price", "ts_utc": days, "value": np.round(rng.uniform(20, 40, len(days)), 2)})
                                                for e in ("eia:brent", "eia:wti_cushing", "eia:henry_hub")]))


class Reproduce(unittest.TestCase):
    def test_every_candidate_reproduces_from_the_table(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            for P in fc.CANDIDATES:
                got = P["_fn"](d)
                regions = sorted({r["region"] for r in got["rows"]})
                self.assertTrue(regions, P["name"])
                region = regions[0]
                want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                path = os.path.join(d, f"r_{P['name']}.py")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(P["reproduce"](region)["py"])
                r = subprocess.run([sys.executable, "-I", path, os.path.join(d, fc.SPEC[P["name"]][1] + ".csv")], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, (P["name"], r.stderr))
                printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                self.assertEqual(sorted(printed), sorted(want), P["name"])
                for y in want:
                    self.assertAlmostEqual(printed[y], want[y], places=5, msg=(P["name"], y))
                do = P["reproduce"](region)["do"]
                self.assertNotIn("///", do)
                self.assertIn("destring value, replace force", do)
                self.assertTrue(all("\n" not in b for b in do.strip("\n").split("\n\n")), P["name"])

    def test_states_by_name_and_the_first_year_said(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            got = fc.power_vs_citygate(d)
        self.assertEqual({r["words"] for r in got["rows"]}, {"Texas", "California"})
        P = next(p for p in fc.CANDIDATES if p["name"] == "europe_gas_premium")
        c = {"last": 8.0, "first": 1.0, "last_year": "2025", "first_year": "2000"}
        self.assertIn("the first year this comparison counts", builder.sentence(P, "x", c))
        Q = next(p for p in fc.CANDIDATES if p["name"] == "brent_wti_spread")
        self.assertIn("the first full year the ERW holds", builder.sentence(Q, "x", c))


if __name__ == "__main__":
    unittest.main()
