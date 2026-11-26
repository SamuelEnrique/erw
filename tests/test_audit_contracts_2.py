"""Audit of the contracts page, finding 2 (session 10226, docs/reviews/contracts-model-audit-2026-11-26.md): a rate filed
as a number is drawn alone, without the filer's description beside it.

`rateText` (site/lib/contracts.ts) returns the number and its units when `x_rate` is not empty, and the description only
when it is. A filer can file a number and words that make it an adder to an index or LMP, one term of a formula, an
escalation or a percent; a trader reads the number in the cell as the price.

1. Measured from the table (skipped where it is not on the machine, or is another retrieval): of the 1,317 numbers of
   energy, capacity and tolling signed on or after 9 January 2024 (the window of the load of 5 October 2026), 1,110
   stand beside a description and 178 of those name an index, LMP, an adder, plus, a formula, an escalation, a heat
   rate or a percent; 156 of the 178 are not 0. The code drops the words when a number is filed. Passes on main.
2. The fix on this branch, words only: the fold "What a row is" says so, and the note. Fails on main. No figure moves.
   Drawing the description beside the number is the owner's ruling (default: left as it is).
Counts only: no party's name, figure or row (the table is internal)."""
import csv
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
POWER = {"ENERGY", "CAPACITY", "TOLLING ENERGY"}
INDEX = re.compile(r"\b(LMP|INDEX|INDEXED|ADDER|PLUS|ICE|PLATTS|NYMEX|FORMULA|MARGIN|HEAT RATE|GAS DAILY|CPI|ESCALAT\w*)\b|\+|%", re.I)


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


class NumberDrawnWithoutItsWords(unittest.TestCase):
    def test_the_code_drops_the_words_when_a_number_is_filed(self):
        lib = read("site", "lib", "contracts.ts")
        body = lib[lib.index("export function rateText("):]
        body = body[:body.index("\n}\n")]
        self.assertLess(body.index('if (n !== "") return'), body.index("rate_description"))

    def test_measured_from_the_table(self):
        p = table()
        if p is None:
            self.skipTest("ferc_eqr_contracts is not on this machine")
        with open(p, encoding="utf-8") as f:
            head = "".join(next(f) for _ in range(6))
        if "Retrieved: 20261004T035009Z" not in head:
            self.skipTest("another retrieval than the one measured (20261004T035009Z)")
        csv.field_size_limit(1 << 30)
        nums = words = index = index_not_zero = 0
        with open(p, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(line for line in f if not line.startswith("#")):
                if r["event_date"][:10] < "2024-01-09" or r["x_product_name"].strip().upper() not in POWER:
                    continue
                v = number(r["x_rate"])
                if v is None:
                    continue
                nums += 1
                d = r["x_rate_description"].strip()
                words += bool(d)
                if d and INDEX.search(d):
                    index += 1
                    index_not_zero += v != 0
        self.assertEqual((nums, words, index, index_not_zero), (1317, 1110, 178, 156))

    def test_the_fold_and_the_note_say_it(self):
        page = read("site", "app", "contracts", "page.tsx")
        line = page[page.index("<strong>Price, as filed:</strong>"):]
        line = line[:line.index("</li>")]
        self.assertIn("When a number is filed, the filer&apos;s description is not drawn beside it", line)
        self.assertIn("not always the price paid", line)
        self.assertIn("since session 10226 the fold\nsays so", read("docs", "methods", "contracts.md").replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
