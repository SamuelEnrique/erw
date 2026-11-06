"""Session 2328: Statistics Canada's table 25-10-0016-01, electricity receipts, deliveries and availability by province,
a month.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statcan_electricity_trade.py on a zip built here in
StatCan's form (made up for the test, not StatCan's): a row a month, area and component, the totals marked, ".." without
a row and counted, the revised mark kept; a unit not megawatt hours, a component not in the map, a month that does not
read, a status not in the map and a key given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2328 -v
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
import statcan_electricity_trade as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402

COLS = ["REF_DATE", "GEO", "DGUID", "Electric power, components", "UOM", "UOM_ID", "SCALAR_FACTOR", "SCALAR_ID", "VECTOR",
        "COORDINATE", "VALUE", "STATUS", "SYMBOL", "TERMINATED", "DECIMALS"]


def zipped(rows, name="25100016.csv"):
    f = io.StringIO()
    w = csv.writer(f)
    w.writerow(COLS)
    for date, geo, comp, value, status, symbol, uom in rows:
        w.writerow([date, geo, "", comp, uom, "210", "units", "0", "v1", "1.1", value, status, symbol, "", "0"])
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr(name, f.getvalue())
        z.writestr("25100016_MetaData.csv", "meta")
    return b.getvalue()


def row(date="2026-01", geo="Quebec", comp="Deliveries to the United States", value="1500", status="", symbol="", uom="Megawatt hours"):
    return (date, geo, comp, value, status, symbol, uom)


class Rows(unittest.TestCase):
    def test_rows(self):
        counts = {}
        out = S.parse(zipped([row(), row(comp="Total deliveries", value="2000", symbol="r"), row(geo="Canada", comp="Total generation", value="", status="..")]), {}, counts)
        self.assertEqual(counts, {"..": 1})
        self.assertEqual(len(out), 2)
        us = next(r for r in out if r["variable"] == "deliveries_us")
        self.assertEqual((us["entity"], us["value"], us["unit"], us["geo"], us["ts_utc"], us["x_total"]),
                         ("statcan_trade:qc", 1500.0, "MWh", "CA-QC", "2026-01-01T00:00:00Z", ""))
        tot = next(r for r in out if r["variable"] == "deliveries_total")
        self.assertEqual((tot["x_total"], tot["x_revised"]), ("yes", "r"))

    def test_stops(self):
        for rows in ([row(uom="Gigawatt hours")], [row(comp="Losses")], [row(date="2026-1")], [row(status="E")], [row(), row()]):
            with self.assertRaises(RuntimeError):
                S.parse(zipped(rows), {}, {})
        with self.assertRaises(RuntimeError):
            S.parse(zipped([row()], name="25100015.csv"), {}, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.TABLE), "power")
        self.assertIn(S.TABLE, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
