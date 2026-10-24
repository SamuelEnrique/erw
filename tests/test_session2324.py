"""Session 2324: ANEEL's SIGA, Brazil's generation plants, in place of Ecuador.

Energy Research Warehouse (ERW). Tests warehouse/connectors/aneel_siga.py on a file built here in SIGA's form (made up
for the test, not ANEEL's): kW written as MW, decimal commas, ANEEL's phases as the standard's statuses, coordinates of
0 and 0 left empty, a plant listed under two grant types kept once with both; a header not ANEEL's, a phase not in the
map, a number not in ANEEL's form, a plant given twice with other fields differing and two generation dates stopping
the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2324 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import aneel_siga as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402

HEAD = ";".join(f'"{h}"' for h in A.HEAD) + "\n"


def line(ceg="UFV.RS.PA.000001-1.1", phase="Operação", grant="Registro", kw="1400,00", lat="-20,5", lon="-43,25", date="2026-10-01", typ="UFV"):
    cells = [date, "Usina X", "000001", ceg, "PA", typ, phase, "Solar", "Radiação solar", grant, "Radiação solar", "2020-01-02",
             kw, "1400", ",00", "Não", lat, lon, "2020-01-01", "2050-01-01", "100% para Y", "", "Belém - PA"]
    return ";".join(f'"{c}"' for c in cells) + "\n"


class Rows(unittest.TestCase):
    def test_rows(self):
        text = HEAD + line() + line("UFV.RS.PA.000002-1.1", phase="Construção não iniciada", lat="0", lon="0")
        t = A.finish(A.file_rows(text, "r", "v"))
        a = t[t.entity_id == "aneel_siga:UFV.RS.PA.000001-1.1"].iloc[0]
        self.assertEqual((a.capacity_mw, a.x_capacity_operating_mw, a.x_physical_guarantee_mw, a.lat, a.lon, a.status, a.geo, a.status_date),
                         (1.4, 1.4, 0.0, -20.5, -43.25, "operating", "BR-PA", "2020-01-02"))
        b = t[t.entity_id == "aneel_siga:UFV.RS.PA.000002-1.1"].iloc[0]
        self.assertTrue(b.lat != b.lat and b.lon != b.lon)   # empty, not 0
        self.assertEqual(b.status, "planned")

    def test_two_grants(self):
        t = A.finish(A.file_rows(HEAD + line(grant="Autorização") + line(grant="Concessão"), "r", "v"))
        self.assertEqual((len(t), t.x_grant_type.iloc[0]), (1, "Autorização;Concessão"))

    def test_stops(self):
        for text in (HEAD.replace("CodCEG", "Cod") + line(), HEAD + line(phase="Desativada"), HEAD + line(kw="1.400,00"), HEAD + line(typ="XYZ")):
            with self.assertRaises(RuntimeError):
                A.file_rows(text, "r", "v")
        with self.assertRaises(RuntimeError):
            A.finish(A.file_rows(HEAD + line() + line(kw="1500,00"), "r", "v"))
        with self.assertRaises(RuntimeError):
            A.finish(A.file_rows(HEAD + line() + line("UFV.RS.PA.000003-1.1", date="2026-09-01"), "r", "v"))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
