"""Session 953: the Monthly Energy Review's Tables 1.1 to 1.3 in eia_series.py.

Energy Research Warehouse (ERW). Tests the eia_primary_energy_monthly entry of warehouse/connectors/eia_series.py with
the API's answer built here (figures made up for the test, not EIA's): each series' variable from its MSN, "Not
Available" omitted, a non-number stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session953 -v
"""

import os
import sys
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_series as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

NAME = "eia_primary_energy_monthly"


def answer(values):
    rows = []
    for msn, period, v in values:
        rows.append({"msn": msn, "seriesDescription": msn + " in Trillion Btu", "period": period, "value": v, "unit": "Trillion Btu",
                     "_url": "u", "_retrieved": "2026-10-23T00:00:00Z"})
    return pd.DataFrame(rows)


class Primary(unittest.TestCase):
    def run_build(self, values):
        written = {}
        recent = (pd.Timestamp.now(tz="UTC") - pd.DateOffset(months=2)).strftime("%Y-%m")
        values = [(m, recent if p == "recent" else p, v) for m, p, v in values]
        with mock.patch.object(E, "fetch", return_value=answer(values)), \
                mock.patch.object(E.ip, "write_csv", side_effect=lambda s, name, header, log: written.update(s=s, header=header)), \
                mock.patch.object(E.ip, "update_sources"):
            E.build(NAME, E.TABLES[NAME], "k", "run", lambda *a: None)
        return written["s"]

    def test_variables(self):
        s = self.run_build([("TEPRBUS", "recent", "8000"), ("TENIBUS", "recent", "-300"), ("NUETBUS", "recent", "700"),
                            ("SOTCBUS", "1980-01", "Not Available")]).set_index("entity")
        self.assertEqual(len(s), 3)
        self.assertEqual((s.loc["eia:TEPRBUS"].variable, s.loc["eia:TENIBUS"].variable, s.loc["eia:NUETBUS"].variable),
                         ("production", "net_imports", "consumption_production"))
        self.assertEqual((s.loc["eia:TEPRBUS"].unit, s.loc["eia:TEPRBUS"].geo), ("TBtu", "US"))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            self.run_build([("TEPRBUS", "recent", "8000"), ("TETCBUS", "recent", "W")])

    def test_every_msn_has_a_variable(self):
        self.assertEqual(len(E.MER_PRIMARY), 24)
        self.assertTrue(set(E.MER_PRIMARY.values()) <= {"production", "imports", "exports", "net_imports", "stock_change_and_other",
                                                      "consumption", "consumption_production"})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(NAME), "power;gas;oil;coal")
        self.assertIn(NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
