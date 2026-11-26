"""Session 10223 (the states audit, finding 2): the capacity table's "Hydro (with pumped storage)" held no pumped storage.

EIA-860M's pumped storage generators (technology "Hydroelectric Pumped Storage") are in the ERW's group `storage`,
which the page names "Batteries and pumped storage"; the group `hydro` is conventional hydro. Virginia's file shows it:
Bath County's 3,003 MW sit in storage, its hydro line is under 1,000 MW. Words only: no figure moves.
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "states")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "va.json")), "the states' page files are not on this machine")
class TheFile(unittest.TestCase):
    def test_virginia_pumped_storage_is_in_storage(self):
        with open(os.path.join(DIR, "va.json"), encoding="utf-8") as f:
            c = json.load(f)["plants"]["capacity_by_technology"]
        self.assertGreater(c["storage"]["nameplate_mw"], 3000)     # Bath County 3,003 MW among them
        self.assertLess(c["hydro"]["nameplate_mw"], 1000)


class TheWords(unittest.TestCase):
    def test_hydro_is_not_said_to_hold_pumped_storage(self):
        lib = src("site", "lib", "states.ts")
        hydro = re.search(r'hydro: "([^"]+)"', lib.split("export const TECH_WORDS")[1]).group(1)
        self.assertNotIn("with pumped storage", hydro)
        self.assertIn("pumped storage is under batteries", hydro)
        self.assertIn('storage: "Batteries and pumped storage"', lib)


if __name__ == "__main__":
    unittest.main()
