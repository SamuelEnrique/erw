"""Session 2176: Statistics Canada's monthly electricity generation (table 25-10-0015-01).

Energy Research Warehouse (ERW). Tests warehouse/connectors/statcan_electricity.py on a zip built here in StatCan's
form (figures made up for the test, not StatCan's): a province's row, a total marked, a revised figure, ".." and "x"
left out and counted; a unit not as read, an area not in the map and a row given twice each stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2176 -v
"""

import io
import os
import sys
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import statcan_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
HEAD = ('"REF_DATE","GEO","DGUID","Class of electricity producer","Type of electricity generation","UOM","UOM_ID","SCALAR_FACTOR",'
        '"SCALAR_ID","VECTOR","COORDINATE","VALUE","STATUS","SYMBOL","TERMINATED","DECIMALS"')


def row(month="2024-01", geo="Ontario", cls="Electricity producers, electric utilities", typ="Nuclear steam turbine", value="7500000",
        status="", symbol="", uom="Megawatt hours"):
    return f'"{month}","{geo}","x","{cls}","{typ}","{uom}","210","units","0","v1","1.1.1","{value}","{status}","{symbol}","","0"'


def zipped(lines):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("25100015.csv", "﻿" + "\n".join([HEAD] + lines) + "\n")
        z.writestr("25100015_MetaData.csv", "meta")
    return b.getvalue()


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        rows = S.parse(zipped([row(), row(typ="Total all types of electricity generation", value="12000000", symbol="r"),
                               row(geo="Nunavut", typ="Solar", value="", status=".."), row(geo="Yukon", value="", status="x")]), BASE, counts)
        self.assertEqual((len(rows), counts), (2, {"..": 1, "x": 1}))
        n, t = rows
        self.assertEqual((n["entity"], n["value"], n["unit"], n["geo"], n["ts_utc"], n["x_total"]),
                         ("statcan_gen:on:utilities:nuclear_steam_turbine", 7500000.0, "MWh", "CA-ON", "2024-01-01T00:00:00Z", ""))
        self.assertEqual((t["x_total"], t["x_revised"]), ("yes", "r"))

    def test_stops(self):
        for lines, words in [([row(uom="Gigawatt hours")], "unit not as read"), ([row(geo="Greenland")], "not in the maps"),
                             ([row(), row()], "given twice")]:
            with self.assertRaises(RuntimeError) as c:
                S.parse(zipped(lines), BASE, {})
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.TABLE), "power")
        self.assertIn(S.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
