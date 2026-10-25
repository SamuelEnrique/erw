"""Session 2240: ONS's open data, Brazil's energy balance an hour by subsystem (Balanco de Energia nos Subsistemas).

Energy Research Warehouse (ERW). Tests warehouse/connectors/ons_balance.py on a file built here in ONS's form (made up for
the test, not ONS's): Brasilia time placed in UTC (plus three hours), the six measures in MW, a blank without a row; a
header not ONS's, a subsystem not named, a stamp not in ONS's form, a value that is not a number and an hour given twice
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2240 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ons_balance as O  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402

HEAD = ";".join(O.HEADER) + "\n"


def line(sub="N  ", name="NORTE", stamp="2026-01-01 00:00:00", vals=("11587.0", "1864.9", "263.0", "0.0", "7622.6", "6092.3")):
    return ";".join([sub, name, stamp, *vals]) + "\n"


class Rows(unittest.TestCase):
    def test_rows(self):
        t = O.finish([O.file_rows(HEAD + line() + line(sub="SIN", name="SISTEMA INTERLIGADO NACIONAL", vals=("1", "2", "", "4", "5", "0")), "u", "r", "v")])
        n = t[(t.entity == "ons:N") & (t.variable == "load")].iloc[0]
        self.assertEqual((n.ts_utc, n.value, n.unit, n.freq, n.geo, n.node, n.x_brasilia_hour),
                         ("2026-01-01T03:00:00Z", 7622.6, "MW", "PT1H", "BR", "NORTE", "2026-01-01 00:00:00"))
        self.assertEqual(len(t[t.entity == "ons:SIN"]), 5)
        self.assertEqual(set(t.variable), set(O.FIELDS.values()))

    def test_stops(self):
        for text in ("id;nome;din_instante\n" + line(), HEAD + line(sub="XX"), HEAD + line(stamp="01/01/2026 00:00"),
                     HEAD + line(vals=("lots", "1", "1", "1", "1", "1"))):
            with self.assertRaises(RuntimeError):
                O.file_rows(text, "u", "r", "v")
        with self.assertRaises(RuntimeError):
            O.finish([O.file_rows(HEAD + line() + line(), "u", "r", "v")])


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(O.NAME), "power")
        self.assertIn(O.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {O.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
