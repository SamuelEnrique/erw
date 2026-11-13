"""Session 5256 (chain 238, Ask): a table of the record that the live set does not hold is refused, never answered.

Energy Research Warehouse (ERW). The platform set's oi07 (docs/reviews/ask-eval-2026-11-13.md): asked how much crude oil
the United States imported from Canada, the chat was refused eia_crude_imports_by_country (a table the catalogue lists
and the live set lacks), said so rightly, stated no number, and still answered as an answer, with that table as its
source. Two causes, two mends, in both loops:

  the words   the tool's refusal said where the table is and not how to answer; a held table's says both. Now it says
              both (site/lib/chat/refused.ts notLiveWords, warehouse/chat/tools.py not_live_words: the same sentence)
  the rule    the loop counts every table list_tables names as read, so the citation passed. An answer's citation of a
              table a tool refused to read, and that no call read, is now a citation of a table no tool read: the draft
              is sent back, as for any cited table never read. A refusal may still name what it was refused, and a table
              refused in one call and read in another is a source

No model, no network: the model's turns are scripted and the rows are session 1300's fixture, as tests/test_session1300.py
runs both loops (that test holds the two loops equal on this scenario; this one holds the rule's edges on the Python side).
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
TABLE = "eia_crude_imports_by_country"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T = module("test_session1300_for_5256", os.path.join(ROOT, "tests", "test_session1300.py"))   # its Frames and Scripted, and ask and tools
ask, tools = T.ask, T.tools

LIST = {"tools": [{"name": "list_tables", "input": {}}]}
REFUSED_QUERY = {"tools": [{"name": "query", "input": {"table": TABLE, "aggregation": "sum", "entity": "eia:MCRIMUSCA2"}}]}
AS_AN_ANSWER = {"text": {"answer": f"I can't give a figure. The warehouse has a table for it, {TABLE}, but the live set this chat reads does not include it.",
                         "citations": [{"table": TABLE, "source_report": "eia:petroleum/move/impcus", "data_version": "not returned", "tier": "source"}], "not_in_warehouse": False}}
A_REFUSAL = {"text": {"answer": f"Not in the warehouse this chat reads: {TABLE} is on Redivis and not in the live set.", "citations": [], "not_in_warehouse": True}}


def run(turns, question="How much crude oil did the United States import from Canada last year?"):
    """One scripted question through the Python loop over session 1300's fixture. Returns (the record, the client)."""
    with T.Frames() as frames:
        client = T.Scripted(turns)
        asker = ask.Asker(model="claude-sonnet-5-5", client=client)
        frames.load()
        return asker.ask(question, today="2026-11-13"), client


class TheWords(unittest.TestCase):
    def test_both_loops_say_the_same_sentence(self):
        with open(os.path.join(ROOT, "site", "lib", "chat", "refused.ts"), encoding="utf-8") as f:
            ts = f.read()
        said = tools.not_live_words("TABLE")
        self.assertIn(said.replace("TABLE", "${table}"), ts, "site/lib/chat/refused.ts notLiveWords and tools.py not_live_words differ")
        for part in ("is not in this site's live set", "its full history is on Redivis", "No tool here can read it", "answer with not_in_warehouse true"):
            self.assertIn(part, said)
        with open(os.path.join(ROOT, "site", "lib", "chat", "tools.ts"), encoding="utf-8") as f:
            self.assertIn("throw new ToolError(notLiveWords(name))", f.read())

    def test_both_loops_tell_a_refusal_by_the_same_words(self):
        with open(os.path.join(ROOT, "site", "lib", "chat", "refused.ts"), encoding="utf-8") as f:
            self.assertIn("/" + ask.REFUSED_READ.pattern + "/", f.read())
        self.assertTrue(ask.refused_read(tools.not_live_words("x")))
        self.assertTrue(ask.refused_read(tools.hold.MISO_PAUSED))
        self.assertTrue(ask.refused_read(f"table energy_deals is {tools.hold.LICENSE_NEEDED}: the publishers"))
        for other in ("no column 'state' in this table", "aggregation must be one of", "unknown time zone 'Texas'", "", None, 12, {"error": "license needed"}):
            self.assertFalse(ask.refused_read(other), repr(other))

    def test_the_tool_s_refusal_on_a_live_backend_and_on_another(self):
        with T.Frames() as frames:
            frames.load()
            out, err = tools.run("query", {"table": TABLE, "aggregation": "latest"})
            self.assertTrue(err)
            self.assertEqual(out["error"], tools.not_live_words(TABLE))
            out, err = tools.run("describe_table", {"table": TABLE})
            self.assertEqual((err, out["error"]), (True, tools.not_live_words(TABLE)))
            # a clone's files, or Redivis: the words are the backend's own, as before
            with mock.patch.object(tools, "live_only", return_value=False):
                tools._frames.pop(TABLE, None)
                out, err = tools.run("query", {"table": TABLE, "aggregation": "latest"})
                self.assertTrue(err)
                self.assertIn("cannot be read from this backend", out["error"])
                self.assertFalse(ask.refused_read(out["error"]))
            out, err = tools.run("query", {"table": "no_such_table", "aggregation": "latest"})
            self.assertIn("no table named", out["error"])

    def test_which_backends_are_the_live_set_alone(self):
        for backend, live in (("supabase", True), ("live", True), ("local", False), ("redivis", False), ("fixture", False), (None, False)):
            with mock.patch.object(tools.erw, "version", return_value={"backend": backend}):
                self.assertEqual(tools.live_only(), live, backend)


