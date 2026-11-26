"""Audit of the project map, finding 3 (session 10216, docs/reviews/map-model-audit-2026-11-26.md): the tile
"Operating" is EIA's operating sheet, which also holds units on standby and out of service (on the copy of 19 November
2026: 1,577 SB, 219 OA, 538 OS; 2,334 units and 26,568.6 MW of 28,712 and 1,423,491.7), and its hover did not say so.
The heavier ring, "planned, under construction" in the key, is drawn for EIA's U, V and TS, and TS is "Construction
complete, not yet operating" (158 units, 17,720 MW). No figure moves.

1. Through the page's file: "Operating" holds codes other than OP, and the heavier ring's TS units exist. Passes on main.
2. The fix on this branch, words only. Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class OperatingAndUnderConstruction(unittest.TestCase):
    def test_the_codes_in_the_file(self):
        f = json.loads(src("site", "data", "map.json"))
        codes = [c["code"] for c in f["more"]["operating"]["codes"]]
        held = {codes[c] for c in f["more"]["operating"]["code"]}
        self.assertTrue({"SB", "OA", "OS"} & held, "the operating kind holds units EIA codes standby or out of service")
        self.assertIn('HEAVY = new Set(["u", "v", "ts"])', src("site", "app", "map", "ProjectMap.tsx"))
        ts = [s["slug"] for s in f["statuses"]].index("ts")
        self.assertGreater(sum(1 for x in f["st"] if x == ts), 0, "units EIA lists as built and not yet operating")

    def test_the_words(self):
        page = src("site", "app", "map", "ProjectMap.tsx")
        self.assertIn("\\\"Operating\\\" is EIA's operating inventory: it also holds units on standby and units out of service, some not expected "
                      "back within the next calendar year (EIA's codes SB, OA and OS; a unit's card names its code).", page)
        self.assertIn('{mark("heavy")}planned, under construction or built and not yet operating</li>', page)
        self.assertIn("finding 3", src("docs", "methods", "energy_projects.md"))
        self.assertNotIn(chr(0x2014), page)


if __name__ == "__main__":
    unittest.main()
