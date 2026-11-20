"""Session 8014, chain 581 (part F1): batteries in every authority and state (/storage/places, site/data/storage/places.json)."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILE = os.path.join(ROOT, "site", "data", "storage", "places.json")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(os.path.exists(FILE), "the storage places file is not on this machine")
class TheFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = json.load(open(FILE, encoding="utf-8"))

    def test_places_sum_to_the_nation(self):
        us = self.f["us"]["operating_mw"]
        self.assertAlmostEqual(sum(p["operating_mw"] or 0 for p in self.f["authorities"].values()), us, delta=1)
        self.assertAlmostEqual(sum(p["operating_mw"] or 0 for p in self.f["states"].values()), us, delta=1)

    def test_mwh_never_from_mw(self):
        for p in self.f["authorities"].values():
            if p["operating_mwh"] is None:
                self.assertIsNone(p["operating_mw_with_mwh"])
            for r in p["planned_by_year"].values():
                self.assertNotIn("mwh", r)

    def test_the_seven_grids_are_named(self):
        grids = {p["grid"] for p in self.f["authorities"].values() if p["grid"]}
        self.assertTrue({"ERCOT", "CAISO"} <= grids)


class ThePage(unittest.TestCase):
    def test_in_no_menu_and_the_storage_page_unchanged(self):
        self.assertNotIn("/storage/places", src("site", "lib", "pages.ts"))
        self.assertNotIn("/storage/places", src("site", "lib", "release.ts"))
        self.assertNotIn("places", src("site", "lib", "tabs.ts"))

    def test_the_fold_and_the_note_are_one_list(self):
        keys = re.findall(r'\{ key: "([a-z0-9-]+)", session: "', src("site", "app", "storage", "places", "Decisions.tsx"))
        note = src("docs", "methods", "storage_places.md").split("### Decisions (session 8014)")[1]
        self.assertEqual(re.findall(r"^\| `([a-z0-9-]+)` \|", note, re.M), keys)

    def test_no_em_dash(self):
        for p in (("site", "app", "storage", "places", "page.tsx"), ("site", "app", "storage", "places", "Decisions.tsx"),
                  ("warehouse", "derived", "storage_places.py"), ("docs", "methods", "storage_places.md")):
            self.assertNotIn(chr(0x2014), src(*p))


if __name__ == "__main__":
    unittest.main()
