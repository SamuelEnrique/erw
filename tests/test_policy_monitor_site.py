"""Session 3060 (chain 166): the policy monitor's data file (warehouse/policy/monitor_site.py), built from frames of
policy_actions and policy_reads, and the daily step's rule that it never writes a thinner file.

    .venv/Scripts/python.exe -m pytest -q tests/test_policy_monitor_site.py
"""

import json
import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "policy"))
import monitor_site as MS  # noqa: E402


def actions():
    base = {"event_type": "filing", "parties": "", "entity_ids": "", "mw": "", "price": "", "currency": "", "source": "federalregister:api",
            "abstract": "", "rin": "", "fr_document_number": "", "sector_tags": "", "related_urls": "", "news_story_ids": "", "news_story_urls": "",
            "significance": "5", "sector": "gas", "why": "", "first_paragraph": ""}
    return pd.DataFrame([
        dict(base, event_id="federalregister:1", event_date="2026-09-01", agency="FERC", action_type="notice", status="",
             title="Acme Pipeline, LLC; Notice of Application and Establishing Intervention Deadline", docket="Docket No. CP26-1-000",
             states="TX", source_url="https://example.gov/1",
             first_paragraph="The deadline for filing protests, motions to intervene, and comments is 5:00 p.m. Eastern Time on December 8, 2026."),
        dict(base, event_id="federalregister:2", event_date="2026-10-01", agency="FERC", action_type="notice", status="", significance="6",
             title="Acme Pipeline, LLC; Notice of Scoping Period Requesting Comments on Environmental Issues for the Proposed Acme Project in PJM",
             docket="Docket No. CP26-1-000", states="TX", source_url="https://example.gov/2"),
        dict(base, event_id="nrc:abc", event_date="2026-10-05", agency="NRC", action_type="press_release", status="news release", sector="nuclear",
             title="NRC to Hold Public Meeting", docket="", states="", source_url="https://example.gov/3"),
    ])


class Build(unittest.TestCase):
    def test_one_row_a_proceeding_with_its_fields_and_sources(self):
        reads = pd.DataFrame([{"action_event_id": "federalregister:2", "affected_isos": "PJM;ERCOT", "plain_read": "A plain read."}])
        impacts = {"federalregister:2": ("FERC opened scoping; it bears on eia_gas_pipeline_projects (/data#eia_gas_pipeline_projects).", "Acme", "claude-sonnet-5-5")}
        doc = MS.build(actions(), reads, impacts, today="2026-11-06")
        self.assertEqual((doc["documents"], doc["records"]), (3, 2))
        r = next(x for x in doc["rows"] if x["id"] == "ferc:CP26-1")
        self.assertEqual((r["date"], r["first"], r["n"], r["body"], r["status"], r["significance"]), ("2026-10-01", "2026-09-01", 2, "FERC", "open", 6))
        self.assertEqual(r["next"]["date"], "2026-12-08")
        self.assertEqual(r["sources"][0], "https://example.gov/2", "the newest document's page first")
        self.assertEqual(sorted(r["grids"]), ["ercot", "pjm"])
        self.assertEqual(r["impact"]["event_id"], "federalregister:2")
        self.assertEqual(r["bears_on"]["table"], "eia_gas_pipeline_projects")
        self.assertEqual([x["date"] for x in doc["rows"]], sorted([x["date"] for x in doc["rows"]], reverse=True))

    def test_the_daily_step_never_writes_a_thinner_file_and_leaves_one_that_only_changed_its_day(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "monitor.json")
            doc = MS.build(actions(), None, {}, today="2026-11-06")
            self.assertEqual(MS.write(doc, out, daily=True, log=lambda *a: None), 0)
            thin = MS.build(actions().iloc[:1], None, {}, today="2026-11-07")
            self.assertEqual(MS.write(thin, out, daily=True, log=lambda *a: None), 1)
            same = MS.build(actions(), None, {}, today="2026-11-07")
            self.assertEqual(MS.write(same, out, daily=True, log=lambda *a: None), 0)
            with open(out, encoding="utf-8") as f:
                held = json.load(f)
            self.assertEqual((held["records"], held["built"]), (2, "2026-11-06"))

    def test_the_file_in_the_repository_is_the_builder_s_and_has_no_dash(self):
        path = os.path.join(ROOT, "site", "data", "policy", "monitor.json")
        with open(path, encoding="utf-8") as f:
            s = f.read()
        self.assertNotRegex(s, f"[{chr(0x2014)}{chr(0x2013)}]")
        doc = json.loads(s)
        self.assertEqual(doc["records"], len(doc["rows"]))
        self.assertGreater(doc["records"], 1000)


if __name__ == "__main__":
    unittest.main()
