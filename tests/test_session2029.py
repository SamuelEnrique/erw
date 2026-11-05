"""Session 2029: ORNL's EAGLE-I customer outages, a county's peak a day.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eaglei_outages.py on 15-minute records built here in the
dataset's form (made up for the test, not ORNL's): a county's daily peak and record count, the early years' column
name sum, a FIPS code given as a number regaining its leading zero, the state from the FIPS code; a file without the
columns, a time not a time and a FIPS code the states do not know stopping the run; the clock days; the sector rule
and the holds. No network.

    python -m unittest tests.test_session2029 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eaglei_outages as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def csv_bytes(header, rows):
    return (",".join(header) + "\n" + "\n".join(",".join(str(v) for v in r) for r in rows) + "\n").encode()


ROWS = [
    ["1001", "Autauga", "Alabama", "12", "2024-01-09 00:00:00"],
    ["1001", "Autauga", "Alabama", "340", "2024-01-09 00:15:00"],
    ["1001", "Autauga", "Alabama", "5", "2024-01-10 23:45:00"],
    ["48201", "Harris", "Texas", "120000", "2024-07-08 12:00:00"],
]


class Peaks(unittest.TestCase):
    def test_rows(self):
        g, _ = E.daily_peaks(csv_bytes(["fips_code", "county", "state", "customers_out", "run_start_time"], ROWS), 2024)
        s = E.to_series(g, BASE).set_index(["entity", "ts_utc"])
        a = s.loc[("eaglei:01001", "2024-01-09T00:00:00Z")]
        self.assertEqual((a.value, a.x_records, a.geo, a.unit, a.freq), (340, 2, "US-AL", "count", "P1D"))
        self.assertEqual(s.loc[("eaglei:01001", "2024-01-10T00:00:00Z")].value, 5)
        self.assertEqual(s.loc[("eaglei:48201", "2024-07-08T00:00:00Z")].geo, "US-TX")
        self.assertEqual(len(s), 3)

    def test_early_years_sum(self):
        g, _ = E.daily_peaks(csv_bytes(["fips_code", "county", "state", "sum", "run_start_time"], ROWS[:2]), 2015)
        self.assertEqual(int(g.n.iloc[0]), 340)

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            E.daily_peaks(csv_bytes(["fips_code", "county", "state", "run_start_time"], [r[:3] + r[4:] for r in ROWS]), 2024)
        with self.assertRaises(RuntimeError):
            E.daily_peaks(csv_bytes(["fips_code", "county", "state", "customers_out", "run_start_time"], [ROWS[0][:4] + ["soon"]]), 2024)
        g, _ = E.daily_peaks(csv_bytes(["fips_code", "county", "state", "customers_out", "run_start_time"], [["99001"] + ROWS[0][1:]]), 2024)
        with self.assertRaises(RuntimeError):
            E.to_series(g, BASE)

    def test_clock_days(self):
        self.assertEqual(E.clock_days(2024), ["2024-03-10", "2024-11-03"])
        self.assertEqual(E.clock_days(2025), ["2025-03-09", "2025-11-02"])


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.TABLE), "power")
        self.assertIn(E.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
