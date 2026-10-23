"""Session 2034: MSHA's coal mines and their quarterly production.

Energy Research Warehouse (ERW). Tests warehouse/connectors/msha_mines.py on files built here in MSHA's form (made up for
the test, not MSHA's): the coal mines kept and the metal mines left out, the status mapped with MSHA's words kept, a lone
coordinate left empty with its pair; a mine's subunits summed by quarter, a production every subunit leaves empty having
no row, one some leave empty summed and counted; a mine given twice, a status not known and a quarter outside 1 to 4
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2034 -v
"""

import io
import os
import sys
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import msha_mines as M  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def zipped(name, header, rows):
    text = "|".join(header) + "\n" + "\n".join("|".join(f'"{v}"' if v != "" else "" for v in r) for r in rows) + "\n"
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr(name, text.encode("latin-1"))
    return b.getvalue()


MH = M.NEED["mines"]


def mine(i, ind="C", status="Active", lat="37.1", lon="-82.5"):
    r = dict.fromkeys(MH, "")
    r.update(MINE_ID=i, CURRENT_MINE_NAME=f"Mine {i}", COAL_METAL_IND=ind, CURRENT_MINE_TYPE="Underground", CURRENT_MINE_STATUS=status,
             CURRENT_STATUS_DT="01/22/2019", CURRENT_OPERATOR_NAME="Op LLC", STATE="KY", LATITUDE=lat, LONGITUDE=lon)
    return [r[c] for c in MH]


PH = M.NEED["prod"]


def prod(i, sub, y, q, emp, hours, tons, ind="C"):
    return [i, f"Mine {i}", "KY", sub, str(y), str(q), emp, hours, tons, ind]


class Mines(unittest.TestCase):
    def test_rows(self):
        m = M.read(zipped("Mines.txt", MH, [mine("1500001"), mine("1500002", status="Temporarily Idled", lat=""),
                                             mine("0100003", ind="M")]), "mines")
        e = M.mines(m, BASE).set_index("entity_id")
        self.assertEqual(len(e), 2)
        a, b = e.loc["msha_mine:1500001"], e.loc["msha_mine:1500002"]
        self.assertEqual((a.status, a.status_date, a.lat, a.lon, a.geo), ("active", "2019-01-22", "37.100000", "-82.500000", "US-KY"))
        self.assertEqual((b.status, b.x_mine_status, b.lat, b.lon), ("suspended", "Temporarily Idled", "", ""))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            M.mines(M.read(zipped("Mines.txt", MH, [mine("1500001"), mine("1500001")]), "mines"), BASE)
        with self.assertRaises(RuntimeError):
            M.mines(M.read(zipped("Mines.txt", MH, [mine("1500001", status="Reopened")]), "mines"), BASE)
        with self.assertRaises(RuntimeError):
            M.read(zipped("Other.txt", MH, [mine("1500001")]), "mines")


class Production(unittest.TestCase):
    def test_quarters(self):
        q = M.read(zipped("MinesProdQuarterly.txt", PH, [
            prod("1500001", "01", 2024, 1, "10", "5000", "1000"), prod("1500001", "30", 2024, 1, "2.5", "900", ""),
            prod("1500002", "01", 2024, 2, "4", "1200", ""), prod("1500001", "01", 2009, 4, "9", "1", "5"),
            prod("0100003", "03", 2024, 1, "37", "22266", "", ind="M")]), "prod")
        s, blanks = M.production(q, BASE, 2010)
        s = s.set_index(["entity", "variable", "ts_utc"])
        a = s.loc[("msha_mine:1500001", "coal_production", "2024-01-01T00:00:00Z")]
        self.assertEqual((a.value, a.unit, a.freq, a.x_subunits, a.x_production_blank), ("1000", "short_ton", "P3M", 2, 1))
        self.assertEqual(s.loc[("msha_mine:1500001", "average_employees", "2024-01-01T00:00:00Z")].value, "12.50")
        self.assertEqual(s.loc[("msha_mine:1500002", "employee_hours", "2024-04-01T00:00:00Z")].value, "1200")
        self.assertNotIn(("msha_mine:1500002", "coal_production", "2024-04-01T00:00:00Z"), s.index)
        self.assertFalse(any(t.startswith("2009") for t in s.index.get_level_values(2)))
        self.assertEqual(blanks, 2)
        with self.assertRaises(RuntimeError):
            M.production(M.read(zipped("MinesProdQuarterly.txt", PH, [prod("1500001", "01", 2024, 5, "1", "1", "1")]), "prod"), BASE, 2010)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        for t in (M.MINES, M.PROD):
            self.assertEqual(B.sector_of(t), "coal")
            self.assertIn(t, R.STORAGE_HELD)
            with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
                self.assertIn(f"  - {t}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
