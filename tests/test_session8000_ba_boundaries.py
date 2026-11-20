"""Session 8000 (chain 501, step B2): the balancing authority areas of warehouse/connectors/hifld_control_areas.py.

Energy Research Warehouse (ERW). docs/methods/ba_boundaries.md; the web file's shape: docs/state/page_files_regions.md.

    python -m unittest tests.test_session8000_ba_boundaries -v
"""

import json
import math
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import hifld_control_areas as hca  # noqa: E402

SITE = os.path.join(ROOT, "site", "data", "regions", "ba_boundaries.json")
NAMES = os.path.join(ROOT, "site", "data", "eia930_ba_names.json")


class Area(unittest.TestCase):
    def test_one_degree_cell_at_the_equator(self):
        # a 1 by 1 degree cell from the equator: R^2 * (pi/180) * sin(1 degree)
        want = hca.R_KM ** 2 * math.radians(1) * math.sin(math.radians(1))
        ring = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        self.assertAlmostEqual(hca.ring_area_km2(ring), want, delta=want * 1e-9)

    def test_a_hole_is_subtracted(self):
        outer = [[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]
        hole = [[0.5, 0.5], [1.5, 0.5], [1.5, 1.5], [0.5, 1.5], [0.5, 0.5]]
        whole = hca.area_km2({"type": "Polygon", "coordinates": [outer]})
        holed = hca.area_km2({"type": "Polygon", "coordinates": [outer, hole]})
        self.assertAlmostEqual(whole - holed, hca.ring_area_km2([tuple(p) for p in hole]), places=6)

    def test_multipolygon_parts_add(self):
        a = [[0, 10], [1, 10], [1, 11], [0, 11], [0, 10]]
        b = [[5, 10], [6, 10], [6, 11], [5, 11], [5, 10]]
        one = hca.area_km2({"type": "Polygon", "coordinates": [a]})
        both = hca.area_km2({"type": "MultiPolygon", "coordinates": [[a], [b]]})
        self.assertAlmostEqual(both, 2 * one, places=6)


class Values(unittest.TestCase):
    def test_negative_codes_are_blank(self):
        self.assertEqual(hca.clean_num(-999), "")
        self.assertEqual(hca.clean_num("NOT AVAILABLE"), "")
        self.assertEqual(hca.clean_num(35086), 35086.0)

    def test_dates_from_milliseconds(self):
        self.assertEqual(hca.ms_date(1624233600000), "2021-06-21")
        self.assertEqual(hca.ms_date(None), "")


@unittest.skipUnless(os.path.exists(SITE), "the web file is written on the data machine")
class WebFile(unittest.TestCase):
    def setUp(self):
        with open(SITE, encoding="utf-8") as f:
            self.doc = json.load(f)

    def test_under_the_limit(self):
        self.assertLess(os.path.getsize(SITE), int(1.5 * 1024 ** 2))

    def test_contract_keys(self):
        for k in ("type", "built", "tables", "method", "license", "source", "source_url", "retrieved_at",
                  "simplify_tolerance_deg", "bas_without_polygon", "polygons_without_ba", "features"):
            self.assertIn(k, self.doc)
        self.assertEqual(self.doc["tables"], ["ba_boundaries"])
        for ft in self.doc["features"]:
            self.assertEqual(set(ft["properties"]), {"code", "name", "region", "source_id", "area_km2"})
            self.assertIn(ft["geometry"]["type"], ("Polygon", "MultiPolygon"))

    def test_every_code_is_eia930s_and_once(self):
        with open(NAMES, encoding="utf-8") as f:
            names = json.load(f)
        known = set(names["authorities"])
        codes = [ft["properties"]["code"] for ft in self.doc["features"]]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual([c for c in codes if c not in known], [])
        # the known pairs of 19 November 2026: TVA's EIA ID 18642, ERCOT's 5723
        by = {ft["properties"]["code"]: ft["properties"]["source_id"] for ft in self.doc["features"]}
        self.assertEqual(by.get("TVA"), "18642")
        self.assertEqual(by.get("ERCO"), "5723")


if __name__ == "__main__":
    unittest.main()
