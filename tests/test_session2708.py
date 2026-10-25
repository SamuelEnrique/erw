"""Session 2708: NS Power's OASIS Hourly Total Net Nova Scotia Load, 2022 to 2026.

Energy Research Warehouse (ERW). Tests warehouse/connectors/nspower_ns_load.py on files built here (made up for the test, not NS
Power's): Atlantic local hours ending placed in UTC on an ordinary day, the spring day (no hour ending 03:00) and the autumn day
(02:00 listed once or twice, never placed); the day's 24th hour read from its own date at 00:00; both time forms; lost, blank and
not-yet-posted hours counted, not filled; days not ended at retrieval left out; a wrong title, a missing hour, an hour given twice,
a falling HOUR and a load not positive stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2708 -v
"""

import datetime as dt
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import nspower_ns_load as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

LATE = dt.datetime(2027, 1, 1, tzinfo=dt.timezone.utc)
HEAD = [["Nova Scotia Power in-province load", "", "", ""], ["", "", "", ""], ["HOUR", "Date/time", "Load [MW]", ""], ["", "", "", ""]]


def day(d, hours, start, form="%Y-%m-%d", values=None, twice=()):
    out, n = [], start
    for he in hours:
        for _ in range(2 if he in twice else 1):
            n += 1
            stamp = d.strftime(form) + (" 00:00" if he == 24 else f" {he:02d}:00")
            out.append([str(n), stamp, (values or {}).get(he, f"{1000 + he}.5"), ""])
    return out


class Place(unittest.TestCase):
    def test_ordinary_day(self):
        rows, c = A.parse_rows(HEAD + day(dt.date(2025, 1, 1), range(1, 25), 0), 2025, LATE)
        self.assertEqual(rows[0], ("2025-01-01T04:00:00Z", 1001.5))       # hour ending 01:00 AST starts at 04:00 UTC
        self.assertEqual(rows[-1], ("2025-01-02T03:00:00Z", 1024.5))      # "2025-01-01 00:00" ends the first of January
        self.assertEqual(len(rows), 24)

    def test_spring_day(self):
        hours = [1, 2] + list(range(4, 25))
        rows, _ = A.parse_rows(HEAD + day(dt.date(2025, 3, 9), hours, 1608), 2025, LATE)
        got = dict(rows)
        self.assertEqual(len(rows), 23)
        self.assertEqual(got["2025-03-09T05:00:00Z"], 1002.5)           # hour ending 02:00 AST
        self.assertEqual(got["2025-03-09T06:00:00Z"], 1004.5)           # hour ending 04:00 ADT follows at once
        self.assertEqual(rows[-1][0], "2025-03-10T02:00:00Z")

    def test_autumn_day_once_or_twice(self):
        for twice in ((), (2,)):
            rows, c = A.parse_rows(HEAD + day(dt.date(2025, 11, 2), range(1, 25), 7320, twice=twice), 2025, LATE)
            got = dict(rows)
            self.assertEqual(len(rows), 23)
            self.assertEqual(c["not_placed"], 1 + len(twice))
            self.assertEqual(got["2025-11-02T03:00:00Z"], 1001.5)       # hour ending 01:00 ADT
            self.assertNotIn("2025-11-02T04:00:00Z", got)
            self.assertNotIn("2025-11-02T05:00:00Z", got)
            self.assertEqual(got["2025-11-02T06:00:00Z"], 1003.5)       # hour ending 03:00 AST
            self.assertEqual(rows[-1][0], "2025-11-03T03:00:00Z")

    def test_other_time_form(self):
        rows, _ = A.parse_rows(HEAD + [[str(i + 1), r[1], r[2], ""] for i, r in enumerate(
            day(dt.date(2023, 1, 1), range(1, 25), 0, form="%m/%d/%Y"))], 2023, LATE)
        self.assertEqual(rows[0], ("2023-01-01T04:00:00Z", 1001.5))


class Gaps(unittest.TestCase):
    def test_lost_blank_and_not_posted(self):
        a = day(dt.date(2025, 4, 1), range(1, 25), 0, values={h: A.LOST for h in range(1, 13)} | {15: " "})
        b = day(dt.date(2025, 4, 2), range(1, 25), 24, values={h: "" for h in range(20, 25)})
        c = day(dt.date(2025, 4, 3), range(1, 25), 48, values={h: "" for h in range(1, 25)})
        rows, n = A.parse_rows(HEAD + a + b + c, 2025, LATE)
        self.assertEqual(n, {"lost": 12, "blank": 1, "not_posted": 29, "not_placed": 0})
        self.assertEqual(len(rows), 11 + 19)

    def test_day_not_ended(self):
        rows, _ = A.parse_rows(HEAD + day(dt.date(2025, 1, 1), range(1, 25), 0), 2025,
                               dt.datetime(2025, 1, 2, 2, tzinfo=dt.timezone.utc))
        self.assertEqual(rows, [])

    def test_stops(self):
        d = dt.date(2025, 1, 1)
        bad_title = [["Some other load", "", "", ""]] + HEAD[1:] + day(d, range(1, 25), 0)
        missing = HEAD + day(d, range(1, 24), 0)
        twice = HEAD + day(d, range(1, 25), 0, twice=(5,))
        falling = HEAD + day(d, range(1, 25), 0)
        falling[10][0] = "2"
        negative = HEAD + day(d, range(1, 25), 0, values={7: "-3"})
        spring3 = HEAD + day(dt.date(2025, 3, 9), range(1, 25), 1608)
        for rows in (bad_title, missing, twice, falling, negative, spring3):
            with self.assertRaises(RuntimeError):
                A.parse_rows(rows, 2025, LATE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
