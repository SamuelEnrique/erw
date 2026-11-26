"""Session 10220 (congestion audit, finding 4, and finding 7 on the same branch): SPP's market changed on 1 April 2026,
and the page set SPP's years side by side with no word of it; the ERCOT decision left out the API the page's own hover
names.

SPP's files name its western balancing area (SWPW) from 1 April 2026 (docs/methods/spp_dam_cleared_energy.md, the
codebook's SPP tables). SPP North hub's mean congestion part was -2.07 USD/MWh over April to November 2025 and +1.84 over
April to November 2026. The first class shows the facts (passes on main); the second the words of the fix (fails on main).
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILE = os.path.join(ROOT, "site", "data", "conditions", "congestion.json")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheFacts(unittest.TestCase):
    def test_spp_names_its_western_area_from_1_april_2026(self):
        self.assertIn("From that day the file names SPP and SWPW (the western area)", src("docs", "methods", "spp_dam_cleared_energy.md"))

    @unittest.skipUnless(os.path.exists(FILE), "the congestion file is not on this machine")
    def test_spp_norths_congestion_part_turned_after_april(self):
        with open(FILE, encoding="utf-8") as f:
            F = json.load(f)
        p = next(x for x in F["places"]["spp"] if x["id"] == "spp:SPPNORTH_HUB")

        def w(a, z):
            ms = [m for m in p["monthly"] if a <= m[0] <= z]
            return sum(m[1] * m[4] for m in ms) / sum(m[1] for m in ms)
        self.assertLess(w("2025-04", "2025-11"), 0)
        self.assertGreater(w("2026-04", "2026-11"), 0)
        if F["built"].startswith("2026-11-20"):
            self.assertAlmostEqual(w("2025-04", "2025-11"), -2.07, delta=0.01)
            self.assertAlmostEqual(w("2026-04", "2026-11"), 1.84, delta=0.01)

    def test_the_ercot_hover_names_the_api(self):
        self.assertIn("or through an API whose key", src("warehouse", "derived", "congestion_page.py"))


class TheWordsSayIt(unittest.TestCase):
    def test_the_page_says_spps_market_changed(self):
        s = src("site", "app", "congestion", "page.tsx")
        self.assertIn('data-spp-west="1"', s)
        self.assertIn("SPP's market took in its western area on 1 April 2026", s)
        self.assertNotIn("export const SPP_WEST_WORDS", s)

    def test_the_decision_and_the_note_say_it(self):
        d = src("site", "app", "congestion", "Decisions.tsx")
        self.assertIn("or through an API whose key has not been made", d)
        self.assertIn("SPP's market took in its western area on 1 April 2026", d)
        n = src("docs", "methods", "grid_congestion.md")
        self.assertIn("SPP's market took in its western area on 1 April 2026", n)

    def test_no_em_dash(self):
        for p in (("site", "app", "congestion", "page.tsx"), ("site", "app", "congestion", "Decisions.tsx"),
                  ("docs", "methods", "grid_congestion.md")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
