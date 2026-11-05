"""Session 2183: EPA's National Electric Energy Data System (NEEDS), the 2025 reference case.

Energy Research Warehouse (ERW). Tests warehouse/connectors/epa_needs.py on a workbook built here with NEEDS's four
sheets (units made up for the test, not EPA's): a generator and a boiler read with their sheet, state and capacity; the
retirement year 9999 written blank; a dropped unit with a state name and no code, and one with no capacity (counted);
a unit id given twice across sheets, a state unlike its code and a unit kind not in the map each stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2183 -v
"""

import io
import os
import sys
import unittest

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import epa_needs as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

COLS = list(dict.fromkeys(list(E.X_MAP.values()) + ["Plant Name", "State Name", "State Code", "Capacity (MW)"]))


def unit(uid, kind="G", state="Missouri", code=29, mw=593, retire=9999, **more):
    v = dict.fromkeys(COLS + [E.DROP_REASON])
    v.update({"Plant Name": "Labadie", "UniqueID_Final": uid, "ORIS Plant Code": 2103, "Boiler/Generator/Committed Unit": kind,
              "Unit ID": uid.split("_")[-1], "PlantType": "Coal Steam", "State Name": state, "State Code": code, "Capacity (MW)": mw,
              "Retirement Year": retire, "Region Name": "MIS_MO"})
    v.update(more)
    return v


def book(sheets):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for name in E.SHEETS:
        w = wb.create_sheet(name)
        cols = COLS + ([E.DROP_REASON] if name == "NEEDS_DroppedCapMW" else [])
        w.append(cols)
        for u in sheets.get(name, []):
            w.append([u.get(c) for c in cols])
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        rows = {r["entity_id"]: r for r in E.parse(book({
            "NEEDS_Active": [unit("2103_B_2", kind="B"), unit("2103_G_3", retire=2030)],
            "NEEDS_DroppedCapMW": [unit("1_G_1", state="Alaska", code=None, mw=0.4, **{E.DROP_REASON: "Dropped - in Alaska"}),
                                   unit("1_G_2", state="Alaska", code=None, mw=None)]}), {}, counts)}
        b = rows["epa_needs:2103_B_2"]
        self.assertEqual((b["entity_type"], b["geo"], b["capacity_mw"], b["status"], b["x_needs_sheet"], b["x_retirement_year"]),
                         ("equipment", "US-MO", 593.0, "active", "active", ""))
        self.assertEqual(rows["epa_needs:2103_G_3"]["x_retirement_year"], "2030")
        d = rows["epa_needs:1_G_1"]
        self.assertEqual((d["geo"], d["status"], d["x_needs_sheet"], d["x_drop_reason"]), ("US-AK", "", "dropped_capacity", "Dropped - in Alaska"))
        self.assertEqual(rows["epa_needs:1_G_2"]["capacity_mw"], "")
        self.assertEqual((counts["active"], counts["dropped_capacity"], counts["no capacity"]), (2, 2, 1))

    def test_stops(self):
        for sheets, words in [({"NEEDS_Active": [unit("2103_G_1")], "NEEDS_Retiredby2028": [unit("2103_G_1")]}, "given twice"),
                              ({"NEEDS_Active": [unit("2103_G_1", code=17)]}, "unlike its code"),
                              ({"NEEDS_Active": [unit("2103_G_1", kind="Z")]}, "unit kind")]:
            with self.assertRaises(RuntimeError) as c:
                E.parse(book(sheets), {}, {})
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.TABLE), "power")
        self.assertIn(E.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
