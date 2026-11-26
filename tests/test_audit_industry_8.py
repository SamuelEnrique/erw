"""Session 10224 (chain 710, the industry page audit, finding 8, for Samuel's ruling): no share in four regions of four.

/industry's "Share" is an industry's total over the sum of the 21 three-digit industries' totals in the region, and is
"not held" for every industry when one total is withheld there. In each census region at least one is withheld, so a
reader who chooses a region sees no share at all. The survey prints its own all-manufacturing total for each region;
on it the South's Chemicals would be 32.8 percent. A test that shows it, not a fix: a share drawn where none is now
would be a new figure, the owner's to allow. docs/reviews/industry-model-audit-2026-11-26.md.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class RegionalShares(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "site", "data", "industry.json"), encoding="utf-8") as f:
            self.ind = json.load(f)["industries"]["industries"]
        self.three = [n for n in self.ind if len(n) == 3 and n.isdigit()]

    def total(self, n, r):
        return self.ind[n]["by_region"].get(r, {}).get("total")

    def test_every_region_has_a_withheld_total_so_no_share_is_drawn(self):
        withheld = {r: sorted(n for n in self.three if self.total(n, r) is None) for r in ("us", "northeast", "midwest", "south", "west")}
        self.assertEqual(withheld["us"], [])
        self.assertEqual(withheld["northeast"], ["314", "316"])
        self.assertEqual(withheld["midwest"], ["315"])
        self.assertEqual(withheld["south"], ["312", "316", "332", "337"])
        self.assertEqual(withheld["west"], ["315", "316"])

    def test_the_survey_prints_each_region_total(self):
        shares = {}
        for r in ("northeast", "midwest", "south", "west"):
            allr = self.total("total", r)
            self.assertIsNotNone(allr)
            shares[r] = {n: round(100 * self.total(n, r) / allr, 1) for n in self.three if self.total(n, r) is not None}
        self.assertEqual(shares["south"]["325"], 32.8)
        self.assertEqual(shares["west"]["324"], 42.4)
        self.assertEqual(shares["midwest"]["325"], 22.1)
        self.assertEqual(shares["northeast"]["322"], 16.1)
        # the South's withheld four hold at most 8,306 - 7,884 = 422 TBtu
        held = sum(self.total(n, "south") for n in self.three if self.total(n, "south") is not None)
        self.assertEqual(round(self.total("total", "south") - held), 422)


if __name__ == "__main__":
    unittest.main()
