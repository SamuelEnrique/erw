"""Session 10223 (the states audit, finding 4, a figure for the owner's ruling; not for landing).

The page prints a source's share of "the last twelve months" when EIA printed it in only some of them. In the District
of Columbia natural gas, the headline's largest source, is 9 of 12 months: 40.05 percent. Were a source printed only
when all twelve months are held (as a whole year is), DC's natural gas would be "not held" and its headline's largest
source solar, 21.83 percent; were the withheld months' unitemized generation read as gas, 49.15 percent. This test
passes on main: it shows the figure, and changes nothing.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "states")


def load(st):
    with open(os.path.join(DIR, f"{st}.json"), encoding="utf-8") as f:
        return json.load(f)


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "index.json")), "the states' page files are not on this machine")
class AFigureForTheRuling(unittest.TestCase):
    def test_dc_headline_rests_on_nine_months(self):
        g = load("dc")["generation"]
        gas = g["by_source"]["natural_gas"][-12:]
        ni = g["by_source"]["not_itemized"][-12:]
        tot = g["last12"]["total_mwh"]
        self.assertEqual(sum(v is None for v in gas), 3)
        self.assertAlmostEqual(100 * g["last12"]["mwh"]["natural_gas"] / tot, 40.05, places=2)
        withheld = sum(n for n, v in zip(ni, gas) if v is None)
        self.assertAlmostEqual(100 * (g["last12"]["mwh"]["natural_gas"] + withheld) / tot, 49.15, places=2)
        whole = {s: v for s, v in g["last12"]["share_pct"].items()
                 if v is not None and all(x is not None for x in g["by_source"][s][-12:])}
        self.assertEqual(max(whole, key=whole.get), "solar")
        self.assertAlmostEqual(whole["solar"], 21.83, places=2)

    def test_places_with_a_source_summed_over_fewer_months(self):
        with open(os.path.join(DIR, "index.json"), encoding="utf-8") as f:
            idx = json.load(f)
        places, beyond_ni = [], []
        for r in idx["states"]:
            g = load(r["state"].lower())["generation"]
            part = [s for s, a in g["by_source"].items() if any(v is None for v in a[-12:]) and any(v is not None for v in a[-12:])]
            if part:
                places.append(r["state"])
                if any(s != "not_itemized" for s in part):
                    beyond_ni.append(r["state"])
        self.assertEqual(len(places), 44)
        self.assertEqual(len(beyond_ni), 17)


if __name__ == "__main__":
    unittest.main()
