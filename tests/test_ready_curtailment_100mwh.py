"""Ready branch for the curtailment tracker (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.3, the
curtailment tracker; audit docs/reviews/curtailment-model-audit-2026-11-26.md, finding 3, test
wip/audit-curtailment-3, carried over and turned). Not the default: it waits for Samuel's ruling.

The other choice: in California an hour counts as curtailed, for the hours and the flat load, only when it holds at
least 100 MWh (warehouse/derived/curtailment_worth.py, MIN_HOUR_MWH, value_of's min_mwh); the MWh and the dollars keep
every hour; Texas unchanged. The figures before and after are in the session's report (the builder's caiso() run on this
machine's tables); site/data/curtailment/worth.json is rebuilt at landing by the desk.

1. value_of on a small frame: with no floor it counts every hour above zero (as main); at 100 MWh only the large hours,
   the MWh and the dollars unchanged.
2. The builder passes the floor for California only, and the page's and the note's words say so.
3. On the page's file, once rebuilt (its rules name the floor): no counted hour holds a flat-load mean above zero hours."""
import json
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import curtailment_worth as cw  # noqa: E402


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class AnHourCountsAtOneHundredMWh(unittest.TestCase):
    def frame(self):
        idx = pd.date_range("2026-04-01", periods=4, freq="h", tz="UTC")
        return pd.Series([0.0, 0.8, 150.0, 400.0], index=idx), pd.Series([30.0, 10.0, -5.0, -20.0], index=idx)

    def test_no_floor_as_main(self):
        c, p = self.frame()
        r = cw.value_of(c, p)
        self.assertEqual(r["hours_curtailed_priced"], 3)
        self.assertAlmostEqual(r["price_curtailed_hours_mean"], round((10 - 5 - 20) / 3, 2))

    def test_at_one_hundred(self):
        c, p = self.frame()
        r0, r = cw.value_of(c, p), cw.value_of(c, p, 100.0)
        self.assertEqual(r["hours_curtailed_priced"], 2)
        self.assertEqual(r["hours_curtailed"], 2)
        self.assertAlmostEqual(r["price_curtailed_hours_mean"], -12.5)
        for k in ("curtailed_mwh_priced", "value_usd", "usd_per_mwh_curtailed", "price_all_hours_mean"):
            self.assertEqual(r[k], r0[k], k)

    def test_the_builder_and_the_words(self):
        self.assertEqual(cw.MIN_HOUR_MWH, 100.0)
        b = src("warehouse", "derived", "curtailment_worth.py")
        self.assertIn("r = value_of(c, p, MIN_HOUR_MWH)", b)
        self.assertIn("r = value_of(below, sides[k])", b)                 # Texas: any hour below the limit, as now
        self.assertNotIn("pp[cp_ > 0].mean()", b)
        page = src("site", "app", "curtailment", "Sections.tsx")
        self.assertIn("hours with at least 100 MWh curtailed.", page)
        self.assertIn("(in California, at least 100 MWh in the hour)", page)
        self.assertIn("In California an hour counts when it holds at least 100 MWh curtailed", src("docs", "methods", "curtailment.md"))

    def test_the_page_file_once_rebuilt(self):
        with open(os.path.join(ROOT, "site", "data", "curtailment", "worth.json"), encoding="utf-8") as f:
            w = json.load(f)
        if "at least 100 MWh" not in w["rules"]["flat_load"]:
            self.skipTest("the page's file is rebuilt at landing by the desk")
        for m, v in w["grids"]["caiso"]["hubs"]["TH_SP15_GEN-APND"]["rt"]["months"].items():
            if v.get("hours_curtailed_priced", 0) > 0:
                self.assertIn("price_curtailed_hours_mean", v, m)


if __name__ == "__main__":
    unittest.main()
