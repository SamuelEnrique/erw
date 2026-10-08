"""Session 149, part B: the values check-values reported as differing from Supabase, each fixed at its cause.

Energy Research Warehouse (ERW). No request is made and nothing is written. The rules are read from the source of the
page and of the check, so that the two cannot drift apart again without a test saying so.

    TheCatalogue   the home page counts the public tables that are not held for a page in review (site/lib/data.ts);
                   site/scripts/check-values.mjs asks Supabase the same question for the four figures
    TheDeals       /deals reads the AI tag whatever its case; the check does too
    TheProblemSet  question 5 of "know your grid" takes a day whose hourly demand is held whole, and writes no sum
                   over hours that are not held

    python -m unittest tests.test_session149_checks
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheCatalogue(unittest.TestCase):
    def test_the_page_and_the_check_count_the_same_tables(self):
        self.assertIn('rows.filter((r) => r.license === "public" && r.in_live_set !== "review")', src("site", "lib", "data.ts"))
        check = src("site", "scripts", "check-values.mjs")
        self.assertIn('const SEEN = { license: "eq.public", in_live_set: "neq.review" };', check)
        block = check[check.index('if (p[0] === "catalogue")'):check.index('if (p[0] === "latest_prices")')]
        for what in ("count", "n_pass", "sum_n_rows", "max_last_run"):
            line = next(ln for ln in block.splitlines() if f'p[1] === "{what}"' in ln)
            self.assertIn("...SEEN", line, what)
        self.assertEqual(len(re.findall(r'license: "eq\.public"', block)), 1)   # only inside SEEN: no figure counts every public row


class TheDeals(unittest.TestCase):
    def test_the_tag_is_read_whatever_its_case_on_the_page_and_in_the_check(self):
        self.assertIn('String(x.ai_power ?? "").toLowerCase() === "true"', src("site", "app", "deals", "page.tsx"))
        check = src("site", "scripts", "check-values.mjs")
        self.assertIn('m.filter((r) => String(r.ai ?? "").toLowerCase() === "true")', check)
        self.assertNotIn('r.ai === "true"', check)


class TheProblemSet(unittest.TestCase):
    def test_question_five_needs_a_whole_day_of_demand(self):
        p = src("site", "lib", "problems.ts")
        self.assertIn("whole: new Set(rows.map((r) => Date.parse(r.ts_utc))).size === (b - a) / 3_600_000", p)
        self.assertIn("const d5 = eDays.find((d) => localDay(d).whole);", p)
        self.assertIn("Not held yet: no day of the batteries' table has every hour of ERCOT's demand in the live set.", p)
        self.assertEqual(len(re.findall(r'id: "a5"', p)), 1)           # one question 5, with or without its day
        # the sum's own window is the one the check recomputes: the same two instants in the key and in the filter
        self.assertIn("k: `series_sum|${D}|demand_mw|${iso(m0)}|${iso(m1)}|${E}`", p)

    def test_no_em_dash(self):
        for parts in (("site", "lib", "problems.ts"), ("site", "scripts", "check-values.mjs"), ("tests", "test_session149_checks.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
