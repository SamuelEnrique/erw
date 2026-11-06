"""Session 3007 (chain 164): the findings hunt, family generation, the build-out (deep/buildout.py).

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
import buildout as bo  # noqa: E402
import hunt_measures as hm  # noqa: E402


def write(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        frame.to_csv(f, index=False, lineterminator="\n")


def tables(d):
    rng = np.random.default_rng(3007)
    op = []
    for i in range(400):
        tech = rng.choice(["Batteries", "Solar Photovoltaic", "Onshore Wind Turbine"])
        y = int(rng.integers(2010, 2026))
        mw = float(rng.uniform(5, 300)) if not (tech == "Batteries" and y == 2011) else 2.0
        op.append({"entity_id": f"eia860:{i}:1", "state": rng.choice(["TX", "CA"]), "technology": tech, "nameplate_mw": round(mw, 1),
                   "operating_year": y, "energy_capacity_mwh": round(mw * rng.uniform(1, 4), 1) if tech == "Batteries" else ""})
    write(d, "eia860m_operating_generators", pd.DataFrame(op))
    write(d, "eia860m_retired_generators_all", pd.DataFrame([{"entity_id": f"eia860:r{i}:1", "technology": "Conventional Steam Coal",
                                                             "nameplate_mw": round(float(rng.uniform(50, 800)), 1), "retirement_date": f"{int(rng.integers(2002, 2026))}-06-01"} for i in range(60)]))
    write(d, "uswtdb_wind_turbines", pd.DataFrame([{"entity_id": f"uswtdb:{i}", "project_year": int(rng.integers(2003, 2026)), "turbine_capacity_kw": round(float(rng.uniform(1000, 4000)), 0),
                                                    "rotor_diameter_m": round(float(rng.uniform(70, 150)), 1), "offshore": "0", "retrofit": "0"} for i in range(500)]))
    tts = []
    for y in range(2010, 2024):
        for var, v in (("price_median", float(rng.uniform(3000, 8000))), ("systems_priced", float(rng.choice([300, 900, 5000])))):
            tts.append({"entity": "tts:ca_res", "variable": var, "ts_utc": f"{y}-01-01T00:00:00Z", "value": round(v, 1)})
    write(d, "lbnl_tracking_the_sun", pd.DataFrame(tts))
    months = pd.date_range("2015-01-01", "2025-12-01", freq="MS").strftime("%Y-%m-%dT00:00:00Z")
    sb = []
    for ent in bo.GRIDS:
        for var in ("battery_operating_mw", "battery_operating_mwh_per_mw"):
            sb.append(pd.DataFrame({"entity": ent, "variable": var, "ts_utc": months, "value": np.round(rng.uniform(1, 1000, len(months)), 2)}))
    write(d, "storage_buildout_monthly", pd.concat(sb))


TABLE = {"added_mw": "eia860m_operating_generators", "battery_hours": "eia860m_operating_generators", "coal_retired": "eia860m_retired_generators_all",
         "turbine_kw": "uswtdb_wind_turbines", "turbine_rotor": "uswtdb_wind_turbines", "res_pv_price": "lbnl_tracking_the_sun",
         "battery_fleet_mw": "storage_buildout_monthly", "fleet_hours": "storage_buildout_monthly"}


class Buildout(unittest.TestCase):
    def test_every_candidate_reproduces_from_the_table(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            hm.clear_cache()
            for P in bo.CANDIDATES:
                got = P["_fn"](d)
                regions = sorted({r["region"] for r in got["rows"]})
                self.assertTrue(regions, P["name"])
                if P["name"] == "battery_hours":
                    self.assertNotIn(2011, {r["year"] for r in got["rows"]})     # under 100 MW entered service: left out
                if P["name"] == "res_pv_price":
                    self.assertEqual({r["n"] for r in got["rows"]}, {1.0})
                for region in [r for r in regions if r.endswith("_US") or r.endswith("_TX") or not r.startswith("add_")][:2]:
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                    path = os.path.join(d, f"r_{P['name']}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    r = subprocess.run([sys.executable, "-I", path, os.path.join(d, TABLE[P["name"]] + ".csv")], capture_output=True, text=True)
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
