"""Session 11407 (chain 770, part C): the industry page's finding 8 readied for Samuel's ruling, each region's shares.

Carried over from session 10224's tests/test_audit_industry_8.py (branch wip/audit-industry-8), which showed that
/industry's "Share" was "not held" for every industry in every census region, one three-digit total being withheld in
each. On this branch, where a total is withheld in the region, the share is of the survey's own all-manufacturing total
for the region (the file's industry "total"), the withheld industries' part assigned to none. The South's Chemicals
32.8 percent, the West's Petroleum and Coal Products 42.4, the Midwest's Chemicals 22.1, the Northeast's Paper 16.1; the
nation's shares do not move (Chemicals 25.26 percent). docs/reviews/industry-model-audit-2026-11-26.md, finding 8.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class RegionalShares(unittest.TestCase):
    """The page's rule restated from the file: the 21's sum where none is withheld, else the survey's regional total."""

    def setUp(self):
        with open(os.path.join(ROOT, "site", "data", "industry.json"), encoding="utf-8") as f:
            self.ind = json.load(f)["industries"]
        self.three = self.ind["ranked_3_digit"]

    def total(self, n, r):
        return self.ind["industries"][n]["by_region"].get(r, {}).get("total")

    def share(self, n, r):
        tots = [self.total(x, r) for x in self.three]
        base = self.total("total", r) if any(t is None for t in tots) else sum(tots)
        me = self.total(n, r)
        return None if me is None or not base else 100 * me / base

    def test_every_region_has_a_withheld_total(self):
        withheld = {r: sorted(n for n in self.three if self.total(n, r) is None) for r in ("us", "northeast", "midwest", "south", "west")}
        self.assertEqual(withheld["us"], [])
        self.assertEqual(withheld["northeast"], ["314", "316"])
        self.assertEqual(withheld["midwest"], ["315"])
        self.assertEqual(withheld["south"], ["312", "316", "332", "337"])
        self.assertEqual(withheld["west"], ["315", "316"])

    def test_the_shares_drawn_in_each_region(self):
        self.assertEqual(round(self.share("325", "south"), 1), 32.8)
        self.assertEqual(round(self.share("324", "west"), 1), 42.4)
        self.assertEqual(round(self.share("325", "midwest"), 1), 22.1)
        self.assertEqual(round(self.share("322", "northeast"), 1), 16.1)
        drawn = {r: sum(1 for n in self.three if self.share(n, r) is not None) for r in ("us", "northeast", "midwest", "south", "west")}
        self.assertEqual(drawn, {"us": 21, "northeast": 19, "midwest": 20, "south": 17, "west": 19})
        # a withheld industry stays "not held", never zero
        self.assertIsNone(self.share("332", "south"))
        # the South's withheld four hold at most 8,306 - 7,884 = 422 TBtu, assigned to none
        held = sum(self.total(n, "south") for n in self.three if self.total(n, "south") is not None)
        self.assertEqual(round(self.total("total", "south") - held), 422)

    def test_the_nation_does_not_move(self):
        self.assertEqual(round(self.share("325", "us"), 2), 25.26)


class ThePageAndTheLib(unittest.TestCase):
    def test_the_lib_falls_back_to_the_regional_total(self):
        lib = src("site", "lib", "industry.ts")
        body = lib.split("export function shareOfSum")[1].split("\n}\n")[0]
        self.assertIn("f.industries.industries.total?.by_region?.[region]?.total", body)
        self.assertNotIn("if (rows.some((r) => r.total === null)) return null;", body)

    def test_the_hover_the_note_and_the_replication_say_so(self):
        page = src("site", "app", "industry", "page.tsx")
        self.assertIn("as a percent of the survey's own all-manufacturing total for the region, the withheld industries' part not assigned to any", page)
        self.assertNotIn("not held where EIA withholds a total there", page)
        note = src("docs", "methods", "industry_page.md")
        self.assertIn("the share of the survey's own all-manufacturing total for the region", note)
        self.assertIn("survey's own regional total", src("replication", "industry", "replicate.py"))

    def test_no_em_dash(self):
        for p in (("site", "app", "industry", "page.tsx"), ("site", "lib", "industry.ts"), ("docs", "methods", "industry_page.md")):
            self.assertNotIn(chr(0x2014), src(*p))


if __name__ == "__main__":
    unittest.main()
