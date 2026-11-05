"""Session 794 (chain 065): two ERCOT nodes as A and B: their monthly bases on one chart and in a table, each month keyed
(allgrids|nodemonth), and B less A for the basis spread and the intraday swing (allgrids|nodediff); sitingStat answers
both kinds, so check-values recomputes them. No request, no model call."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Pair(unittest.TestCase):
    def test_the_panel_draws_two_nodes(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn('ra?.kind === "node" && rb?.kind === "node" ? <NodePair a={ra} b={rb} />', v)
        self.assertIn("check={`allgrids|nodemonth|${r.id}|${m}`}", v)
        self.assertIn("check={`allgrids|nodediff|${a.id}|${b.id}|spread`}", v)
        self.assertIn("<LineChart", v)

    def test_sitingStat_answers_both(self):
        s = src("site", "lib", "siting.ts")
        self.assertIn('if (p[1] === "nodemonth")', s)
        self.assertIn('if (p[1] === "nodediff")', s)
        self.assertIn('"/cost-of-power?view=allgrids&a=ercot%3ABBREEZE_1_2&b=ercot%3APALACIOS_RN"', src("site", "scripts", "check-values.mjs"))


if __name__ == "__main__":
    unittest.main()
