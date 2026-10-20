"""Session 346: the tax side of the economic impact tool, impact_tax_rules.

Energy Research Warehouse (ERW). The table is read where this machine holds it; the builder's rows are also made in
memory from site/data/severance_rules.json, which is in git, so the rule tests run everywhere.

    python -m unittest tests.test_session346 -v
"""

import json
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import impact_tax_rules as tr  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output", "impact_tax_rules.csv")


class TheRows(unittest.TestCase):
    def setUp(self):
        d = json.load(open(tr.RULES, encoding="utf-8"))
        self.sev = tr.severance_rows(d)
        self.prop = tr.property_rows()

    def test_every_held_rule_keeps_its_page_and_sentence(self):
        for r in self.sev:
            self.assertEqual(r["status"], "held")
            self.assertTrue(r["source_url"].startswith("http"), r["event_id"])
            self.assertTrue(r["x_quote"], r["event_id"])

    def test_no_rule_held_states_no_figure(self):
        self.assertEqual({r["x_state"] for r in self.prop}, {"TX", "LA", "NM"})
        self.assertEqual({r["x_rule"] for r in self.prop}, {
            "tx_property_general", "tx_chapter_312", "tx_chapter_313", "la_property_general", "la_itep",
            "nm_property_general", "nm_irb"})
        for r in self.prop:
            self.assertEqual(r["status"], "no_rule_held")
            self.assertEqual((r["x_rate"], r["x_per_unit"], r["x_quote"]), ("", "", ""))
            self.assertIn("No rule held", r["x_note"])

    def test_a_date_in_words_falls_back_to_the_day_it_was_read(self):
        fee = [r for r in self.sev if r["x_rule"] == "tx_oil_fee"][0]
        self.assertEqual(fee["event_date"], tr.READ_ON)
        self.assertIn("report periods September 2015", fee["x_effective_text"])
        oil = [r for r in self.sev if r["x_rule"] == "tx_oil"][0]
        self.assertEqual(oil["event_date"], "1951-09-01")

    def test_a_rate_per_unit_names_its_unit(self):
        gas = [r for r in self.sev if r["x_rule"] == "la_gas"][0]
        self.assertEqual((gas["x_basis"], gas["x_unit"]), ("per_unit", "Mcf"))

    def test_severance_applies_to_none_of_the_tools_technologies(self):
        for r in self.sev:
            self.assertIn("none of the economic impact tool's technologies", r["x_applies_to"])


class TheTable(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(OUT):
            self.skipTest("impact_tax_rules is not on this machine")
        self.d = pd.read_csv(OUT, comment="#", keep_default_na=False)

    def test_the_counts(self):
        self.assertEqual(len(self.d), 49)
        self.assertEqual(self.d.status.value_counts().to_dict(), {"held": 42, "no_rule_held": 7})
        self.assertFalse(self.d.event_id.duplicated().any())


if __name__ == "__main__":
    unittest.main()
