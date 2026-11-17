"""Session 7052 (chain 370, the data machine): done-line request 199.

flex_alert_effects writes, for each alert day, its cut under each of the four other specifications with their 90 percent
bounds (variant_<name>_reduction_mw, _lo, _hi), from the refits the builder already made; before, only each variant's
pooled figure was written.
"""

import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheVariantsByDay(unittest.TestCase):
    def test_the_builder_keeps_and_writes_each_variants_days(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "flex_alert_scorecard.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('Dv, _, _, pv, _ = estimate(p, alerts, eligible, vv, prices, b=VARIANT_B, drop=drop)', src)
        self.assertIn('variant_days[name] = Dv.set_index("day")', src)
        self.assertIn('f"variant_{name}_{var}"', src)
        for var in ("reduction_mw", "reduction_mw_lo", "reduction_mw_hi"):
            self.assertIn(f'"{var}"', src)


if __name__ == "__main__":
    unittest.main()