class TheRule(unittest.TestCase):
    def test_an_answer_that_cites_the_refused_table_is_sent_back_and_the_refusal_stands(self):
        rec, client = run([LIST, REFUSED_QUERY, AS_AN_ANSWER, A_REFUSAL])
        self.assertEqual((rec["status"], rec["retried"], rec["tool_calls"], client.n), ("not_in_warehouse", True, 2, 4))
        self.assertEqual(rec["first_violations"], [f"cited table not read: {TABLE}"])
        self.assertEqual(rec["citations"], [])
        self.assertIn("on Redivis and not in the live set", rec["answer"])

    def test_the_fault_as_it_was(self):
        """With the rule off, the first draft stands as an answer whose source is a table no tool read: oi07."""
        with mock.patch.object(ask, "refused_read", return_value=False):
            rec, client = run([LIST, REFUSED_QUERY, AS_AN_ANSWER, A_REFUSAL])
        self.assertEqual((rec["status"], rec["retried"], client.n), ("answered", False, 3))
        self.assertEqual([c["table"] for c in rec["citations"]], [TABLE])

    def test_a_second_such_draft_is_refused_with_no_figure_and_no_source(self):
        rec, _ = run([LIST, REFUSED_QUERY, AS_AN_ANSWER, AS_AN_ANSWER])
        self.assertEqual(rec["status"], "refused_unverified")
        self.assertTrue(rec["answer"].startswith(ask.REFUSAL))
        self.assertIn("it cited a table no tool read", rec["why"])
        self.assertEqual(rec["citations"], [])

    def test_a_refusal_may_name_what_it_was_refused(self):
        cited = {"text": {**A_REFUSAL["text"], "citations": AS_AN_ANSWER["text"]["citations"]}}
        rec, client = run([LIST, REFUSED_QUERY, cited])
        self.assertEqual((rec["status"], rec["retried"], client.n), ("not_in_warehouse", False, 3))

    def test_a_table_refused_in_one_call_and_read_in_another_is_a_source(self):
        paused = {"tools": [{"name": "query", "input": {"table": "cost_of_power_monthly", "aggregation": "mean", "entity": "miso:INDIANA.HUB", "variable": "rt_load_weighted",
                                                        "start": "2026-01-01", "end": "2026-02-01"}}]}
        read = {"tools": [{"name": "query", "input": {"table": "cost_of_power_monthly", "aggregation": "mean", "entity": "ercot:HB_HUBAVG", "variable": "rt_load_weighted",
                                                      "start": "2026-01-01", "end": "2026-02-01"}}]}
        answer = {"text": {"answer": "ERCOT's hub average was 54.481 USD/MWh in January 2026 (cost_of_power_monthly). MISO is paused while its terms are reviewed.",
                           "citations": [{"table": "cost_of_power_monthly", "source_report": "erw:cost_of_power", "data_version": "fixture", "tier": "derived"}], "not_in_warehouse": False}}
        rec, client = run([paused, read, answer], "What was the load-weighted real-time price at ERCOT's hub average and at MISO's Indiana hub in January 2026?")
        self.assertEqual((rec["status"], rec["retried"], rec["tool_calls"]), ("answered", False, 2))
        # and with the read left out, the same draft has no source: MISO's pause refused the table and no call read it
        rec, _ = run([LIST, paused, answer, A_REFUSAL], "What was the load-weighted real-time price at MISO's Indiana hub in January 2026?")
        self.assertEqual((rec["status"], rec["retried"]), ("not_in_warehouse", True))
        self.assertTrue(any("cited table not read: cost_of_power_monthly" == v for v in rec["first_violations"]), rec["first_violations"])

    def test_a_table_held_whole_is_no_source_of_an_answer_either(self):
        held = {"tools": [{"name": "query", "input": {"table": "energy_deals", "aggregation": "count"}}]}
        answer = {"text": {"answer": "The deal tracker, energy_deals, is license needed, so I state no count.",
                           "citations": [{"table": "energy_deals", "source_report": "erw:energy_deals", "data_version": "fixture", "tier": "model_extracted"}], "not_in_warehouse": False}}
        refusal = {"text": {"answer": "Not in the warehouse for a reader: energy_deals is held for a license (license needed).", "citations": [], "not_in_warehouse": True}}
        rec, _ = run([LIST, held, answer, refusal], "How many energy deals were announced in October 2026?")
        self.assertEqual((rec["status"], rec["retried"]), ("not_in_warehouse", True))
        self.assertEqual(rec["first_violations"], ["cited table not read: energy_deals"])

    def test_a_table_refused_whole_is_not_asked_again(self):
        again = {"tools": [{"name": "query", "input": {"table": TABLE, "aggregation": "latest"}}, {"name": "describe_table", "input": {"table": TABLE}},
                           {"name": "compare", "input": {"a": {"table": TABLE, "aggregation": "count"}, "b": {"table": "cost_of_power_monthly", "aggregation": "count"}}}]}
        with mock.patch.object(tools, "run", wraps=tools.run) as ran:
            rec, client = run([REFUSED_QUERY, again, A_REFUSAL])
        self.assertEqual(ran.call_count, 1, "the three later calls that name the refused table are not made")
        self.assertEqual((rec["status"], rec["tool_calls"], rec["retried"], client.n, client.choices), ("not_in_warehouse", 4, False, 3, ["auto", "auto", "none"]))
        self.assertEqual(len(rec.get("reads") or []), 0)

    def test_what_is_refused_whole_and_what_is_not(self):
        words = tools.not_live_words(TABLE)
        self.assertEqual(ask.refused_whole(words, [TABLE]), TABLE)
        self.assertEqual(ask.refused_whole(words, ["another", TABLE]), TABLE)
        self.assertEqual(ask.refused_whole(f"table energy_deals is {tools.hold.LICENSE_NEEDED}: the publishers", ["energy_deals"]), "energy_deals")
        self.assertIsNone(ask.refused_whole(words, ["another"]))
        self.assertIsNone(ask.refused_whole(tools.hold.MISO_PAUSED, ["cost_of_power_monthly"]), "MISO's pause refuses rows of a table, not the table")
        self.assertIsNone(ask.refused_whole("no column 'state' in this table", [TABLE]))
        self.assertIsNone(ask.refused_whole(None, [TABLE]))
        self.assertEqual(ask.tables_named("query", {"table": "a"}), ["a"])
        self.assertEqual(ask.tables_named("describe_table", {"table": "a"}), ["a"])
        self.assertEqual(ask.tables_named("compare", {"a": {"table": "a"}, "b": {"table": "b"}}), ["a", "b"])
        self.assertEqual(ask.tables_named("list_tables", {"sector": "oil"}), [])
        self.assertEqual(ask.tables_named("query", None), [])
        note = ask.refused_again_note(TABLE, words)
        self.assertTrue(note.startswith(f"table {TABLE} was already refused for this question and no call can read it: do not ask it again."))
        self.assertTrue(note.endswith(words))
        with open(os.path.join(ROOT, "site", "lib", "chat", "refused.ts"), encoding="utf-8") as f:
            ts = f.read()
        self.assertIn("`table ${table} was already refused for this question and no call can read it: do not ask it again. ${words}`", ts)
        self.assertIn("error.startsWith(`table ${t} is not in this site's live set`) || error.startsWith(`table ${t} is license needed`)", ts)

    def test_misos_pause_does_not_close_a_table_to_the_other_grids(self):
        paused = {"tools": [{"name": "query", "input": {"table": "cost_of_power_monthly", "aggregation": "mean", "entity": "miso:INDIANA.HUB", "variable": "rt_load_weighted",
                                                        "start": "2026-01-01", "end": "2026-02-01"}}]}
        read = {"tools": [{"name": "query", "input": {"table": "cost_of_power_monthly", "aggregation": "mean", "entity": "ercot:HB_HUBAVG", "variable": "rt_load_weighted",
                                                      "start": "2026-01-01", "end": "2026-02-01"}}]}
        answer = {"text": {"answer": "ERCOT's hub average was 54.481 USD/MWh in January 2026 (cost_of_power_monthly).",
                           "citations": [{"table": "cost_of_power_monthly", "source_report": "erw:cost_of_power", "data_version": "fixture", "tier": "derived"}], "not_in_warehouse": False}}
        rec, _ = run([paused, read, answer], "What was the load-weighted real-time price at ERCOT's hub average in January 2026?")
        self.assertEqual((rec["status"], len(rec["reads"])), ("answered", 1), "the second call was made and read")

    def test_listing_alone_still_makes_a_table_citable(self):
        """What the catalogue says of a table (its span, its rows) is a tool result about it: a table listed and never
        refused may be cited, as before."""
        answer = {"text": {"answer": "The warehouse lists cost_of_power_monthly, a derived table.",
                           "citations": [{"table": "cost_of_power_monthly", "source_report": "erw:cost_of_power", "data_version": "fixture", "tier": "derived"}], "not_in_warehouse": False}}
        rec, _ = run([LIST, answer], "Which table holds the monthly cost of power?")
        self.assertEqual((rec["status"], rec["retried"]), ("answered", False))


