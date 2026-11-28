"""Session 11408 (chain 770, part C): the interconnection queues, the other choice of the queues audit's finding 5
(docs/reviews/queues-model-audit-2026-11-26.md; no test branch there: the figure was measured, not made). Not for
landing until the owner rules.

The rule on this branch: warehouse/derived/queue_summary.py takes each status as at the end of the edition's last year,
so a request withdrawn after it (53 requests, 13,275 MW, withdrawn 2 to 16 January 2026) counts as active. Measured by
running the builder on this machine's lbnl_interconnection_queue.csv (read only; written only into the worktree): the
United States' active requests 8,513 to 8,566 and MW 1,864,963.3 to 1,878,238.1 (+0.7 percent); PJM 1,134 to 1,145
requests; CAISO 432 to 434; the United States' past share withdrawn 70.89 to 70.86 percent. The site file is rebuilt at
landing by the desk.

1. prepared() on small rows: a withdrawal of January after the edition's year counts as active, one of December does not.
2. Where the warehouse's rows are held: 8,566 active requests."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
LBNL = os.environ.get("ERW_LBNL_CSV") or os.path.join(ROOT, "warehouse", "output", "lbnl_interconnection_queue.csv")


class StatusesAtTheYearEnd(unittest.TestCase):
    def test_prepared(self):
        import pandas as pd
        import queue_summary as qs
        d = pd.DataFrame({"region": ["MISO"] * 3, "status": ["withdrawn", "withdrawn", "active"], "type_clean": ["Solar"] * 3,
                          "q_year": [2024, 2025, 2025], "q_date": ["2024-05-01"] * 3, "on_date": [None] * 3,
                          "wd_date": ["2026-01-05", "2025-12-20", None], "capacity_mw": [100.0, 50.0, 10.0]})
        self.assertEqual(list(qs.prepared(d)["status"]), ["active", "withdrawn", "active"])

    @unittest.skipUnless(os.path.exists(LBNL), "lbnl_interconnection_queue.csv is not on this machine")
    def test_on_the_rows(self):
        import queue_summary as qs
        d, _ = qs.read_input(os.path.dirname(LBNL))
        self.assertEqual(int((qs.prepared(d)["status"] == "active").sum()), 8566)


if __name__ == "__main__":
    unittest.main()
