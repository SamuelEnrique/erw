"""Session 2221 (chain 152, Ask): the Python loop's evaluation runner (warehouse/chat/eval/eval_loop.py), with no model.

Held here: a run it writes has the shape of eval_s1113_run.json (the keys replay.py, refusals.py and history.py read),
each record marked loop python and each trace entry carrying isError beside is_error; the cap stops it before a call,
the reserve being USD 0.50 until ten are asked and then one question at the dearest cost; a run file that exists is
resumed, its questions skipped; a question whose asking raises is recorded as an error and the run goes on; and the
files of a session are named by it, beside the stored runs and never over them. (The file is named with _ask because
tests/test_session2221.py is chain 098's.)
No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import importlib.util
import json
import os
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


L = module("eval_loop_for_test", os.path.join(EVAL, "eval_loop.py"))

QS = [{"id": "b01", "grid": "ERCOT", "via": "grid", "question": "q one"},
      {"id": "g01", "grid": "ERCOT", "via": "general", "question": "q two"},
      {"id": "d10", "grid": "PJM", "via": "general", "question": "q three"}]


class FakeE:
    GRID_SLUG = {"ERCOT": "ercot", "PJM": "pjm"}


class FakeAsk:
    """An Asker that answers from a script: {question: record} or {question: Exception}."""

    def __init__(self, script):
        self.script, self.made = script, []
        outer = self

        class Asker:
            def __init__(self, grid=None, record_tools=False):
                outer.made.append((grid, record_tools))

            def ask(self, question):
                r = outer.script[question]
                if isinstance(r, Exception):
                    raise r
                return r

        self.Asker = Asker


def record(answer, cost, calls=2, status="answered"):
    return {"status": status, "answer": answer, "citations": [{"table": "t"}], "tool_calls": calls, "retried": False, "cost_usd": cost,
            "seconds": 1.5, "model": "fake", "trace": [{"tool": "query", "input": {"table": "t"}, "out": {"result": [{"value": 1}]}, "is_error": False}],
            "reads": [{"table": "t"}]}


class TheRun(unittest.TestCase):
    def test_the_record_has_the_stored_runs_shape_and_the_loop_is_marked(self):
        with open(os.path.join(EVAL, "eval_s1133_s320_run.json"), encoding="utf-8") as f:
            stored = set(json.load(f)["questions"][0])
        ask = FakeAsk({"q one": record("81.40 USD per kW", 0.1), "q two": record("x", 0.2), "q three": RuntimeError("the live set did not answer")})
        with tempfile.TemporaryDirectory() as d:
            run = L.ask_all(FakeE, ask, QS, os.path.join(d, "run.json"), cap=3.0, only=None, session="9999", which="s320")
        got = {q["id"]: q for q in run["questions"]}
        self.assertEqual(sorted(got), ["b01", "d10", "g01"])
        self.assertTrue(stored <= set(got["b01"]), stored - set(got["b01"]))
        self.assertEqual([q["loop"] for q in run["questions"]], ["python"] * 3)
        self.assertEqual(got["b01"]["trace"][0]["isError"], False)
        self.assertEqual(got["b01"]["trace"][0]["is_error"], False)
        self.assertEqual(ask.made, [("ercot", True), (None, True), (None, True)])
        self.assertEqual((got["d10"]["status"], got["d10"]["cost_usd"], got["d10"]["tool_calls"]), ("error", 0.0, None))
        self.assertIn("the live set did not answer", got["d10"]["error"])
        self.assertEqual(got["b01"]["not_in_warehouse"], False)

    def test_the_cap_stops_before_the_call_and_a_run_is_resumed(self):
        ask = FakeAsk({"q one": record("a", 0.3), "q two": record("b", 0.3), "q three": record("c", 0.3)})
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "run.json")
            run = L.ask_all(FakeE, ask, QS, path, cap=0.7, only=None, session="9999", which="s320")
            # 0.3 spent + the reserve of 0.50 (fewer than ten asked) is over 0.7: the second question is never asked
            self.assertEqual([q["id"] for q in run["questions"]], ["b01"])
            self.assertEqual(len(ask.made), 1)
            run = L.ask_all(FakeE, ask, QS, path, cap=3.0, only=None, session="9999", which="s320")
            self.assertEqual([q["id"] for q in run["questions"]], ["b01", "g01", "d10"])
            self.assertEqual(len(ask.made), 3, "the first question was not asked again")
            with open(path, encoding="utf-8") as f:
                self.assertEqual([q["id"] for q in json.load(f)["questions"]], ["b01", "g01", "d10"])

    def test_the_reserve_after_ten_is_the_dearest_cost(self):
        qs = [{"id": f"q{i:02d}", "grid": "ERCOT", "via": "general", "question": f"q {i}"} for i in range(1, 14)]
        cost = {3: 0.25, 11: 0.40}
        ask = FakeAsk({f"q {i}": record("a", cost.get(i, 0.05)) for i in range(1, 14)})
        with tempfile.TemporaryDirectory() as d:
            run = L.ask_all(FakeE, ask, qs, os.path.join(d, "run.json"), cap=1.2, only=None, session="9999", which="s320")
        # before the tenth: 0.65 spent + the reserve of 0.50 = 1.15, under the cap, so it is asked (0.70); before the eleventh the
        # reserve is the dearest, 0.25: 0.95, asked (1.10, and the dearest is now 0.40); before the twelfth 1.10 + 0.40 is over.
        # Under eval_s1113's reserve of two and a half times the dearest the eleventh would not have been asked (0.70 + 0.625).
        self.assertEqual([q["id"] for q in run["questions"]], [f"q{i:02d}" for i in range(1, 12)])

    def test_the_files_are_the_sessions_own(self):
        f = L.files("2221", "s320")
        self.assertEqual({k: os.path.basename(v) for k, v in f.items()},
                         {"keys": "eval_s2221_loop_keys.json", "run": "eval_s2221_loop_run.json", "grades": "eval_s2221_loop_grades.json"})
        self.assertEqual(os.path.basename(L.files("2221", "s1114")["run"]), "eval_s2221_loop_s1114_run.json")
        for name in ("eval_s1113_run.json", "eval_s1133_s320_run.json", "eval_s1113_keys.json", "eval_s1113_grades.json"):
            self.assertNotIn(name, [os.path.basename(v) for v in f.values()])

    def test_only_asks_the_named_questions(self):
        ask = FakeAsk({"q one": record("a", 0.1), "q two": record("b", 0.1), "q three": record("c", 0.1)})
        with tempfile.TemporaryDirectory() as d:
            run = L.ask_all(FakeE, ask, QS, os.path.join(d, "run.json"), cap=3.0, only={"g01"}, session="9999", which="s320")
        self.assertEqual([q["id"] for q in run["questions"]], ["g01"])


if __name__ == "__main__":
    unittest.main()
