"""Session 2446: EPE's Statistical Yearbook of Electricity, raw data (Brazil's monthly consumption by state, class and sector).

Energy Research Warehouse (ERW). Tests warehouse/connectors/epe_brazil_electricity.py on rows built here in the
workbook's form (made up for the test, not EPE's): EPE's leaf rows summed over system, the sector's lower levels, voltage
and band into one row a state, class, sector and month, consumption in MWh and consumers as a count, a blank with no part
in a sum, a cell with neither figure having no row; a header not as read, a date not of the form YYYYMM01, a class or state
not in the map and a value that is not a number stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2446 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import epe_brazil_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def leaf(date=20240301, klass="Cativo", system="Sul", uf="RS", sector="Residencial", n3="TOTAL", volt="TOTAL", users=10, cons=12.5):
    return (date, klass, system, uf, sector, "Convencional", n3, "B - Baixa Tensão", volt, "TOTAL", "Convencional", "Convencional", users, cons)


class Parse(unittest.TestCase):
    def test_rows(self):
        rows = [tuple(S.HEADER), leaf(), leaf(system="Sistemas Isolados", n3="Baixa Renda N2", users=5, cons=2.5), leaf(users=None, cons=1.0),
                leaf(klass="Livre", sector="Industrial", users=2, cons=None), leaf(uf="SP", users=None, cons=None), (None,) * 14]
        t = S.parse(rows, BASE).set_index(["entity", "variable", "ts_utc"])
        c = t.loc[("epe:br:rs:captive:residencial", "consumption", "2024-03-01T00:00:00Z")]
        self.assertEqual((c.value, c.unit, c.freq, c.geo, c.x_rows), (16.0, "MWh", "P1M", "BR-RS", 3))
        self.assertEqual(t.loc[("epe:br:rs:captive:residencial", "consumers", "2024-03-01T00:00:00Z")].value, 15.0)
        self.assertEqual(t.loc[("epe:br:rs:free:industrial", "consumers", "2024-03-01T00:00:00Z")].unit, "count")
        self.assertNotIn(("epe:br:rs:free:industrial", "consumption", "2024-03-01T00:00:00Z"), t.index)
        self.assertFalse(any(e.startswith("epe:br:sp:") for e, _, _ in t.index))
        self.assertEqual(len(t), 3)

    def test_stops(self):
        h = tuple(S.HEADER)
        for rows in ([h[:-1] + ("Consumo MWh",), leaf()], [h, leaf(date=20240315)], [h, leaf(klass="Especial")], [h, leaf(uf="XX")],
                     [h, leaf(cons="doze")]):
            with self.assertRaises(RuntimeError):
                S.parse(rows, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
