"""Session 7052 (chain 370, the data machine): done-line request 239.

Each frozen level of the home battery game now carries `fleet`, the grid's operating battery storage at the start of
the level's month (MW, MWh where EIA-860M gives an energy capacity, the unit count), from the EIA-860M operating and
retired generators, by the same rule as the solar nameplate. No level, date or price moves.
"""

import importlib.util
import json
import os
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def builder():
    spec = importlib.util.spec_from_file_location("battery_solar_7052", os.path.join(ROOT, "warehouse", "derived", "battery_solar.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def gens():
    # test data written here by hand, never a reported figure
    return pd.DataFrame([
        {"balancing_authority": "ERCO", "energy_source": "MWH", "nameplate_mw": 10.0, "energy_capacity_mwh": 20.0,
         "start": pd.Timestamp("2020-01-01"), "ret": pd.NaT},
        {"balancing_authority": "ERCO", "energy_source": "MWH", "nameplate_mw": 5.0, "energy_capacity_mwh": None,
         "start": pd.Timestamp("2020-06-01"), "ret": pd.NaT},
        {"balancing_authority": "ERCO", "energy_source": "MWH", "nameplate_mw": 7.0, "energy_capacity_mwh": 7.0,
         "start": pd.Timestamp("2019-01-01"), "ret": pd.Timestamp("2020-03-15")},
        {"balancing_authority": "ERCO", "energy_source": "MWH", "nameplate_mw": 9.0, "energy_capacity_mwh": 9.0,
         "start": pd.Timestamp("2021-01-01"), "ret": pd.NaT},
        {"balancing_authority": "ERCO", "energy_source": "SUN", "nameplate_mw": 100.0, "energy_capacity_mwh": None,
         "start": pd.Timestamp("2019-01-01"), "ret": pd.NaT},
        {"balancing_authority": "CISO", "energy_source": "MWH", "nameplate_mw": 50.0, "energy_capacity_mwh": 200.0,
         "start": pd.Timestamp("2019-01-01"), "ret": pd.NaT},
    ])


class TheFleetAtTheMonth(unittest.TestCase):
    def test_operating_at_the_months_first_day(self):
        m = builder()
        self.assertEqual(m.fleet_at(gens(), "ERCO", "2020-03"), (17.0, 27.0, 2, 2))   # the retired unit still runs on 1 March
        self.assertEqual(m.fleet_at(gens(), "ERCO", "2020-04"), (10.0, 20.0, 1, 1))
        self.assertEqual(m.fleet_at(gens(), "ERCO", "2020-07"), (15.0, 20.0, 2, 1))   # a unit without MWh adds MW and a count
        self.assertEqual(m.fleet_at(gens(), "ERCO", "2018-12"), (0.0, 0.0, 0, 0))

    def test_the_record_names_its_source(self):
        m = builder()
        r = m.fleet_record("ERCO", "2020-07", m.fleet_at(gens(), "ERCO", "2020-07"), ["2026-09"], "2026-11-17T00:00:00Z")
        self.assertEqual((r["mw"], r["mwh"], r["units"], r["units_with_mwh"]), (15.0, 20.0, 2, 1))
        self.assertIn("EIA-860M operating and retired generators", r["source"])

    def test_the_committed_levels_carry_a_fleet(self):
        with open(os.path.join(ROOT, "site", "data", "battery_levels.json"), encoding="utf-8") as f:
            d = json.load(f)
        for lv in d["levels"]:
            fl = lv["fleet"]
            self.assertEqual(fl["month"], lv["date"][:7], lv["slug"])
            self.assertEqual(fl["ba"], {"ERCOT": "ERCO", "CAISO": "CISO"}[lv.get("grid", "ERCOT")])
            self.assertGreater(fl["units"], 0)
            self.assertLessEqual(fl["units_with_mwh"], fl["units"])
            self.assertIn("EIA-860M", fl["source"])

    def test_the_level_builder_keeps_the_fleet(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "battery_levels.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('lv["fleet"] = was["fleet"]', src)


if __name__ == "__main__":
    unittest.main()
