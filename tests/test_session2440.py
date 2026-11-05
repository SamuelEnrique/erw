"""Session 2440: Statistics Canada's table 25-10-0020-01, annual electricity generation by class of producer.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statcan_generation_class.py on a zip built here in the
download's form (made up for the test, not StatCan's): each figure a row in MWh on the year's 1 January, the class and the
type as StatCan names them, a revision marked, a figure marked ".." or "x" not written and counted; a unit not megawatt
hours, an area not in the map, a status not in the map and a key given twice stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session2440 -v
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
import statcan_generation_class as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
COLS = ["REF_DATE", "GEO", "DGUID", "Class of electricity producer", "Type of electricity generation", "UOM", "UOM_ID", "SCALAR_FACTOR",
        "SCALAR_ID", "VECTOR", "COORDINATE", "VALUE", "STATUS", "SYMBOL", "TERMINATED", "DECIMALS"]


def row(year="2024", geo="Quebec", klass="Electricity producer, electric utilities", kind="Hydraulic turbine", value="190000000",
        status="", symbol="", uom="Megawatt hours"):
    return [year, geo, "", klass, kind, uom, "", "units", "0", "v123", "1.1.1", value, status, symbol, "", "0"]


def build(rows):
    b = io.StringIO()
    w = csv.writer(b)
    w.writerow(COLS)
    w.writerows(rows)
    z = io.BytesIO()
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("25100020.csv", b.getvalue())
        f.writestr("25100020_MetaData.csv", "x")
    return z.getvalue()


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        out = S.parse(build([row(), row(geo="Canada", klass="Total all classes of electricity producer", kind="Total all types of electricity generation",
                                        value="621600000.5", symbol="r"),
                             row(klass="Electricity producer, industries", value="", status=".."), row(year="2023", value="", status="x")]), BASE, counts)
        self.assertEqual(len(out), 2)
        a = out[0]
        self.assertEqual((a["entity"], a["variable"], a["ts_utc"], a["value"], a["unit"], a["geo"], a["x_revised"]),
                         ("statcan_gc:qc:utilities", "hydraulic_turbine", "2024-01-01T00:00:00Z", 190000000.0, "MWh", "CA-QC", ""))
        self.assertEqual((out[1]["entity"], out[1]["variable"], out[1]["x_revised"]), ("statcan_gc:ca:all", "total_all_types_of_electricity_generation", "r"))
        self.assertEqual(counts, {"..": 1, "x": 1})

    def test_stops(self):
        for rows in ([row(uom="Gigawatt hours")], [row(geo="Atlantis")], [row(status="F", value="")], [row(), row()]):
            with self.assertRaises(RuntimeError):
                S.parse(build(rows), BASE, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.TABLE), "power")
        self.assertIn(S.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
