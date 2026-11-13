"""Session 5260 (chain 238, Ask): the hold by grid holds a table of things too.

Energy Research Warehouse (ERW). The platform set's pj08 (docs/reviews/ask-eval-2026-11-13.md, "The second class"):
asked how many MW are active in ISO New England's interconnection queue, the chat read isone_interconnection_queue, a
table the license file holds, and answered with the figure. Both loops let it: a table held by grid is read and the held
grids' rows are left out row by row, by each row's `entity`; a table of things names its rows by `entity_id`, so none of
its rows was ever left out. The mends, in the chat's tools of both loops:

  a held grid's own table (its name begins with the grid's prefix, and that grid decides it) is refused by name, in the
  words of a table held whole, for a query, a description and a compare
  a table of things several grids share (energy_projects) is read without the rows whose id is a held grid's, and
  without MISO's own; a read that matched only such rows is refused in the hold's words

No model, no network, and no held row in the repository: the rows these tests read are written here, with made-up ids
and no figure of any real project.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
SITE = os.path.join(ROOT, "site")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T = module("test_session1300_for_5260", os.path.join(ROOT, "tests", "test_session1300.py"))
ask, tools = T.ask, T.tools
hold = tools.hold

OWN = {"isone_interconnection_queue": "isone", "nyiso_interconnection_queue": "nyiso", "nyiso_dam_zone_prices": "nyiso", "isone_rtm_zone_prices": "isone",
       "miso_interconnection_queue": "miso"}
SHARED = ("energy_projects", "iso_dam_hub_prices", "merchant_revenue_monthly", "cost_of_power_monthly")


def things(table="energy_projects"):
    """A table of things as the tools hold one (its first two columns are entity_id and entity_type): five rows with
    made-up ids, one of each kind of owner."""
    return pd.DataFrame([
        {"entity_id": "eia860:1:1", "entity_type": "generator", "name": "a unit", "capacity_mw": 100.0, "status": "operating", "status_date": pd.Timestamp("2020-01-01"), "source_table": "eia860m_operating_generators"},
        {"entity_id": "ercot_queue:1", "entity_type": "generator", "name": "a request", "capacity_mw": 200.0, "status": "active", "status_date": pd.Timestamp("2024-01-01"), "source_table": "ercot_interconnection_queue"},
        {"entity_id": "isone_queue:1", "entity_type": "generator", "name": "a request", "capacity_mw": 300.0, "status": "active", "status_date": pd.Timestamp("2024-01-01"), "source_table": "isone_interconnection_queue"},
        {"entity_id": "isone_queue:2", "entity_type": "generator", "name": "a request", "capacity_mw": 400.0, "status": "withdrawn", "status_date": pd.Timestamp("2023-01-01"), "source_table": "isone_interconnection_queue"},
        {"entity_id": "miso_queue:1", "entity_type": "generator", "name": "a request", "capacity_mw": 500.0, "status": "active", "status_date": pd.Timestamp("2024-01-01"), "source_table": "miso_interconnection_queue"},
    ])


class Things:
    """Session 1300's fixture, with one table of things more in it (written above, no real row)."""

    def __init__(self, table="energy_projects"):
        self.table = table

    def __enter__(self):
        self.frames = T.Frames()
        self.frames.__enter__()
        self.frames.load()
        cov = tools._frames["_coverage"]
        tools._frames["_coverage"] = pd.concat([cov, pd.DataFrame([{**{c: None for c in cov.columns}, "table": self.table, "source_report": "erw:fixture", "license": "public",
                                                                    "tier": "derived", "sector": "power", "iso": "none", "interval": "snapshot", "n_rows": 5, "derived": "yes"}])],
                                               ignore_index=True)
        tools._frames[self.table] = things(self.table)
        return self

    def __exit__(self, *exc):
        return self.frames.__exit__(*exc)


