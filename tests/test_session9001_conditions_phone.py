"""Session 9001, chain 601 part H, row H4: /conditions with two operators in one of the nine events
(/conditions?a=caiso&event=caiso_heat_2022&b=spp) scrolled sideways at 390 px on production: the page was 619 px wide.
The two operators are grid items, and a grid item does not shrink below its content's minimum, so the heat wave's
table of 47 notices widened the whole column. The column now carries min-w-0 and the table scrolls in its own frame;
with that style put on production's page in a browser the page measured 390 px of 390.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheColumnShrinksToThePhone(unittest.TestCase):
    def test_each_operator_column_may_shrink_below_its_content(self):
        with open(os.path.join(ROOT, "site", "app", "conditions", "page.tsx"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('<div className="min-w-0" data-operator={f.op} data-tag={tag}>', s)
        self.assertIn('<div className={ops.length > 1 ? "grid gap-6 lg:grid-cols-2" : ""}>', s)


if __name__ == "__main__":
    unittest.main()
