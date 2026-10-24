"""Session 2418: Statistics Canada's installed generating capacity by type and class of producer, a year (25-10-0022-01).

Energy Research Warehouse (ERW). Tests warehouse/connectors/statcan_generating_capacity.py on a small zip built here in
StatCan's full-table form (made up for the test, not its figures): kilowatts written as MW, a figure marked .. without
a row, the revised symbol kept; a unit, area or status not as read and a key twice stopping the run; the totals against
their parts; the sector rule, the live-set hold and the release hold (public). No network.

    python -m unittest tests.test_session2418 -v
"""

import io
import os
import sys
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import statcan_generating_capacity as C  # noqa: E402
import build_coverage as B  # noqa: E402

HEAD = "REF_DATE,GEO,DGUID,Class of electricity producer,Type of electricity generation,UOM,UOM_ID,SCALAR_FACTOR,SCALAR_ID,VECTOR,COORDINATE,VALUE,STATUS,SYMBOL,TERMINATED,DECIMALS"
ALL = "Total all classes of electricity producer"


def line(typ, value, geo="Quebec", year="2024", status="", symbol="", uom="Kilowatts", cls=ALL):
    return f'{year},{geo},x,"{cls}",{typ},{uom},200,units,0,v1,1.1.1,{value},{status},{symbol},,0'


def zipped(lines, name="25100022.csv"):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr(name, "\n".join([HEAD] + lines) + "\n")
        z.writestr("25100022_MetaData.csv", "x\n")
    return b.getvalue()


GOOD = [line("Total installed capacity", "1000000"), line("Hydraulic turbine", "900000"), line("Wind power turbine", "60000"),
        line("Total thermal", "40000", symbol="r"), line("Combustion turbine", "30000"), line("Internal combustion turbine", "10000"),
        line("Solar power", "", status="..")]


class Parse(unittest.TestCase):
    def test_parse(self):
        counts = {}
        rows = C.parse(zipped(GOOD), {}, counts)
        self.assertEqual(len(rows), 6)
        self.assertEqual(counts, {"..": 1})
        tot = next(r for r in rows if r["variable"] == "capacity_total")
        self.assertEqual((tot["entity"], tot["value"], tot["unit"], tot["geo"]), ("statcan_cap:qc:all", 1000.0, "MW", "CA-QC"))
        self.assertEqual(next(r for r in rows if r["variable"] == "capacity_total_thermal")["x_symbol"], "r")

    def test_stops(self):
        for bad in ([line("Hydraulic turbine", "1", uom="Megawatts")], [line("Hydraulic turbine", "1", geo="Ontaria")],
                    [line("Hydraulic turbine", "1", status="E")], [line("Hydraulic turbine", "1"), line("Hydraulic turbine", "2")]):
            with self.assertRaises(RuntimeError):
                C.parse(zipped(bad), {}, {})
        with self.assertRaises(RuntimeError):
            C.parse(zipped(GOOD, name="other.csv"), {}, {})

    def test_sums(self):
        import pandas as pd
        s = pd.DataFrame(C.parse(zipped(GOOD), {}, {}))
        self.assertEqual(C.sum_check(s), (2, []))
        s2 = pd.DataFrame(C.parse(zipped(GOOD[:1] + [line("Hydraulic turbine", "800000")] + GOOD[2:]), {}, {}))
        compared, off = C.sum_check(s2)
        self.assertEqual(off, [("statcan_cap:qc:all", "2024", "total", -100.0)])


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(C.TABLE), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.TABLE}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{C.TABLE}"', f.read())


if __name__ == "__main__":
    unittest.main()
