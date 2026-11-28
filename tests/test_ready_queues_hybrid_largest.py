"""Session 11408 (chain 770, part C): the interconnection queues, the other choice of the queues audit's finding 1
(docs/reviews/queues-model-audit-2026-11-26.md; its test branch wip/audit-queues-2, carried over here and turned to the
new rule). Not for landing until the owner rules.

The rule on this branch: warehouse/derived/queue_summary.py counts a request whose file gives two or more parts their
own MW at its largest part; a request of one part at its capacity, as before. Measured by running the builder on this
machine's lbnl_interconnection_queue.csv (read only; written only into the worktree), active MW origin/main against
here: CAISO 190,717.1 to 129,434.6, the West 448,601.0 to 394,235.4, the United States 1,864,963.3 to 1,749,315.2
(-6.2 percent), its solar with storage 503,794.2 to 407,011.5; ERCOT 408,107.6 and PJM 130,610.8 unchanged; counts and
count shares unchanged. The site file (site/data/queues.json) is rebuilt at landing by the desk; it then records
hybrid "largest part".

1. prepared() on small rows: a two-part request at its largest part, a one-part request at its capacity.
2. Where the warehouse's rows are held: the audit's sums (each hybrid at its largest part) equal the builder's.
3. Once the site file is rebuilt: CAISO's active MW 129,435."""
import csv
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
LBNL = os.environ.get("ERW_LBNL_CSV") or os.path.join(ROOT, "warehouse", "output", "lbnl_interconnection_queue.csv")


class EachHybridAtItsLargestPart(unittest.TestCase):
    def frame(self):
        import pandas as pd
        return pd.DataFrame({
            "region": ["CAISO", "ERCOT", "CAISO"], "q_status": ["active"] * 3, "status": ["active"] * 3,
            "type_clean": ["Solar+Battery", "Solar+Battery", "Solar"], "q_year": [2024, 2024, 2024],
            "q_date": ["2024-01-01"] * 3, "on_date": [None] * 3, "capacity_mw": [767.0, 201.04, -5.0],
            "type_1": ["Solar", "Solar", "Solar"], "mw_1": [500.0, 201.04, -5.0],
            "type_2": ["Battery", "Battery", None], "mw_2": [267.0, None, None], "type_3": [None] * 3, "mw_3": [None] * 3})

    def test_prepared(self):
        import queue_summary as qs
        x = qs.prepared(self.frame())
        self.assertEqual(list(x["mw"]), [500.0, 201.04, 0.0])

    @unittest.skipUnless(os.path.exists(LBNL), "lbnl_interconnection_queue.csv is not on this machine")
    def test_on_the_rows(self):
        import queue_summary as qs
        d, _ = qs.read_input(os.path.dirname(LBNL))
        x = qs.prepared(d)
        act = x[(x["status"] == "active") & (x["region"] == "CAISO")]
        self.assertEqual(round(float(act["mw"].sum())), 129435)
        self.assertEqual(round(float(x.loc[x["status"] == "active", "mw"].sum())), 1749315)

    def test_the_site_file_once_rebuilt(self):
        with open(os.path.join(ROOT, "site", "data", "queues.json"), encoding="utf-8") as f:
            q = json.load(f)
        if q.get("hybrid") != "largest part":
            self.skipTest("the site file is rebuilt at landing by the desk")
        self.assertEqual(round(q["views"]["caiso|all"]["whole"]["total_active_mw"]), 129435)


if __name__ == "__main__":
    unittest.main()
