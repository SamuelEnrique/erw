"""Session 1016 (chain 070): the brand pass on the data pages. The pages already follow docs/brand.md; the one fault was
this chain's own: the code of /data's "In your tools" column fell under the brand's rule for small words in a cell and
was set in the sans. A narrower rule in tokens.css keeps it in the mono face. No request, no model call."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Brand(unittest.TestCase):
    def test_the_column_s_code_is_mono(self):
        css = src("site", "app", "tokens.css")
        rule = ".brand-a tbody td[data-tool-lines] pre {\n  font-family: var(--font-mono);\n}"
        self.assertIn(rule, css)
        self.assertGreater(css.index(rule), css.index(".brand-a tbody td .text-xs,"))   # after the rule it narrows
        self.assertIn("data-tool-lines={r.table_name}", src("site", "app", "data", "page.tsx"))


if __name__ == "__main__":
    unittest.main()
