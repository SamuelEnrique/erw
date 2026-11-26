"""Audit of the contracts page, finding 6 (session 10226, docs/reviews/contracts-model-audit-2026-11-26.md): the fold names
one reason a row is left out; the connector has two.

The fold "What a row is" said "A row whose execution date cannot be read is left out, not guessed."
warehouse/connectors/ferc_eqr_contracts.py also leaves out a row whose date reads and lies outside 1677-09-22 to
2262-04-11, the dates pandas can hold: 11 rows of 2026 Q2's file (2526-01-01, 2706-01-01, 2915-01-01), and 0 rows whose
date cannot be read (the table's header).

1. The connector's two rules, and the header's count where the table is on the machine. Passes on main.
2. The fix on this branch, words only: the fold and the note name both. Fails on main. No figure moves."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TwoReasonsARowIsLeftOut(unittest.TestCase):
    def test_the_connector_has_two_rules(self):
        c = read("warehouse", "connectors", "ferc_eqr_contracts.py")
        self.assertIn('DATE_MIN, DATE_MAX = "1677-09-22", "2262-04-11"', c)
        self.assertIn("if when is None:", c)
        self.assertIn("if not DATE_MIN <= when <= DATE_MAX:", c)
        for d in (os.path.join(ROOT, "warehouse", "output"), os.path.join(os.path.dirname(ROOT), "erw", "warehouse", "output")):
            p = os.path.join(d, "ferc_eqr_contracts.csv")
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    head = "".join(next(f) for _ in range(6))
                if "Retrieved: 20261004T035009Z" in head:
                    self.assertIn("0 left out for an execution date that cannot be read and 11 for one outside 1677-09-22 to 2262-04-11", head)
                break

    def test_the_fold_and_the_note_say_both(self):
        page = read("site", "app", "contracts", "page.tsx")
        line = page[page.index("<strong>Signed:</strong>"):]
        line = line[:line.index("</li>")]
        self.assertIn("or reads as a year after 2262", line)
        self.assertIn("is left out and counted, not guessed", line)
        self.assertIn("(session 10226, finding 6)", read("docs", "methods", "contracts.md"))


if __name__ == "__main__":
    unittest.main()
