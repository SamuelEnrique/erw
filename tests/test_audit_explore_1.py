"""Session 10231 (chain 710, part D: the signature explorers audited, docs/reviews/explore-model-audit-2026-11-26.md,
finding 1).

/explore/ercot-peak-premium sets 2015 beside 2025 in each year's own dollars and never says so: nothing is adjusted for
inflation, and by the GDP price index the site already holds (site/data/forecast/deflator.json) prices rose 32.5
percent between the two years. The fix is words only: the decision on the price says the dollars are nominal and what
that is worth. The data test reads the annual table where it is held (warehouse/output, or a folder named by
ERW_AUDIT_OUTPUT); the words test and the index test run everywhere.
"""
import csv
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def table(name):
    for d in (os.environ.get("ERW_AUDIT_OUTPUT"), os.path.join(ROOT, "warehouse", "output")):
        if d and os.path.exists(os.path.join(d, name + ".csv")):
            return os.path.join(d, name + ".csv")
    return None


def hubavg(path):
    out = {}
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(line for line in f if not line.startswith("#")):
            if r["entity"] == "ercot:HB_HUBAVG":
                out[(r["variable"], r["ts_utc"][:4])] = float(r["value"])
    return out


class TheDollarsAreEachYearsOwn(unittest.TestCase):
    def test_the_index_the_site_holds_moves_a_third_between_the_two_years(self):
        idx = json.loads(src("site", "data", "forecast", "deflator.json"))["index"]
        self.assertAlmostEqual(idx["2025"] / idx["2015"], 1.3251, places=4)
        self.assertEqual(round(idx["2015"], 2), 97.28)
        self.assertEqual(round(idx["2025"], 2), 128.90)

    def test_the_peak_iqr_in_2025_dollars(self):
        path = table("ercot_peak_premium_annual")
        if not path:
            self.skipTest("ercot_peak_premium_annual is not held on this machine")
        a = hubavg(path)
        idx = json.loads(src("site", "data", "forecast", "deflator.json"))["index"]
        k = idx["2025"] / idx["2015"]
        iqr15, iqr25 = a[("peak_iqr", "2015")], a[("peak_iqr", "2025")]
        self.assertEqual(f"{iqr15:.2f}", "7.64")
        self.assertEqual(f"{iqr15 * k:.2f}", "10.12")
        self.assertEqual(f"{iqr25 / iqr15:.2f}", "4.47")
        self.assertEqual(f"{iqr25 / (iqr15 * k):.2f}", "3.37")

    def test_the_page_computes_no_adjustment(self):
        lib = src("site", "lib", "explore", "peakpremium.ts")
        self.assertNotIn("deflator", lib)
        self.assertNotIn("deflator", src("site", "app", "explore", "ercot-peak-premium", "page.tsx"))

    def test_the_decision_on_the_price_says_the_dollars_are_nominal(self):
        d = src("site", "app", "explore", "ercot-peak-premium", "Decisions.tsx")
        self.assertIn("The dollars are each year's own (nominal): nothing is adjusted for inflation. By the GDP price index, prices rose 32.5 percent from 2015 to 2025, so 2015's peak-block IQR of 7.64 USD/MWh is 10.12 in 2025 dollars, and the IQR grew 3.37 times in real terms where the page's figures give 4.47.", d)
        self.assertIn("BEA's GDP implicit price deflator as EIA's Short-Term Energy Outlook carries it", d)
        self.assertNotIn(chr(0x2014), d)


if __name__ == "__main__":
    unittest.main()
