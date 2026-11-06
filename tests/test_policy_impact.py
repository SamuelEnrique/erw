"""Session 3058 (chain 166): the impact read of a policy action (warehouse/policy/impact.py). No model is called here:
the map to the warehouse's tables is graded on the 30 actions of tests/fixtures/policy/actions_3056.json against the
tables written from their texts (impact_tables_3058.json), and the check a model's clause must pass is tested on
clauses that pass and clauses that must not.

    .venv/Scripts/python.exe -m pytest -q tests/test_policy_impact.py
"""

import csv
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "policy"))
import impact as I  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "policy")


class TheMap(unittest.TestCase):
    def test_the_map_names_the_table_written_from_each_text(self):
        with open(os.path.join(FIX, "impact_tables_3058.json"), encoding="utf-8") as f:
            want = json.load(f)["tables"]
        with open(os.path.join(FIX, "actions_3056.json"), encoding="utf-8") as f:
            items = json.load(f)["items"]
        got = [(it["r"], I.bears_on(row, text)[0]) for it, (row, text) in zip(items, I.read_items(os.path.join(FIX, "actions_3056.json")))]
        bad = [(r, t, want[str(r)]) for r, t in got if t != want[str(r)]]
        print(f"\npolicy impact map on 30 stored actions: {30 - len(bad)} of 30")
        self.assertEqual(bad, [])

    def test_every_table_of_the_map_is_a_table_of_the_warehouse(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8") as f:
            tables = {r["table"] for r in csv.DictReader(f)}
        self.assertEqual([t for t, _ in I.TABLE_RULES if t not in tables], [])

    def test_a_page_is_one_that_lists_the_table_or_the_catalogue_s_row(self):
        self.assertEqual(I.PAGES.get("policy_actions"), "/policy")
        row = {"agency": "NRC", "title": "Biweekly Notice; Applications and Amendments to Facility Operating Licenses and Combined Licenses",
               "docket": "NRC-2026-4984", "action_type": "notice"}
        self.assertEqual(I.bears_on(row), ("nrc_license_actions", "/data#nrc_license_actions"))


class TheCheck(unittest.TestCase):
    TEXT = ("FERC staff issued an environmental assessment (EA) for the Forza Pipeline Project. Forza would lease 750,000 "
            "Dth/d of natural gas transportation. The Commission must receive your comments on or before 5:00 p.m. Eastern "
            "Time on September 28, 2026. The EA concludes approval would not constitute a major federal action "
            "significantly affecting the human environment, a finding of no significant impact.")

    def test_a_clause_from_the_text_is_kept(self):
        clause = ("FERC staff issued an environmental assessment of the Forza pipeline, which would lease 750,000 Dth/d, "
                  "finding no significant impact, with comments due by 5:00 p.m. Eastern on September 28, 2026")
        self.assertEqual(I.check(clause, "Forza would lease 750,000 Dth/d of natural gas transportation", self.TEXT), [])
        self.assertEqual(I.sentence(clause + ".", "eia_gas_pipeline_projects", "/data#eia_gas_pipeline_projects"),
                         clause + "; it bears on eia_gas_pipeline_projects (/data#eia_gas_pipeline_projects).")

    def test_a_number_the_text_does_not_state_is_refused(self):
        why = I.check("FERC reviewed the 800,000 Dth/d Forza pipeline", "Forza would lease 750,000", self.TEXT)
        self.assertTrue(any("numbers not in the text" in w for w in why))

    def test_a_quotation_not_in_the_text_is_refused(self):
        why = I.check("FERC reviewed the Forza pipeline", "Forza would build a pipeline", self.TEXT)
        self.assertIn("its quotation is not in the text word for word", why)

    def test_an_opinion_a_dash_and_a_second_sentence_are_refused(self):
        q = "Forza would lease 750,000 Dth/d of natural gas transportation"
        self.assertTrue(any("opinion" in w for w in I.check("FERC took a major step on the Forza pipeline", q, self.TEXT)))
        self.assertIn("an em or en dash", I.check("FERC reviewed the Forza pipeline " + chr(0x2014) + " at last", q, self.TEXT))
        self.assertIn("not one sentence", I.check("FERC reviewed the Forza pipeline. Comments are due", q, self.TEXT))

    def test_terms_of_art_and_abbreviations_are_not_faults(self):
        q = "Forza would lease 750,000 Dth/d of natural gas transportation"
        self.assertEqual(I.check("FERC found no significant impact; comments are due by 5:00 p.m. Eastern Time on September 28, 2026", q, self.TEXT), [])
        self.assertEqual(I.check("FERC accepted the new major license application of Acme Inc. for review", q, self.TEXT), [])


class TheReadsOfThisSession(unittest.TestCase):
    def test_the_reads_for_the_owner_hold_the_rules(self):
        path = os.path.join(ROOT, "docs", "reviews", "policy-impact-2026-11-06.csv")
        with open(path, encoding="utf-8") as f:
            rows = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
        self.assertEqual(len(rows), 60)
        for r in rows:
            if r["kept"] == "yes":
                self.assertTrue(r["impact"].endswith(f"; it bears on {r['table']} ({r['page']})."), r["event_id"])
                self.assertIsNone(I.UNSAID.search(r["impact"].split("; it bears on")[0]), r["event_id"])
            else:
                self.assertEqual(r["impact"], "")
                self.assertTrue(r["why_not"])


if __name__ == "__main__":
    unittest.main()
