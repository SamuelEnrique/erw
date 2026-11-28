"""Ready branch for the project map (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.3, the project
map; audit docs/reviews/map-model-audit-2026-11-26.md, finding 6, test wip/audit-map-6). Not the default: it waits for
Samuel's ruling.

The other choice: outside Alaska, a unit whose EIA point is more than 200 miles from the internal point of the county
EIA names for it is drawn at that county's point, marked as a county point (warehouse/derived/project_map.py,
far_from_county, applied in page_rows). On the page file now on main (built 28 November 2026 03:48 UTC) the rule moves
8 units, 1,489.2 MW (6 planned, 1,484.2 MW); the audit's 7 units and 1,469.2 MW were on the file of 19 November. No
count or sum changes. site/data/map.json is rebuilt at landing by the desk.

1. The rule on a small frame: a far unit moves, a near one, an Alaskan one and one with no county stay.
2. On the page file now on main, with the Census county gazetteers where held (ERW_GAZETTEER_DIR, or the newest folder
   of warehouse/raw/census_gazetteer/); skipped where neither is held.
3. The page's words."""
import json
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import project_map as pm  # noqa: E402


class AUnitFarFromItsCountyIsDrawnAtTheCountysPoint(unittest.TestCase):
    def test_the_rule(self):
        points = {("AR", pm._county_key("Lee County")): (34.78, -90.78), ("TX", "travis"): (30.33, -97.78),
                  ("AK", pm._county_key("Aleutians West Census Area")): (52.0, -175.0)}
        d = pd.DataFrame({"state": ["AR", "TX", "AK", "TX"], "county": ["Lee", "Travis", "Aleutians West", ""],
                          "lat": [36.5, 30.30, 53.9, 30.3], "lon": [-119.5, -97.70, -166.5, -97.7]})
        far = pm.far_from_county(d, points)
        self.assertEqual(list(far), [0])
        self.assertEqual(far[0], (34.78, -90.78))
        self.assertEqual(pm.FAR_MILES, 200)

    def test_on_the_page_file(self):
        points = pm.county_points()
        if not points:
            self.skipTest("the Census Bureau's county gazetteer is not held here")
        with open(os.path.join(ROOT, "site", "data", "map.json"), encoding="utf-8") as fh:
            f = json.load(fh)
        n = f["kinds"][2]["start"]
        d = pd.DataFrame({"state": [f["states"][s] for s in f["s"][:n]],
                          "county": [f["counties"][c] if c >= 0 else "" for c in f["c"][:n]],
                          "lat": f["la"][:n], "lon": f["lo"][:n]})
        far = pm.far_from_county(d, points)
        ids = sorted(f["id"][i] for i in far)
        # the audit's seven of 19 November are among them
        for want in ["64670:KOV4A", "67982:ATHS1", "67982:ATHSB", "68296:MC1", "68833:1", "70519:19735", "70557:G003"]:
            if f["pr"][f["id"].index(want)] == 0:
                self.assertIn(want, ids)
        self.assertTrue(all(f["states"][f["s"][i]] != "AK" for i in far))

    def test_the_words(self):
        with open(os.path.join(ROOT, "site", "app", "map", "Decisions.tsx"), encoding="utf-8") as fh:
            self.assertIn("is drawn at that county's point and marked so: one of the two is wrong.", fh.read())
        with open(os.path.join(ROOT, "docs", "methods", "map.md"), encoding="utf-8") as fh:
            self.assertIn("and a unit far from its own county: outside Alaska", fh.read())
        with open(os.path.join(ROOT, "warehouse", "derived", "project_map.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn('d.loc[i, "lat"], d.loc[i, "lon"], d.loc[i, "precision"] = la, lo, 1', src)
        self.assertIn('"units_at_county_point": int((eia["precision"] == 1).sum())', src)


if __name__ == "__main__":
    unittest.main()
