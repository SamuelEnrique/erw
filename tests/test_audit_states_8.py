"""Session 10223 (the states audit, finding 8): two small sentences of /states against its figures.

1. The decision "not-held" says a figure is never drawn as zero unless the source printed a zero; a figure under half
   the last digit shown prints as 0.0, 0.0% or $0.00 bn (Texas's transportation sales, 4,676.6 MWh, as "0.0" TWh and
   "$0.00 bn"; 42 such figures in the 52 files). The decision now says so.
2. The total energy table lists "Electricity sold to customers" among the fuels; SEDS's total already holds the energy
   that made it (Texas 2024: the five fuels 14,672.2 trillion Btu against a total of 14,536.9, electricity sold 1,724.5).
   The row now says it is counted in the total. Words only: no figure moves.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "states")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "tx.json")), "the states' page files are not on this machine")
class TheFile(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(DIR, "tx.json"), encoding="utf-8") as f:
            self.tx = json.load(f)

    def test_a_small_figure_is_not_a_zero(self):
        b = self.tx["retail"]["last12"]["by_sector"]["transportation"]
        self.assertGreater(b["sales_mwh"], 0)
        self.assertEqual(f"{b['sales_mwh'] / 1e6:.1f}", "0.0")

    def test_the_fuels_already_hold_the_electricity(self):
        e = self.tx["energy"]
        i = e["years"].index("2024")
        b = {k: a[i] for k, a in e["by_source"].items()}
        five = sum(b[k] for k in ("coal", "natural_gas", "petroleum", "nuclear", "renewables"))
        self.assertGreater(five, b["total"])                               # adding electricity sold would count it twice
        self.assertGreater(b["electricity_retail_sales"], 1000)


class TheWords(unittest.TestCase):
    def test_the_decision_and_the_row(self):
        self.assertIn("A figure smaller than half the last digit shown prints as 0.0, 0.0% or $0.00 bn", src("site", "app", "states", "Decisions.tsx"))
        self.assertIn('electricity_retail_sales: "Electricity sold to customers (already counted in the total)"', src("site", "lib", "states.ts"))


if __name__ == "__main__":
    unittest.main()
