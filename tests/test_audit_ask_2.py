"""Session 10234 (chain 710, part D): the spending guards of the chat, at their edges, with stubbed clients only.

docs/reviews/ask-model-audit-2026-11-26.md, finding 2. No client of the model's provider is built and no request is
sent: every "client" here is a stub that counts what would have been sent. The ledger file is never written
(ERW_LEDGER=0) and never read from the repository (its path is a missing file in a temporary folder).

  warehouse/llm.py check_cap      the session cap (ERW_SPEND_CAP_USD) before each call: a cap of 0 refuses; a call that
                                  starts under the cap is sent whatever it costs (no reserve), so a session ends above
                                  its cap by up to one call; with the ledger off the cap is blind, because the session's
                                  total is read from the ledger file alone.
  warehouse/llm.py guarded        the key's own limit: the provider's refusal is kept, and no later call is sent.
  eval/eval_loop.py ask_all       the evaluation's cap with its reserve (USD 0.50 for the first ten questions): strict
                                  at the edge; and a question that ends in an error is counted at USD 0, so the calls it
                                  made before the error are not under the cap (tr13 and tr14 of session 3280 were so).
  site/lib/chat/ledger.ts         a visitor's call whose ledger row fails to write is logged and not counted; only an
                                  evaluation's write is strict. The ceilings count the ledger, so they do not close for
                                  a call the ledger lost (read from the source, no node).

Each test clears and sets ERW_SPEND_CAP_USD itself. Passes on main: it shows the finding, it does not fix it.
"""
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace as NS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAREHOUSE = os.path.join(ROOT, "warehouse")
EVAL = os.path.join(WAREHOUSE, "chat", "eval")
MODEL = "claude-sonnet-5"   # USD 2 a million input tokens, USD 10 a million output tokens (warehouse/config/model_prices.yaml)


def llm_module():
    if WAREHOUSE not in sys.path:
        sys.path.insert(0, WAREHOUSE)
    import llm  # noqa: E402
    return llm


class StubInner:
    """Stands for the provider's client: counts the calls that would have been sent; each costs `out` output tokens."""

    def __init__(self, out=30_000, fail=None):
        self.sent, self.out, self.fail = 0, out, fail
        self.messages = NS(create=self.create)

    def create(self, **kw):
        self.sent += 1
        if self.fail:
            raise self.fail
        return NS(model=MODEL, _request_id=f"req{self.sent}",
                  usage=NS(input_tokens=0, output_tokens=self.out, cache_creation_input_tokens=0, cache_read_input_tokens=0))


class Env:
    def setUp(self):
        self.L = llm_module()
        self.saved_env = {k: os.environ.get(k) for k in ("ERW_SPEND_CAP_USD", "ERW_LEDGER", "ERW_SESSION")}
        os.environ.pop("ERW_SPEND_CAP_USD", None)
        os.environ["ERW_LEDGER"] = "0"
        os.environ["ERW_SESSION"] = "audit10234"
        self.tmp = tempfile.mkdtemp(prefix="audit_ask_2_")
        self.saved = {k: getattr(self.L, k) for k in ("session_total", "ledger_path")}
        self.L.ledger_path = lambda: os.path.join(self.tmp, "no_ledger_here.csv")
        self.L.reset_key_limit()

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(self.L, k, v)
        for k, v in self.saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.L.reset_key_limit()

    def ledger(self, start):
        """A stand-in for the session's ledger total: starts at `start` and grows by each recorded call's cost."""
        book = {"usd": start}
        self.L.session_total = lambda name=None: book["usd"]
        return book


class TheSessionCap(Env, unittest.TestCase):
    def call(self, client, book=None):
        client.messages.create(model=MODEL, max_tokens=10, messages=[])
        if book is not None:
            book["usd"] += float(client.calls[-1]["usd"])

    def test_a_cap_of_zero_refuses_before_the_call(self):
        self.ledger(0.0)
        os.environ["ERW_SPEND_CAP_USD"] = "0"
        inner = StubInner()
        with self.assertRaises(self.L.SpendCapReached):
            self.call(self.L.wrap(inner, "chat"))
        self.assertEqual(inner.sent, 0)

    def test_a_call_that_starts_under_the_cap_is_sent_whatever_it_costs(self):
        book = self.ledger(0.99)
        os.environ["ERW_SPEND_CAP_USD"] = "1.00"
        inner = StubInner(out=30_000)          # USD 0.30 at the configured price
        client = self.L.wrap(inner, "chat")
        self.call(client, book)
        self.assertEqual(inner.sent, 1)
        self.assertAlmostEqual(book["usd"], 1.29, places=6)   # 0.29 over the cap: there is no reserve
        with self.assertRaises(self.L.SpendCapReached):
            self.call(client, book)
        self.assertEqual(inner.sent, 1)

    def test_at_the_cap_exactly_the_call_is_refused(self):
        self.ledger(1.00)
        os.environ["ERW_SPEND_CAP_USD"] = "1.00"
        inner = StubInner()
        with self.assertRaises(self.L.SpendCapReached):
            self.call(self.L.wrap(inner, "chat"))
        self.assertEqual(inner.sent, 0)

    def test_with_the_ledger_off_the_cap_never_closes(self):
        # the session's total is read from the ledger file; with ERW_LEDGER=0 no row is written, so it stays at 0
        os.environ["ERW_SPEND_CAP_USD"] = "0.05"
        inner = StubInner(out=30_000)
        client = self.L.wrap(inner, "chat")
        for _ in range(10):
            self.call(client)
        self.assertEqual(inner.sent, 10)
        self.assertAlmostEqual(client.spent(), 3.0, places=6)   # USD 3.00 sent under a cap of USD 0.05


