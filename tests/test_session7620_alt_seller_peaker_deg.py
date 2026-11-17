"""Session 7620: the other choice of the ruling on the peaker's degradation (branch wip/alt-seller-1, not landed). For a
gas peaker, "What matters most" on /cost-of-power/seller drew "Degradation by 1 point" (USD 2.38 million at the
defaults), though a gas plant's output is not degraded by that rule. Under the other choice the field and its bar are
dropped for a peaker, and the rate is held at the peaker's default, none.

What is held to:
  the page's facts mark a peaker (model.ts: noDeg is the asset's being a peaker), and the page hands it to the scenarios;
  the scenarios hold a peaker's degradation at its default whatever an address says, draw no degradation field for it,
    and drop the degradation bar from the sensitivity chart, which keeps every other bar as the library computes it;
  the peaker's default degradation is none (lib/seller/finance.ts: defaultsOf takes costs.deg ?? 0, and the page gives
    a peaker no deg), so no NPV moves at the defaults;
  for solar, wind and a battery nothing changes (noDeg is false).

No request, no model call."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ThePeakerHasNoDegradation(unittest.TestCase):
    def setUp(self):
        self.sc = src("site", "app", "cost-of-power", "seller", "SellerScenarios.tsx")
        self.model = src("site", "app", "cost-of-power", "seller", "model.ts")
        self.page = src("site", "app", "cost-of-power", "seller", "page.tsx")
        self.fin = src("site", "lib", "seller", "finance.ts")

    def test_the_page_marks_a_peaker_and_hands_it_on(self):
        self.assertIn("noDeg: peaker,", self.model)
        self.assertIn('const peaker = x.asset === "peaker";', self.model)
        self.assertIn("credits={facts.credits} noDeg={facts.noDeg}>", self.page)

    def test_the_bar_and_the_field_are_dropped_and_the_rate_held(self):
        self.assertIn('.filter((b) => !(f.noDeg && b.key === "deg"))', self.sc)
        self.assertIn('&& !(f.noDeg && k === "deg")).map((k) => {', self.sc)
        self.assertIn('if (noDeg) for (const p of ["a", "b"] as View[]) start[p].deg = d.deg;', self.sc)

    def test_the_peakers_default_is_none_so_no_npv_moves(self):
        self.assertIn("deg: costs.deg ?? 0", self.fin)
        self.assertIn('asked.asset === "battery" ? { deg: BATTERY_DEG, degSource: BATTERY_DEG_SOURCE } : asked.asset === "solar" ? { deg: SOLAR_DEG, degSource: SOLAR_DEG_SOURCE } : {}', self.model)

    def test_no_em_dash(self):
        for t in (self.sc, self.model, self.page):
            self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()
