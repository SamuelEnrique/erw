"""Audit of "What a generator earns", finding 9 (session 9841, docs/reviews/generator-model-audit-2026-11-20.md): the gas
peaker runs in every hour whose price is above its fuel and variable cost, with no start cost and no minimum run
(warehouse/derived/merchant_revenue.py, build_iso; the note's section 3.4; the page's decision 4). In ERCOT over the
page's last twelve months that rule starts the plant hundreds of times for runs whose median margin is small.

From the page's own snapshot (site/data/merchant_snapshot.json: the hub's hourly prices and Henry Hub by hour, the arrays
the page itself reprices the peaker from), ERCOT, October 2025 to September 2026, at the default heat rate and variable O&M:
1. the rule's margin is the snapshot's month rows' (USD 48.15 per kW over 1,772 run hours);
2. it starts 403 times, a quarter of its runs last one hour, and the median run's margin is about USD 25 per MW;
3. with a start cost of USD 50 per MW (runs that do not pay their start skipped) the margin falls by more than a fifth.
It passes on main: it shows the fault. Nothing is written."""
import json
import os
import statistics
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SNAP = os.path.join(ROOT, "site", "data", "merchant_snapshot.json")
L12 = [f"2025-{k:02d}" for k in (10, 11, 12)] + [f"2026-{k:02d}" for k in range(1, 10)]


class PeakerStarts(unittest.TestCase):
    def test_starts_and_their_margin(self):
        with open(SNAP, encoding="utf-8") as f:
            e = json.load(f)["isos"]["ercot"]
        rows = e["months"]
        i0, i1 = rows[L12[0]]["i0"], rows[L12[-1]]["i1"]
        p, hh = e["price"][i0:i1], e["hh"][i0:i1]
        run = [(pp is not None and h is not None and pp > h * 10.725 + 4.25) for pp, h in zip(p, hh)]
        margin = [(pp - (h * 10.725 + 4.25)) if r else 0.0 for pp, h, r in zip(p, hh, run)]
        table = sum(rows[m]["peaker"]["revenue_per_mw"] for m in L12)
        self.assertAlmostEqual(sum(margin) / 1000, table / 1000, delta=0.05)     # the page's own rows (prices to the cent)
        self.assertEqual(sum(run), 1772)
        blocks, lens, cur, n = [], [], 0.0, 0
        for r, mm in zip(run + [False], margin + [0.0]):
            if r:
                cur += mm; n += 1
            elif n:
                blocks.append(cur); lens.append(n); cur, n = 0.0, 0
        self.assertEqual(len(blocks), 403)
        self.assertAlmostEqual(sum(1 for x in lens if x == 1) / len(lens), 0.25, delta=0.02)
        self.assertLess(statistics.median(blocks), 30.0)
        kept = sum(b - 50 for b in blocks if b > 50)
        self.assertLess(kept, 0.8 * sum(margin))


if __name__ == "__main__":
    unittest.main()