class TheKeysOwnLimit(Env, unittest.TestCase):
    def test_a_refused_call_is_kept_and_no_later_call_is_sent(self):
        self.ledger(0.0)
        os.environ["ERW_SPEND_CAP_USD"] = "5"
        refusal = Exception("Error code: 400")
        refusal.body = {"error": {"message": "You have reached your specified API usage limits. You will regain access on 2026-12-01 at 00:00 UTC."}}
        inner = StubInner(fail=refusal)
        client = self.L.wrap(inner, "chat")
        with self.assertRaises(self.L.KeyLimitReached):
            client.messages.create(model=MODEL, max_tokens=10, messages=[])
        with self.assertRaises(self.L.KeyLimitReached):
            client.messages.create(model=MODEL, max_tokens=10, messages=[])
        self.assertEqual(inner.sent, 1)
        self.assertEqual(self.L.key_limit()["returns"], "2026-12-01 at 00:00 UTC")


def eval_loop():
    if EVAL not in sys.path:
        sys.path.insert(0, EVAL)
    if os.path.dirname(EVAL) not in sys.path:
        sys.path.insert(0, os.path.dirname(EVAL))
    import eval_loop as EL  # noqa: E402
    return EL


class TheEvaluationsCap(unittest.TestCase):
    def setUp(self):
        self.saved = os.environ.get("ERW_SPEND_CAP_USD")
        os.environ.pop("ERW_SPEND_CAP_USD", None)
        self.EL = eval_loop()
        self.tmp = tempfile.mkdtemp(prefix="audit_ask_2_eval_")
        self.E = NS(GRID_SLUG={})
        self.qs = [{"id": f"q{i:02d}", "grid": None, "via": "general", "question": f"question {i}"} for i in range(1, 11)]

    def tearDown(self):
        if self.saved is None:
            os.environ.pop("ERW_SPEND_CAP_USD", None)
        else:
            os.environ["ERW_SPEND_CAP_USD"] = self.saved

    def stub(self, cost, fail=False):
        spent = {"usd": 0.0, "questions": 0}

        class Asker:
            def __init__(self, grid=None, record_tools=False):
                pass

            def ask(self, question):
                spent["questions"] += 1
                spent["usd"] += cost            # what the calls of this question cost before it ended
                if fail:
                    raise RuntimeError("final message is not JSON: ...")
                return {"status": "answered", "answer": "x", "cost_usd": cost, "tool_calls": 1}
        return NS(Asker=Asker), spent

    def run_all(self, ask, cap):
        path = os.path.join(self.tmp, f"run_{cap}.json")
        return self.EL.ask_all(self.E, ask, self.qs, path, cap, None, "10234", "audit")

    def test_the_reserve_at_its_edge(self):
        ask, spent = self.stub(0.20)
        self.run_all(ask, 0.49)                 # 0 + 0.50 > 0.49: nothing asked
        self.assertEqual(spent["questions"], 0)
        ask, spent = self.stub(0.20)
        self.run_all(ask, 0.70)                 # 0 + 0.50 <= 0.70 asked; 0.20 + 0.50 <= 0.70 asked; 0.40 + 0.50 > 0.70 stops
        self.assertEqual(spent["questions"], 2)

    def test_a_question_that_ends_in_an_error_is_counted_at_nothing(self):
        ask, spent = self.stub(0.25, fail=True)
        run = self.run_all(ask, 1.00)
        self.assertEqual(spent["questions"], 10)                       # every question asked
        self.assertAlmostEqual(spent["usd"], 2.50, places=6)           # USD 2.50 of calls under a cap of USD 1.00
        self.assertEqual(sum(q["cost_usd"] for q in run["questions"]), 0.0)


class TheSitesLedger(unittest.TestCase):
    """Read from the source: a visitor's failed ledger write is not strict, so its cost is never counted."""

    def read(self, rel):
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            return f.read()

    def test_only_an_evaluations_ledger_write_is_strict(self):
        ledger = self.read("site/lib/chat/ledger.ts")
        self.assertIn("if (strict) throw", ledger)
        self.assertIn("console.error(`[erw] cost ledger:", ledger)
        route = self.read("site/app/api/ask/route.ts")
        self.assertIn("const ledgerOpts = evaluation ? { step: EVAL_STEP, strictLedger: true, record: true } : {};", route)
        ask = self.read("site/lib/chat/ask.ts")
        self.assertIn("if (opts.strictLedger) await row; else ledger.push(row);", ask)
        self.assertIn("await Promise.allSettled(ledger);", ask)

    def test_the_note_says_it_fails_closed_and_that_a_lost_row_is_not_counted(self):
        note = self.read("docs/methods/ask_limits.md")
        self.assertIn("**It fails closed.**", note)
        self.assertIn("A call that fails to reach the ledger is not counted.", note)


if __name__ == "__main__":
    unittest.main()
