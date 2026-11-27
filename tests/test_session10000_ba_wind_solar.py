"""Session 10000 (chain 701, predict data request 10): eia930_ba_wind_solar_hourly, wind and solar net generation by
balancing authority from the saved six-month files. Made-up frames; no table or file is read."""
import importlib.util
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def load():
    spec = importlib.util.spec_from_file_location("ws_t", os.path.join(ROOT, "warehouse", "connectors", "eia930_ba_wind_solar_hourly.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheRows(unittest.TestCase):
    def setUp(self):
        self.m = load()
        ts = pd.to_datetime(["2025-07-01T07:00:00Z", "2025-07-01T08:00:00Z"], utc=True)
        self.d = pd.DataFrame({"ba": ["SWPP", "SWPP", "TVA", "TVA"], "ts": list(ts) * 2,
                               "wind": [12000.0, 11000.0, 0.0, 0.0], "solar": [300.0, None, 5.0, 6.0]})

    def test_an_all_zero_series_is_left_out_and_a_blank_hour_not_written(self):
        out = self.m.file_rows(self.d, "EIA930_BALANCE_2025_Jul_Dec.csv", "u", "2026-11-27T00:00:00Z", "")
        got = {(r.entity, r.variable): r.value for r in out.itertuples() if r.ts == self.d.ts[0]}
        self.assertEqual(got[("eia930:SWPP", "net_generation_wind_mw")], 12000.0)
        self.assertNotIn(("eia930:TVA", "net_generation_wind_mw"), got)       # TVA's wind is zero in every hour of the file
        self.assertEqual(got[("eia930:TVA", "net_generation_solar_mw")], 5.0)
        self.assertEqual(len(out[(out.entity == "eia930:SWPP") & (out.variable == "net_generation_solar_mw")]), 1)
        self.assertEqual(set(out["ba"]), {"swpp", "tva"})

    def test_the_battery_columns_are_one_source(self):
        import eia930_region_fuel_hourly as rf
        self.assertEqual(rf.source_of("Net Generation (MW) from Solar witho Integrated Battery Storage (Adjusted)")[0], "solar")
        self.assertEqual(rf.source_of("Net Generation (MW) from Wind with Integrated Battery Storage")[0], "wind")


class TheRecords(unittest.TestCase):
    def test_held_out_of_the_catalogue_and_release_v1_and_rebuilt_daily(self):
        def read(*p):
            with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
                return f.read()
        self.assertIn("  - eia930_ba_wind_solar_hourly", read("warehouse", "supabase", "live_set.yaml"))
        self.assertIn('STORAGE_HELD["eia930_ba_wind_solar_hourly"]', read("warehouse", "redivis", "release_v1.py"))
        s = read("warehouse", "run_data_machine.sh")
        self.assertLess(s.index("soft_step dm_regions_fuel "), s.index("soft_step dm_ba_wind_solar "))


if __name__ == "__main__":
    unittest.main()
