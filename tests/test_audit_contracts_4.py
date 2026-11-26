"""Audit of the contracts page, finding 4 (session 10226, docs/reviews/contracts-model-audit-2026-11-26.md): "one row per
product of an agreement".

The note under "Contract rows signed that quarter" said a row is one product of an agreement. One agreement can also file
a row for each year, month or peak period of its price, as the page's own fold says: in the default view (2026 Q2
signed; energy, capacity and tolling) 18 of the 198 pairs of agreement and product hold 2 to 4 rows each, 47 of the 227.

1. Measured from the table (skipped where it is not on the machine, or is another retrieval). Passes on main.
2. The fix on this branch, words only: the note says "and per price period where the filer files one"; the note of
   method says it with the count. Fails on main. No figure moves.
Counts only: no party's name, figure or row (the table is internal)."""
import collections
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
POWER = {"ENERGY", "CAPACITY", "TOLLING ENERGY"}


def table():
    for d in (os.path.join(ROOT, "warehouse", "output"), os.path.join(os.path.dirname(ROOT), "erw", "warehouse", "output")):
        p = os.path.join(d, "ferc_eqr_contracts.csv")
        if os.path.exists(p):
            return p
    return None


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class RowsRepeatByPricePeriod(unittest.TestCase):
    def test_measured_from_the_table(self):
        p = table()
        if p is None:
            self.skipTest("ferc_eqr_contracts is not on this machine")
        with open(p, encoding="utf-8") as f:
            head = "".join(next(f) for _ in range(6))
        if "Retrieved: 20261004T035009Z" not in head:
            self.skipTest("another retrieval than the one measured (20261004T035009Z)")
        csv.field_size_limit(1 << 30)
        pairs = collections.Counter()
        with open(p, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(line for line in f if not line.startswith("#")):
                day, prod = r["event_date"][:10], r["x_product_name"].strip().upper()
                if "2026-04-01" <= day < "2026-07-01" and prod in POWER:
                    pairs[(r["x_seller_company_name"], r["x_contract_service_agreement_id"], prod)] += 1
        many = [v for v in pairs.values() if v > 1]
        self.assertEqual((sum(pairs.values()), len(pairs), len(many), sum(many), max(many)), (227, 198, 18, 47, 4))

    def test_the_headline_note_says_it(self):
        page = read("site", "app", "contracts", "page.tsx")
        self.assertIn("one row per product of an agreement, and per price period where the filer files one.", page)
        self.assertNotIn("one row per product of an agreement.{", page)
        self.assertIn("finding 4", read("docs", "methods", "contracts.md"))


if __name__ == "__main__":
    unittest.main()
