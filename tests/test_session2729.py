"""Session 2729: DESNZ's DUKES 5.14, the CO2 intensity of the UK's electricity supplied a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_dukes_co2_intensity.py on a sheet built here (made up for the
test, not DESNZ's): the year row's note marks read off, tonnes per GWh stated as kgCO2/MWh, a blank cell without a row; a wrong
title, a year out of turn, a row out of order, a value not positive and all fuels above the non-renewable stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2729 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_dukes_co2_intensity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def sheet(title=A.TITLE + " [note 1][note 2]", years=("1996", "1997 [note 3]"), coal=(900.0, None), allf=(500.0, 480.0),
          order=None):
    rows = {"Coal": ("Coal [note 4]",) + coal, "Gas": ("Gas", 450.0, 440.0),
            "All non renewable fuels": ("All non renewable fuels [note 5]", 700.0, 690.0),
            "All fuels (including nuclear and renewables)": ("All fuels (including nuclear and renewables) [note 6]",) + allf}
    names = order or [n for n, _ in A.ROWS]
    return [(title,), ("notes",), ("notes",), ("Fuel",) + tuple(years)] + [rows[n] for n in names]


class Parse(unittest.TestCase):
    def test_rows(self):
        v = A.parse_sheet(sheet())
        self.assertEqual(v[(1997, "all_fuels")][0], 480.0)
        self.assertNotIn((1997, "coal"), v)
        self.assertEqual(len(v), 7)

    def test_frame_units(self):
        import io
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "5.14"
        for r in sheet():
            ws.append(list(r))
        f = io.BytesIO()
        wb.save(f)
        t = A.parse(f.getvalue(), {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""})
        r = dict(zip(t.entity + "|" + t.ts_utc.str[:4], zip(t.value, t.unit)))
        self.assertEqual(r["desnz_ci:gas|1996"], (450.0, "kgCO2/MWh"))

    def test_stops(self):
        swapped = [A.ROWS[1][0], A.ROWS[0][0], A.ROWS[2][0], A.ROWS[3][0]]
        for rows in (sheet(title="Table 5.14 something else"),
                     sheet(years=("1996", "1998")),
                     sheet(order=swapped),
                     sheet(coal=(-1.0, None)),
                     sheet(allf=(800.0, 480.0))):       # 1996: all fuels 800 above non-renewable 700
            with self.assertRaises(RuntimeError):
                A.parse_sheet(rows)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "carbon")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
