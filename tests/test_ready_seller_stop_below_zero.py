"""Session 11408, readied for the owner's ruling (weekend page part 3.4, generator choice 6; the generator audit of 20
November, finding 6, docs/reviews/generator-model-audit-2026-11-20.md, carried from wip/audit-generator-6): a merchant
solar or wind plant stops in an hour priced below zero.

1. warehouse/derived/merchant_revenue.py, sold_sums: energy and sales over the hours priced at zero or more.
2. Measured from the page's public hourly file (ERCOT solar at the hub average; the file of the current build, its last
   twelve months October 2025 to September 2026): the model's rule gives USD 60.2599 per kW, against 59.8523 when every
   hour is sold (189 negative hours with output, -0.4076). The site's snapshot is rebuilt at landing by the desk.
3. The decision and the note's section 13 say so, word for word alike."""
import csv
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import merchant_revenue as mr  # noqa: E402

CSV = os.path.join(ROOT, "site", "public", "seller", "erw_2026_generator_hourly.csv")


def last_twelve():
    with open(CSV, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    ix = {c: i for i, c in enumerate(rows[0])}
    out = []
    for r in rows[1:]:
        if r[ix["solar_mwh"]] == "-99999" or r[ix["in_last_twelve"]] != "1":
            continue
        out.append(dict(p=float(r[ix["price_usd_mwh"]]), solar=float(r[ix["solar_mwh"]]) / float(r[ix["nameplate_mw"]])))
    return pd.DataFrame(out)


class StopBelowZero(unittest.TestCase):
    def test_sold_sums_leaves_out_negative_hours(self):
        x = pd.DataFrame({"p": [10.0, -5.0, 0.0, 20.0], "solar": [0.5, 0.8, 0.3, 0.1]})
        e, s = mr.sold_sums(x, "solar")
        self.assertAlmostEqual(e, 0.9)
        self.assertAlmostEqual(s, 7.0)

    def test_the_default_case_measured(self):
        x = last_twelve()
        every = (x["solar"] * x["p"]).sum() / 1000
        e, s = mr.sold_sums(x, "solar")
        self.assertAlmostEqual(every, 59.8523, places=3)
        self.assertAlmostEqual(s / 1000, 60.2599, places=3)
        self.assertEqual(int(((x["p"] < 0) & (x["solar"] > 0)).sum()), 189)

    def test_the_words(self):
        words = "The plant sells every MWh it makes at the hour's price at a hub or zone, and a solar or wind plant stops in an hour priced below zero"
        for p in (("site", "lib", "decisions.ts"), ("docs", "methods", "generator_earns_algorithm.md")):
            with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
                self.assertIn(words, f.read())


if __name__ == "__main__":
    unittest.main()
