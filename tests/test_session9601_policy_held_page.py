"""Session 9601 (chain 620, 20 November 2026): /policy keeps its heading and its views when its list is held.

Energy Research Warehouse (ERW). The first minute of the site, read in a browser: the menu's "Policy" (Analysis)
opened a page that showed the two words "license needed" and nothing else: no heading, no views, no link. The list of
every action is held for one publisher's permission (the hover names it); the page returned the held mark alone. Its
other views (`/policy?view=week`, the monitor) draw, and could not be reached from it.

Held here, on the source: when the list cannot be drawn the page still has its heading and its views, and the reason
stands where the list would have been; nothing of the held list is drawn (the same mark, the same reason, no row);
the mark itself and the hold are as they were. Nothing here sets the environment, reads a table or makes a request.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ThePage(unittest.TestCase):
    def setUp(self):
        self.p = src("site", "app", "policy", "page.tsx")
        m = re.search(r"if \(!a\.ok\) return \(([\s\S]*?)\n  \);", self.p)
        self.assertIsNotNone(m, "the branch for a list that cannot be drawn")
        self.branch = m.group(1)

    def test_the_heading_and_the_views_stay(self):
        self.assertIn('<h1 className="mb-1 text-3xl">Policy</h1>', self.branch)
        self.assertIn("<Views view={view} />", self.branch)
        self.assertIn('data-policy="not-drawn"', self.branch)

    def test_the_reason_stands_where_the_list_would_be_and_nothing_held_is_drawn(self):
        self.assertIn('<NoData what="policy actions" reason={a.reason} />', self.branch)
        self.assertNotIn("a.data", self.branch)
        self.assertNotIn("rows", self.branch)

    def test_the_page_is_never_the_mark_alone(self):
        self.assertNotIn('return <Brand><NoData what="policy actions" reason={a.reason} /></Brand>;', self.p)

    def test_the_mark_and_the_hold_are_as_they_were(self):
        n = src("site", "components", "NoData.tsx")
        self.assertIn('<span className="text-muted" role="status" data-license-held={what ?? ""} title={reason.slice(LICENSE_REASON.length)}>{LICENSE_NEEDED}</span>', n)

    def test_the_views_are_the_three(self):
        w = src("site", "lib", "policyweek.ts")
        self.assertIn('export const VIEWS = [["all", "Every action, scored"], ["week", "What changed this week"], ["monitor", "The monitor"]] as const;', w)

    def test_no_em_dash(self):
        self.assertNotIn(EM, self.p)
        self.assertNotIn(EM, src("tests", "test_session9601_policy_held_page.py"))


if __name__ == "__main__":
    unittest.main()
