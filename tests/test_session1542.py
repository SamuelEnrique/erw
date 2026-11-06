"""Session 1542 (chain 172), fault 58 of docs/reviews/periodicals-faults-2026-11-05.md: the Digest's chart section
linked its table to /data#<table> when /data does not list the table. The Digests of 22 and 23 October and 6 November
linked eia861m_utility_sales_monthly, eia_padd_rail_barge_movements_monthly and onrr_revenue_monthly, all three in
live_set.yaml's catalogue_hold, so the reader landed at the top of /data. daily_chart.on_data_page reads what /data
lists (the public catalogue: coverage.csv's public tables less catalogue_hold and review_hold), and the line links only
those. Fixtures in a temporary folder, plus the repository's own two files; no network, no model, no table written.
Nothing here sets the environment at import.
"""
import importlib.util
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIND = os.path.join(ROOT, "warehouse", "analysis", "findings")


def module():
    if FIND not in sys.path:
        sys.path.insert(0, FIND)
    spec = importlib.util.spec_from_file_location("daily_chart_1542", os.path.join(FIND, "daily_chart.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


COVERAGE = """# a fixture
table,iso,market,n_nodes,interval,ts_min,ts_max,n_rows,source_report,last_run,validator_status,license,sector,derived,tier
listed_table,,,1,P1M,2020-01-01T00:00:00Z,2026-08-01T00:00:00Z,10,eia:x,2026-11-01T00:00:00Z,pass,public,oil,no,source
held_table,,,1,P1M,2020-01-01T00:00:00Z,2026-08-01T00:00:00Z,10,eia:y,2026-11-01T00:00:00Z,pass,public,oil,no,source
review_table,,,1,P1M,2020-01-01T00:00:00Z,2026-08-01T00:00:00Z,10,eia:z,2026-11-01T00:00:00Z,pass,public,oil,no,source
internal_table,,,1,P1M,2020-01-01T00:00:00Z,2026-08-01T00:00:00Z,10,eia:w,2026-11-01T00:00:00Z,pass,internal,oil,no,source
"""
LIVE = """full:
  - '^listed_table$'
catalogue_hold:
  - held_table
review_hold:
  - review_table
"""


class OnTheDataPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = module()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.meta = cls.tmp.name
        with open(os.path.join(cls.meta, "coverage.csv"), "w", encoding="utf-8") as f:
            f.write(COVERAGE)
        cls.live = os.path.join(cls.meta, "live_set.yaml")
        with open(cls.live, "w", encoding="utf-8") as f:
            f.write(LIVE)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def on(self, t):
        return self.m.on_data_page(t, self.meta, self.live)

    def test_a_listed_public_table(self):
        self.assertTrue(self.on("listed_table"))
        self.assertEqual(self.m.table_words("listed_table", self.meta, self.live), "[the table and its download](/data#listed_table)")

    def test_held_review_internal_and_unknown_are_not_linked(self):
        for t in ("held_table", "review_table", "internal_table", "no_such_table"):
            self.assertFalse(self.on(t), t)
            self.assertEqual(self.m.table_words(t, self.meta, self.live), "not yet among the tables /data lists")

    def test_an_unreadable_live_set_links_nothing(self):
        self.assertFalse(self.m.on_data_page("listed_table", self.meta, os.path.join(self.meta, "missing.yaml")))


class TheRepositorysOwnLists(unittest.TestCase):
    """The three tables the stored Digests linked, and one /data lists, against the repository's live_set.yaml and
    coverage.csv as they are."""

    @classmethod
    def setUpClass(cls):
        cls.m = module()
        if not os.path.exists(os.path.join(cls.m.META_DIR, "coverage.csv")):
            raise unittest.SkipTest("coverage.csv is not in this copy")

    def test_the_three_held_tables(self):
        for t in ("eia861m_utility_sales_monthly", "eia_padd_rail_barge_movements_monthly", "onrr_revenue_monthly"):
            self.assertFalse(self.m.on_data_page(t), t)

    def test_a_listed_table(self):
        self.assertTrue(self.m.on_data_page("eia_fuel_spot_prices"))

    def test_the_line_has_no_dead_anchor(self):
        c = {"fact": "A fact.", "series_key": "entity=onrr_revenue:x|variable=revenue", "table": "onrr_revenue_monthly", "source": "watch", "score": 50}
        lines = self.m.markdown("2026-11-06", c)
        line = next(l for l in lines if l.startswith("Table `") or "Table `onrr_revenue_monthly`" in l)
        self.assertNotIn("/data#onrr_revenue_monthly", line)
        self.assertIn("not yet among the tables /data lists.", line)


if __name__ == "__main__":
    unittest.main()
