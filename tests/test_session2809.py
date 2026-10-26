"""Session 2809: the CZSO's regional electricity tables (Comparison of Regions, 14.101 and 14.103).

Energy Research Warehouse (ERW). Tests warehouse/connectors/czso_regional_electricity.py on a zip built here (made up for the
test, not the CZSO's): the year read from each title, the regions' names read across their line breaks and given ISO codes,
"- " read as zero, GWh written as MWh and MW kept, the share rows and the households' kWh a head not written; the regions
compared with Czechia and the parts with each total, a case counted; a member not in the zip, a title without its year, a
region missing and a row not in the structure stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2809 -v
"""

import io
import os
import sys
import unittest
import zipfile

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import czso_regional_electricity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

NL = chr(10)
HEADS = ["Hl. m." + NL + " Praha", "Středo-" + NL + "český"] + [k for k in list(A.REGIONS)[3:]]


def sheet(title, rows, regions=None):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ENERGETIKA"])
    ws.append([])
    ws.append([title])
    ws.append([None, "Česko " + NL + "Czechia", "v tom kraje"])
    ws.append([None, None] + (regions or HEADS))
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def line(label, cz, each, english=""):
    return [label, cz] + [each] * 14 + [english]


def zipped(year="2024", cons_total=280.0, extra=None, regions=None, drop=None):
    t101 = sheet(f"14.101 Instalovaný výkon ... podle krajů v roce {year}", [
        line("Instalovaný výkon elektráren-ských soustrojí k 31. 12. (MW)", 28.0, 2.0, "Installed capacity (MW)"),
        line("podíl na instalovaném výkonu elektrizační soustavy Česka (%)", 100, 7.1),
        line("jaderné elektrárny", 14.0, 1.0, "Nuclear power plants"),
        line("větrné elektrárny", 14.0, 1.0, "Wind power plants"),
        line("paroplynové elektrárny", "- ", "- ", "Combined power plants"),
        line("Podíl na instalovaném výkonu (%)", 100, 100),
        line("jaderné elektrárny", 50, 50),
        line("Výroba elektřiny brutto (GWh)", 140.0, 10.0, "Gross electricity production (GWh)"),
        line("jaderné elektrárny", 140.0, 10.0, "Nuclear power plants")] + ([line(extra, 1.0, 1.0)] if extra else []), regions)
    t103 = sheet("14.103 Spotřeba elektřiny podle odvětví a krajů v roce 2024", [
        line("Spotřeba elektřiny netto (GWh)", cons_total, 20.0, "Net consumption of electricity (GWh)"),
        line("podíl na spotřebě Česka (%)", 100, 7.1),
        line("domácnosti", 140.0, 10.0, "Households"),
        line("obchod, služby, školství " + NL + "a zdravotnictví", 140.0, 10.0, "Trade and services"),
        line("Spotřeba elektřiny netto v domác-" + NL + "nostech na 1 obyvatele (kWh)", 1436.0, 1400.0)])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for code, member in A.MEMBERS.items():
            if member != drop:
                z.writestr(member, t101 if code == "14101" else t103)
    return buf.getvalue()


class Parse(unittest.TestCase):
    def test_rows(self):
        t = A.build(zipped(), "r", "v")
        self.assertEqual(set(t.ts_utc), {"2024-01-01T00:00:00Z"})
        self.assertEqual(len(t), 15 * 6 + 15 * 3)                            # 101: capacity's four items, production's two; 103: three
        v = {(r.entity, r.variable): r.value for r in t.itertuples()}
        self.assertEqual(v[("czso_regions:CZ-20:nuclear", "installed_capacity")], 1.0)
        self.assertEqual(v[("czso_regions:CZ:combined_cycle", "installed_capacity")], 0.0)
        self.assertEqual(v[("czso_regions:CZ-80:nuclear", "gross_production")], 10000.0)
        self.assertEqual(v[("czso_regions:CZ-10:trade_services", "net_consumption")], 10000.0)
        self.assertEqual(set(t.unit), {"MW", "MWh"})
        self.assertTrue(all(s.isascii() for s in t.node))
        n, off = A.checks(t)
        self.assertEqual(off, [])

    def test_counted(self):
        _, off = A.checks(A.build(zipped(cons_total=290.0), "r", "v"))     # Czechia's total 290, its regions 280
        self.assertIn(("net_consumption", "total", "regions against Czechia", -10.0), off)
        self.assertIn(("net_consumption", "CZ", "parts against the total", -10.0), off)

    def test_stops(self):
        for z in (zipped(year="20x4"), zipped(extra="solární věže"), zipped(regions=HEADS[:-1] + ["Jiný"]),
                  zipped(drop=A.MEMBERS["14103"])):
            with self.assertRaises(RuntimeError):
                A.build(z, "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()
