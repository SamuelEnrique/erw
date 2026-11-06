"""Session 2877 (chain 147): a zone's own demand growth, every EIA-930 sub-region by year (subregion_demand_growth).

Energy Research Warehouse (ERW). warehouse/derived/subregion_demand_growth.py on a fixture of two sub-regions and two
years: the peak and its hour, the mean of the hours used, the energy, the 95 percent rule, a faulty hour left out, the
growth only between two written years, a yearly table preferred to the rolling one. No request, no model call.
"""
import os
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import subregion_demand_growth as sdg  # noqa: E402

COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url", "retrieved_at", "vintage"]


def table(path, year, values, ent="eia930_subba:ERCO:COAS", node="Coast", drop=()):
    hours = pd.date_range(f"{year}-01-01", f"{year + 1}-01-01", freq="h", inclusive="left", tz="UTC")
    rows = [(ent, "demand_mw", h.strftime("%Y-%m-%dT%H:%M:%SZ"), v, "MW", "PT1H", "US", "", node, "eia", "u", "r", "")
            for i, (h, v) in enumerate(zip(hours, values(len(hours)))) if i not in drop]
    mode = "a" if os.path.exists(path) else "w"
    with open(path, mode, encoding="utf-8", newline="") as f:
        if mode == "w":
            f.write("# fixture\n")
        pd.DataFrame(rows, columns=COLS).to_csv(f, index=False, header=(mode == "w"), lineterminator="\n")


class TheYears(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp()
        flat = lambda base: (lambda n: [base + (i % 24) for i in range(n)])      # a day's shape, the same every day
        p23, p24 = (os.path.join(cls.d, f"eia930_subba_demand_hourly_{y}.csv") for y in (2023, 2024))
        table(p23, 2023, flat(1000))
        spike = lambda n: [5000 if i == 4000 else 1100 + (i % 24) for i in range(n)]   # one faulty hour, left out
        table(p24, 2024, spike)
        table(p23, 2023, flat(500), ent="eia930_subba:ERCO:WEST", node="West", drop=set(range(0, 1000)))   # 88.6 percent of 8760
        table(p24, 2024, flat(600), ent="eia930_subba:ERCO:WEST", node="West")
        rolling = os.path.join(cls.d, "eia930_subba_demand_hourly.csv")
        table(rolling, 2024, lambda n: [9999] * n)                                # the rolling copy of a year held: not read
        cls.t = sdg.build(sdg.inputs(cls.d))
        cls.v = {(r.entity, r.ts_utc[:4], r.variable): r for r in cls.t.itertuples()}

    def test_a_years_figures_and_its_peak_hour(self):
        v = self.v
        c23 = ("eia930_subba:ERCO:COAS", "2023")
        self.assertEqual(v[c23 + ("peak_mw",)].value, 1023.0)
        self.assertEqual(v[c23 + ("hours_used",)].value, 8760)
        self.assertAlmostEqual(v[c23 + ("avg_mw",)].value, 1011.5, places=4)
        self.assertAlmostEqual(v[c23 + ("energy_mwh",)].value, 1011.5 * 8760, places=2)
        self.assertEqual(v[c23 + ("peak_mw",)].x_at, "2023-01-01T23:00:00Z")    # the first hour the day reaches 23

    def test_a_faulty_hour_is_not_the_peak_and_the_growth_is_of_the_hours_used(self):
        v = self.v
        c24 = ("eia930_subba:ERCO:COAS", "2024")
        self.assertEqual(v[c24 + ("peak_mw",)].value, 1123.0)                      # not the 5000 of hour 4000
        self.assertEqual(v[c24 + ("hours_used",)].value, 8783)
        self.assertEqual(v[c24 + ("hours_in_year",)].value, 8784)
        self.assertAlmostEqual(v[c24 + ("peak_growth_pct",)].value, 100 * (1123 / 1023 - 1), places=3)
        self.assertAlmostEqual(v[c24 + ("avg_growth_pct",)].value, 100 * (1111.5 / 1011.5 - 1), places=3)
        self.assertNotIn(("eia930_subba:ERCO:COAS", "2023", "avg_growth_pct"), v)  # no year before it

    def test_a_year_under_95_percent_has_its_hours_and_no_figure_and_no_growth_after_it(self):
        v = self.v
        w23, w24 = ("eia930_subba:ERCO:WEST", "2023"), ("eia930_subba:ERCO:WEST", "2024")
        self.assertEqual(v[w23 + ("hours_used",)].value, 7760)
        self.assertNotIn(w23 + ("peak_mw",), v)
        self.assertIn(w24 + ("peak_mw",), v)
        self.assertNotIn(w24 + ("avg_growth_pct",), v)

    def test_the_rolling_copy_of_a_held_year_is_not_read(self):
        self.assertTrue(all(r.value != 9999 for r in self.t.itertuples() if r.variable == "peak_mw"))

    def test_the_rows_shape(self):
        t = self.t
        self.assertEqual(list(t.columns), sdg.COLS)
        self.assertEqual(set(t["freq"]), {"P1Y"})
        self.assertTrue(t["ts_utc"].str.match(r"^\d{4}-01-01T00:00:00Z$").all())
        self.assertEqual(set(t["unit"]), {"MW", "MWh", "count", "pct"})
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertEqual(set(t["x_parent"]), {"ERCO"})


class TheNote(unittest.TestCase):
    def test_no_dash(self):
        for parts in (("warehouse", "derived", "subregion_demand_growth.py"), ("docs", "methods", "subregion_demand_growth.md")):
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn(chr(0x2014), text)
            self.assertNotIn(chr(0x2013), text)


if __name__ == "__main__":
    unittest.main()
