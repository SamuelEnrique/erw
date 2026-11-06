"""Session 1715 (chain 191): a scrolling box's run-time name takes its fold's heading, not the fold's whole summary.
site/components/ScrollRegions.tsx's regionName asked for the first of "h2, h3, summary"; a selector list returns the
first match in the page's order, and a fold's <summary> comes before the <h2> inside it, so /board's region was named
"Capacity and equities2 rows" (the heading and its row count run together; session 1694 read it in a browser). The
heading is now asked for first and the summary only where the fold has none. Source reading only. Nothing here sets
the environment at import.
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src():
    with open(os.path.join(ROOT, "site", "components", "ScrollRegions.tsx"), encoding="utf-8") as f:
        return f.read()


class TheRegionName(unittest.TestCase):
    def test_a_heading_before_the_summary(self):
        s = src()
        self.assertIn('const box = el.closest("section, details");', s)
        self.assertIn('const heading = pick(box?.querySelector("h2, h3") ?? box?.querySelector("summary"));', s)
        self.assertNotIn('querySelector("h2, h3, summary")', s)

    def test_the_order_of_names_is_kept(self):
        s = src()
        body = s[s.index("export function regionName"):s.index("export function markScrollers")]
        self.assertLess(body.index("caption"), body.index("figcaption"))
        self.assertLess(body.index("figcaption"), body.index("const heading"))
        self.assertIn('return el.tagName === "PRE" ? "Code" : "Table";', body)


if __name__ == "__main__":
    unittest.main()
