"""Session 3015 (chain 164): regions, the pump, propane and the chokepoints (deep/oil_regional.py); a held table's note.

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
import hunt_measures as hm  # noqa: E402
import oil_regional as orr  # noqa: E402


def write(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        frame.to_csv(f, index=False, lineterminator="\n")


def tables(d):
    rng = np.random.default_rng(3015)
    weeks = pd.date_range("2019-01-07", "2021-12-27", freq="7D").strftime("%Y-%m-%dT00:00:00Z")
    days = pd.bdate_range("2019-01-01", "2021-12-31").strftime("%Y-%m-%dT00:00:00Z")
    write(d, orr.REG, pd.concat([pd.DataFrame({"entity": e, "variable": "retail_price", "ts_utc": weeks, "value": np.round(rng.uniform(2, 5, len(weeks)), 3)})
                                 for e in [orr.US_GAS, "eia:EMM_EPMR_PTE_SCA_DPG", "eia:EMM_EPMR_PTE_R30_DPG"]]))
    write(d, orr.RET, pd.concat([pd.DataFrame({"entity": e, "variable": "retail_price", "ts_utc": weeks, "value": np.round(rng.uniform(2, 5, len(weeks)), 3)})
                                 for e in [orr.US_GAS, orr.US_DIESEL]]))
    write(d, orr.PROD, pd.DataFrame({"entity": orr.PROPANE, "variable": "spot_price", "ts_utc": days, "value": np.round(rng.uniform(0.4, 1.2, len(days)), 4)}))
    write(d, orr.FUEL, pd.DataFrame({"entity": "eia:wti_cushing", "variable": "spot_price", "ts_utc": days[3:], "value": np.round(rng.uniform(40, 90, len(days) - 3), 2)}))
    cal = pd.date_range("2019-01-01", "2021-12-31", freq="D").strftime("%Y-%m-%dT00:00:00Z")
    write(d, orr.PW, pd.concat([pd.DataFrame({"entity": e, "variable": "n_tanker", "ts_utc": cal, "value": rng.integers(5, 60, len(cal))}) for e in orr.CHOKES]))


ARGS = {"gas_premium": [orr.REG], "diesel_premium": [orr.RET], "propane_to_crude": [orr.PROD, orr.FUEL], "tanker_transits": [orr.PW]}


class Regional(unittest.TestCase):
    def test_every_candidate_reproduces_from_the_tables(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            hm.clear_cache()
            for P in orr.CANDIDATES:
                got = P["_fn"](d)
                for region in sorted({r["region"] for r in got["rows"]}):
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
                    self.assertTrue(all("\n" not in b for b in P["reproduce"](region)["do"].strip("\n").split("\n\n")), P["name"])
            hm.clear_cache()

    def test_a_held_table_says_license_needed_before_its_figure(self):
        P = next(p for p in orr.CANDIDATES if p["name"] == "tanker_transits")
        s = builder.sentence(P, "the Strait of Hormuz", {"last": 1.0, "first": 2.0, "last_year": "2025", "first_year": "2019"})
        self.assertTrue(s.startswith("License needed (IMF PortWatch's portwatch_chokepoint_transits is held internal):"))
        Q = next(p for p in orr.CANDIDATES if p["name"] == "diesel_premium")
        self.assertNotIn("License needed", builder.sentence(Q, "x", {"last": 1.0, "first": 2.0, "last_year": "2025", "first_year": "2019"}))


if __name__ == "__main__":
    unittest.main()
