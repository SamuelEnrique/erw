"""Session 2108: EIA's State Energy Data System, the residential sector's expenditures.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_seds_residential.py on API rows built here in EIA's
form (figures made up for the test, not EIA's): million dollars, billion Btu and thousands scaled, a withheld value left
out, the nation's geo; a unit not in the map, a series not asked for and a key given twice each stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2108 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_seds_residential as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def row(sid, st, value, unit, period=2024):
    return {"period": str(period), "seriesId": sid, "stateId": st, "value": value, "unit": unit, "seriesDescription": f"{sid} in {st}"}


class Rows(unittest.TestCase):
    def test_scaled(self):
        t = S.rows([row("ESRCV", "VT", "512.3", "Million dollars"), row("TERCB", "VT", "41234", "Billion Btu"),
                    row("TPOPP", "US", "340110.5", "Thousand"), row("TERCD", "VT", "31.2", "Dollars per million Btu"),
                    row("WDRCV", "VT", "(s)", "Million dollars")], "u", "r")
        self.assertEqual(len(t), 4)  # the withheld value has no row
        e = t[t.x_series == "ESRCV"].iloc[0]
        self.assertEqual((e.entity, e.variable, e.value, e.unit, e.geo, e.x_source),
                         ("eia_seds_res:ESRCV:VT", "expenditures", 512.3e6, "USD", "US-VT", "electricity"))
        self.assertAlmostEqual(t[t.x_series == "TERCB"].value.iloc[0], 41.234)
        p = t[t.x_series == "TPOPP"].iloc[0]
        self.assertEqual((p.value, p.unit, p.geo, p.variable), (340110500.0, "count", "US", "population"))
        self.assertEqual(t[t.x_series == "TERCD"].iloc[0].unit, "USD/MMBtu")

    def test_stops(self):
        for data, words in [([row("ESRCV", "VT", "1", "Dollars")], "unit not in the map"), ([row("ESTCV", "VT", "1", "Million dollars")], "not asked"),
                            ([row("ESRCV", "VT", "1", "Million dollars"), row("ESRCV", "VT", "2", "Million dollars")], "twice")]:
            with self.assertRaises(RuntimeError) as c:
                S.rows(data, "u", "r")
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.TABLE), "power;gas;oil")
        self.assertIn(S.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
