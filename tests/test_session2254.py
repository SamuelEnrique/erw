"""Session 2254: the Electricity Authority's EMI, New Zealand's generation and demand a month.

Energy Research Warehouse (ERW). Tests warehouse/connectors/emi_nz.py on CSVs built here in EMI's report form (figures
made up for the test, not EMI's): GWh written as MWh for New Zealand and an island; the dollar column not taken; a report
not the one read, parameters not as asked, a region not in the map, a month given twice and a period that is not a
calendar month each stopping the run; the report's address; the sector rule and the holds. No network.

    python -m unittest tests.test_session2254 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import emi_nz as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def report(rows, title="Generation trends", rtype="Island", scale="Month", col="Generation (GWh)"):
    lines = [title, "", "From www.emi.ea.govt.nz provided by the Electricity Authority (New Zealand)", "Run at: 20261024165535", "",
             "Parameters", "Date range,01 Jan 2015 - 30 Sep 2026", f"Region type,{rtype}", f"Time scale,{scale}", "Show,GWh", "",
             f"Period start,Period end,Region ID,Region,{col},Generation ($)"]
    lines += [",".join(r) for r in rows]
    return "\n".join(lines).encode("utf-8")


ROWS = [("01/01/2015", "01/02/2015", "NI", "North Island", "1870.664", "187804644.50"),
        ("01/02/2015", "01/03/2015", "SI", "South Island", "1546.458", "149001116.40")]


class Parse(unittest.TestCase):
    def test_rows(self):
        out = E.parse(report(ROWS), "W_GG_C", "ISLAND", {})
        a, b = out
        self.assertEqual((a["entity"], a["variable"], a["ts_utc"], a["value"], a["unit"], a["freq"], a["geo"]),
                         ("emi:ni", "generation", "2015-01-01T00:00:00Z", 1870664.0, "MWh", "P1M", "NZ"))
        self.assertEqual((b["entity"], b["ts_utc"], b["x_report"]), ("emi:si", "2015-02-01T00:00:00Z", "W_GG_C"))
        d = E.parse(report([("01/01/2015", "01/02/2015", "NZ", "New Zealand", "3318.979", "1")], title="Demand trends", rtype="New Zealand",
                           col="Demand (GWh)"), "W_GD_C", "NZ", {})[0]
        self.assertEqual((d["entity"], d["variable"], d["value"]), ("emi:nz", "demand", 3318979.0))

    def test_stops(self):
        for content, words in [(report(ROWS, title="Price trends"), "not the report read"),
                               (report(ROWS, scale="Day"), "parameters not as asked"),
                               (report([("01/01/2015", "01/02/2015", "XX", "Elsewhere", "1", "1")]), "not in the map"),
                               (report(ROWS[:1] * 2), "given twice"),
                               (report([("01/01/2015", "15/01/2015", "NI", "North Island", "1", "1")]), "not a calendar month")]:
            with self.assertRaises(RuntimeError) as c:
                E.parse(content, "W_GG_C", "ISLAND", {})
            self.assertIn(words, str(c.exception))

    def test_url(self):
        self.assertEqual(E.url_of("W_GD_C", "NZ", "20260930"), "https://www.emi.ea.govt.nz/Wholesale/Download/DataReport/CSV/W_GD_C?"
                         "DateFrom=20150101&DateTo=20260930&RegionType=NZ&TimeScale=MONTH&_si=v|3")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.TABLE), "power")
        self.assertIn(E.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