class TheOwnTable(unittest.TestCase):
    def test_which_tables_are_a_held_grid_s_own(self):
        for t, g in OWN.items():
            self.assertEqual(hold.own_grid(t), g, t)
        for t in SHARED + ("energy_deals", "policy_actions", "ercot_interconnection_queue", "lbnl_interconnection_queue", "no_such_table"):
            self.assertEqual(hold.own_grid(t), "", t)

    @unittest.skipUnless(shutil.which("node"), "node is not on this machine")
    def test_both_loops_name_the_same_tables(self):
        r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "scripts/test-ask-heldrows.test.mjs", "--own"], cwd=SITE, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=300)
        self.assertEqual(r.returncode, 0, (r.stdout or "")[-800:] + (r.stderr or "")[-800:])
        site = json.loads([line for line in r.stdout.splitlines() if line.startswith("{")][-1])
        self.assertEqual(sorted(site), sorted(hold.tables()))
        for t in site:
            self.assertEqual(hold.own_grid(t), site[t], t)
        self.assertGreaterEqual(sum(1 for g in site.values() if g), 5)

    def test_it_is_refused_by_name_before_any_row_is_read(self):
        with T.Frames() as frames:
            frames.load()
            for name, args in (("query", {"table": "isone_interconnection_queue", "aggregation": "count"}),
                               ("query", {"table": "isone_interconnection_queue", "aggregation": "sum", "where": {"status": "active"}}),
                               ("describe_table", {"table": "isone_interconnection_queue"}),
                               ("compare", {"a": {"table": "cost_of_power_monthly", "aggregation": "count"}, "b": {"table": "isone_interconnection_queue", "aggregation": "count"}})):
                with mock.patch.object(tools.erw, "fetch", side_effect=AssertionError("a held table was asked of the backend")):
                    out, err = tools.run(name, args)
                self.assertTrue(err, name)
                self.assertTrue(out["error"].startswith("table isone_interconnection_queue is license needed: ISO-NE: "), out["error"])
                self.assertEqual(ask.refused_whole(out["error"], ["isone_interconnection_queue"]), "isone_interconnection_queue", "and it is not asked again")

    def test_misos_own_table_is_refused_in_the_pause_s_words_for_a_description_too(self):
        """The pause says more than the license (session 1126). Refused in the license's words alone, the platform set's
        pj09 was answered from another table; and until this session a description of MISO's own table was given."""
        with T.Frames() as frames:
            frames.load()
            for name, args in (("describe_table", {"table": "miso_interconnection_queue"}), ("query", {"table": "miso_interconnection_queue", "aggregation": "count"})):
                with mock.patch.object(tools.erw, "fetch", side_effect=AssertionError("MISO's table was asked of the backend")):
                    out, err = tools.run(name, args)
                self.assertEqual((err, out["error"]), (True, hold.MISO_PAUSED), name)
                self.assertIsNone(ask.refused_whole(out["error"], ["miso_interconnection_queue"]))
        with open(os.path.join(SITE, "lib", "chat", "tools.ts"), encoding="utf-8") as f:
            src = f.read()
        self.assertLess(src.index("  if (misoOwn(name)) throw new ToolError(MISO_PAUSED);"), src.index("  if (ownGrid(name)) throw new ToolError(ownTableWords(name));"))

    def test_the_words_are_the_site_s(self):
        with open(os.path.join(SITE, "lib", "chat", "heldrows.ts"), encoding="utf-8") as f:
            ts = f.read()
        self.assertIn('return `table ${table} is ${LICENSE_NEEDED}: ${licenseTitle(table)}. State no figure of it: answer with not_in_warehouse true and say that it is "${LICENSE_NEEDED}"`;', ts)
        said = hold.held_rows_words("energy_projects")
        self.assertIn("return `" + said.replace("energy_projects", "${table}").replace(hold.title("energy_projects"), "${licenseTitle(table)}").replace("license needed", "${LICENSE_NEEDED}") + "`;", ts)
        with open(os.path.join(SITE, "lib", "chat", "tools.ts"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("if (ownGrid(name)) throw new ToolError(ownTableWords(name));", src)
        self.assertIn("}, HOURLY, max).then(thingsKept);", src)
        self.assertIn("if (rows.length && !k.kept.length && (k.held || k.paused)) throw new ToolError(k.held ? heldRowsWords(a.table) : MISO_PAUSED);", src)
        # the lines sessions 215, 502 and 267 pin are still there, word for word
        self.assertIn("if (licenseNeeded(name) && !licenseByGrid(name)) throw new ToolError", src)
        self.assertIn("const out = rows.filter((r) => !misoOwn(r.entity)); if (rows.length && !out.length) throw new ToolError(MISO_PAUSED);", src)


class TheSharedTable(unittest.TestCase):
    def test_a_held_grid_s_rows_and_misos_own_are_left_out(self):
        with Things():
            out, err = tools.run("query", {"table": "energy_projects", "aggregation": "count"})
            self.assertEqual((err, out["result"]), (False, [{"count": 2}]))
            out, err = tools.run("query", {"table": "energy_projects", "aggregation": "sum"})
            self.assertEqual((err, out["result"][0]["value"], out["result"][0]["n"]), (False, 300.0, 2))
            out, err = tools.run("query", {"table": "energy_projects", "aggregation": "count", "group_by": "source_table"})
            self.assertEqual(sorted(r["source_table"] for r in out["result"]), ["eia860m_operating_generators", "ercot_interconnection_queue"])
            out, err = tools.run("describe_table", {"table": "energy_projects"})
            self.assertFalse(err)
            self.assertEqual(out["rows"], 2)
            self.assertEqual(sorted(out["text_column_values"]["source_table"]), ["eia860m_operating_generators", "ercot_interconnection_queue"])

    def test_a_read_that_matched_only_held_rows_is_refused_in_the_hold_s_words(self):
        with Things():
            for where in ({"source_table": "isone_interconnection_queue"}, {"status": "withdrawn"}):
                out, err = tools.run("query", {"table": "energy_projects", "aggregation": "count", "where": where})
                self.assertTrue(err, where)
                self.assertEqual(out["error"], hold.held_rows_words("energy_projects"))
                self.assertTrue(ask.refused_read(out["error"]))
                self.assertIsNone(ask.refused_whole(out["error"], ["energy_projects"]), "the table's other rows are still read")
            # a query that names a held grid's row is given the held grid's answer, as for a series (session 1112): the
            # grid named, the hold's words, the public rows' own figures, and none of the held grid's
            out, err = tools.run("query", {"table": "energy_projects", "aggregation": "count", "entity": "isone_queue:1"})
            self.assertEqual((err, out.get("held"), out.get("grid")), (False, True, "ISO-NE"))
            self.assertNotIn("result", out)
            self.assertFalse(any(str(r.get("entity", "")).startswith(("isone", "miso")) for r in out.get("public_grids") or []))
            # MISO's own rows: the pause's words
            out, err = tools.run("query", {"table": "energy_projects", "aggregation": "count", "where": {"source_table": "miso_interconnection_queue"}})
            self.assertEqual((err, out["error"]), (True, hold.MISO_PAUSED))
            # and a filter that matches nothing at all is still "no rows match"
            out, err = tools.run("query", {"table": "energy_projects", "aggregation": "count", "where": {"status": "no such status"}})
            self.assertEqual((err, out.get("note")), (False, "no rows match these filters"))

    def test_with_the_hold_off_the_cli_reads_every_row_as_before(self):
        with Things():
            with mock.patch.dict(os.environ, {"ASK_HOLD": "off"}):
                tools._frames.pop(("_held", "energy_projects"), None)
                out, err = tools.run("query", {"table": "energy_projects", "aggregation": "count"})
                self.assertEqual((err, out["result"]), (False, [{"count": 5}]))

    def test_a_table_not_held_loses_misos_own_rows_only(self):
        with Things("lbnl_interconnection_queue"):
            out, err = tools.run("query", {"table": "lbnl_interconnection_queue", "aggregation": "count"})
            self.assertEqual((err, out["result"]), (False, [{"count": 4}]))


class TheLoop(unittest.TestCase):
    def test_the_question_that_found_it_ends_as_a_refusal(self):
        q = {"tools": [{"name": "query", "input": {"table": "isone_interconnection_queue", "aggregation": "sum", "where": {"status": "active"}}}]}
        again = {"tools": [{"name": "describe_table", "input": {"table": "isone_interconnection_queue"}}]}
        refusal = {"text": {"answer": "Not in the warehouse for a reader: ISO New England's interconnection queue is held for a license (license needed).",
                            "citations": [], "not_in_warehouse": True}}
        with T.Frames() as frames:
            client = T.Scripted([q, again, refusal])
            asker = ask.Asker(model="claude-sonnet-5-5", client=client)
            frames.load()
            with mock.patch.object(tools, "run", wraps=tools.run) as ran:
                rec = asker.ask("How many MW of projects are active in ISO New England's interconnection queue?", today="2026-11-13")
        self.assertEqual((rec["status"], rec["tool_calls"], ran.call_count, client.choices), ("not_in_warehouse", 2, 1, ["auto", "auto", "none"]))
        self.assertEqual(len(rec.get("reads") or []), 0)

    def test_the_two_loops_are_held_equal_on_the_scenario(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "session1300", "turns.json"), encoding="utf-8") as f:
            turns = json.load(f)
        self.assertIn("a_held_grids_own_table", [s["id"] for s in turns["scenarios"]])
        self.assertIn({"fixture": "tests/fixtures/session5260/own_table.json", "table": "isone_interconnection_queue"}, turns["extra"])
        with open(os.path.join(ROOT, "tests", "fixtures", "session5260", "own_table.json"), encoding="utf-8") as f:
            fx = json.load(f)
        self.assertEqual((fx["catalogue"][0]["table_name"], fx["rows"]), ("isone_interconnection_queue", []), "no held row is in the repository")
        self.assertEqual(json.loads(fx["catalogue"][0]["columns"])[0], "entity_id", "a table of things")


class TheSite(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "node is not on this machine")
    def test_the_site_s_module(self):
        r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "--test", "scripts/test-ask-heldrows.test.mjs"], cwd=SITE, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=300)
        self.assertEqual(r.returncode, 0, (r.stdout or "")[-1500:] + (r.stderr or "")[-500:])


class TheStoredRuns(unittest.TestCase):
    def test_the_question_that_found_it_is_a_refusal_in_its_newest_answer(self):
        S = module("eval_site_for_5260", os.path.join(EVAL, "eval_site.py"))
        newest = None
        for s in S.sessions_of("platform"):
            for q in S.read_json(S.files(s, "platform")["run"])["questions"]:
                if q["id"] == "pj08":
                    newest = (s, q)
        self.assertIsNotNone(newest)
        s, q = newest
        self.assertGreaterEqual(int(s), 5260, "pj08 has not been asked since the fix")
        self.assertEqual(q["status"], "not_in_warehouse")
        self.assertIn("license needed", q["answer"])
        self.assertFalse(any(not t.get("isError") and (t.get("input") or {}).get("table") == "isone_interconnection_queue" for t in q.get("trace") or []),
                         "a call of the held table was answered")


if __name__ == "__main__":
    unittest.main()
