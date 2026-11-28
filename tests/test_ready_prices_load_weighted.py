"""The ruling readied for finding 3 of the prices audit (docs/reviews/prices-model-audit-2026-11-26.md), session 11407
(chain 770, part C; the measure carried over from wip/audit-prices-3): a load-weighted average beside the simple one on
"Where power is cheap" (/prices/compare).

warehouse/derived/price_compare.py writes <m>_load_weighted_avg_price and <m>_hours_load_weighted: each hour's price
weighted by the grid's own load in that hour (ERCOT's system load, CAISO's CA ISO-TAC area, SPP's EIA-930 demand), over
the hours holding both, only when those are at least 95 percent of the window's hours. The page shows it as a column
beside the simple average ("not held" where the file has none). The site's file is rebuilt at landing by the desk.

Measured on the old laptop's tables (runs/c770/11407/F_compare_lw.json): CAISO SP15's twelve months to October 2026,
day-ahead, simple 30.27 (every hour) and load-weighted 31.42 (8,576 hours with load); NP15 34.11 and 35.15."""
import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import price_compare as pc  # noqa: E402

TABLES = os.environ.get("ERW_READY_TABLES") or os.path.join(ROOT, "warehouse", "output")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheWeighting(unittest.TestCase):
    def hours(self, n, start="2026-10-01T05:00:00Z"):
        return pd.date_range(start, periods=n, freq="h", tz="UTC")

    def test_weights_each_hour_by_its_load(self):
        idx = self.hours(100)
        h = pd.Series([10.0] * 50 + [30.0] * 50, index=idx)
        load = pd.Series([1.0] * 50 + [3.0] * 50, index=idx)
        lw = pc.load_weighted(h, load, 100)
        self.assertEqual(lw, {"load_weighted_avg_price": 25.0, "hours_load_weighted": 100})
        self.assertEqual(round(float(h.mean()), 2), 20.0)

    def test_only_the_hours_holding_both_and_only_at_the_floor(self):
        idx = self.hours(100)
        h = pd.Series(10.0, index=idx)
        self.assertEqual(pc.load_weighted(h, pd.Series(1.0, index=idx[:95]), 100)["hours_load_weighted"], 95)
        self.assertEqual(pc.load_weighted(h, pd.Series(1.0, index=idx[:94]), 100), {})
        self.assertEqual(pc.load_weighted(h, None, 100), {})

    def test_the_load_read_from_a_table(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "caiso_area_load_hourly.csv"), "w", encoding="utf-8", newline="\n") as f:
                f.write("# a test table\nentity,variable,ts_utc,value,unit,freq\n"
                        "caiso:system,load,2026-10-01T07:00:00Z,100,MW,PT1H\n"
                        "caiso:system,load,2026-10-01T08:00:00Z,200,MW,PT1H\n"
                        "caiso:system,load,2026-10-01T08:00:00Z,300,MW,PT1H\n"
                        "caiso:PGE-TAC,load,2026-10-01T07:00:00Z,999,MW,PT1H\n")
            s = pc.load_series(d, "caiso", "2026-10-01")
            self.assertEqual(list(s.values), [100.0, 250.0])   # the hour held twice is their mean; another area is not read
            self.assertIsNone(pc.load_series(d, "ercot", "2026-10-01"))   # its table is not there
            self.assertIsNone(pc.load_series(d, "nyiso", "2026-10-01"))   # no load named for it

    def test_each_public_grid_has_its_own_load(self):
        self.assertEqual(pc.LOAD["ercot"][:2], ("ercot_zone_load_hourly", "ercot:system"))
        self.assertEqual(pc.LOAD["caiso"][:2], ("caiso_area_load_hourly", "caiso:system"))
        self.assertEqual(pc.LOAD["spp"][:2], ("eia930_all_demand", "eia930:SWPP"))


class ThePage(unittest.TestCase):
    def test_the_measure_sits_beside_the_simple_average(self):
        lib = src("site", "lib", "pricecompare.ts")
        self.assertLess(lib.index('slug: "avg", field: "avg_price"'), lib.index('slug: "lw", field: "load_weighted_avg_price"'))
        self.assertLess(lib.index('slug: "lw"'), lib.index('slug: "neg"'))
        self.assertIn("dam_load_weighted_avg_price?: number", lib)
        self.assertIn("rtm_load_weighted_avg_price?: number", lib)

    def test_the_page_reads_measures_by_slug_and_says_what_the_weight_is(self):
        page = src("site", "app", "prices", "compare", "page.tsx")
        self.assertNotIn("MEASURES[1]", page)
        self.assertNotIn("MEASURES[3]", page)
        self.assertNotIn("MEASURES[4]", page)
        self.assertIn('data-lw-said="1"', page)
        self.assertIn("The average is the simple mean of the hours held, each hour once, not weighted by the grid&apos;s load or by any buyer&apos;s.", page)

    def test_the_note_names_the_variable(self):
        self.assertIn("`<m>_load_weighted_avg_price`", src("docs", "methods", "hub_price_comparison.md"))


class TheMeasuredFigure(unittest.TestCase):
    def test_sp15_twelve_months_day_ahead(self):
        need = ["iso_hub_prices_history.csv", "iso_dam_hub_prices.csv", "caiso_area_load_hourly.csv"]
        if not all(os.path.exists(os.path.join(TABLES, n)) for n in need):
            self.skipTest(f"the price and load tables are not in {TABLES} (ERW_READY_TABLES may name them)")
        x = pc.read_prices(TABLES, "2025-10-31", lambda s: None, tables=["iso_hub_prices_history", "iso_dam_hub_prices"])
        x = x[(x["entity"] == "caiso:TH_SP15_GEN-APND") & (x["side"] == "dam")]
        a, b, n = pc.window_hours("2025-11-01", "2026-11-01", "America/Los_Angeles")
        h = pd.Series(x["value"].values, index=x["ts"]).sort_index()
        h = h[(h.index >= a) & (h.index < b)]
        self.assertEqual(round(float(h.mean()), 2), 30.27)
        lw = pc.load_weighted(h, pc.load_series(TABLES, "caiso", "2025-11-01"), n)
        if not lw:
            self.skipTest("the load table here holds under 95 percent of the twelve months")
        self.assertEqual(lw["load_weighted_avg_price"], 31.42)


if __name__ == "__main__":
    unittest.main()
