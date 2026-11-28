"""Audit of /equities, finding 5 (session 11403, docs/reviews/equities-model-audit-2026-11-28.md): the page called
the line "Debt"; it is long-term debt.

The connector reads the line from LongTermDebt, LongTermDebtNoncurrent, LongTermDebtAndCapitalLeaseObligations or
LongTermDebtAndFinanceLeaseObligations (warehouse/connectors/sec_edgar.py CONCEPTS, the variable long_term_debt_usd,
docs/methods/equities.md "long-term debt"): never short-term borrowings or commercial paper. A utility analyst reading
"Debt" for Duke Energy takes it as all of it.

1. Every company's debt concept in the files is a long-term debt concept (passes on main).
2. The fix on this branch (fails on main): the page's name for the line is "Long-term debt" (site/lib/equities.ts
   STATEMENT, which names the table's row, the figure's choice, its headline and its chart), and the list's download
   says long-term debt. No figure moves."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
D = os.path.join(ROOT, "site", "data", "equities")
LIB = os.path.join(ROOT, "site", "lib", "equities.ts")
LONG = {"us-gaap:LongTermDebt", "us-gaap:LongTermDebtNoncurrent", "us-gaap:LongTermDebtAndCapitalLeaseObligations",
        "us-gaap:LongTermDebtAndFinanceLeaseObligations"}


class LongTermDebt(unittest.TestCase):
    def test_every_concept_is_long_term(self):
        with open(os.path.join(D, "index.json"), encoding="utf-8") as f:
            cos = [c for c in json.load(f)["companies"] if c["fundamentals_status"] == "shown"]
        seen = set()
        for c in cos:
            with open(os.path.join(D, c["file"]), encoding="utf-8") as f:
                k = json.load(f)["concepts"].get("debt")
            if k:
                seen.add(k)
        self.assertTrue(seen)
        self.assertLessEqual(seen, LONG)

    def test_the_page_says_long_term(self):
        src = open(LIB, encoding="utf-8").read()
        self.assertRegex(src, r'\["debt", "Long-term debt", "USD million"\]')
        self.assertIsNone(re.search(r'\["debt", "Debt",', src))
        self.assertIn("long-term debt in USD and shares outstanding at the period's end", src)


if __name__ == "__main__":
    unittest.main()
