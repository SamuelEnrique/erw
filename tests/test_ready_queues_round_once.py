"""Session 11408 (chain 770, part C): the interconnection queues, the other choice of the queues audit's finding 6
(docs/reviews/queues-model-audit-2026-11-26.md; its test branch wip/audit-queues-7, carried over here and turned to the
new rule). Not for landing until the owner rules.

The rule on this branch: warehouse/derived/queue_summary.py writes each MW sum to two decimals, so the page rounds once
to a whole MW; warehouse/derived/queue_places.py counts an entry with no positive capacity as adding no MW, as /queues
does. Measured by running both builders on this machine's lbnl_interconnection_queue.csv (read only; written only into
the worktree): the United States' 2005 MW still active 1,288.5 to 1,288.45 (printed 1,289 to 1,288), 2016's MW entered
213,252.5 to 213,252.46 (213,253 to 213,252), 2022's 681,952.5 to 681,952.47 (681,953 to 681,952); TVA's withdrawn MW on
/queues/places 218,498 to 218,573. Both site files (site/data/queues.json, queue_places.json) are rebuilt at landing by
the desk.

1. The builders' rules, on small rows.
2. Where the warehouse's rows are held: the three sums to two decimals equal the exact sums' whole MW."""
import os
import sys
import unittest
from decimal import Decimal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
LBNL = os.environ.get("ERW_LBNL_CSV") or os.path.join(ROOT, "warehouse", "output", "lbnl_interconnection_queue.csv")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class RoundOnceAndNoNegative(unittest.TestCase):
    def test_the_builders(self):
        s = src("warehouse", "derived", "queue_summary.py")
        self.assertNotIn('["mw"].sum()), 1)', s)
        self.assertIn('"mw_entered": round(float(c["mw"].sum()), 2)', s)
        p = src("warehouse", "derived", "queue_places.py")
        self.assertIn('d["mw"] = mw.where(mw > 0, 0.0)', p)

    @unittest.skipUnless(os.path.exists(LBNL), "lbnl_interconnection_queue.csv is not on this machine")
    def test_the_three_figures_print_their_exact_whole_mw(self):
        import queue_summary as qs
        d, _ = qs.read_input(os.path.dirname(LBNL))
        x = qs.prepared(d)
        summary = qs.summarize(x, int(x["year"].max()))
        ys = summary[("us", "all")]["years"]
        for year, key, printed in ((2005, "mw_active", 1288), (2016, "mw_entered", 213252), (2022, "mw_entered", 681952)):
            v = ys[year][key]
            self.assertEqual(int((Decimal(str(v)) + Decimal("0.5")) // 1), printed, year)   # Math.round on the file's figure


if __name__ == "__main__":
    unittest.main()
