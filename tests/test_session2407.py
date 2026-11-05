"""Session 2407: Panama's Secretaria Nacional de Energia, Generacion Historica Electrica (1970-2021): gross generation by
plant type, net production, maximum demand and load factor, a year; total gross generation, a month.

Energy Research Warehouse (ERW). Tests warehouse/connectors/sne_panama.py's sheet readers on small workbooks built here in
the layout of the Secretaria's sheets (made up for the test, not its figures): the types and the parts adding to the
total, a blank cell read as no value, the months adding to the annual column; a sum that does not hold, a label missing
and a text value stopping the run; the sector rule and the live-set hold (internal). No network, no workbook file.

    python -m unittest tests.test_session2407 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import sne_panama as P  # noqa: E402
import build_coverage as B  # noqa: E402


class Sheet:
    def __init__(self, rows):
        self.rows = rows

    @property
    def nrows(self):
        return len(self.rows)

    @property
    def ncols(self):
        return max(len(r) for r in self.rows)

    def cell_value(self, r, c):
        row = self.rows[r]
        return row[c] if c < len(row) else ""


class Book:
    def __init__(self, sheets):
        self.sheets = sheets

    def sheet_by_name(self, name):
        return self.sheets[name]


LABELS = ["Total del Sistema", "Total - Sistema Interconectado Nacional\n(1a+2a)", "Total - Autoridad del Canal de Panama",
          "1.  Total Hidroelectricas", "2.  Vapor ( Bunker)", "3.  Combustion Interna  (Bunker/Diesel)",
          "4.  Turbina de Gas  (Diesel Liviano)", "5.  Turbina de Gas  (Diesel Marino)", "6.  Sub-Total  (Diesel Liviano)",
          "7.  Centrales Eolicas", "8.  Central Solar", "9.  Planta de Gas Natural", "10. Planta de Biogas", "11.  Sistemas Aislados"]


def ge8(total=100.0, hydro=60.0):
    vals = {"Total del Sistema": [total, 50.0], "Total - Sistema": [90.0, 45.0], "Total - Autoridad": [5.0, ""],
            "1.": [hydro, 30.0], "2.": [20.0, 10.0], "3.": [10.0, 5.0], "4.": [0.0, 0.0], "5.": [0.0, ""], "6.": [0.0, 0.0],
            "7.": [5.0, ""], "8.": ["", ""], "9.": ["", ""], "10.": ["", ""], "11.": [5.0, 5.0]}
    rows = [["", "CUADRO GE-8"], ["", "Tipo y Planta", 2020.0, 2021.0]]
    for lab in LABELS:
        key = next(k for k in vals if lab.startswith(k))
        rows.append(["", lab] + vals[key])
        rows.append(["", "a plant", 1.0, 1.0])
    return Sheet(rows)


def ge10(dec=10.0):
    return Sheet([["", "CUADRO GE-10"], ["", "Ano", "Anual", "Enero"] + [""] * 11,
                  ["", 2021.0, 120.0] + [10.0] * 11 + [dec], [""], ["", "Tasa Promedio"], ["", "1980-1990", 3.9]])


def ge14():
    return Sheet([["", "CUADRO GE-14"], ["", "Ano", "Produccion Neta\n(GWh)", "Incremento\n(GWh)", "Demanda Maxima\n(MW)", "Incremento\n(MW)", "Factor de Carga\n(%)"],
                  ["", 1970.0, 801.7, "", "", "", ""], ["", 2021.0, 13234.0, 1136.5, 2020.0, 51.0, 74.79], [""], ["", "TASA PROMEDIO"], ["", "1975-1980", 0.07]])


class Readers(unittest.TestCase):
    def test_ge8(self):
        got = P.ge8(Book({P.GE8: ge8()}))
        self.assertEqual(got["generation_gross_total"], {2020: 100.0, 2021: 50.0})
        self.assertEqual(got["generation_gross_canal_authority"], {2020: 5.0, 2021: None})
        self.assertEqual(got["generation_gross_solar"], {2020: None, 2021: None})
        self.assertEqual(got["generation_gross_hydro"][2021], 30.0)

    def test_ge8_stops(self):
        for sheet in (ge8(total=101.0), ge8(hydro=61.0), ge8(hydro="sixty")):
            with self.assertRaises(RuntimeError):
                P.ge8(Book({P.GE8: sheet}))
        broken = ge8()
        broken.rows = [r for r in broken.rows if not str(r[1]).startswith("8.")]
        with self.assertRaises(RuntimeError):
            P.ge8(Book({P.GE8: broken}))

    def test_ge10(self):
        got = P.ge10(Book({P.GE10: ge10()}))
        self.assertEqual(list(got), [2021])
        self.assertEqual(got[2021][0], 120.0)
        self.assertEqual(len(got[2021][1]), 12)
        with self.assertRaises(RuntimeError):
            P.ge10(Book({P.GE10: ge10(dec=11.0)}))
        with self.assertRaises(RuntimeError):
            P.ge10(Book({P.GE10: ge10(dec="")}))

    def test_ge14(self):
        got = P.ge14(Book({P.GE14: ge14()}))
        self.assertEqual(got[1970], [801.7, None, None])
        self.assertEqual(got[2021], [13234.0, 2020.0, 74.79])
        self.assertEqual(sorted(got), [1970, 2021])


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            held = f.read().replace("\r\n", "\n")
        for name in (P.ANNUAL, P.MONTHLY):
            self.assertEqual(B.sector_of(name), "power")
            self.assertIn(f"  - {name}\n", held)


if __name__ == "__main__":
    unittest.main()
