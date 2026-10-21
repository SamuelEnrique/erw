"""Session 401: the five tool pages through the installed design tools (docs/reviews/tooling-pass-2026-10-20.md).

Impeccable, UI/UX Pro Max, frontend-design, the Vercel web-design-guidelines and react-best-practices, and AccessLint
were run on /cost-of-power/battery, /cost-of-power/seller, /cost-of-power, /research and /grid. The fixes that need no
ruling within docs/brand.md were made in the pages' own files only (shared components are session 412's): a 24 px
target for the folds' summaries, the Reset links, the income table's two buttons and the research page index; 12 px
for the grids view's tier tag (it was 10, the brand's floor is 12) and square corners; header cells with their scope;
the window's two selects named from their visible word; the pasted profile at 16 px on a phone; no browser suggestions
on number fields; "(picked)" out of cardinal. No figure moved: 1,646 checked figures read before and after, at 1280
and 390 px, are the same (docs/brand/review-401/). These tests hold the fixes and the two documents in place.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
APP = os.path.join(ROOT, "site", "app")
REVIEW = os.path.join(ROOT, "docs", "reviews", "tooling-pass-2026-10-20.md")
TOOLING = os.path.join(ROOT, "docs", "tooling.md")
SHOTS = os.path.join(ROOT, "docs", "brand", "review-401")
PAGES = ("battery", "seller", "cost-of-power", "cost-of-power-grids", "research", "grid")


def src(*p):
    with open(os.path.join(APP, *p), encoding="utf-8") as f:
        return f.read()


class TheFixes(unittest.TestCase):
    def test_no_text_under_the_brands_floor_in_the_grids_view(self):
        gv = src("cost-of-power", "GridsView.tsx")
        self.assertNotRegex(gv, r"text-\[1[01]px\]")
        self.assertNotIn(" rounded ", gv)
        self.assertIn("inline-flex min-h-6 items-center border border-rule px-1 text-xs text-muted no-underline", gv)
        self.assertNotIn(" rounded ", src("cost-of-power", "charts.tsx"))

    def test_hand_written_tables_name_their_header_cells(self):
        for parts in (("cost-of-power", "GridsView.tsx"), ("cost-of-power", "charts.tsx"), ("research", "page.tsx")):
            s = src(*parts)
            bare = [m.group(0) for m in re.finditer(r"<th(?=[\s>])(?![^>]*scope=)[^>]*>", s)]
            self.assertEqual(bare, [], parts)
            self.assertIn('<th scope="row"', s, parts)
            self.assertNotIn("scope=\"col\"ead", s, parts)

    def test_the_folds_and_small_controls_are_24_px_targets(self):
        for parts in (("cost-of-power", "page.tsx"), ("cost-of-power", "LoadAnswers.tsx"), ("cost-of-power", "battery", "page.tsx"), ("cost-of-power", "seller", "page.tsx")):
            s = src(*parts)
            self.assertNotIn('<summary className="cursor-pointer">', s, parts)
            self.assertIn('<summary className="cursor-pointer py-1">', s, parts)
        self.assertIn('<summary className="cursor-pointer py-1 text-accent">', src("grid", "page.tsx"))
        self.assertIn('<summary className="cursor-pointer py-1">Citations</summary>', src("research", "view.tsx"))
        self.assertIn('className="inline-block py-1 text-xs">Reset</Link>', src("cost-of-power", "LoadForm.tsx"))
        self.assertIn("`px-2.5 py-1 ", src("cost-of-power", "battery", "Income.tsx"))
        self.assertEqual(src("research", "page.tsx").count('<a className="inline-block py-0.5" href="#'), 5)

    def test_a_name_starts_with_the_word_on_screen(self):
        inc = src("cost-of-power", "battery", "Income.tsx")
        self.assertIn('aria-label="From: your window\'s first year"', inc)
        self.assertIn('aria-label="to: your window\'s last year"', inc)
        self.assertIn('data-window-from="1"', inc)   # test_session296 reads these
        self.assertIn('data-window-to="1"', inc)

    def test_the_pasted_profile_is_16_px_on_a_phone_and_announced(self):
        sp = src("cost-of-power", "seller", "SellerProfile.tsx")
        self.assertIn("font-mono text-base sm:text-xs sm:leading-normal", sp)
        self.assertIn('aria-live="polite"', sp)

    def test_number_fields_ask_for_no_browser_suggestion(self):
        for parts, n in ((("cost-of-power", "LoadForm.tsx"), 4), (("cost-of-power", "battery", "BatteryForm.tsx"), 1), (("cost-of-power", "seller", "SellerForm.tsx"), 5), (("cost-of-power", "charts.tsx"), 3)):
            s = src(*parts)
            fields = re.findall(r'<input[^>]*type="number"[^>]*>', s)
            self.assertGreaterEqual(len(fields), n, parts)
            self.assertTrue(all('autoComplete="off"' in f for f in fields), parts)

    def test_cardinal_is_not_a_status_word(self):
        self.assertNotIn('<strong className="text-accent"> (picked)</strong>', src("research", "page.tsx"))
        self.assertIn("<strong> (picked)</strong>", src("research", "page.tsx"))


class TheDocuments(unittest.TestCase):
    def test_the_review_names_every_tool_and_every_page(self):
        with open(REVIEW, encoding="utf-8") as f:
            r = f.read()
        for tool in ("Impeccable", "UI/UX Pro Max", "frontend-design", "web-design-guidelines", "react-best-practices", "AccessLint"):
            self.assertIn(tool, r)
        for page in ("/cost-of-power/battery", "/cost-of-power/seller", "/cost-of-power", "/research", "/grid"):
            self.assertIn(page, r)
        for part in ("## Fixed", "## For Samuel's ruling", "## For session 412"):
            self.assertIn(part, r)
        self.assertNotIn(chr(0x2014), r)

    def test_tooling_gives_each_tools_first_use(self):
        with open(TOOLING, encoding="utf-8") as f:
            t = f.read()
        self.assertIn("## First use of each tool", t)
        block = t.split("## First use of each tool")[1].split("\n## ")[0]
        for tool in ("Impeccable", "UI/UX Pro Max", "frontend-design", "web-design-guidelines", "react-best-practices", "chrome-devtools-mcp", "AccessLint"):
            self.assertRegex(block, rf"\| {re.escape(tool)} \| 12 October 2026, session 201 \|")
        self.assertNotIn(chr(0x2014), t)

    def test_the_shots_before_and_after_at_both_widths(self):
        for page in PAGES:
            for w in (1280, 390):
                for stage in ("before", "after"):
                    self.assertTrue(os.path.exists(os.path.join(SHOTS, f"{page}_{w}_{stage}.png")), (page, w, stage))


if __name__ == "__main__":
    unittest.main()
