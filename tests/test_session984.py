"""Session 984: EIA's Electric Power Annual capacity factors and heat rates.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_epa_tables.py on sheets built here in EIA's form
(figures made up for the test, not EIA's): a fuel's technologies, the annual rows and the months under a year, heat
rates as MMBtu/MWh; a heading not as read stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session984 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_epa_tables as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
TAC, CFH = "Time Adjusted Capacity (MW)", "Capacity Factor"


def cf_sheet():
    rows = [["Table 4.08.A", None, None, None, None],
            [None, "Coal", None, "Natural Gas", None],
            ["Year/Month", None, None, "Combined Cycle", None],
            [None, TAC, CFH, TAC, CFH],
            ["Annual Data", None, None, None, None],
            [2024, 180000, 0.426, 290000, 0.605],
            ["Year 2024", None, None, None, None],
            ["January", 170000, 0.5, 291000, None],
            ["Note", None, None, None, None]]
    return pd.DataFrame(rows)


def hr_sheet():
    return pd.DataFrame([["Table 8.1", None, None, None, None], ["2015 through 2025   (Btu per Kilowatthour)", None, None, None, None],
                         ["Year", "Coal", "Petroleum", "Natural Gas", "Nuclear"], [2025, 10647, 10969, 7781, 10443], ["Note", None, None, None, None]])


class Sheets(unittest.TestCase):
    def test_capacity_factors(self):
        s = pd.DataFrame(E.capacity_factors(cf_sheet(), BASE))
        a = s[(s.entity == "eia_epa_cf:natural_gas:combined_cycle") & (s.variable == "capacity_factor") & (s.freq == "P1Y")].iloc[0]
        self.assertEqual((a.ts_utc, a.value, a.unit), ("2024-01-01T00:00:00Z", 0.605, "ratio"))
        m = s[(s.entity == "eia_epa_cf:coal:all") & (s.freq == "P1M")]
        self.assertEqual(sorted(m.variable), ["capacity_factor", "time_adjusted_capacity"])
        self.assertEqual(m.ts_utc.unique().tolist(), ["2024-01-01T00:00:00Z"])
        self.assertEqual(len(s[(s.freq == "P1M") & (s.entity == "eia_epa_cf:natural_gas:combined_cycle")]), 1)  # an empty cell has no row

    def test_heat_rates(self):
        h = pd.DataFrame(E.heat_rates(hr_sheet(), BASE)).set_index("entity")
        self.assertEqual((h.loc["eia_epa_heat_rate:coal"].value, h.loc["eia_epa_heat_rate:coal"].unit), (10.647, "MMBtu/MWh"))

    def test_stops(self):
        bad = cf_sheet()
        bad.iloc[3, 2] = "Factor"
        with self.assertRaises(RuntimeError):
            E.capacity_factors(bad, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            live = f.read().replace("\r\n", "\n")
        for name in (E.CFA, E.CF, E.HR):
            self.assertEqual(B.sector_of(name), "power")
            self.assertIn(name, R.STORAGE_HELD)
            self.assertIn(f"  - {name}\n", live)


if __name__ == "__main__":
    unittest.main()
