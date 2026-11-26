"""Session 10000 (chain 701, done-line request 576): a grid held for a license (license_status.held_grids: NYISO and ISO-NE
from 20 October 2026) has no price file among what the site serves, and the builders that wrote them write none. MISO is
held too, but its pause (docs/methods/miso_pause.md) keeps its tables and pages as they are until a person lifts it, so
it is not part of this rule. Reads the repository's files only."""
import glob
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HELD = {"nyiso": "NYIS", "isone": "ISNE"}


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class NoHeldPriceFileIsServed(unittest.TestCase):
    def test_the_hold_is_these_two_grids_and_miso(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
        import license_status as lstat
        self.assertEqual(set(lstat.held_grids()) - {"MISO"}, {"NYISO", "ISO-NE"})

    def test_no_seller_year_file_of_a_held_grid(self):
        names = [os.path.basename(f) for f in glob.glob(os.path.join(ROOT, "site", "public", "seller", "prices", "*.json"))]
        self.assertEqual([n for n in names if n.split("_", 1)[0] in HELD], [])
        years = json.loads(src("site", "data", "seller", "hybrid.json")).get("years", {})
        self.assertFalse(set(years) & set(HELD))

    def test_no_hourly_board_file_of_a_held_grid(self):
        names = [os.path.basename(f) for f in glob.glob(os.path.join(ROOT, "site", "public", "board", "h", "*.json"))]
        self.assertEqual([n for n in names if n.split("-", 1)[0] in HELD], [])

    def test_no_gallery_chart_of_a_held_grid(self):
        files = glob.glob(os.path.join(ROOT, "docs", "analysis", "gallery", "*", "*.json"))
        self.assertEqual([f for f in files if any(f"iso={g}" in os.path.basename(f) for g in HELD)], [])
        idx = json.loads(src("docs", "analysis", "gallery", "index.json"))
        for t in idx["templates"]:
            for c in t["combos"].values():
                if str(c.get("params", {}).get("iso", "")).lower() in HELD:
                    self.assertIsNone(c.get("file"), t["template"])

    def test_no_network_hub_price_of_a_held_grid(self):
        for f in glob.glob(os.path.join(ROOT, "site", "public", "network", "*.json")):
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
            if isinstance(d, dict) and isinstance(d.get("hub_prices"), dict):
                self.assertFalse(set(d["hub_prices"]) & set(HELD.values()), os.path.basename(f))

    def test_the_builders_skip_a_held_grid(self):
        self.assertIn("g not in held]", src("warehouse", "derived", "seller_hybrid.py"))
        self.assertIn("if grid in held and grid != \"MISO\":", src("warehouse", "derived", "page_keep.py"))
        self.assertIn("in held_isos():", src("warehouse", "analysis", "run.py"))
        self.assertIn("held = held_bas()", src("warehouse", "derived", "network_stories.py"))
        nd = src("warehouse", "derived", "network_daily.py")
        self.assertEqual(nd.count("ns.held_bas()"), 2)


if __name__ == "__main__":
    unittest.main()
