"""Session 2441: Statistics Canada's table 25-10-0021-01, the annual supply and disposition of electric power.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statcan_power_disposition.py on a zip built here in the
download's form (made up for the test, not StatCan's): each quantity a row in MWh on the year's 1 January, the component
as StatCan names it, a revision marked, a figure marked ".." not written and counted, the estimate in dollars not taken
and counted; a quantity in another unit, an estimate or area not in the map, a status not in the map and a key given
twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2441 -v
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
import statcan_power_disposition as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
COLS = ["REF_DATE", "GEO", "DGUID", "Electric power, components", "Estimates", "UOM", "UOM_ID", "SCALAR_FACTOR", "SCALAR_ID", "VECTOR",
        "COORDINATE", "VALUE", "STATUS", "SYMBOL", "TERMINATED", "DECIMALS"]


def row(year="2024", geo="Quebec", comp="Total exports of electricity to the United States", est="Electricity quantity", value="25000000",
        status="", symbol="", uom="Megawatt hours", scalar="units"):
    return [year, geo, "", comp, est, uom, "", scalar, "0", "v9", "1.1.1", value, status, symbol, "", "0"]


def build(rows):
    b = io.StringIO()
    w = csv.writer(b)
    w.writerow(COLS)
    w.writerows(rows)
    z = io.BytesIO()
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("25100021.csv", b.getvalue())
        f.writestr("25100021_MetaData.csv", "x")
    return z.getvalue()


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        out = S.parse(build([row(), row(geo="Canada", comp="Total generation of electricity", value="639500000.5", symbol="r"),
                             row(est="Electricity value", uom="Dollars", scalar="thousands", value="1200000"),
                             row(comp="Residential sales of electricity", value="", status="..")]), BASE, counts)
        self.assertEqual(len(out), 2)
        a = out[0]
        self.assertEqual((a["entity"], a["variable"], a["ts_utc"], a["value"], a["unit"], a["geo"], a["freq"]),
                         ("statcan_pd:qc", "total_exports_of_electricity_to_the_united_states", "2024-01-01T00:00:00Z", 25000000.0, "MWh", "CA-QC", "P1Y"))
        self.assertEqual((out[1]["entity"], out[1]["variable"], out[1]["x_revised"]), ("statcan_pd:ca", "total_generation_of_electricity", "r"))
        self.assertEqual(counts, {"value rows not taken": 1, "..": 1})

    def test_stops(self):
        for rows in ([row(uom="Gigawatt hours")], [row(est="Electricity price")], [row(geo="Atlantis")], [row(status="F", value="")], [row(), row()]):
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
