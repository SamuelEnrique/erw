"""Session 541: the brand rules session 401 found broken, the items docs/brand.md already decides.

Of session 401's "For Samuel's ruling" (archive/sessions/SESSION_401_REPORT.md), the chain of 21 October named four
for this session, each to be made only where docs/brand.md decides it:

- Research's three empty-state lines began in lower case. Brand section 1: "Labels are in sentence case." Made.
- "Reset" on Your load did not say what it resets. Brand section 7: "can be put back with one press, named for its
  field ("Reset capital cost")". Made: "Reset your load", the 24 px target unchanged.
- "Method note" names two links on the datacenter page, and the battery's box "Assumptions" sits over a fold also called
  "Assumptions". docs/brand.md has no rule on a link's name or on a title repeated by the fold under it (both
  datacenter links go to the one address, /data/methods/datacenter_cost), so both stay on the ruling list, unchanged.

No figure moved: every checked figure of /research and /cost-of-power read before and after at 1280 and 390 px is the
same (docs/brand/review-541/, the report).
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
APP = os.path.join(ROOT, "site", "app")
SHOTS = os.path.join(ROOT, "docs", "brand", "review-541")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_541_REPORT.md")
BRAND = os.path.join(ROOT, "docs", "brand.md")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def src(*p):
    return read(os.path.join(APP, *p))


class TheBrandsOwnRules(unittest.TestCase):
    def test_the_brand_still_says_what_the_fixes_rest_on(self):
        b = read(BRAND)
        self.assertIn("Labels are in sentence case.", b)
        self.assertIn('can be put back with one press, named for its field ("Reset capital cost")', b)

    def test_research_empty_lines_begin_with_a_capital(self):
        s = src("research", "page.tsx")
        for line in ("No card yet: no finding has run", "No daily chart is held yet", "No week has been analysed yet"):
            self.assertIn(">" + line, s)
        for line in ("no card yet", "no daily chart is held", "no week has been analysed"):
            self.assertNotIn(">" + line, s)
        # no paragraph of the page's own text opens on a lower-case letter
        self.assertEqual(re.findall(r'<p className="[^"]*"(?: data-[a-z-]+="[^"]*")*>([a-z])', s), [])

    def test_the_load_reset_names_what_it_puts_back(self):
        s = src("cost-of-power", "LoadForm.tsx")
        self.assertIn('className="inline-block py-1 text-xs" data-load-reset="1">Reset your load</Link>', s)
        self.assertNotIn(">Reset</Link>", s)
        # it puts back the same five values it did
        self.assertIn('hrefOf(x, { mw: DEFAULTS.mw, run: "flat", buy: "rt", gpu: DEFAULTS.gpu, pue: DEFAULTS.pue })', s)

    def test_no_em_dash_in_the_changed_files(self):
        dash = chr(0x2014)
        for parts in (("research", "page.tsx"), ("cost-of-power", "LoadForm.tsx")):
            self.assertNotIn(dash, src(*parts), parts)
        self.assertNotIn(dash, read(os.path.join(SHOTS, "shots-541.mjs")))
        self.assertNotIn(dash, read(os.path.abspath(__file__)))


class TheRecord(unittest.TestCase):
    def test_shots_before_and_after_at_both_widths(self):
        for name in ("research-library", "research-archive", "cost-of-power-load"):
            for width in (1280, 390):
                for stage in ("before", "after"):
                    self.assertTrue(os.path.isfile(os.path.join(SHOTS, f"{name}_{width}_{stage}.png")), (name, width, stage))

    def test_the_report_quotes_the_rules_and_keeps_two_items_for_a_ruling(self):
        if not os.path.isfile(REPORT):
            self.skipTest("the report is written at the end of the session")
        r = read(REPORT)
        self.assertNotIn(chr(0x2014), r)
        self.assertIn("Labels are in sentence case.", r)
        self.assertIn("named for its field", r)
        ruling = r.split("## For Samuel's ruling", 1)[1].split("\n## ", 1)[0]
        self.assertIn("Method note", ruling)
        self.assertIn("Assumptions", ruling)


if __name__ == "__main__":
    unittest.main()
