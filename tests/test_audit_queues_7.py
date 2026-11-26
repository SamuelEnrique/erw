"""Audit of the interconnection queue, finding 6, two figures (session 10213, docs/reviews/queues-model-audit-2026-11-26.md).
NOT for landing: a test only, for Samuel's ruling, default "left as it is".

1. Rounded twice. The builder writes each MW sum to a tenth (queue_summary.py, round(x, 1)) and the page rounds that to a
   whole MW, so a sum whose exact tenths and hundredths lie from .45 to .49 is printed one MW high. In the default view 3
   of the 315 keyed figures: 2005's MW still active (exact 1,288.45, printed 1,289), 2016's MW entered (213,252.46,
   printed 213,253) and 2022's (681,952.47, printed 681,953). The other choice (the builder writes two decimals, or the
   page rounds the exact sum) moves each by one MW.
2. Two pages, two rules for a negative capacity. /queues counts a request with no positive capacity as adding no MW
   (decision 4); /queues/places sums capacity as filed (queue_places.py), so TVA's one withdrawn entry of -75 MW makes
   its withdrawn MW 218,498 where /queues' rule gives 218,573.

Both read Berkeley Lab's rows where the warehouse holds them (skipped elsewhere) and the page files. Nothing changes."""
import csv
import json
import os
import unittest
from decimal import ROUND_HALF_EVEN, Decimal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LBNL = os.environ.get("ERW_LBNL_CSV") or os.path.join(ROOT, "warehouse", "output", "lbnl_interconnection_queue.csv")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def page_whole(v):
    # Math.round on the file's tenth
    return int((Decimal(str(v)) + Decimal("0.5")) // 1)


@unittest.skipUnless(os.path.exists(LBNL), "lbnl_interconnection_queue.csv is not on this machine")
class TwoSmallFigures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(LBNL, encoding="utf-8", newline="") as f:
            cls.rows = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
        cls.q = json.loads(src("site", "data", "queues.json"))
        cls.places = json.loads(src("site", "data", "queue_places.json"))

    def exact(self, year, status=None):
        s = Decimal(0)
        for r in self.rows:
            if r["q_year"] and int(float(r["q_year"])) == year and (status is None or r["q_status"] == status):
                v = Decimal(r["capacity_mw"])
                s += v if v > 0 else 0
        return s

    def test_rounded_twice_prints_one_mw_high(self):
        ys = self.q["views"]["us|all"]["years"]
        for year, key, status, printed in ((2005, "mw_active", "active", 1289), (2016, "mw_entered", None, 213253), (2022, "mw_entered", None, 681953)):
            e = self.exact(year, status)
            self.assertEqual(Decimal(str(ys[str(year)][key])), e.quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN))
            self.assertEqual(page_whole(ys[str(year)][key]), printed)
            self.assertEqual(int((e + Decimal("0.5")) // 1), printed - 1, year)

    def test_places_sums_a_negative_capacity_as_filed(self):
        tva = next(o for o in self.places["owners"] if o["owner"] == "TVA")
        neg = [r for r in self.rows if r["lbnl_entity"] == "TVA" and r["region"] == "Southeast" and float(r["capacity_mw"]) < 0]
        self.assertEqual([(r["q_status"], r["capacity_mw"]) for r in neg], [("withdrawn", "-75.0")])
        as_queues = sum(max(float(r["capacity_mw"]), 0) for r in self.rows if r["lbnl_entity"] == "TVA" and r["region"] == "Southeast" and r["q_status"] == "withdrawn")
        self.assertEqual(tva["by_status"]["withdrawn"]["mw"], 218498.0)
        self.assertEqual(round(as_queues, 1), 218573.0)


if __name__ == "__main__":
    unittest.main()
