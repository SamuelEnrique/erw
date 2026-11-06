"""Session 2823: HOPS, Croatia's transmission network a year (Elektroenergetski podaci).

Energy Research Warehouse (ERW). Tests warehouse/connectors/hops_croatia.py on a page built here (made up for the test, not
HOPS's): the dot as a thousands separator, GWh written as MWh and the loads in MW with their day and hour, rows continuing the
block above; the page's four balances, a case off counted; no table, a header not of years, a row not in the structure and a
value not a number stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2823 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import hops_croatia as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def tr(*c):
    return "<tr>" + "".join(f"<td>{x}</td>" for x in c) + "</tr>"


def page(hydro="4.809", head="Osnovni podaci", extra=None, carried="22.098"):
    rows = [tr(head, "2017.", "2018."),
            tr("Proizvodnja na prijenosnoj mreži (GWh)", "Hidroelektrane", hydro, "6.691"),
            tr("Termoelektrane", "4.044", "3.206"), tr("Vjetroelektrane", "1.088", "1.240"), tr("Solarne elektrane", "0", "0"),
            tr("Ukupna proizvodnja", "9.941", "11.137"),
            tr("Prekogranična razmjena (GWh)", "Ulaz u RH (uključujući 50% NE Krško)", "12.157", "12.692"),
            tr("Izlaz iz RH", "4.778", "6.532"), tr("Razlika razmjene", "7.379", "6.160"),
            tr("Ukupna prenesena energija na prijenosnoj mreži (GWh)", carried, "23.931"),
            tr("Najveće opterećenje sustava", "MWh/h", "3.079", "3.168"), tr("Datum", "04.08.2017.", "26.02.2018."), tr("Sat", "14 h", "20 h"),
            tr("Najmanje opterećenje sustava", "MWh/h", "1.305", "1.249"), tr("Datum", "18.09.2017.", "20.05.2018."), tr("Sat", "04 h", "06 h"),
            tr("Potrošnja na prijenosnoj mreži bez gubitaka (GWh)", "16.903", "16.763"),
            tr("Gubici u prijenosnoj mreži (GWh)", "417", "534"),
            tr("Isporuka svim kupcima izravno priključenim na prijenosnu mrežu (GWh)", "1.085", "1.060")]
    if extra:
        rows.append(tr(extra, "1", "2"))
    return ("<html><body><table>" + "".join(rows) + "</table></body></html>").encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        years, out, extra = A.parse(page())
        self.assertEqual(years, [2017, 2018])
        t = A.frame(out, extra, "r", "v")
        self.assertEqual(len(t), 14 * 2)
        v = t.set_index(["entity", "variable", t.ts_utc.str[:4]])
        self.assertEqual(v.loc[("hops:hr:hydro", "generation", "2017"), "value"], 4809000.0)
        self.assertEqual(v.loc[("hops:hr", "imports", "2017"), "x_label"], "Prekogranična razmjena (GWh) / Ulaz u RH (uključujući 50% NE Krško)")
        pk = v.loc[("hops:hr", "peak_load", "2017")]
        self.assertEqual((pk.value, pk.unit, pk.x_day, pk.x_hour), (3079.0, "MW", "04.08.2017.", "14 h"))
        self.assertEqual(v.loc[("hops:hr", "minimum_load", "2018"), "x_hour"], "06 h")
        n, off = A.checks(t)
        self.assertEqual(n, 8)
        self.assertEqual([x[:2] for x in off], [("2018", "production and imports against the energy carried"),
                                                ("2018", "consumption, losses and exports against the energy carried")])

    def test_counted(self):
        n, off = A.checks(A.frame(*A.parse(page(carried="22.200"))[1:], "r", "v"))
        self.assertIn(("2017", "production and imports against the energy carried", -102.0), off)

    def test_stops(self):
        for content in (b"<html></html>", page(head="Podaci"), page(extra="Nuklearna elektrana"), page(hydro="n.a.")):
            with self.assertRaises(RuntimeError):
                A.parse(content)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()
