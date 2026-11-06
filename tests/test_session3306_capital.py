"""Session 3306 (chain 200): /deals/capital, capital flows' first view (warehouse/derived/capital_page.py).

Energy Research Warehouse (ERW). The committed file (site/data/capital.json) holds nothing of a held row; the
computation on deals written here (test fixtures, not the warehouse's): the quarters, the USD summed only where stated,
the rows without USD counted apart, the counterparty's kind, the twenty largest. No network, no lock.

    python -m unittest tests.test_session3306_capital -v
"""

import json
import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import capital_page as K  # noqa: E402


def deals():
    rows = [
        dict(event_id="deal:1", event_date="2026-01-10T00:00:00Z", deal_type="m_and_a", buyer="Alpha Capital", seller="Beta Power",
             asset="", technology="gas", dollars="1000000000", mw="500", story_urls="https://x/1;https://x/2"),
        dict(event_id="deal:2", event_date="2026-02-01T00:00:00Z", deal_type="debt", buyer="", seller="Gamma Solar",
             asset="", technology="solar", dollars="", mw="", story_urls="https://x/3"),
        dict(event_id="deal:3", event_date="2026-04-02T00:00:00Z", deal_type="equity_raise", buyer="Alpha Capital", seller="Delta",
             asset="", technology="", dollars="250000000", mw="", story_urls=""),
        dict(event_id="deal:4", event_date="2026-04-03T00:00:00Z", deal_type="ppa", buyer="Epsilon", seller="Zeta",
             asset="", technology="wind", dollars="999", mw="100", story_urls=""),
    ]
    return pd.DataFrame(rows)


def links():
    return pd.DataFrame([dict(input_table="energy_deals", role="buyer", input_row="deal:1", company_id="company:alpha-capital"),
                         dict(input_table="energy_deals", role="buyer", input_row="deal:3", company_id="company:alpha-capital")])


def directory():
    return pd.DataFrame([dict(entity_id="company:alpha-capital", kind="lender or investor")])


class Compute(unittest.TestCase):
    def setUp(self):
        self.d = K.compute(deals(), links(), directory())

    def test_only_capital_rows(self):
        self.assertEqual(self.d["total"]["rows"], 3)          # the PPA is not capital
        self.assertEqual(self.d["total"]["usd"], 1250000000)
        self.assertEqual(self.d["total"]["no_usd"], 1)
        self.assertEqual(self.d["disclosed_share"], round(2 / 3, 4))

    def test_quarters(self):
        q = {x["quarter"]: x for x in self.d["quarters"]}
        self.assertEqual(sorted(q), ["2026Q1", "2026Q2"])
        self.assertEqual(q["2026Q1"]["m_and_a"]["usd"], 1000000000)
        self.assertEqual(q["2026Q1"]["debt"]["no_usd"], 1)
        self.assertNotIn("debt", q["2026Q2"])

    def test_kinds_and_segments(self):
        k = {x["kind"]: x for x in self.d["kinds"]}
        self.assertEqual(k["lender or investor"]["rows"], 2)
        self.assertEqual(k["not named"]["rows"], 1)
        s = {x["segment"]: x for x in self.d["segments"]}
        self.assertEqual(s["gas"]["mw"], 500.0)
        self.assertEqual(s["not stated"]["usd"], 250000000)

    def test_largest_with_sources(self):
        self.assertEqual([x["event_id"] for x in self.d["largest"]], ["deal:1", "deal:3"])   # no USD, not listed
        self.assertEqual(self.d["largest"][0]["sources"], ["https://x/1", "https://x/2"])


class TheHold(unittest.TestCase):
    def test_a_held_table_writes_its_count_only(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "energy_deals.csv")
            with open(src, "w", encoding="utf-8", newline="") as f:
                f.write("# a test table\n")
                deals().to_csv(f, index=False)
            out = os.path.join(d, "capital.json")
            doc = K.build(d, out, lic={"energy_deals": "internal"})
            self.assertEqual(set(doc), {"built", "table", "n_rows", "method", "held"})
            self.assertTrue(doc["held"])
            self.assertEqual(doc["n_rows"], 4)

    def test_the_committed_file(self):
        p = os.path.join(ROOT, "site", "data", "capital.json")
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
        if doc["held"]:
            self.assertEqual(set(doc), {"built", "table", "n_rows", "method", "held"})
        else:
            self.assertIn("largest", doc)


if __name__ == "__main__":
    unittest.main()
