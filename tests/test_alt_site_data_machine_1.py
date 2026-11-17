"""Ruling alternative 1 of the data machine's tables (session 7713, 17 November 2026, branch wip/alt-site-data-machine-1;
not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-site-data-machine-2026-11-17.md, line 1): may
EIA's six-month file fill the 2025 interchange gap (2,779 balancing authority days) though it matches the API on only
96.3 percent of the days compared? On main it does (session 3941). On this branch it does not
(warehouse/connectors/eia930_daily_total_interchange.py SIX_FILL): a short month stays as the API answers it. The table's
rows of November and December 2025 stay at 1,067 balancing authority days (November 333, December 734) instead of 3,846
(+2,779, +260 percent, under main's fill on the data machine). Pinned on the connector's own switch and on the local copy
of the table where it is on the machine (warehouse/output, or the folder ERW_TABLES_DIR names): it was written before the
fill ran (retrieved 10 November 2026) and holds exactly the API's answer, the other choice's figure. The six-month file's
own arithmetic (six_fill, eastern_days) is kept and still tested by tests/test_session3941.py.

    python -m unittest tests.test_alt_site_data_machine_1 -v
"""

import csv
import os
import sys
import unittest
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia930_daily_total_interchange as ti  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "eia930_daily_total_interchange.csv")


class TheSwitch(unittest.TestCase):
    def test_the_fill_is_off(self):
        self.assertIs(ti.SIX_FILL, False)

    def test_the_fill_is_called_only_when_on(self):
        with open(ti.__file__, encoding="utf-8") as f:
            code = f.read()
        self.assertIn("if still and SIX_FILL:", code)
        self.assertEqual(code.count("six_fill(set(still)"), 1)


@unittest.skipUnless(os.path.exists(CSV), "the daily interchange table is not on this machine")
class OnTheLocalTable(unittest.TestCase):
    def test_november_and_december_2025_as_the_api_answers(self):
        days, six = Counter(), 0
        with open(CSV, encoding="utf-8") as f:
            for r in csv.DictReader(line for line in f if not line.startswith("#")):
                if r["ts_utc"][:7] in ("2025-11", "2025-12"):
                    days[r["ts_utc"][:7]] += 1
                    six += ti.SIX_SOURCE in (r["source"] or "") or "sixMonthFiles" in (r["source_url"] or "")
        self.assertEqual((days["2025-11"], days["2025-12"], six), (333, 734, 0))


if __name__ == "__main__":
    unittest.main()
