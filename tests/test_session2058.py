"""Session 2058: the U.S. Drought Monitor's percent of area in drought, by state, a week.

Energy Research Warehouse (ERW). Tests warehouse/connectors/usdm_drought.py on answers built here in the data services'
CSV form (figures made up for the test, not the Monitor's): each category a row, the traditional form checked; a state
missing, figures out of order, none plus d0 not 100 and a missing column stopping the run; the spans; the sector rule
and the holds. No network.

    python -m unittest tests.test_session2058 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import usdm_drought as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
HEAD = "MapDate,StateAbbreviation,None,D0,D1,D2,D3,D4,ValidStart,ValidEnd,StatisticFormatID\n"


def answer(override=None, drop=None, head=HEAD):
    lines = []
    for st in U.STATES.values():
        figs = "40.00,60.00,30.00,10.00,0.00,0.00"
        if override and st in override:
            figs = override[st]
        if st != drop:
            lines.append(f"20250128,{st},{figs},2025-01-28,2025-02-03,1")
    return (head + "\n".join(lines) + "\n").encode()


class Parse(unittest.TestCase):
    def test_rows(self):
        rows = U.parse(answer({"CA": "33.22,66.78,54.31,32.86,11.88,0.00"}), BASE)
        self.assertEqual(len(rows), 48 * 6)
        got = {(r["entity"], r["variable"]): r for r in rows}
        c = got[("usdm:CA", "d1")]
        self.assertEqual((c["value"], c["unit"], c["ts_utc"], c["geo"], c["freq"]), (54.31, "pct", "2025-01-28T00:00:00Z", "US-CA", "P1W"))
        self.assertEqual(got[("usdm:CA", "none")]["value"], 33.22)

    def test_stops(self):
        for content in (answer(drop="TX"), answer({"TX": "40.00,60.00,10.00,30.00,0.00,0.00"}), answer({"TX": "50.00,60.00,30.00,10.00,0.00,0.00"}),
                        answer(head=HEAD.replace("D4,", ""))):
            with self.assertRaises(RuntimeError):
                U.parse(content, BASE)

    def test_spans(self):
        self.assertEqual(U.spans(2015, 2026), [(2015, 2018), (2019, 2022), (2023, 2026)])


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(U.TABLE), "power")
        self.assertIn(U.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {U.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
