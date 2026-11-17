"""Session 7622: the other choice of the ruling on a fourth way of running a flexible load (branch
wip/alt-cost-of-power-1, not landed). "Your load" on /cost-of-power offers price-following ways only, and they avoided
0 of ERCOT's four summer peaks in 2025. Under the other choice a fourth way is drawn beside the four-peak paragraph: a
load off in the four intervals of the newest summer held, as they fell (no forecast of the peaks is held), which avoids
all of its four-peak demand.

What is held to:
  the page draws the fourth way only where the four-peak read and a rate are held, with its words and the rate's year;
  its figure is the Commission's newest approved postage stamp rate (the page's own rule: status approved, matrix not
    B, the newest year) times 1,000 times the load's MW: on site/data/datacenter/texas_delivery.json (built
    16 November 2026) the 2026 rate, USD 75.527270 per kW, so USD 22,658,181 a year for the read's 300 MW load and
    USD 7,552,727 for the page's 100 MW;
  the price-following ways' figure is unchanged (the existing paragraph is kept as it was).

No request, no model call."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheFourthWay(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "cost-of-power", "page.tsx")
        with open(os.path.join(ROOT, "site", "data", "datacenter", "texas_delivery.json"), encoding="utf-8") as f:
            self.matrix = json.load(f)["matrix"]

    def rate(self):
        rows = sorted((r for r in self.matrix if r.get("quantity") == "postage_stamp_rate" and r.get("status") == "approved" and r.get("matrix") != "B"),
                      key=lambda r: r["year"])
        return rows[-1]["year"], rows[-1]["value"]

    def test_the_figure_is_the_newest_approved_rate_for_the_whole_load(self):
        year, value = self.rate()
        self.assertEqual((year, f"{value:.6f}"), ("2026", "75.527270"))
        self.assertEqual(round(value * 1000 * 300), 22658181)
        self.assertEqual(round(value * 1000 * 100), 7552727)

    def test_the_page_draws_the_fourth_way_beside_the_paragraph(self):
        self.assertIn('data-fourth-way="peaks"', self.page)
        self.assertIn("{M.cp.newest && M.cp.rate ? (", self.page)
        self.assertIn("A fourth way, off at the four peaks:", self.page)
        self.assertIn("Math.round(M.cp.rate.value * 1000 * x.mw)", self.page)
        self.assertIn("no forecast of the peaks is held", self.page)
        self.assertIn("so it avoided {two(100 * M.cp.newest.avoided!)} percent of its four-peak demand", self.page)
        self.assertNotIn(chr(0x2014), self.page)


if __name__ == "__main__":
    unittest.main()
