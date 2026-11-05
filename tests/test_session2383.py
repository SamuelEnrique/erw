"""Session 2383: Statistics Canada's table 25-10-0029-01, supply and demand of primary and secondary energy, by province,
a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statcan_energy_balance.py on a zip built here in
StatCan's form (made up for the test, not StatCan's): a row a year, area, fuel and line, terajoules written as MWh, an aggregate of provinces without a geo, an ended series marked, "x" without
a row and counted; a unit not terajoules, an area not in the map, a year that does not
read, a status not in the map and a key given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2383 -v
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
import statcan_energy_balance as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402

COLS = ["REF_DATE", "GEO", "DGUID", "Fuel type", "Supply and demand characteristics", "UOM", "UOM_ID", "SCALAR_FACTOR",
        "SCALAR_ID", "VECTOR", "COORDINATE", "VALUE", "STATUS", "SYMBOL", "TERMINATED", "DECIMALS"]


def zipped(rows, name="25100029.csv"):
    f = io.StringIO()
    w = csv.writer(f)
    w.writerow(COLS)
    for date, geo, fuel, line, value, status, term, uom in rows:
        w.writerow([date, geo, "", fuel, line, uom, "283", "units", "0", "v1", "1.1.1", value, status, "", term, "0"])
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr(name, f.getvalue())
        z.writestr("25100029_MetaData.csv", "meta")
    return b.getvalue()


def row(date="2024", geo="Alberta", fuel="Natural gas", line="Production", value="3600", status="", term="", uom="Terajoules"):
    return (date, geo, fuel, line, value, status, term, uom)


class Rows(unittest.TestCase):
    def test_rows(self):
        counts = {}
        out = S.parse(zipped([row(), row(geo="Atlantic provinces", fuel="Gas plant natural gas liquids (NGL's)", term="t"),
                              row(geo="Canada", value="", status="x")]), {}, counts)
        self.assertEqual(counts, {"x": 1})
        self.assertEqual(len(out), 2)
        a = out[0]
        self.assertEqual((a["entity"], a["variable"], a["value"], a["unit"], a["geo"], a["ts_utc"], a["freq"]),
                         ("statcan_eb:ab:natural_gas", "production", 1000000.0, "MWh", "CA-AB", "2024-01-01T00:00:00Z", "P1Y"))
        b = out[1]
        self.assertEqual((b["entity"], b["geo"], b["x_terminated"]), ("statcan_eb:atl:gas_plant_natural_gas_liquids_ngls", "", "t"))

    def test_stops(self):
        for rows in ([row(uom="Petajoules")], [row(geo="Atlantis")], [row(date="2024-01")], [row(status="E")], [row(), row()]):
            with self.assertRaises(RuntimeError):
                S.parse(zipped(rows), {}, {})
        with self.assertRaises(RuntimeError):
            S.parse(zipped([row()], name="25100081.csv"), {}, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.TABLE), "power;gas;oil;coal")
        self.assertIn(S.TABLE, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
