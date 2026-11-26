"""Session 10223 (the states audit, finding 7, a figure for the owner's ruling; not for landing).

The United States' plants part takes EIA-860M whole (warehouse/derived/states_page.py, build_plants: `op` unfiltered
for "US"), so the nation's operating capacity holds Puerto Rico's 6,474.3 MW while its generation and retail sales,
EIA's national totals, leave Puerto Rico out. Without Puerto Rico the capacity is 1,417,017.4 MW, not 1,423,491.7
(-0.45 percent); the planned and retiring tables move by Puerto Rico's rows too. This test passes on main.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "states")


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "index.json")), "the states' page files are not on this machine")
class AFigureForTheRuling(unittest.TestCase):
    def test_the_nation_counts_puerto_rico_in_capacity_only(self):
        with open(os.path.join(DIR, "index.json"), encoding="utf-8") as f:
            idx = json.load(f)
        files = {}
        for r in idx["states"]:
            with open(os.path.join(DIR, r["file"]), encoding="utf-8") as f:
                files[r["state"]] = json.load(f)
        us = files.pop("US")
        cap51 = sum(f["plants"]["capacity_total_mw"] for f in files.values())
        self.assertAlmostEqual(us["plants"]["capacity_total_mw"], 1423491.7, delta=0.1)
        self.assertAlmostEqual(cap51, 1417017.4, delta=0.5)
        self.assertAlmostEqual(100 * (cap51 - us["plants"]["capacity_total_mw"]) / us["plants"]["capacity_total_mw"], -0.45, places=2)
        sales51 = sum(f["retail"]["last12"]["by_sector"]["all"]["sales_mwh"] for f in files.values())
        self.assertAlmostEqual(us["retail"]["last12"]["by_sector"]["all"]["sales_mwh"], sales51, delta=1)   # no Puerto Rico in sales
        gen51 = sum(f["generation"]["last12"]["total_mwh"] for f in files.values())
        self.assertLess(us["generation"]["last12"]["total_mwh"], gen51)                                      # nor in generation

    def test_the_builder_takes_eia860m_whole_for_the_nation(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "states_page.py"), encoding="utf-8") as f:
            b = f.read()
        self.assertIn('o = op[op["state"] == st] if st != "US" else op', b)


if __name__ == "__main__":
    unittest.main()
