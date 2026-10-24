"""Session 2350 (chain 105's session 2300, renumbered): Statnett's operational data, Norway's production and consumption a day.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statnett_norway.py on answers built here in Statnett's form
(figures made up for the test, not Statnett's): the slots placed on Norway's days, the empty slot after an autumn
clock-change day skipped, any other empty slot a day not published, an answer whose slots do not end at its end time
stopping the run; the sector rule and the hold. No network.

    python -m unittest tests.test_session2350 -v
"""

import datetime as dt
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import statnett_norway as S  # noqa: E402
import build_coverage as B  # noqa: E402

START_2025_10_24 = 1761256800000.0  # 2025-10-23T22:00Z, Norway's midnight of 24 October 2025 (summer time)


def answer(prod, cons, end_day):
    end = dt.datetime.combine(end_day, dt.time(), S.OSLO).astimezone(dt.timezone.utc)
    return {"StartPointUTC": START_2025_10_24, "EndPointUTC": end.timestamp() * 1000, "PeriodTickMs": S.DAY_MS,
            "Production": prod, "Consumption": cons}


class Place(unittest.TestCase):
    def test_autumn_slot(self):
        self.assertEqual(S.autumn_change(2025), dt.date(2025, 10, 26))
        # 24, 25, 26 October (the clocks go back on the 26th), the empty slot, 27 and 28 October
        days, missing = S.place(answer([1, 2, 3, None, 4, 5], [6, 7, 8, None, 9, 10], dt.date(2025, 10, 28)))
        self.assertEqual([d for d, _, _ in days], [dt.date(2025, 10, d) for d in (24, 25, 26, 27, 28)])
        self.assertEqual(days[3], (dt.date(2025, 10, 27), 4.0, 9.0))
        self.assertEqual(missing, [])

    def test_missing_day(self):
        days, missing = S.place(answer([1, None, 3], [4, None, 6], dt.date(2025, 10, 26)))
        self.assertEqual(missing, [dt.date(2025, 10, 25)])
        self.assertEqual([d for d, _, _ in days], [dt.date(2025, 10, 24), dt.date(2025, 10, 26)])

    def test_end_checked(self):
        with self.assertRaises(RuntimeError) as c:
            S.place(answer([1, 2, 3], [4, 5, 6], dt.date(2025, 10, 28)))
        self.assertIn("the slots end at", str(c.exception))
        with self.assertRaises(RuntimeError):
            S.place(dict(answer([1], [2], dt.date(2025, 10, 24)), PeriodTickMs=3600000))


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(S.TABLE), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
