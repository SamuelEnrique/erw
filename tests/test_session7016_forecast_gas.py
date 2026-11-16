"""Session 7016 (chain 301, done-line request 11): the impact page's gas price reads the newest STEO release. The table
keeps each release; with two of them (6 October and 10 November 2026) it held 24 history months of 2025 and the build
refused. On 16 November both releases give the same 2025 Henry Hub mean, USD 3.5267 per MMBtu. No request, no model
call."""
import csv
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "forecast"))
import params  # noqa: E402

COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_kind"]


class TheNewestRelease(unittest.TestCase):
    def test_two_releases_give_the_newest_twelve_months(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "eia_steo_forecasts.csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# a stand-in\n")
                w = csv.writer(f)
                w.writerow(COLS)
                for vintage, base in (("2026-10-06T00:00:00Z", 1.0), ("2026-11-10T00:00:00Z", 2.0)):
                    for m in range(1, 13):
                        w.writerow(["eia_steo:NGHHUUS", "price", f"2025-{m:02d}-01T00:00:00Z", base + m / 100, "USD/MMBtu", "P1M",
                                    "US", "", "", "eia:steo", "u", "r", vintage, "history"])
            doc, err = params.gas(d)
        self.assertIsNone(err)
        self.assertEqual(len(doc["price_months"]), 12)
        self.assertAlmostEqual(doc["price_usd_per_mmbtu"], round(2.0 + 78 / 1200, 4))


if __name__ == "__main__":
    unittest.main()
