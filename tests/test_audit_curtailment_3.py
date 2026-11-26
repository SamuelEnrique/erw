"""Session 10210 (curtailment audit, finding 3): "an hour with any curtailment" changes meaning at the turn of 2026.

"A flat load in those hours paid" (worth.json price_curtailed_hours_mean) is the mean price of every hour with any
curtailment above zero. To 2025 the hours come from CAISO's five-minute record; from 2026 from its Daily Renewable
Report by the hour, whose small category values (a self-schedule cut of 0.8 MWh) put a figure in most hours. Measured
on the page's file (SP15 real time): 55.6 percent of priced hours counted in 2025, 80.5 percent in January to October
2026, and the flat load sat 9.62 USD per MWh under the all-hours mean in 2025 against 1.36 in 2026. Restated from the
tables (docs/reviews/curtailment-model-audit-2026-11-26/measures.json): 1,365 of 2026's counted hours hold under 1 MWh
(208 in 2025); in the hours with at least 100 MWh curtailed the flat load paid 10.82 in 2026 and 13.19 in 2025, against
the page's 26.96 and 21.57. The same hours scale "the fleet charged in the curtailed hours".

These tests show it on main (they pass there). A threshold would move figures a reader sees, so it is not made: for
Samuel's ruling, default "left as it is".
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def worth():
    with open(os.path.join(ROOT, "site", "data", "curtailment", "worth.json"), encoding="utf-8") as f:
        return json.load(f)["grids"]["caiso"]


class AnyCurtailmentHour(unittest.TestCase):
    def year(self, y):
        ms = [v for m, v in worth()["hubs"]["TH_SP15_GEN-APND"]["rt"]["months"].items() if m.startswith(y)]
        hp, hc = sum(v["hours_priced"] for v in ms), sum(v["hours_curtailed_priced"] for v in ms)
        flat = sum(v["price_curtailed_hours_mean"] * v["hours_curtailed_priced"] for v in ms) / hc
        allh = sum(v["price_all_hours_mean"] * v["hours_priced"] for v in ms) / hp
        return hc / hp, allh - flat

    def test_the_share_of_hours_counted_jumps_at_the_turn_of_2026(self):
        s25, _ = self.year("2025")
        s26, _ = self.year("2026")
        self.assertLess(s25, 0.60)
        self.assertGreater(s26, 0.78)

    def test_the_flat_load_falls_toward_the_all_hours_mean(self):
        _, g25 = self.year("2025")
        _, g26 = self.year("2026")
        self.assertGreater(g25, 8.0)
        self.assertLess(g26, 2.0)

    def test_the_rule_is_any_hour_above_zero(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "curtailment_worth.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('price_curtailed_hours_mean=round(float(pp[cp_ > 0].mean()), 2)', src)
        self.assertIn('"hours_curtailed_priced": int((cp_ > 0).sum())', src)


if __name__ == "__main__":
    unittest.main()
