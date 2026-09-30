"""Session 35: the grid pages' scoped chat and the loop's citation gate.

Energy Research Warehouse (ERW). No model is called: the loop runs against a fake client, and the tools read the
local tables.

    python -m unittest tests.test_session35 -v
"""

import json
import os
import sys
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
os.environ.setdefault("ERW_LEDGER", "0")

import ask  # noqa: E402
import tools  # noqa: E402

GRIDS = json.load(open(os.path.join(ROOT, "docs", "grids", "grids.json"), encoding="utf-8"))["grids"]


class Scope(unittest.TestCase):
    def tearDown(self):
        tools.set_scope(None)

    def test_every_grid_has_its_written_layer_with_five_sections_and_sources(self):
        for g in GRIDS:
            md = open(os.path.join(ROOT, "docs", "grids", f"{g['slug']}.md"), encoding="utf-8").read()
            sections = [s for s in md.split("\n## ")[1:]]
            self.assertEqual(len(sections), 5, g["slug"])
            for s in sections:
                self.assertIn("Sources: https://", s, (g["slug"], s[:40]))
            self.assertNotIn(chr(0x2014), md)

    def test_iso_filter_finds_the_consolidated_tables(self):
        names = [t["table"] for t in tools.list_tables(iso="CAISO")["tables"]]
        self.assertIn("carbon_intensity_hourly", names)  # its iso is "CAISO;ERCOT;...": the exact match missed it
        self.assertIn("caiso_battery_storage", names)

    def test_a_scoped_chat_sees_only_its_grid(self):
        tools.set_scope("pjm")
        names = {t["table"] for t in tools.list_tables()["tables"]}
        self.assertTrue(names <= set(tools.GRIDS["pjm"]["tables"]))
        out, err = tools.run("query", {"table": "nyiso_dam_zone_prices", "aggregation": "count"})
        self.assertTrue(err)
        out, err = tools.run("query", {"table": "storage_capacity", "aggregation": "count", "group_by": "iso"})
        self.assertFalse(err)
        self.assertEqual([r["iso"] for r in out["result"]], ["PJM"])
        out, err = tools.run("grid_notes", {"grid": "ercot"})
        self.assertTrue(err)
        out, err = tools.run("grid_notes", {"grid": "pjm"})
        self.assertFalse(err)
        self.assertEqual(out["table"], "docs/grids/pjm.md")


def reply(text):
    return types.SimpleNamespace(
        content=[types.SimpleNamespace(type="text", text=text)], stop_reason="end_turn", _request_id="req_fake",
        usage=types.SimpleNamespace(input_tokens=10, output_tokens=5, cache_creation_input_tokens=0, cache_read_input_tokens=0))


class FakeClient:
    def __init__(self, answers):
        self.answers = list(answers)
        self.messages = types.SimpleNamespace(create=lambda **kw: reply(self.answers.pop(0)))


class CitationGate(unittest.TestCase):
    def tearDown(self):
        tools.set_scope(None)

    def test_an_empty_uncited_answer_is_sent_back_then_refused(self):
        empty = json.dumps({"answer": "", "citations": [], "not_in_warehouse": False})
        rec = ask.Asker(model="claude-sonnet-5-5", client=FakeClient([empty, empty]), grid="caiso").ask("q")
        self.assertTrue(rec["retried"])
        self.assertEqual(rec["status"], "refused_unverified")

    def test_not_in_the_warehouse_needs_no_citation(self):
        nw = json.dumps({"answer": "Not in the warehouse: no such series.", "citations": [], "not_in_warehouse": True})
        rec = ask.Asker(model="claude-sonnet-5-5", client=FakeClient([nw])).ask("q")
        self.assertEqual(rec["status"], "not_in_warehouse")
        self.assertFalse(rec["retried"])


if __name__ == "__main__":
    unittest.main()
