"""Session 7050 (chain 370, the data machine): done-line request 139.

hub_price_comparison is held for ISO-NE, MISO and NYISO from 21 October 2026 (license needed), yet the site's copy,
site/data/price_compare.json, which is in the public repository, carried every figure of ISO-NE's and NYISO's rows.
A held grid's rows are now written there by name only (entity, grid, node), as a paused grid's hubs already were.
"""

import importlib.util
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def builder():
    spec = importlib.util.spec_from_file_location("price_compare_7050", os.path.join(ROOT, "warehouse", "derived", "price_compare.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheHeldGridsByName(unittest.TestCase):
    def test_a_held_grids_rows_are_names_only(self):
        m = builder()
        view = {"year": [{"entity": "ercot:HB_WEST", "grid": "ERCOT", "node": "HB_WEST", "dam_avg_price": 31.0},
                         {"entity": "isone:.H.INTERNAL_HUB", "grid": "ISO-NE", "node": ".H.INTERNAL_HUB", "dam_avg_price": 50.0}],
                "month": [{"entity": "isone:.H.INTERNAL_HUB", "grid": "ISO-NE", "node": ".H.INTERNAL_HUB", "dam_avg_price": 44.0},
                          {"entity": "nyiso:N.Y.C.", "grid": "NYISO", "node": "N.Y.C.", "rtm_avg_price": 60.0}]}
        paused = [{"entity": "miso:INDIANA.HUB", "grid": "MISO", "node": "INDIANA.HUB", "reason": "terms under review"}]
        out, names = m.site_view(view, paused, {"ISO-NE", "MISO", "NYISO"})
        self.assertEqual([r["entity"] for r in out["year"]], ["ercot:HB_WEST"])
        self.assertEqual(out["month"], [])
        self.assertEqual([r["entity"] for r in names], ["miso:INDIANA.HUB", "isone:.H.INTERNAL_HUB", "nyiso:N.Y.C."])
        for r in names:
            self.assertEqual(set(r), {"entity", "grid", "node", "reason"})
        self.assertNotIn("50.0", json.dumps(names))

    def test_the_committed_copy_holds_no_held_grids_figure(self):
        with open(os.path.join(ROOT, "site", "data", "price_compare.json"), encoding="utf-8") as f:
            d = json.load(f)
        for w in ("year", "month"):
            self.assertEqual([r["entity"] for r in d[w] if r["grid"] in ("ISO-NE", "MISO", "NYISO")], [], w)


if __name__ == "__main__":
    unittest.main()
