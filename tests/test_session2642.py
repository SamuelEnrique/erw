"""Session 2642: the Anguilla Statistics Department's Energy Statistics, Table 2.4.2-1, Anguilla's electricity generation a month.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statai_anguilla_electricity.py on sheet rows built here (made up for
the test, not the Department's): the header's years read from 1995, whole years taken and stated in MWh, a year with missing
months left out; a header not from 1995, months that miss the Total and a month row out of place stopping the run; the sector
rule and the holds. No network.

    python -m unittest tests.test_session2642 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import statai_anguilla_electricity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def rows(first=1995, total=None, swap=False):
    head = [(None, "Table 2.4.2-1"), (None, "Energy"), (None, "Electricity Generation"), (None, None),
            (None, "Month", first, first + 1, first + 2, "% Change")]
    months = list(A.MONTHS)
    if swap:
        months[0], months[1] = months[1], months[0]
    body = [(None, m, 1000.0, 2000.0, 3000.0 if i < 3 else None, None) for i, m in enumerate(months)]
    body.append((None, "Total", total if total is not None else 12000.0, 24000.0, 9000.0, None))
    return head + body + [(None, "Annual % Change", None, 100.0, None, None)]


class Parse(unittest.TestCase):
    def test_rows(self):
        y = A.parse_rows(rows())
        self.assertEqual(sorted(y), [1995, 1996])
        t = A.frame(y, {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"})
        self.assertEqual(len(t), 24)
        self.assertEqual(t.value.iloc[0], 1.0)
        self.assertEqual(set(t.unit), {"MWh"})
        self.assertEqual(t.ts_utc.iloc[13], "1996-02-01T00:00:00Z")

    def test_stops(self):
        for bad in (rows(first=1996), rows(total=12500.0), rows(swap=True)):
            with self.assertRaises(RuntimeError):
                A.parse_rows(bad)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
