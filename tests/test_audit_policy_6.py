"""Audit of the policy monitor, finding 8 (session 10217, docs/reviews/policy-model-audit-2026-11-26.md): the states'
laws block marks a law "enacted" with the hover "Signed into law; its effective date is later, or the text read prints
none." (site/lib/largeloadrules.ts, LAW_STATUS_TIP). In the page file of 16 November 2026 (state_large_load_laws, read
13 and 14 November), Maryland's S.B. 937 is enacted with its Effective column 2025-06-01, seventeen months before the
read; Maryland's H.B. 1532 prints "shall take effect July 1, 2026" and Minnesota's H.F. 16 "effective the day following
final enactment" (signed 14 June 2025) in their cites, while their Effective column says "not published".

1. Through the page file: an enacted law whose own effective date is before the day it was read. Passes on main.
2. The fix on this branch, words only: the "enacted" hover says the status is the read's and the effective day may
   have passed. Fails on main. Which status each law should carry is the research table's (a data request), and moving
   the counts is for the owner's ruling (wip/audit-policy-11)."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheEnactedHoverSaysWhatItIs(unittest.TestCase):
    def test_an_enacted_law_whose_effective_date_had_passed_when_read(self):
        f = json.loads(src("site", "data", "siting", "large_load_rules.json"))
        md = [l for l in f["laws"] if l["state"] == "MD" and l["bill"].startswith("S.B. 937")]
        self.assertEqual(len(md), 1)
        # session 10000 (chain 701, data request 27 from this audit): the law read again on 26 November 2026 is in force
        # since 1 June 2025, so the file now says so; the hover's words (below) stay for the two laws still marked enacted
        self.assertEqual(md[0]["status"], "in effect")
        self.assertEqual(md[0]["effective"], "2025-06-01")
        self.assertLess(md[0]["effective"], md[0]["read"][:10])

    def test_the_hover_says_it(self):
        lib = src("site", "lib", "largeloadrules.ts")
        self.assertNotIn("Signed into law; its effective date is later, or the text read prints none.", lib)
        self.assertIn("enacted: \"Signed into law, as the ERW's read of the text marked it; the read did not mark it in effect. Where the text "
                      "prints when it takes effect, the Effective column or the status's cite says so, and that day may already have passed.\"", lib)


if __name__ == "__main__":
    unittest.main()
