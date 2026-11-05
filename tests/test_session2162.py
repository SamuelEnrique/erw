"""Session 2162: Great Britain's daily demand from Elexon's BMRS.

Energy Research Warehouse (ERW). Tests warehouse/connectors/elexon_demand.py on an answer built here in the INDOD
endpoint's CSV form (made up for the test, not Elexon's): a settlement day written at 00:00:00Z (Decision 11), the windows of at most two years ending the day before --end,
a blank demand left out; a header not the endpoint's, a date not YYYY-MM-DD, a demand that is not a whole number and a
day given twice stopping the run; the verdict, the sector rule and the holds. No network.

    python -m unittest tests.test_session2162 -v
"""

import csv
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import elexon_demand as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = "PublishTime,SettlementDate,Demand\n"


class Build(unittest.TestCase):
    def test_rows(self):
        t = E.finish(E.rows_of(HEAD + "2025-01-01T00:15:00Z,2024-12-31,603905\n2024-07-02T00:15:00Z,2024-07-01,500000\n"
                               "2024-07-03T00:15:00Z,2024-07-02,\n", "u", "r", ""))
        self.assertEqual(list(t.ts_utc), ["2024-07-01T00:00:00Z", "2024-12-31T00:00:00Z"])
        w = t[t.x_settlement_date == "2024-12-31"].iloc[0]
        self.assertEqual((w.value, w.unit, w.freq, w.geo, w.entity, w.variable), (603905.0, "MWh", "P1D", "GB", "elexon:GB", "indo_daily"))
        self.assertEqual(w.x_publish_time, "2025-01-01T00:15:00Z")

    def test_windows(self):
        self.assertEqual(E.windows("2026-10-24"), [("2020-01-01", "2021-12-31"), ("2022-01-01", "2023-12-31"),
                                                   ("2024-01-01", "2025-12-31"), ("2026-01-01", "2026-10-23")])
        self.assertEqual(E.windows("2025-06-01")[-1], ("2024-01-01", "2025-05-31"))
        for a, b in E.windows("2026-10-24"):
            self.assertLessEqual((E.dt.date.fromisoformat(b) - E.dt.date.fromisoformat(a)).days + 1, 731)

    def test_stops(self):
        for bad in (HEAD.replace("Demand", "Volume") + "x,2024-01-01,1\n", HEAD + "x,01/01/2024,1\n",
                    HEAD + "x,2024-01-01,1.5\n"):
            with self.assertRaises(RuntimeError):
                E.rows_of(bad, "u", "r", "")
        with self.assertRaises(RuntimeError):
            E.finish(E.rows_of(HEAD + "x,2024-01-01,1\n", "u", "r", "") + E.rows_of(HEAD + "y,2024-01-01,2\n", "v", "r", ""))


class Registered(unittest.TestCase):
    def test_verdict_sector_and_holds(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "license_verdicts.csv"), encoding="utf-8", newline="") as f:
            v = {r["key"]: r for r in csv.DictReader(f)}
        self.assertEqual(v["Elexon Limited (BMRS)"]["verdict"], "may be public")
        self.assertEqual(B.sector_of(E.NAME), "power")
        self.assertIn(E.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
