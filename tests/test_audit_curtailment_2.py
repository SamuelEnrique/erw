"""Session 10210 (curtailment audit, finding 2): "What it is worth" said nothing of what its value is.

The headline "Curtailed energy at SP15 prices, 2026: USD -29.0 million" values CAISO's system-wide curtailment at one
hub. The method note says the hub's price stands for a place the data does not name and that a value below zero is not
a loss anyone booked; the page did not. Measured on the page's own file: over January to October 2026 SP15 real time
gives USD -29.0 million (-5.48 per MWh) and NP15 real time USD +27.7 million (+5.23); in 2025, -41.2 million against
+24.9 million. 81 percent of 2026's curtailed MWh was for local congestion (curtailment_profile.json).

Words only (site/app/curtailment/Sections.tsx, WORTH_WORDS): no figure moves.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class WorthWords(unittest.TestCase):
    def test_the_two_hubs_value_the_same_energy_with_opposite_signs(self):
        w = json.loads(read("site", "data", "curtailment", "worth.json"))["grids"]["caiso"]["hubs"]
        for y in ("2025", "2026"):
            sp = sum(v["value_usd"] for m, v in w["TH_SP15_GEN-APND"]["rt"]["months"].items() if m.startswith(y))
            np_ = sum(v["value_usd"] for m, v in w["TH_NP15_GEN-APND"]["rt"]["months"].items() if m.startswith(y))
            self.assertLess(sp, 0, y)
            self.assertGreater(np_, 0, y)

    def test_most_of_2026_was_for_local_congestion(self):
        p = json.loads(read("site", "data", "curtailment_profile.json"))["years"]["2026"]
        local = p["curtailed_solar_local_mwh"] + p["curtailed_wind_local_mwh"]
        self.assertGreater(local / (p["curtailed_solar_mwh"] + p["curtailed_wind_mwh"]), 0.75)

    def test_the_page_says_what_the_value_is_and_is_not(self):
        s = read("site", "app", "curtailment", "Sections.tsx")
        self.assertIn("export const WORTH_WORDS", s)
        self.assertIn("stands for a place the data does not name", s)
        self.assertIn("not a loss anyone booked", s)
        self.assertIn("tax credits and renewable certificates", s)
        self.assertIn('data-worth-words="1">{WORTH_WORDS}</p>', s)
        self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
