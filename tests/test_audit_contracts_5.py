"""Audit of the contracts page, finding 5 (session 10226, docs/reviews/contracts-model-audit-2026-11-26.md): the limits box
is silent on zeros.

The box says about half the rows give their price as words, not a number, and counts the rows that file no number. Of
the rows held in the window of the load of 5 October 2026 (executed on or after 9 January 2024), 8,033 file a number and
4,119 of those file 0 (302 among energy, capacity and tolling, 3,817 in the other products): 3,914 of 18,989 rows file
a number other than 0.

1. Measured from the table (skipped where it is not on the machine, or is another retrieval). Passes on main.
2. The fix on this branch, words only: the box says "Of the numbers filed, about half are 0, most of them outside energy,
   capacity and tolling". Fails on main. No figure moves (the share is words; the stored summary counts no zeros).
Counts only: no party's name, figure or row (the table is internal)."""
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


def number(v):
    try:
        x = float(v.strip())
        return x if x == x else None
    except ValueError:
        return None


class HalfTheNumbersAreZero(unittest.TestCase):
    def test_measured_from_the_table(self):
        p = table()
        if p is None:
            self.skipTest("ferc_eqr_contracts is not on this machine")
        with open(p, encoding="utf-8") as f:
            head = "".join(next(f) for _ in range(6))
        if "Retrieved: 20261004T035009Z" not in head:
            self.skipTest("another retrieval than the one measured (20261004T035009Z)")
        csv.field_size_limit(1 << 30)
        held = nums = zero = zero_power = 0
        with open(p, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(line for line in f if not line.startswith("#")):
                if r["event_date"][:10] < "2024-01-09":
                    continue
                held += 1
                if r["x_rate"].strip() == "":
                    continue
                nums += 1
                if number(r["x_rate"]) == 0:
                    zero += 1
                    zero_power += r["x_product_name"].strip().upper() in POWER
        self.assertEqual((held, nums, zero, zero_power), (18989, 8033, 4119, 302))
        self.assertTrue(0.45 <= zero / nums <= 0.55)
        self.assertGreater(zero - zero_power, zero / 2)

    def test_the_box_says_it(self):
        page = read("site", "app", "contracts", "page.tsx")
        box = page[page.index("function Limits("):page.index("export default")]
        self.assertEqual(box.count("<li>"), 3)
        self.assertIn("Of the numbers filed, about half are 0, most of them outside energy, capacity and tolling.", box)
        self.assertIn("finding 5", read("docs", "methods", "contracts.md"))


if __name__ == "__main__":
    unittest.main()