class TheStoredRuns(unittest.TestCase):
    def test_the_only_answer_that_cites_a_refused_table_is_the_one_found(self):
        S = module("eval_site_for_5256", os.path.join(EVAL, "eval_site.py"))
        found = []
        for s in S.sessions_of("platform"):
            for q in S.read_json(S.files(s, "platform")["run"])["questions"]:
                refused, read = set(), set()
                for t in q.get("trace") or []:
                    i = t.get("input") or {}
                    named = [x["table"] for x in ask.reads_of(t.get("tool"), i)] + ([i["table"]] if t.get("tool") == "describe_table" and isinstance(i.get("table"), str) else [])
                    if t.get("isError") and ask.refused_read((t.get("out") or {}).get("error")):
                        refused.update(named)
                    if not t.get("isError"):
                        read.update(named)
                if q.get("status") == "answered" and any(c.get("table") in refused - read for c in q.get("citations") or []):
                    found.append((s, q["id"]))
        self.assertEqual(found, [("5253", "oi07")], "an answer since the rule cites a table it was refused, or the one found is gone from its run")


class TheSite(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "node is not on this machine")
    def test_the_site_s_module(self):
        r = subprocess.run(["node", "--test", "scripts/test-ask-refused.test.mjs"], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=300)
        self.assertEqual(r.returncode, 0, (r.stdout or "")[-1500:] + (r.stderr or "")[-500:])

    def test_the_site_s_loop_holds_the_rule(self):
        with open(os.path.join(ROOT, "site", "lib", "chat", "ask.ts"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("if (!draft.not_in_warehouse) for (const c of draft.citations) if (refusedTables.has(c.table) && !readOk.has(c.table) && !uncited.includes(c.table)) uncited.push(c.table);", src)
        self.assertIn("if (isError && refusedRead(out.error)) for (const t of named) refusedTables.add(t);", src)
        self.assertIn("if (!isError) for (const t of named) readOk.add(t);", src)
        # the check as sessions 143 and 148 pin it is still there, word for word: the rule adds to its list
        self.assertIn("const uncited = draft.citations.map((c) => c.table).filter((t) => !tablesRead.has(t));", src)

    def test_the_site_s_loop_does_not_ask_a_refused_table_again(self):
        with open(os.path.join(ROOT, "site", "lib", "chat", "ask.ts"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("const again = tablesNamed(name, input).find((x) => refusedWholeWords.has(x));", src)
        self.assertIn("if (again !== undefined) return { out: { note: refusedAgainNote(again, refusedWholeWords.get(again) ?? \"\") }, isError: false, repeat: true };", src)
        self.assertIn("if (whole) refusedWholeWords.set(whole, String(got.out.error));", src)
        self.assertIn("const repeat = k !== null && ran.has(k);", src, "session 143's line, as it was")

    def test_the_two_loops_are_held_equal_on_the_scenario(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "session1300", "turns.json"), encoding="utf-8") as f:
            turns = json.load(f)
        s = next(x for x in turns["scenarios"] if x["id"] == "a_table_not_in_the_live_set")
        self.assertEqual([("tools" in t, "text" in t) for t in s["turns"]], [(True, False), (True, False), (False, True), (False, True)])
        self.assertIn({"fixture": "tests/fixtures/session5256/not_live.json", "table": TABLE}, turns["extra"])
        with open(os.path.join(ROOT, "tests", "fixtures", "session5256", "not_live.json"), encoding="utf-8") as f:
            fx = json.load(f)
        self.assertEqual((fx["catalogue"][0]["table_name"], fx["catalogue"][0]["in_live_set"], fx["rows"]), (TABLE, "no", []))


if __name__ == "__main__":
    unittest.main()
