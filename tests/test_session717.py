"""Session 717: the lab's path walked (docs/reviews/siting-path.md) and its three mends: the sorted column drawn first,
the line of the nodes' shared figures as one sentence with its keys, the node list's header without a band. No request,
no model call."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Path(unittest.TestCase):
    def test_the_walk_is_written(self):
        p = src("docs", "reviews", "siting-path.md")
        self.assertEqual(p.count("\n| "), 11 + 0)   # the header row and ten steps (the separator starts with "|---")
        for q in range(1, 11):
            self.assertIn(f"\n{q}. **", p)
        self.assertIn("deep-research-report.md", p)
        self.assertNotIn(chr(0x2014), p)

    def test_the_sorted_column_is_drawn_first(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn('const cols = x.sort === "name" ? COLUMNS : [...COLUMNS.filter((c) => c.id === x.sort), ...COLUMNS.filter((c) => c.id !== x.sort)];', v)
        self.assertEqual(v.count("cols.map("), 2)

    def test_the_shared_line_keeps_its_keys(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        for k in ("check={`allgrids|tx|${hub.id}|${k}`}", "check={`allgrids|connect|${hub.id}`}", "check={`allgrids|demand|${hub.id}`}", "check={`allgrids|carbon|${hub.id}`}"):
            self.assertIn(k, v)

    def test_the_node_header_has_no_band(self):
        css = src("site", "app", "tokens.css")
        self.assertIn('.brand-a [data-allgrids-nodes] [role="table"] > [role="row"]:first-child {', css)
        self.assertEqual(css.count("{"), css.count("}"))


if __name__ == "__main__":
    unittest.main()
