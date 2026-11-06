"""Session 3176 (chain 166): emissions and climate (deep/emissions.py).

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
import emissions as em  # noqa: E402
import hunt_measures as hm  # noqa: E402


def write(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        frame.to_csv(f, index=False, lineterminator="\n")


class Emissions(unittest.TestCase):
    def test_every_candidate_reproduces_and_dc_is_left_out(self):
        rng = np.random.default_rng(3176)
        years = [f"{y}-01-01T00:00:00Z" for y in range(1999, 2006)]
        rows = []
        for st in ("US", "TX", "DC"):
            for sec in ("EC", "TC", "TT"):
                for fuel in ("CO", "TO"):
                    rows.append(pd.DataFrame({"entity": f"eia_co2:{st}:{sec}:{fuel}", "variable": "co2", "ts_utc": years, "value": np.round(rng.uniform(1e6, 9e8, len(years)), 0)}))
        months = pd.date_range("1999-01-01", "2005-12-01", freq="MS").strftime("%Y-%m-%dT00:00:00Z")
        gen = [pd.DataFrame({"entity": f"eia:generation:{st}:ALL", "variable": "net_generation", "ts_utc": months, "value": np.round(rng.uniform(1e6, 9e7, len(months)), 0),
                             "geo": f"US-{st}"}) for st in ("US", "TX", "DC")]
        clim = pd.DataFrame({"entity": "noaa_climdiv:110", "variable": "temp_avg", "ts_utc": months, "value": np.round(rng.uniform(20, 80, len(months)), 2),
                             "x_mean_1901_2000": np.round(rng.uniform(20, 80, len(months)), 2)})
        with tempfile.TemporaryDirectory() as d:
            write(d, em.CO2, pd.concat(rows))
            write(d, em.GEN, pd.concat(gen))
            write(d, em.CLIM, clim)
            hm.clear_cache()
            for P in em.CANDIDATES:
                got = P["_fn"](d)
                regions = sorted({r["region"] for r in got["rows"]})
                self.assertNotIn("co2mwh_DC", regions)
                for region in regions:
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                    path = os.path.join(d, f"r_{P['name']}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    args = {"power_co2_per_mwh": [em.CO2, em.GEN], "conus_temperature": [em.CLIM]}.get(P["name"], [em.CO2])
                    r = subprocess.run([sys.executable, "-I", path] + [os.path.join(d, t + ".csv") for t in args], capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, (P["name"], r.stderr))
                    printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                    self.assertEqual(sorted(printed), sorted(want), (P["name"], region))
                    for y in want:
                        self.assertAlmostEqual(printed[y], want[y], places=5, msg=(P["name"], region, y))
            hm.clear_cache()


if __name__ == "__main__":
    unittest.main()
