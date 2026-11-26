"""Audit of the policy monitor, finding 8's figure (session 10217, docs/reviews/policy-model-audit-2026-11-26.md), a test
that shows it; not for landing. The hover's words are fixed on wip/audit-policy-6; the statuses are the research
table's (state_large_load_laws, a data request), and the counts move only on the owner's ruling.

The laws block counts "10 in effect, 6 enacted" (page file of 16 November 2026; read 13 and 14 November). Three of the
six enacted laws print, in their own status cite, a day they take effect that came before they were read:
Maryland S.B. 937 ("shall take effect July June 1, 2025"; its Effective column 2025-06-01), Maryland H.B. 1532 (sections
"shall take effect July 1, 2026"; Effective "not published") and Minnesota H.F. 16 ("effective the day following final
enactment", signed 14 June 2025; Effective "not published"). Kansas S.B. 98 takes effect on its publication in the
statute book, a day its text does not print. The other choice, those three marked in effect: in effect 10 to 13,
enacted 6 to 3. Default: left as it is.

1. The three laws are enacted and their cites print a day before the read. Passes on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class EnactedLawsWhoseEffectiveDayHadPassed(unittest.TestCase):
    def test_the_three(self):
        with open(os.path.join(ROOT, "site", "data", "siting", "large_load_rules.json"), encoding="utf-8") as f:
            laws = json.load(f)["laws"]
        by = {(l["state"], l["bill"].split(" (")[0]): l for l in laws}
        want = {("MD", "S.B. 937"): "June 1, 2025", ("MD", "H.B. 1532"): "take effect July 1, 2026", ("MN", "H.F. No. 16"): "effective the day following final enactment"}
        for key, words in want.items():
            self.assertIn(key, by)
            self.assertEqual(by[key]["status"], "enacted", key)
            self.assertIn(words, by[key]["status_cite"], key)
            self.assertLess("2026-07-01", by[key]["read"][:10], key)
        self.assertEqual(sum(1 for l in laws if l["status"] == "enacted") - len(want) >= 0, True)


if __name__ == "__main__":
    unittest.main()
