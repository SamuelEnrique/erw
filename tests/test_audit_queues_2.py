"""Audit of the interconnection queue, finding 1, the figure (session 10213, docs/reviews/queues-model-audit-2026-11-26.md).
NOT for landing: a test only, for Samuel's ruling, default "left as it is".

Berkeley Lab's file gives a hybrid's second part its own MW in CAISO and for some of the West's requests and in no other
grid, so the page's sum of every part counts CAISO's hybrids twice over where ERCOT's count once. The other choice: each
request at its largest part everywhere, so every grid's hybrids are counted alike (a point of interconnection's figure,
roughly). On the 2026 edition: CAISO's active MW 190,717 to 129,435 (-32.1 percent), the West's 448,601 to 394,235
(-12.1 percent), the United States' 1,864,963 to 1,749,315 (-6.2 percent); the United States' solar with storage
503,794 to 407,012 (-19.2 percent); every other grid the same either way.

This test computes both from Berkeley Lab's rows (skipped where the warehouse does not hold them) and checks that the
page's file holds the first, the page's rule. It changes nothing."""
import csv
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LBNL = os.environ.get("ERW_LBNL_CSV") or os.path.join(ROOT, "warehouse", "output", "lbnl_interconnection_queue.csv")
REGION = {"caiso": "CAISO", "west": "West", "ercot": "ERCOT", "pjm": "PJM", "us": None}


def mw(s):
    try:
        return float(s)
    except ValueError:
        return 0.0


@unittest.skipUnless(os.path.exists(LBNL), "lbnl_interconnection_queue.csv is not on this machine")
class EachHybridAtItsLargestPart(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(LBNL, encoding="utf-8", newline="") as f:
            cls.rows = [r for r in csv.DictReader(ln for ln in f if not ln.startswith("#")) if r["q_status"] == "active"]
        with open(os.path.join(ROOT, "site", "data", "queues.json"), encoding="utf-8") as f:
            cls.q = json.load(f)

    def sums(self, grid):
        reg = REGION[grid]
        summed = largest = 0.0
        for r in self.rows:
            if reg is not None and r["region"] != reg:
                continue
            c = max(mw(r["capacity_mw"]), 0.0)
            parts = [mw(r[f"mw_{k}"]) for k in (1, 2, 3) if mw(r[f"mw_{k}"]) > 0]
            summed += c
            largest += max(parts) if len(parts) > 1 else c
        return summed, largest

    def test_the_page_holds_every_part_summed(self):
        for g in REGION:
            s, _ = self.sums(g)
            self.assertAlmostEqual(self.q["views"][f"{g}|all"]["whole"]["total_active_mw"], s, delta=0.06, msg=g)

    def test_the_other_choice_moves_caiso_and_the_west_alone(self):
        want = {"caiso": (190717, 129435), "west": (448601, 394235), "ercot": (408108, 408108), "pjm": (130611, 130611), "us": (1864963, 1749315)}
        for g, (a, b) in want.items():
            s, l = self.sums(g)
            self.assertEqual((round(s), round(l)), (a, b), g)
        s, l = self.sums("caiso")
        self.assertEqual(round(100 * (s - l) / s, 1), 32.1)


if __name__ == "__main__":
    unittest.main()
