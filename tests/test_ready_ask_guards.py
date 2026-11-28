"""wip/ready-ask-guards (session 11406, chain 770, part C): the other choice of the chat audit of 26 November,
finding 2 (docs/reviews/ask-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main (1) warehouse/chat/eval/eval_loop.py records an errored question at USD 0, so ten questions that each spend
USD 0.25 and then fail run past a cap of USD 1.00 (stored: tr13 and tr14 of session 3280); (2) warehouse/llm.py's
check_cap reads the total from the ledger alone, so with ERW_LEDGER=0 a cap never closes. On this branch an errored
question is counted at what its client spent, and a cap set while the ledger is off is refused before the call. The
reserve the audit also asks about is not added (its size is a blank: Samuel's word). No saved answer changes; the
guards are tested with stubs only, no model call: each test sets and clears its own environment."""
import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "chat"), os.path.join("warehouse", "chat", "eval")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))


class TheCapWithTheLedgerOff(unittest.TestCase):
    def test_refused_before_the_call(self):
        import llm
        with mock.patch.dict(os.environ, {"ERW_SPEND_CAP_USD": "0.05", "ERW_LEDGER": "0"}):
            with self.assertRaises(llm.SpendCapReached):
                llm.check_cap()
        with mock.patch.dict(os.environ, {"ERW_LEDGER": "0"}):
            os.environ.pop("ERW_SPEND_CAP_USD", None)
            llm.check_cap()                      # no cap: the call goes through, as before


class AnErroredQuestionIsCounted(unittest.TestCase):
    def test_the_code(self):
        with open(os.path.join(ROOT, "warehouse", "chat", "eval", "eval_loop.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("rec, error, asker = {}, None, None", s)
        self.assertIn("cost = float(asker.client.spent())", s)

    def test_ten_failing_questions_stop_at_the_cap(self):
        try:
            import eval_loop
        except Exception as exc:
            self.skipTest(f"eval_loop does not import here: {exc}")

        class Client:
            def __init__(self):
                self.n = 0

            def spent(self):
                return 0.25 * self.n

        class Asker:
            def __init__(self, grid=None, record_tools=True):
                self.client = Client()

            def ask(self, q):
                self.client.n = 1
                raise RuntimeError("the stand-in fails after spending USD 0.25")

        ask = type("ask", (), {"Asker": Asker})
        E = type("E", (), {"GRID_SLUG": {}})
        qs = [{"id": f"q{i}", "grid": "", "via": "warehouse", "question": "?"} for i in range(10)]
        import tempfile
        with tempfile.TemporaryDirectory() as d, mock.patch.object(eval_loop, "backend_words", lambda: "stand-in"):
            run = eval_loop.ask_all(E, ask, qs, os.path.join(d, "run.json"), 1.00, None, "11406", "test")
        spent = sum(x["cost_usd"] for x in run["questions"])
        print(f"asked {len(run['questions'])} of 10, spent USD {spent:.2f} under a cap of USD 1.00 (main: 10 asked, recorded USD 0)")
        self.assertLess(len(run["questions"]), 10)
        self.assertTrue(all(x["cost_usd"] == 0.25 for x in run["questions"]))


if __name__ == "__main__":
    unittest.main()
