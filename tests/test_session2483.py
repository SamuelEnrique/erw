"""Session 2483: Statistics Canada's table 25-10-0025-01, manufacturing industries' annual energy consumption by fuel.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statcan_manufacturing_energy.py on a zip built here in the
download's form (made up for the test, not StatCan's): each figure a row in MWh (gigajoules / 3.6) on the year's 1 January,
the industry by its NAICS code, the fuel as a slug, StatCan's quality grade kept; a figure marked "..", "x" or "F" not
written and counted; a unit other than gigajoules, an area other than Canada, a status not in the map and a key given
twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2483 -v
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
import statcan_manufacturing_energy as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
COLS = ["REF_DATE", "GEO", "DGUID", "Fuel type", "North American Industry Classification System (NAICS)", "UOM", "UOM_ID", "SCALAR_FACTOR",
        "SCALAR_ID", "VECTOR", "COORDINATE", "VALUE", "STATUS", "SYMBOL", "TERMINATED", "DECIMALS"]


def row(year="2024", geo="Canada", fuel="Electricity", naics="Manufacturing [31-33]", uom="Gigajoules", value="620640000", status="A"):
    return [year, geo, "", fuel, naics, uom, "", "units", "0", "v5", "1.1", value, status, "", "", "0"]


def build(rows):
    b = io.StringIO()
    w = csv.writer(b)
    w.writerow(COLS)
    w.writerows(rows)
    z = io.BytesIO()
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("25100025.csv", b.getvalue())
        f.writestr("25100025_MetaData.csv", "x")
    return z.getvalue()


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        out = S.parse(build([row(), row(fuel="Natural gas", naics="Breweries [31212]", value="3600", status=""),
                             row(fuel="Coal", value="", status="x"), row(fuel="Propane", value="", status="F")]), BASE, counts)
        self.assertEqual(len(out), 2)
        a = out[0]
        self.assertEqual((a["entity"], a["variable"], a["ts_utc"], a["value"], a["unit"], a["geo"], a["x_quality"]),
                         ("statcan_mfg:ca:31-33", "consumption_electricity", "2024-01-01T00:00:00Z", 172400000.0, "MWh", "CA", "A"))
        self.assertEqual((out[1]["entity"], out[1]["variable"], out[1]["value"]), ("statcan_mfg:ca:31212", "consumption_natural_gas", 1000.0))
        self.assertEqual(counts, {"x": 1, "F": 1})

    def test_stops(self):
        for rows in ([row(uom="Terajoules")], [row(geo="Ontario")], [row(status="Z")], [row(), row()]):
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
