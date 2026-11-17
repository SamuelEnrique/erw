"""Session 7624: the other choice of the ruling on small cells on /attention (branch wip/alt-attention-1, not landed). A
cell of a sector, a place and a week with fewer than ten stories prints its counts and no Friction Index; every index
was printed until now, its counts beside it (Virginia's datacenters read 75.00 from 3 of 4 stories).

What is held to:
  on the page's own file (site/data/attention.json, built 16 November 2026), 363 of the 461 cells' indices go (78.7
    percent), every one a state's cell; of them 293 read 0, 26 read 100 and 18 read 50; no cell of all places has
    fewer than ten stories;
  the view applies the rule in the headline (counts only), the line chart (no point, the hover gives the counts), the
    map (the state is not colored on the Friction Index), its hover and its table; the Attention Index is untouched.

No request, no model call."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class SmallCellsPrintCounts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "site", "data", "attention.json"), encoding="utf-8") as f:
            cls.f = json.load(f)
        with open(os.path.join(ROOT, "site", "app", "attention", "AttentionView.tsx"), encoding="utf-8") as f:
            cls.v = f.read()

    def test_the_cells_that_go(self):
        cells = self.f["cells"]
        few = [c for c in cells if c[3] < 10]
        self.assertEqual((len(cells), len(few)), (461, 363))
        self.assertEqual(f"{100 * len(few) / len(cells):.1f}", "78.7")
        geos = self.f["geos"]
        self.assertTrue(all(geos[c[1]].startswith("US-") for c in few))
        vals = [round(c[6], 2) for c in few]
        self.assertEqual((vals.count(0), vals.count(100), vals.count(50)), (293, 26, 18))

    def test_the_view_applies_the_rule(self):
        v = self.v
        self.assertIn("export const MIN_STORIES = 10;", v)
        self.assertIn("fri.push(c && !few(c) ? c.friction : null)", v)
        self.assertIn('if (c && (measure === "attention" || !few(c))) out.push(', v)
        self.assertIn('few(cell) ? <span data-friction-counts-only="1">{countsOnly(cell)}</span>', v)
        self.assertIn("fewer than ${MIN_STORIES} stories, no Friction Index", v)
        self.assertIn('few(r.cell) ? <span key="f" data-friction-counts-only="1">', v)
        self.assertIn("att.push(c ? c.attention : null)", v)
        self.assertNotIn(chr(0x2014), v)


if __name__ == "__main__":
    unittest.main()
