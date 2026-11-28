"""Ready for the owner's ruling (session 11407, chain 770 part C): the contracts page draws the filer's description
beside a rate filed as a number.

The audit (session 10226, docs/reviews/contracts-model-audit-2026-11-26.md, finding 2, test branch wip/audit-contracts-2)
found `rateText` (site/lib/contracts.ts) returning the number and its units alone when `x_rate` is not empty, so words
that make the number an adder to an index or LMP, one term of a formula, an escalation or a percent were never drawn.
The other choice, made here: `rateText` returns the description as `words` beside a number, and the page draws it
after the number in grey. No figure moves.

1. The code returns and draws the words (read from the files; no node run).
2. Measured from the table (skipped where it is not on the machine, or is another retrieval): of the 1,317 numbers of
   energy, capacity and tolling signed on or after 9 January 2024 (the load of 5 October 2026), 1,110 gain words, 178
   of them naming an index, LMP, an adder, plus, a formula, an escalation, a heat rate or a percent (156 not 0); in the
   default view (2026 Q2) 106 of 112, 1 of them such words.
3. The fold, the decision (page and note alike) and the note say it.
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
        return f.read().replace("\r\n", "\n")


def number(v):
    try:
        x = float(v.strip())
        return x if x == x else None
    except ValueError:
        return None


class TheWordsBesideTheNumber(unittest.TestCase):
    def test_the_code_returns_and_draws_the_words(self):
        lib = read("site", "lib", "contracts.ts")
        body = lib[lib.index("export function rateText("):]
        body = body[:body.index("\n}\n")]
        self.assertIn("words?: string", body)
        self.assertLess(body.index("rate_description"), body.index('if (n !== "") return'))   # read before the number returns
        self.assertIn('numeric: true, ...(w !== "" ? { words: w } : {})', body)
        page = read("site", "app", "contracts", "page.tsx")
        self.assertIn('{rate.words ? <span className="text-muted" data-rate-words="1">: {rate.words}</span> : null}', page)

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
        q2 = [0, 0, 0]
        with open(p, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(line for line in f if not line.startswith("#")):
                day = r["event_date"][:10]
                if day < "2024-01-09" or r["x_product_name"].strip().upper() not in POWER:
                    continue
                if r["x_rate"].strip() == "":
                    continue
                d = r["x_rate_description"].strip()
                hit = bool(d) and bool(INDEX.search(d))
                nums += 1
                words += bool(d)
                index += hit
                index_not_zero += hit and number(r["x_rate"]) not in (0, None)
                if "2026-04-01" <= day < "2026-07-01":
                    q2[0] += 1
                    q2[1] += bool(d)
                    q2[2] += hit
        self.assertEqual((nums, words, index, index_not_zero), (1317, 1110, 178, 156))
        self.assertEqual(q2, [112, 106, 1])

    def test_the_fold_the_decision_and_the_note_say_it(self):
        page = read("site", "app", "contracts", "page.tsx")
        line = page[page.index("<strong>Price, as filed:</strong>"):]
        line = line[:line.index("</li>")]
        self.assertIn("with the filer&apos;s own description after it in grey when one is filed beside it", line)
        self.assertIn("not always the price paid", line)
        words = "with the filer's own words after it when filed beside it (since session 11407)"
        self.assertIn(words, read("site", "app", "contracts", "Decisions.tsx"))
        note = read("docs", "methods", "contracts.md")
        self.assertIn(words, note)
        self.assertIn("1,110 of the 1,317 numbers", note)


if __name__ == "__main__":
    unittest.main()
