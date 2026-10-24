"""Session 2408: Guatemala's Administrador del Mercado Mayorista, Generacion Mensual por Planta: generation by fuel,
imports, exports and the national interconnected system's demand, a month.

Energy Research Warehouse (ERW). Tests warehouse/connectors/amm_guatemala.py's sheet reader on rows built here in the
layout of AMM's workbooks (made up for the test, not its figures): labels with and without accents, a blank fuel month
read as no value, the fuels adding to the total and the system rows agreeing; a sum that does not hold, a wrong year, an
unknown fuel and a blank system month stopping the run; the address by year; the sector rule and the live-set hold
(internal). No network, no workbook file.

    python -m unittest tests.test_session2408 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import amm_guatemala as A  # noqa: E402
import build_coverage as B  # noqa: E402

LONG = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE", "TOTAL"]
SHORT = ["Ene.", "Feb.", "Mar.", "Abr.", "May.", "Jun.", "Jul.", "Ago.", "Sep.", "Oct.", "Nov.", "Dic.", "GWh"]


def row(label, v, total=True):
    vals = list(v) if isinstance(v, list) else [v] * 12
    return ["", label] + vals + ([sum(x or 0 for x in vals)] if total else [""])


def sheet(year=2024, hydro=6.0, imports=1.0, coke=None, unknown=False, demand_blank=False):
    coke = coke if coke is not None else [None, None] + [1.0] * 10
    total = [hydro + 3.0 + (c or 0) for c in coke]
    exports = 2.0
    rows = [[""], ["", "           DESPACHO DE CARGA EJECUTADO"], ["", year], [""], ["", ""] + LONG, ["", ""] + ["ENERGIA"] * 13,
            ["", "PLANTAS HIDROELECTRICAS"] + [hydro] * 12 + [hydro * 12], ["", "GENERACIÓN DISTRIBUIDA RENOVABLE"],
            row("TRANSACCIONES REGIONALES", exports - imports), row("IMPORTACIONES", imports), row("EXPORTACIONES", exports),
            row("GENERACIÓN TOTAL S.N.I.", total),
            row("DEMANDA S.N.I.", [None] * 12 if demand_blank else [t - (exports - imports) for t in total]),
            [""], ["", ""] + SHORT, ["", "GENERACIÓN POR TIPO DE COMBUSTIBLE"] + ["GWh"] * 13,
            row("Geotérmica", 1.0), row("Eólica", 2.0), row("Hidroeléctrica", hydro), row("Coque de Petróleo", coke)]
    if unknown:
        rows.append(row("Nuclear", 0.0))
    rows.append(row("TOTAL", total))
    return [["" if c is None else c for c in r] for r in rows]


class Reader(unittest.TestCase):
    def test_values(self):
        got = A.year_values(sheet(), 2024)
        self.assertEqual(sorted(got), sorted(["generation_geothermal", "generation_wind", "generation_hydro", "generation_petcoke",
                                              "net_exports", "imports", "exports", "generation_total", "demand_sni"]))
        self.assertEqual(got["generation_petcoke"][:3], [None, None, 1.0])
        self.assertEqual(got["generation_total"][0], 9.0)
        self.assertEqual(got["demand_sni"][5], 9.0)

    def test_stops(self):
        for rows, year in ((sheet(), 2023), (sheet(unknown=True), 2024), (sheet(demand_blank=True), 2024)):
            with self.assertRaises(RuntimeError):
                A.year_values(rows, year)
        bad = sheet()
        bad[-1][3] = 99.0   # the fuel TOTAL's February
        with self.assertRaises(RuntimeError):
            A.year_values(bad, 2024)
        bad = sheet()
        bad[9][2] = 5.0     # IMPORTACIONES' January no longer agrees with TRANSACCIONES
        with self.assertRaises(RuntimeError):
            A.year_values(bad, 2024)

    def test_address(self):
        self.assertTrue(A.url_of(2020).endswith("/GM20200101.xls"))
        self.assertTrue(A.url_of(2021).endswith("/GM20210101.xlsx"))


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
