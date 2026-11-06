"""Session 3006 (chain 164): the findings hunt, family generation, the fleets (deep/nuclear_fleet.py).

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
import nuclear_fleet as nf  # noqa: E402


def write(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        frame.to_csv(f, index=False, lineterminator="\n")


def tables(d):
    rng = np.random.default_rng(3006)
    rows = []
    for y in range(2001, 2005):
        for plant, geo, fuel, hr in (("1", "US-TX", "NG", 8.0), ("2", "US-TX", "NG", 9.0), ("3", "US-MT", "NG", 70.0), ("4", "US-PA", "BIT", 10.5)):
            g = rng.uniform(1e5, 1e6) * (0.001 if plant == "3" else 1.0)      # Montana's fleet is small, as a CHP-led fleet is
            rows += [{"entity": f"eia923:{plant}:{fuel}:{fuel}", "variable": "net_generation", "ts_utc": f"{y}-01-01T00:00:00Z", "value": round(g, 1), "geo": geo},
                     {"entity": f"eia923:{plant}:{fuel}:{fuel}", "variable": "fuel_consumed", "ts_utc": f"{y}-01-01T00:00:00Z", "value": round(g * hr * rng.uniform(0.95, 1.05) / 1e6, 6), "geo": geo},
                     {"entity": f"eia923:{plant}:ALL:ALL", "variable": "net_generation", "ts_utc": f"{y}-01-01T00:00:00Z", "value": 1.0, "geo": geo}]
    write(d, "eia923_plant_fuel_annual", pd.DataFrame(rows))
    days = pd.date_range("2007-01-01", "2008-12-31", freq="D")
    days2 = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    nrows = []
    for ent, span in (("eia_nuclear_outages_gen:1:1", days.append(days2)), ("eia_nuclear_outages_gen:2:1", days)):
        ts = span.strftime("%Y-%m-%dT00:00:00Z")
        nrows.append(pd.DataFrame({"entity": ent, "variable": "capacity", "ts_utc": ts, "value": 1000.0, "node": "A plant, reactor 1"}))
        nrows.append(pd.DataFrame({"entity": ent, "variable": "outage", "ts_utc": ts, "value": np.round(rng.choice([0.0, 600.0, 1000.0], len(ts)), 1), "node": "A plant, reactor 1"}))
    write(d, "eia_nuclear_outages_generator_daily", pd.concat(nrows))
    us = []
    for var, lo, hi in (("capacity", 98000, 101000), ("outage_share", 0.02, 0.2)):
        us.append(pd.DataFrame({"entity": "eia_nuclear_outages:US", "variable": var, "ts_utc": days.strftime("%Y-%m-%dT00:00:00Z"), "value": np.round(rng.uniform(lo, hi, len(days)), 4)}))
    write(d, "eia_nuclear_outages_daily", pd.concat(us))


class Fleets(unittest.TestCase):
    def test_reproduce_and_filters(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            hm.clear_cache()
            cases = [("gas_heat_rate", "eia923_plant_fuel_annual"), ("coal_heat_rate", "eia923_plant_fuel_annual"),
                     ("reactor_outage_days", "eia_nuclear_outages_generator_daily"), ("us_outage_share", "eia_nuclear_outages_daily"),
                     ("us_nuclear_capacity", "eia_nuclear_outages_daily")]
            for name, table in cases:
                P = next(p for p in nf.CANDIDATES if p["name"] == name)
                got = P["_fn"](d)
                regions = sorted({r["region"] for r in got["rows"]})
                if name == "gas_heat_rate":
                    self.assertEqual(regions, ["hr_gas_TX", "hr_gas_US"])          # Montana's 70 MMBtu per MWh is out of range: left out
                    self.assertEqual({r["n"] for r in got["rows"]}, {1.0})           # an EIA-923 year is one observation
                if name == "reactor_outage_days":
                    self.assertEqual(regions, ["nuc_1_1"])                           # the reactor without 2025 is left out
                for region in regions:
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                    path = os.path.join(d, f"r_{name}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    r = subprocess.run([sys.executable, "-I", path, os.path.join(d, table + ".csv")], capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, (name, r.stderr))
                    printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                    self.assertEqual(sorted(printed), sorted(want), (name, region))
                    for y in want:
                        self.assertAlmostEqual(printed[y], want[y], places=5, msg=(name, region, y))
                    do = P["reproduce"](region)["do"]
                    self.assertIn("destring value, replace force", do)
                    self.assertTrue(all("\n" not in b for b in do.strip("\n").split("\n\n")), name)
            hm.clear_cache()


if __name__ == "__main__":
    unittest.main()
