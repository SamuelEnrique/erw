"""Session 10223 (the states audit, findings 3 and 4): what the generation groups hold, and a source's twelve months.

Pumped storage is in the group "Oil and other" (EIA's code HPS, docs/methods/generation_mix.md), the line that goes
below zero; the page's hover said only "pumped storage uses more than it makes". Small-scale solar is not in EIA's
state figures. A source is summed over the months EIA prints for it: in the District of Columbia natural gas, the
largest source, is 9 of the 12 months, the withheld months' generation in "Not itemized by EIA". Words only.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "states")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def load(st):
    with open(os.path.join(DIR, f"{st}.json"), encoding="utf-8") as f:
        return json.load(f)


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "dc.json")), "the states' page files are not on this machine")
class TheFiles(unittest.TestCase):
    def test_oil_and_other_falls_below_zero_where_pumped_storage_is(self):
        g = load("va")["generation"]
        self.assertLess(g["last12"]["mwh"]["oil_and_other"], 0)          # Bath County pumps more than it makes
        self.assertLess(g["annual"]["oil_and_other"][g["years"].index("2024")], -800000)

    def test_dc_natural_gas_is_nine_months(self):
        g = load("dc")["generation"]
        gas = g["by_source"]["natural_gas"][-12:]
        ni = g["by_source"]["not_itemized"][-12:]
        self.assertEqual(sum(v is None for v in gas), 3)
        self.assertTrue(all(n is not None and n > 0 for n, v in zip(ni, gas) if v is None))
        self.assertAlmostEqual(g["last12"]["share_pct"]["natural_gas"], 40.05, places=2)
        top = max((v, s) for s, v in g["last12"]["share_pct"].items() if v is not None)
        self.assertEqual(top[1], "natural_gas")


class TheWords(unittest.TestCase):
    def test_the_hovers_say_what_the_groups_hold(self):
        page = src("site", "app", "states", "page.tsx")
        self.assertIn("it is counted in Oil and other (EIA's code HPS)", page)
        self.assertIn("small-scale solar, such as rooftop panels, is not in EIA's state figures here", page)
        self.assertIn("A source is summed over the months EIA prints for it", page)

    def test_the_note_says_the_same(self):
        note = src("docs", "methods", "states_page.md")
        self.assertIn("pumped storage is in \"Oil and other\"", note)
        self.assertIn("A source is summed over the months EIA prints for it", note)


if __name__ == "__main__":
    unittest.main()
