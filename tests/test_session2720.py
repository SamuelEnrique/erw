"""Session 2720: DESNZ's DUKES 5.16, the UK's electricity storage a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_dukes_storage.py on a sheet built here (made up for the test,
not DESNZ's): the three tables found by their titles, GWh stated as MWh and power capacity as MW, a zero kept and a blank without
a row; a missing table, a year out of turn, a type out of order and types that miss their total stopping the run; the sector rule
and the holds. No network.

    python -m unittest tests.test_session2720 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_dukes_storage as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

NOTE = {"Battery storage - grid scale": "Battery storage - grid scale [note 2]"}


def block(title, years=("1996", "1997"), vals=((10, 12), (0, 1), (0, 0), (10, 13)), types=None):
    rows = [(title,), ("Storage type",) + tuple(years)]
    for (name, _), v in zip(types or A.TYPES, vals):
        rows.append((NOTE.get(name, name),) + tuple(v))
    return rows + [()]


def sheet(over=None):
    over = over or {}
    rows = [("Tables 5.16 Energy storage input electricity, output electricity, and capacity overview",), ("notes",)]
    for k, (title, *_rest) in enumerate(A.TABLES):
        shown = title.replace("facilities, MW", "facilities [note 1], MW")
        rows += block(shown, **over.get(k, {}))
    return rows


class Parse(unittest.TestCase):
    def test_rows(self):
        v = A.parse_sheet(sheet())
        self.assertEqual(v[(1997, "battery_grid_scale", "output")][:2], (1.0, "MWh"))
        self.assertEqual(v[(1996, "other_storage", "power_capacity")][:3], (0.0, "MW", 1))
        self.assertEqual(len(v), 3 * 4 * 2)

    def test_blank_has_no_row(self):
        v = A.parse_sheet(sheet({1: {"vals": ((10, 12), (0, None), (0, 0), (10, 12))}}))
        self.assertNotIn((1997, "battery_grid_scale", "input"), v)

    def test_frame_units(self):
        import io
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "5.16"
        for r in sheet():
            ws.append(list(r))
        f = io.BytesIO()
        wb.save(f)
        t = A.parse(f.getvalue(), {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""})
        r = dict(zip(t.entity + "|" + t.variable + "|" + t.ts_utc.str[:4], zip(t.value, t.unit)))
        self.assertEqual(r["desnz_st:total|output|1997"], (13000.0, "MWh"))
        self.assertEqual(r["desnz_st:total|power_capacity|1997"], (13.0, "MW"))

    def test_stops(self):
        no_c = sheet()[:-len(block(A.TABLES[2][0]))]
        swapped = [A.TYPES[1], A.TYPES[0]] + A.TYPES[2:]
        for rows in (no_c,
                     sheet({0: {"years": ("1996", "1998")}}),
                     sheet({0: {"types": swapped}}),
                     sheet({2: {"vals": ((10, 12), (0, 1), (0, 0), (10, 15))}})):   # 1997 misses its total by 2
            with self.assertRaises(RuntimeError):
                A.parse_sheet(rows)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
