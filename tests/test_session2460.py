"""Session 2460: Statistics Canada's annual supply and disposition of electricity by province (25-10-0021-01).

Energy Research Warehouse (ERW). Tests warehouse/connectors/statcan_electricity_disposition.py on a small zip built here
in StatCan's form (made up for the test, not its figures): MWh kept, the dollar values left out and counted, a figure
marked .. without a row, the revised symbol kept; a unit, area or status not as read and a key twice stopping the run;
the sales sectors against total sales; the sector rule and the holds (public). No network.

    python -m unittest tests.test_session2460 -v
"""

import io
import os
import sys
import unittest
import zipfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import statcan_electricity_disposition as D  # noqa: E402
import build_coverage as B  # noqa: E402

HEAD = "REF_DATE,GEO,DGUID,\"Electric power, components\",Estimates,UOM,UOM_ID,SCALAR_FACTOR,SCALAR_ID,VECTOR,COORDINATE,VALUE,STATUS,SYMBOL,TERMINATED,DECIMALS"


def line(comp, value, geo="Quebec", est="Electricity quantity", uom="Megawatt hours", scalar="units", status="", symbol=""):
    return f'2024,{geo},x,"{comp}",{est},{uom},210,{scalar},0,v1,1.1.1,{value},{status},{symbol},,0'


def zipped(lines):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("25100021.csv", "\n".join([HEAD] + lines) + "\n")
        z.writestr("25100021_MetaData.csv", "x\n")
    return b.getvalue()


GOOD = [line("Total sales of electricity to ultimate customers", "100"), line("Residential sales of electricity", "40"),
        line("Agriculture sales of electricity", "5"), line("Mining and manufacturing sales of electricity", "30"),
        line("Other industries sales of electricity", "25", symbol="r"),
        line("Total electricity available for use within specific geographic border", "120"),
        line("Total generation of electricity", "130"), line("Total exports of electricity to the United States", "10"),
        line("Electricity used by producers", "", status=".."),
        line("Total sales of electricity to ultimate customers", "9000", est="Electricity value", uom="Dollars", scalar="thousands")]


class Parse(unittest.TestCase):
    def test_parse(self):
        counts = {}
        rows = D.parse(zipped(GOOD), {}, counts)
        self.assertEqual(len(rows), 8)
        self.assertEqual(counts, {"value_rows_not_taken": 1, "..": 1})
        r = next(x for x in rows if x["variable"] == "other_industries_sales_of_electricity")
        self.assertEqual((r["entity"], r["value"], r["unit"], r["geo"], r["x_symbol"]), ("statcan_disp:qc", 25.0, "MWh", "CA-QC", "r"))

    def test_checks(self):
        s = pd.DataFrame(D.parse(zipped(GOOD), {}, {}))
        self.assertEqual(D.checks(s), (1, 1, 0, 1))      # supply holds (130 - 10); use does not (no producers' use row)
        bad = pd.DataFrame(D.parse(zipped([l.replace(",40,", ",45,") for l in GOOD]), {}, {}))
        with self.assertRaises(RuntimeError):
            D.checks(bad)

    def test_stops(self):
        for bad in ([line("Total generation of electricity", "1", uom="Gigawatt hours")], [line("Total generation of electricity", "1", geo="Atlantis")],
                    [line("Total generation of electricity", "1", status="E")],
                    [line("Total generation of electricity", "1"), line("Total generation of electricity", "2")]):
            with self.assertRaises(RuntimeError):
                D.parse(zipped(bad), {}, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(D.TABLE), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {D.TABLE}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{D.TABLE}"', f.read())


if __name__ == "__main__":
    unittest.main()
