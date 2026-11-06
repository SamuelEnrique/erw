"""Session 887: the Canada Energy Regulator's electricity trade with the U.S.

Energy Research Warehouse (ERW). Tests warehouse/connectors/cer_electricity_trade.py on sheets built here in the CER
workbook's form (figures made up for the test, not the CER's): the one workbook the page links, the monthly exports and
imports in MWh, the province rows as complete years only, the provinces and states as codes and the CER's markets kept
as named, a name not in the map stopping the run, the sector rule and the holds, and the CER's verdict recorded. No
network.

    python -m unittest tests.test_session887 -v
"""

import csv
import datetime as dt
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import cer_electricity_trade as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = dict(market="", source="s", source_url="u", retrieved_at="r", vintage="")


class Trade(unittest.TestCase):
    def test_the_one_workbook(self):
        page = '<a href="/en/x/electricity-trades-summary-resume.xlsx">XLSX</a> <a href="/en/terms-conditions.html">t</a>'
        self.assertEqual(C.workbook_url(page), "https://www.cer-rec.gc.ca/en/x/electricity-trades-summary-resume.xlsx")
        with self.assertRaises(RuntimeError):
            C.workbook_url(page + '<a href="/b/electricity-trade-2.xlsx">')

    def test_monthly(self):
        f = pd.DataFrame([["Date", "Exports / Exportations (MW.h)", "Imports / Importations (MW.h)", "Exports / Exportations ($)", "Imports / Importations ($)"],
                          [dt.datetime(2026, 7, 1), 5916651.5, 1176297.5, 492612575.6, 81653144.2]])
        out = {r["variable"]: r for r in C.monthly_rows(f, BASE)}
        self.assertEqual(set(out), {"exports", "imports"})
        self.assertEqual((out["exports"]["value"], out["exports"]["unit"], out["exports"]["ts_utc"]), (5916651.5, "MWh", "2026-07-01T00:00:00Z"))

    def test_provinces_complete_years_and_names(self):
        head = ["Date", "Volume (MW.h)", "Province (Eng. / Ang.)", "Destination (Eng. / Ang.)", "Province (Fra.)", "Destination (Fra.)"]
        f = pd.DataFrame([head, [2025, 7765535, "Ontario", "New York", "x", "y"], [2025, 3456569, "Manitoba", "Minn / N. Dakota", "x", "y"],
                          [2025, 10, "Québec", "New England-ISO", "x", "y"], [2026, 99, "Ontario", "New York", "x", "y"]])
        out, partial = C.province_rows(f, BASE, 2025)
        self.assertEqual([r["entity"] for r in out], ["cer_trade:ON:NY", "cer_trade:MB:MN_ND", "cer_trade:QC:ISONE"])
        self.assertEqual((out[0]["geo"], out[0]["freq"]), ("CA-ON", "P1Y"))
        self.assertEqual(partial, [2026])
        f.loc[1, 3] = "Atlantis"
        with self.assertRaises(RuntimeError):
            C.province_rows(f, BASE, 2025)


class Registered(unittest.TestCase):
    def test_sector_holds_and_verdict(self):
        name = "cer_electricity_trade"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "metadata", "license_verdicts.csv"), encoding="utf-8") as f:
            v = {r["key"]: r for r in csv.DictReader(f)}["Canada Energy Regulator (CER)"]
        self.assertEqual((v["verdict"], v["if_commercial"]), ("may be public", "needs written permission"))


if __name__ == "__main__":
    unittest.main()
