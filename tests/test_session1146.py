"""Session 1146 (chain 085): the CLI's loop as the site's. Held here: the Python loop's general chat (warehouse/chat/
ask.py, what the CLI and eval.py run) holds the conversation as the site's does, in the same words and with the same
first message when there is none (site/lib/chat/history.ts generalOpening, compared through node); records what each
query read as the site's readsOf does; names on a refusal the tables it looked at with what each holds (tools.py
nearest_for, holds_line, as tools.ts); counts an earlier answer's numbers as given and its tables as read; and leaves Ask
ERCOT's profile as it was. The license hold stays the site's: the CLI reads this machine's own files.
No network, no model. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import sys
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAT = os.path.join(ROOT, "warehouse", "chat")
SITE = os.path.join(ROOT, "site")
HISTORY = [{"question": "Q1?", "answer": "A1 was 36.70 USD/MWh.", "reads": [{"table": "cost_of_power_monthly", "entity": "ercot:HB_HUBAVG", "aggregation": "mean"}],
            "citations": [{"table": "cost_of_power_monthly"}]}]


def chat():
    if CHAT not in sys.path:
        sys.path.insert(0, CHAT)
    import ask  # noqa: E402
    import tools  # noqa: E402
    return ask, tools


class Usage:
    input_tokens = output_tokens = 0
    cache_creation_input_tokens = cache_read_input_tokens = 0


class FakeClient:
    """One list_tables call and one describe_table call, then "not in the warehouse"."""
    def __init__(self):
        self.n, self.messages, self.first = 0, self, None

    def create(self, **kw):
        self.n += 1
        if self.first is None:
            self.first = kw["messages"][0]["content"]
        t = lambda stop, content: types.SimpleNamespace(stop_reason=stop, content=content, usage=Usage(), _request_id="req_fixture")
        if self.n == 1:
            return t("tool_use", [types.SimpleNamespace(type="tool_use", name="describe_table", input={"table": "cost_of_power_monthly"}, id="t1")])
        return t("end_turn", [types.SimpleNamespace(type="text", text=json.dumps({"answer": "Not in the warehouse: no such table.", "citations": [], "not_in_warehouse": True}))])


class TheCliLoop(unittest.TestCase):
    def test_the_opening_with_and_without_a_conversation(self):
        ask, _ = chat()
        a = ask.Asker.__new__(ask.Asker)
        self.assertEqual(a.opening("What was X?", "2026-10-23"), "Today is 2026-10-23 (UTC).\n\nQuestion: What was X?")
        text = a.opening("And the year before?", "2026-10-23", history=HISTORY)
        self.assertTrue(text.startswith("The conversation so far, oldest first. The new question continues it.\n\nEarlier question 1: Q1?\nYour answer: A1 was 36.70 USD/MWh.\nQueries you ran: query {\"aggregation\":\"mean\",\"entity\":\"ercot:HB_HUBAVG\",\"table\":\"cost_of_power_monthly\"}"), text)
        self.assertEqual(a.known_tables(HISTORY), {"cost_of_power_monthly"})
        self.assertIn("A1 was 36.70 USD/MWh.", a.extra_sources(None, HISTORY))

    def test_the_words_are_ask_ercots(self):
        ask, _ = chat()
        import ercot  # noqa: E402
        self.assertEqual((ask.GENERAL_HISTORY_HEAD, ask.GENERAL_HISTORY_TURN), (ercot.HISTORY_HEAD, ercot.HISTORY_TURN))

    def test_a_refusal_records_its_reads_and_nearest(self):
        ask, tools = chat()
        c = FakeClient()
        rec = ask.Asker(model="claude-sonnet-5-5", client=c).ask("Is there a table of X?", today="2026-10-23", history=HISTORY)
        self.assertEqual(rec["status"], "not_in_warehouse")
        self.assertTrue(c.first.startswith("The conversation so far"))
        self.assertEqual([x["table"] for x in rec.get("nearest", [])], ["cost_of_power_monthly"])
        self.assertRegex(rec["nearest"][0]["holds"], r"^power data; .*from erw:cost_of_power$")
        self.assertEqual(ask.reads_of("compare", {"a": {"table": "t", "entity": "e", "aggregation": "mean"}, "b": {"table": "u", "aggregation": "sum"}}),
                         [{"table": "t", "entity": "e", "aggregation": "mean"}, {"table": "u", "aggregation": "sum"}])

    def test_the_site_says_the_same(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        script = ("const h = await import('./lib/chat/history.ts'); const a = await import('./lib/chat/ask.ts');"
                  f"const H = {json.dumps(HISTORY)};"
                  "process.stdout.write(JSON.stringify({ open: h.generalOpening('And the year before?', '2026-10-23', h.cleanTurns(H)),"
                  " reads: a.readsOf('query', { table: 't', entity: 'e', aggregation: 'mean', percentile: 9 }) }));")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        got = json.loads(r.stdout)
        ask, _ = chat()
        a = ask.Asker.__new__(ask.Asker)
        self.assertEqual(got["open"], a.opening("And the year before?", "2026-10-23", history=HISTORY))
        self.assertEqual(got["reads"], ask.reads_of("query", {"table": "t", "entity": "e", "aggregation": "mean", "percentile": 9}))


if __name__ == "__main__":
    unittest.main()
