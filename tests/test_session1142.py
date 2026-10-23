"""Session 1142 (chain 085, chain 076's session 1127): a grid's chat reads the tables whose rows are the grid's as
iso:<slug> (session 1114's f06: ERCOT's chat could not read storage_buildout_monthly and rebuilt a year's change from a
snapshot). Held here: the rule file (warehouse/chat/grid_tables.py) asks for the rule after the entity and ba rules, so a
table either admits keeps its rule; docs/grids/grid_tables.json, written by it on 23 October 2026, admits
storage_buildout_monthly for every grid by the new rule and loses no table; the Python tools keep such a table's rows to
the grid's own entity, and the site's scope filter does the same. No network, no model. Nothing here sets the
environment at import.
"""
import json
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAT = os.path.join(ROOT, "warehouse", "chat")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheIsoEntityRule(unittest.TestCase):
    def test_the_rule_comes_after_entity_and_ba(self):
        s = src("warehouse", "chat", "grid_tables.py")
        self.assertIn('RULES = ("name", "entity", "ba", "isoentity", "queue", "iso")', s)
        self.assertLess(s.index('return "ba"'), s.index('return "isoentity"'))

    def test_the_file_admits_the_storage_buildout_for_every_grid(self):
        grids = json.loads(src("docs", "grids", "grid_tables.json"))["grids"]
        self.assertEqual(len(grids), 7)
        for slug, g in grids.items():
            self.assertIn("storage_buildout_monthly", g["tables"], slug)
            self.assertEqual(g["by"]["storage_buildout_monthly"], "isoentity", slug)

    def test_the_tools_keep_the_grids_own_rows(self):
        if CHAT not in sys.path:
            sys.path.insert(0, CHAT)
        import tools  # noqa: E402
        saved = tools.SCOPE
        tools.SCOPE = {"slug": "ercot", "ba": "ERCO", "iso": "ERCOT", "by": {"storage_buildout_monthly": "isoentity"}}
        try:
            df = pd.DataFrame({"entity": ["iso:ercot", "iso:caiso", "iso:ercot_x", None], "value": [1, 2, 3, 4]})
            got = tools.scope_rows("storage_buildout_monthly", df)
        finally:
            tools.SCOPE = saved
        self.assertEqual(list(got["value"]), [1])
        self.assertIn('if (by === "isoentity" && shape === "series") return { entity: `eq.iso:${scope.slug}` };', src("site", "lib", "chat", "tools.ts"))


class ThePagesTables(unittest.TestCase):
    def test_the_model_is_told_which_table_stands_behind_each_page(self):
        # session 1114's f08: asked "on the generator page's rule", the CAISO chat read battery_stack_monthly
        spec = json.loads(src("site", "lib", "chat", "spec.json"))
        rule = "the generator page (/cost-of-power/seller) reads merchant_revenue_monthly, whose battery rows (battery_4h_revenue_per_mw and its kin) are the generator page's rule for a battery"
        self.assertIn(rule, spec["system"])
        self.assertIn("the battery page (/cost-of-power/battery) reads battery_stack_monthly", spec["system"])
        self.assertIn("the datacenter page (/cost-of-power) reads cost_of_power_monthly", spec["system"])


if __name__ == "__main__":
    unittest.main()
