"""Session 3008 (chain 164): the findings hunt, family gas (deep/gas.py).

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
import gas  # noqa: E402
import hunt_measures as hm  # noqa: E402


def write(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        frame.to_csv(f, index=False, lineterminator="\n")


def tables(d):
    rng = np.random.default_rng(3008)
    months = pd.date_range("2015-01-01", "2017-12-01", freq="MS").strftime("%Y-%m-%dT00:00:00Z")
    rows = []
    for ent, scale in (("eia_gas_production:NUS:N1", 3000000), ("eia_gas_production:SPA:N1", 600000), ("eia_gas_production:STX:N1", 900000), ("eia_gas_production:SSD:N1", 100)):
        for var in ("marketed_production", "gross_withdrawals", "vented_flared", "shale_withdrawals"):
            rows.append(pd.DataFrame({"entity": ent, "variable": var, "ts_utc": months, "value": np.round(rng.uniform(0.5, 1.0, len(months)) * scale * (0.02 if var == "vented_flared" else 1), 1)}))
    write(d, "eia_gas_production_state_monthly", pd.concat(rows))
    bal = [pd.DataFrame({"entity": "gas_balance:US", "variable": v, "ts_utc": months, "value": np.round(rng.uniform(100, 3000, len(months)), 1)})
           for v in ("lng_exports", "dry_production", "power_burn", "consumption")]
    weeks = pd.date_range("2015-01-02", "2017-12-29", freq="7D").strftime("%Y-%m-%dT00:00:00Z")
    for v in ("working_gas_bcf", "five_year_min_bcf", "five_year_max_bcf"):
        base = {"working_gas_bcf": 0, "five_year_min_bcf": -50, "five_year_max_bcf": 50}[v]
        bal.append(pd.DataFrame({"entity": "gas_storage:salt", "variable": v, "ts_utc": weeks, "value": np.round(300 + base + rng.normal(0, 40, len(weeks)), 1)}))
    write(d, "gas_balance_weekly", pd.concat(bal))
    cons = [pd.DataFrame({"entity": f"eia_gas_consumption:V{s}:SPA", "variable": v, "ts_utc": months, "value": np.round(rng.uniform(1000, 9000, len(months)), 1)})
            for s, v in zip(("RS", "CS", "IN", "EU"), gas.SECTORS)]
    write(d, "eia_gas_consumption_state_monthly", pd.concat(cons))
    write(d, "eia_gas_trade_country_monthly", pd.DataFrame({"entity": "eia_gas_trade:N9132MX2", "variable": "volume", "ts_utc": months,
                                                             "value": np.round(rng.uniform(1e5, 2e5, len(months)), 1)}))


class Gas(unittest.TestCase):
    def test_every_candidate_reproduces_and_the_rules(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            hm.clear_cache()
            for P in gas.CANDIDATES:
                got = P["_fn"](d)
                regions = sorted({r["region"] for r in got["rows"]})
                self.assertTrue(regions, P["name"])
                if P["name"] == "flared_share":
                    self.assertNotIn("flare_SD", regions)                       # a producer under 100 Bcf a year is not hunted
                if P["name"] == "state_production_share":
                    pa = {r["year"]: r["value"] for r in got["rows"] if r["region"] == "prod_PA"}
                    self.assertTrue(all(v < 50 for v in pa.values()))              # over EIA's US row, not over the US row plus the states
                for region in regions[:2]:
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                    path = os.path.join(d, f"r_{P['name']}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    table = "gas_balance_weekly" if P["name"] == "storage_outside" else gas.SPECS[P["name"]][0]
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
