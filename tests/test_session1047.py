"""Session 1047 (chain 072): EIA-411's capacity margins by NERC assessment area (eia411_capacity_margins_annual, public,
landed by the data machine's chain 049) are not drawn as a grid's reserve margin: the program's last release is of
November 2016, so its figures for the coming summer are projections made then (for ERCOT 38.1 percent against its own
CDR's 11.4). The words of a grid with no margin of its own name the area EIA-411 reports it under, an area that is not
one grid named so. No request, no model call."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheWords(unittest.TestCase):
    def test_every_grid_has_its_area_named(self):
        s = src("site", "lib", "siting.ts")
        i = s.index("export const EIA411_AREA")
        block = s[i:s.index("};", i)]
        for g in ("ercot", "caiso", "nyiso", "isone", "spp", "miso", "pjm"):
            self.assertIn(f"{g}:", block)
        self.assertIn("WECC, the whole Western Interconnection", block)   # not one grid, named so
        self.assertIn("NPCC, New York and New England together", block)

    def test_the_why_says_why_it_is_not_drawn(self):
        s = src("site", "lib", "siting.ts")
        i = s.index("export function reserveMargin")
        body = s[i:s.index("\n}\n", i)]
        self.assertIn("eia411_capacity_margins_annual", body)
        self.assertIn("November 2016", body)
        self.assertIn("not drawn as the grid's", body)

    def test_the_method_note_sets_ercot_s_two_figures_side_by_side(self):
        m = src("docs", "methods", "siting.md")
        self.assertIn("eia411_capacity_margins_annual", m)
        self.assertIn("38.07", m)
        self.assertIn("11.43", m)


if __name__ == "__main__":
    unittest.main()
