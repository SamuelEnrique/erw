"""Session 885: EIA-860's owner, energy storage, solar and wind schedules.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia860_schedules.py on sheets built here in EIA's form
(figures made up for the test, not EIA's): a title row over the headings, EIA's status codes as the data standard's
words with the code kept, the status date from the month of operation or retirement, the owner's share as an entity of
its own, footnote rows read past, a code not in the map stopping the run, a key given twice with two rows left out and
counted, the sector rules and the holds. No network.

    python -m unittest tests.test_session885 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia860_schedules as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")
GEN = ["Utility ID", "Utility Name", "Plant Code", "Plant Name", "State", "County", "Generator ID", "Status", "Technology",
       "Prime Mover", "Nameplate Capacity (MW)", "Operating Month", "Operating Year", "Retirement Month", "Retirement Year",
       "Nameplate Energy Capacity (MWh)"]


def gen_sheet(rows):
    return pd.DataFrame([["2025 Form EIA-860 Data - Schedule 3"] + [N] * (len(GEN) - 1), GEN] + rows)


class Generators(unittest.TestCase):
    def test_status_words_and_dates(self):
        rows = [[1, "U", 141, "Agua Fria", "AZ", "Maricopa", "B1", "OP", "Batteries", "BA", 25, 9, 2021, N, N, 100],
                [1, "U", 260, "Moss", "CA", "Monterey", "B2", "RE", "Batteries", "BA", 300, 5, 2021, 1, 2025, 1200],
                [1, "U", 377, "Grayson", "CA", "LA", "10", "V", "Batteries", "BA", 75, 11, 2026, N, N, 300],
                ["NOTE: footnote", N, N, N, N, N, N, N, N, N, N, N, N, N, N, N]]
        t = S.sheet_rows(gen_sheet(rows), "3_4_Energy_Storage", "Operable", 2025, "u", "r").set_index("entity_id")
        self.assertEqual(list(t.index), ["eia860_storage:141:B1", "eia860_storage:260:B2", "eia860_storage:377:10"])
        self.assertEqual(tuple(t.status), ("operating", "retired", "under_construction"))
        self.assertEqual(tuple(t.status_date), ("2021-09-01", "2025-01-01", ""))
        self.assertEqual(t.loc["eia860_storage:260:B2", "x_eia_status"], "RE")
        self.assertEqual(t.loc["eia860_storage:141:B1", "x_nameplate_energy_capacity_mwh"], "100")
        self.assertEqual((t.loc["eia860_storage:141:B1", "capacity_mw"], t.loc["eia860_storage:141:B1", "geo"]), ("25", "US-AZ"))

    def test_a_code_not_in_the_map_stops(self):
        rows = [[1, "U", 141, "A", "AZ", "M", "B1", "ZZ", "Batteries", "BA", 25, 9, 2021, N, N, 100]]
        with self.assertRaises(RuntimeError):
            S.sheet_rows(gen_sheet(rows), "3_4_Energy_Storage", "Operable", 2025, "u", "r")

    def test_a_key_twice_with_two_rows_is_left_out(self):
        rows = [[1, "U", 5, "A", "TX", "C", "W1", "OP", "Wind", "WT", 2, 1, 2020, N, N, N],
                [1, "U", 5, "A", "TX", "C", "W1", "OP", "Wind", "WT", 3, 1, 2020, N, N, N],
                [1, "U", 6, "B", "TX", "C", "W1", "OP", "Wind", "WT", 3, 1, 2020, N, N, N],
                [1, "U", 6, "B", "TX", "C", "W1", "OP", "Wind", "WT", 3, 1, 2020, N, N, N]]
        sk = {}
        t = S.keyed(S.sheet_rows(gen_sheet(rows), "3_2_Wind", "Operable", 2025, "u", "r"), sk, "w")
        self.assertEqual(t.entity_id.tolist(), ["eia860_wind:6:W1"])
        self.assertEqual(sk["w"], ["eia860_wind:5:W1"])


class Owners(unittest.TestCase):
    def test_each_share_an_entity(self):
        head = ["Utility ID", "Utility Name", "Plant Code", "Plant Name", "State", "Generator ID", "Status", "Owner Name",
                "Owner City", "Ownership ID", "Percent Owned"]
        rows = [[195, "Alabama Power Co", 10, "Greene County", "AL", "1", "OP", "Alabama Power Co", "Birmingham", 195, 0.6],
                [195, "Alabama Power Co", 10, "Greene County", "AL", "1", "OP", "Mississippi Power Co", "Gulfport", 12686, 0.4]]
        t = S.sheet_rows(pd.DataFrame([["title"] + [N] * 10, head] + rows), "4___Owner", "Ownership", 2025, "u", "r")
        self.assertEqual(t.entity_id.tolist(), ["eia860_owner:10:1:195", "eia860_owner:10:1:12686"])
        self.assertEqual(t.name.tolist(), ["Alabama Power Co", "Mississippi Power Co"])
        self.assertEqual(set(t.entity_type), {"company"})
        self.assertEqual(t.x_percent_owned.tolist(), ["0.6", "0.4"])
        self.assertEqual(t.x_plant_name.iloc[0], "Greene County")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        for name in ("eia860_generator_owners", "eia860_storage_generators", "eia860_solar_generators", "eia860_wind_generators"):
            self.assertEqual(B.sector_of(name), "power")
            self.assertIn(name, R.STORAGE_HELD)
            with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
                self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
