"""Session 2179: Statistics Canada's crude oil and natural gas supply and disposition.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statcan_oil_gas.py on zips built here in StatCan's form
(figures made up for the test, not StatCan's): the crude table's cubic metres kept and its barrels checked; an item
named twice given its parent's slug; the gas table's thousands written times 1,000, its customers as a count, its
gigajoules and dollars counted and not kept; withheld figures counted; a barrel figure that disagrees, a row unlike its
metadata and a unit not in the map each stopping the run; Decision 70's unit; the sector rule and the holds. No network.

    python -m unittest tests.test_session2179 -v
"""

import csv
import io
import os
import sys
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))  # appended: warehouse/validate has a build_coverage.py of its own
import statcan_oil_gas as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

HEAD = ('REF_DATE,GEO,DGUID,Supply and disposition,Units of measure,UOM,UOM_ID,SCALAR_FACTOR,SCALAR_ID,VECTOR,COORDINATE,VALUE,'
        'STATUS,SYMBOL,TERMINATED,DECIMALS\n')


def meta(items, units):
    lines = ['"Cube Title","Product Id"', '"t","1"', "", '"Dimension ID","Member Name","Classification Code","Member ID","Parent Member ID",'
             'Terminated,"Member Notes","Member Definitions"', '"1","Canada","[11124]","1","","",,', '"1","Alberta","[48]","2","1","",,']
    lines += [f'"2","{n}","","{m}","{p}","",,' for m, n, p in items]
    lines += [f'"3","{n}","","{m}","","",,' for m, n in units]
    return "\n".join(lines + ["", "Symbol Legend"]) + "\n"


def zipped(stem, rows, m):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        body = io.StringIO()
        csv.writer(body, lineterminator="\n").writerows(rows)
        z.writestr(f"{stem}.csv", HEAD + body.getvalue())
        z.writestr(f"{stem}_MetaData.csv", m)
    return b.getvalue()


def row(geo, g, item, i, uom, u, value, status="", scale="units"):
    return ["2024-01", geo, "x", item, uom, uom, "1", scale, "0", "v1", f"{g}.{i}.{u}", value, status, "", "", "0"]


CRUDE_META = meta([("1", "Exports", ""), ("2", "Opening inventory", ""), ("3", "Refineries", "2"), ("4", "Closing inventory", ""),
                   ("5", "Refineries", "4")], [("1", "Cubic metres"), ("2", "Barrels")])


def crude(barrels="62898", uom2="Barrels"):
    return zipped("25100063", [row("Canada", 1, "Exports", 1, "Cubic metres", 1, "10000"), row("Canada", 1, "Exports", 1, uom2, 2, barrels),
                               row("Alberta", 2, "Refineries", 3, "Cubic metres", 1, "100"), row("Alberta", 2, "Refineries", 3, "Barrels", 2, "629"),
                               row("Alberta", 2, "Refineries", 5, "Cubic metres", 1, "", ".."), row("Alberta", 2, "Refineries", 5, "Barrels", 2, "", "..")],
                  CRUDE_META)


def gas():
    m = meta([("1", "Total exports, disposition", ""), ("2", "Residential consumption", "")],
             [("1", "Cubic metres"), ("2", "Gigajoules"), ("3", "Canadian dollars"), ("4", "Customers")])
    return zipped("25100086", [row("Canada", 1, "Total exports, disposition", 1, "Cubic metres", 1, "1234.5", scale="thousands"),
                               row("Canada", 1, "Total exports, disposition", 1, "Gigajoules", 2, "50000", scale="thousands"),
                               row("Canada", 1, "Total exports, disposition", 1, "Canadian dollars", 3, "9", scale="thousands"),
                               row("Alberta", 2, "Residential consumption", 2, "Customers", 4, "1700000"),
                               row("Alberta", 2, "Residential consumption", 2, "Cubic metres", 1, "", "x", "thousands")], m)


class Parse(unittest.TestCase):
    def test_crude(self):
        counts = {}
        rows = {(r["entity"], r["variable"]): r for r in S.parse("crude_oil", "25-10-0063-01", "25100063", crude(), {}, counts)}
        self.assertEqual(set(rows), {("statcan_oil:ca", "exports"), ("statcan_oil:ab", "opening_inventory_refineries")})
        r = rows[("statcan_oil:ab", "opening_inventory_refineries")]
        self.assertEqual((r["value"], r["unit"], r["geo"], r["x_parent"], r["x_area_total"]), (100.0, "m3", "CA-AB", "opening_inventory", ""))
        self.assertEqual(rows[("statcan_oil:ca", "exports")]["x_area_total"], "yes")
        self.assertEqual(counts, {"25-10-0063-01 ..": 1})

    def test_gas(self):
        counts = {}
        rows = {(r["entity"], r["variable"]): r for r in S.parse("natural_gas", "25-10-0086-01", "25100086", gas(), {}, counts)}
        self.assertEqual(rows[("statcan_gas:ca", "total_exports")]["value"], 1234500.0)
        c = rows[("statcan_gas:ab", "residential_consumption_customers")]
        self.assertEqual((c["value"], c["unit"]), (1700000.0, "count"))
        self.assertEqual(counts, {"25-10-0086-01 Gigajoules not taken": 1, "25-10-0086-01 Canadian dollars not taken": 1, "25-10-0086-01 x": 1})

    def test_stops(self):
        for content, words in [(crude(barrels="70000"), "barrels against"),
                               (crude(uom2="Tonnes"), "a unit not in the map"),
                               (zipped("25100063", [row("Canada", 1, "Imports", 1, "Cubic metres", 1, "5")], CRUDE_META), "not as its metadata")]:
            with self.assertRaises(RuntimeError) as c:
                S.parse("crude_oil", "25-10-0063-01", "25100063", content, {}, {})
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_unit_sector_and_holds(self):
        self.assertIn("m3", V.UNITS)
        self.assertEqual(B.sector_of(S.TABLE), "oil;gas")
        self.assertIn(S.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
