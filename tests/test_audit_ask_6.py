"""Session 10234 (chain 710, part D): the ceilings' note says what its "fails closed" does not cover.

docs/reviews/ask-model-audit-2026-11-26.md, finding 6. docs/methods/ask_limits.md heads its rule "It fails closed".
The admission does (site/lib/chat/limits.ts admit: anything but a plain yes is a no), but the spend it compares with
the ceilings is the ledger's rows, and a visitor's call whose row fails to write is logged and not counted: only an
evaluation's write is strict (site/lib/chat/ledger.ts recordCall, site/app/api/ask/route.ts ledgerOpts). Words only:
the note gains a paragraph that says so. Fails on main, passes on the branch. No node, no network.
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheNote(unittest.TestCase):
    def test_it_says_what_does_not_close(self):
        n = read("docs", "methods", "ask_limits.md")
        self.assertIn("**It fails closed.** Anything that is not a plain yes from the database is a no.", n)
        self.assertIn("**What it does not close for**", n)
        self.assertIn("A visitor's model call whose row the ledger refuses is logged on", n)
        self.assertIn("a call the ledger lost is never counted", n)

    def test_the_code_is_as_the_note_now_says(self):
        self.assertIn("if (strict) throw", read("site", "lib", "chat", "ledger.ts"))
        self.assertIn("const ledgerOpts = evaluation ? { step: EVAL_STEP, strictLedger: true, record: true } : {};",
                      read("site", "app", "api", "ask", "route.ts"))


if __name__ == "__main__":
    unittest.main()
