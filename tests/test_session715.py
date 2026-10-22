"""Session 715: the All grids tab to the brand (docs/brand.md), in app/tokens.css and the shared components only:
words in a figure's cell and every tip in sans, the tip at captions size, a column head's tip rule visible on the white
header. Every rule is closed. No request, no model call."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Brand(unittest.TestCase):
    def test_the_tab_s_rules_are_in_tokens_css(self):
        css = src("site", "app", "tokens.css")
        block = css[css.index("/* session 715 (chain 050)"):]
        for sel in ("[data-allgrids] tbody td.text-right [data-cell-words]", '[data-allgrids] [role="tooltip"]', "[data-allgrids] thead .tip"):
            self.assertIn(sel, block)
        self.assertIn("font-family: var(--font-sans);", block)
        self.assertEqual(block.count("{"), block.count("}"))
        self.assertEqual(css.count("{"), css.count("}"))

    def test_no_style_of_its_own_in_the_tab(self):
        for f in ("AllGridsView.tsx", "AllGridsForm.tsx", "AllGridsNodes.tsx"):
            s = src("site", "app", "cost-of-power", f)
            self.assertNotIn("#", "".join(c for c in s.split("style={{")[1:] if "color" in c), f)   # no hex color in a style
            self.assertNotIn("font-family", s, f)


if __name__ == "__main__":
    unittest.main()
