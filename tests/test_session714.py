"""Session 714: the All grids tab at 390 pixels, for the keyboard and for a screen reader. Every tip of the tab is in
a role="tooltip" span the site's rule shows on hover and on focus (app/tokens.css, ".tip"), not in `title`, which a
keyboard never shows; the node list's headings carry theirs by aria-describedby; the defaults' sources are the shared
Tip; the box folds on a phone once loaded; the tables scroll in their own focusable region. No request, no model call."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Tips(unittest.TestCase):
    def test_no_title_tip_left_in_the_tab(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertEqual(re.findall(r" title=", v), [" title="])   # InputPanel's heading, not a tip
        self.assertIn('<InputPanel title="Your load">', v)
        for f in ("AllGridsNodes.tsx", "AllGridsForm.tsx"):
            self.assertNotIn(" title=", src("site", "app", "cost-of-power", f), f)

    def test_the_tip_is_the_site_s_rule(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn('<span role="tooltip" className="absolute right-0 top-full z-20 hidden', v)
        self.assertIn("tip relative inline-block", v)
        css = src("site", "app", "tokens.css")
        self.assertIn('.brand-a .tip:focus-within [role="tooltip"]', css)
        n = src("site", "app", "cost-of-power", "AllGridsNodes.tsx")
        self.assertIn("aria-describedby={`${uid}-${k}`}", n)
        self.assertIn('role="columnheader"', n)

    def test_the_defaults_sources_are_the_shared_tip(self):
        f = src("site", "app", "cost-of-power", "AllGridsForm.tsx")
        for k in ('id="ag-mw"', 'id="ag-lf"', 'id="ag-strike"'):
            self.assertIn(k, f)

    def test_the_box_folds_on_a_phone_and_the_tables_scroll_in_place(self):
        f = src("site", "app", "cost-of-power", "AllGridsForm.tsx")
        self.assertIn('window.matchMedia("(max-width: 1023px)").matches', f)
        self.assertIn("<details open={open}", f)
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn('className="overflow-x-auto" role="region" aria-label="All grids" tabIndex={0}', v)


if __name__ == "__main__":
    unittest.main()
