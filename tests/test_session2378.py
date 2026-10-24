"""Session 2378: Statistics Canada's table 25-10-0081-01, petroleum products by supply and disposition, by province,
a month.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statcan_petroleum_products.py on a zip built here in
StatCan's form (made up for the test, not StatCan's): a row a month, area, item and product, a product's parent and the products with parts marked, "x" without
a row and counted, the revised mark kept; a unit not cubic metres, a product or item not in the maps, a month that does not
read, a status not in the map and a key given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2378 -v
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
import statcan_petroleum_products as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402

COLS = ["REF_DATE", "GEO", "DGUID", "Supply and disposition", "Products", "Unit of measure", "UOM", "UOM_ID", "SCALAR_FACTOR",
        "SCALAR_ID", "VECTOR", "COORDINATE", "VALUE", "STATUS", "SYMBOL", "TERMINATED", "DECIMALS"]


def zipped(rows, name="25100081.csv"):
    f = io.StringIO()
    w = csv.writer(f)
    w.writerow(COLS)
    for date, geo, item, prod, value, status, symbol, uom in rows:
        w.writerow([date, geo, "", item, prod, uom, uom, "72", "units", "0", "v1", "1.1.1.1", value, status, symbol, "", "0"])
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr(name, f.getvalue())
        z.writestr("25100081_MetaData.csv", "meta")
    return b.getvalue()


def row(date="2026-01", geo="Alberta", item="Products supplied, disposition", prod="Propane", value="1500", status="", symbol="", uom="Cubic metres"):
    return (date, geo, item, prod, value, status, symbol, uom)


class Rows(unittest.TestCase):
    def test_rows(self):
        counts = {}
        out = S.parse(zipped([row(), row(prod="Natural gas liquids", value="2000", symbol="r"), row(geo="Canada", value="", status="x")]), {}, counts)
        self.assertEqual(counts, {"x": 1})
        self.assertEqual(len(out), 2)
        p = next(r for r in out if r["x_product"] == "Propane")
        self.assertEqual((p["entity"], p["variable"], p["value"], p["unit"], p["geo"], p["x_parent"], p["x_total"]),
                         ("statcan_pp:ab:propane", "products_supplied", 1500.0, "m3", "CA-AB", "Natural gas liquids", ""))
        n = next(r for r in out if r["x_product"] == "Natural gas liquids")
        self.assertEqual((n["x_total"], n["x_revised"], n["x_parent"]), ("yes", "r", "Hydrocarbon gas liquids"))

    def test_stops(self):
        for rows in ([row(uom="Litres")], [row(prod="Crude oil")], [row(item="Losses")], [row(date="2026-1")], [row(status="E")], [row(), row()]):
            with self.assertRaises(RuntimeError):
                S.parse(zipped(rows), {}, {})
        with self.assertRaises(RuntimeError):
            S.parse(zipped([row()], name="25100016.csv"), {}, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.TABLE), "oil;products")
        self.assertIn(S.TABLE, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
