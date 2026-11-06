"""Session 728 (chain 062): a zone's own demand growth. For the 19 rows whose zone EIA-930 names as a sub-region
(NYISO's eleven, ISO-NE's eight), headroom.json holds the sub-region's mean hourly demand in the newest whole year of
eia930_subba_demand_hourly_<year> against the year before; the cell draws it under the grid's figure, keyed
allgrids|zonegrowth|<row>. Every other row keeps its grid's figure. No request, no model call."""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Zones(unittest.TestCase):
    def test_the_map_is_nineteen_named_zones(self):
        import siting_page
        m = siting_page.SUBBA_ROW
        self.assertEqual(len(m), 19)
        self.assertEqual(sum(1 for k in m if k.startswith("nyiso:")), 11)
        self.assertEqual(sum(1 for k in m if k.startswith("isone:")), 8)
        self.assertEqual(m["nyiso:N.Y.C."], "NYIS:ZONJ")
        self.assertEqual(m["isone:.Z.SEMASS"], "ISNE:4006")
        self.assertFalse(any(k.startswith(("ercot:", "caiso:")) for k in m))   # weather zones and utilities are not the tab's rows

    def test_the_file_holds_each_zone_s_two_years(self):
        h = json.loads(src("site", "data", "siting", "headroom.json"))
        z = h["zones"]
        self.assertEqual((z["year"], z["prior"]), (2025, 2024))
        self.assertEqual(len(z["rows"]), 19)
        nyc = z["rows"]["nyiso:N.Y.C."]
        self.assertEqual(nyc["subba"], "NYIS:ZONJ")
        self.assertAlmostEqual(nyc["pct"], 100 * (nyc["mean_mw"] / nyc["prior_mean_mw"] - 1), places=1)
        self.assertGreater(nyc["hours"], 8000)

    def test_the_cell_draws_it_keyed(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn("check={`allgrids|zonegrowth|${r.id}`}", v)
        self.assertIn('data-headroom-zone="1"', v)
        s = src("site", "lib", "siting.ts")
        self.assertIn('if (p[1] === "zonegrowth")', s)


if __name__ == "__main__":
    unittest.main()
