"""Session 2237 (chain 156): the daily step's failure mode, and the backfill's estimate.

From 26 to 30 October 2026 both extractors failed with "all 1 calls failed" while the API said "You have reached your
specified API usage limits". `warehouse/deals/calls.py` keeps the API's words, stops at the spending limit, retries a
refusal once and a busy API twice; an extractor whose every call failed writes no table. No model, no network, no
wait (the sleep is a fake).
"""

import json
import os
import sys
import tempfile
import types
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (os.path.join(ROOT, "warehouse", "deals"), os.path.join(ROOT, "warehouse", "deals", "eval"),
          os.path.join(ROOT, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import calls  # noqa: E402
import crosscheck  # noqa: E402
import deals_backfill as bf  # noqa: E402
import fixture  # noqa: E402

LIMIT = ("You have reached your specified API usage limits. You will regain access on 2026-11-01 at 00:00 UTC.")


class LimitError(Exception):
    status_code = 400

    def __init__(self):
        super().__init__(f"Error code: 400 - {{'type': 'error', 'error': {{'message': '{LIMIT}'}}}}")
        self.body = {"type": "error", "error": {"type": "invalid_request_error", "message": LIMIT}}


class Busy(Exception):
    status_code = 529


def answer(stop="end_turn", text='{"results": []}'):
    return types.SimpleNamespace(usage=types.SimpleNamespace(input_tokens=1, output_tokens=1, cache_creation_input_tokens=0,
                                                             cache_read_input_tokens=0),
                                 stop_reason=stop, content=[types.SimpleNamespace(type="text", text=text)],
                                 _request_id="req_test")


class Scripted:
    """A client that answers from a list: an exception is raised, an answer returned."""

    def __init__(self, script):
        self.script, self.n = list(script), 0
        self.messages = self

    def create(self, **kw):
        self.n += 1
        x = self.script.pop(0) if len(self.script) > 1 else self.script[0]
        if isinstance(x, Exception):
            raise x
        return x


class TheCall(unittest.TestCase):
    def setUp(self):
        self.waits, self.lines = [], []

    def call(self, client):
        return calls.call(client, {}, [], self.lines.append, "call 1", sleep=self.waits.append)

    def test_the_spending_limit_stops_with_the_apis_words(self):
        c = Scripted([LimitError()])
        with self.assertRaises(calls.Stop) as cm:
            self.call(c)
        self.assertEqual(c.n, 1)   # no retry
        self.assertIn("the API's spending limit", cm.exception.words)
        self.assertIn("regain access on 2026-11-01", cm.exception.words)

    def test_a_refusal_is_tried_once_more(self):
        c = Scripted([answer(stop="refusal"), answer()])
        resp, text = self.call(c)
        self.assertEqual(c.n, 2)
        self.assertEqual(json.loads(text), {"results": []})
        c = Scripted([answer(stop="refusal")])
        with self.assertRaises(calls.Failed) as cm:
            self.call(c)
        self.assertEqual(c.n, 2)
        self.assertIn("refused", cm.exception.words)

    def test_a_busy_api_is_tried_twice_more_with_waits(self):
        c = Scripted([Busy("overloaded"), Busy("overloaded"), answer()])
        self.call(c)
        self.assertEqual(c.n, 3)
        self.assertEqual(self.waits, [10, 30])

    def test_an_answer_that_is_not_json_is_tried_once_more(self):
        c = Scripted([answer(text="not json at all"), answer()])
        self.call(c)
        self.assertEqual(c.n, 2)


class TheExtractor(unittest.TestCase):
    """On the spending limit, the extractor writes no table and says why in the API's words."""

    def test_no_table_is_written_when_no_call_answers(self):
        ex = fixture.load_extract()
        with fixture.sandbox(ex, Scripted([LimitError()]), "replay") as tmp:
            fixture.write_news(ex, tmp, fixture.read("stories_2232.json"))
            rc = ex.main([])
            log = fixture.log_of(tmp)
            self.assertEqual(rc, 1)
            self.assertFalse(os.path.exists(os.path.join(tmp, "energy_deals.csv")))
            self.assertFalse(os.path.exists(ex.CHECKED))   # every story stays to be sent again
            st = "".join(open(os.path.join(tmp, "status", f), encoding="utf-8").read()
                         for f in os.listdir(os.path.join(tmp, "status")))
        self.assertIn("no further call is sent", log)
        self.assertIn("the tables are not rewritten", st)
        self.assertIn("spending limit", st)
        self.assertNotIn("all 1 calls failed", st)


class TheBackfill(unittest.TestCase):
    def test_the_estimate(self):
        d = tempfile.mkdtemp(prefix="erw_s2237_bf_")
        rows = []
        for i in range(40):   # the 14 days before: 40 scored stories, 4 of them deals, 2 datacenters
            rows.append({"event_id": f"news:a{i}", "event_date": "2026-10-20T10:00:00Z", "cluster_id": f"news:a{i}",
                         "sector": "deal" if i < 4 else "datacenter_power" if i < 6 else "other",
                         "significance": "7", "scored_at": "2026-10-20T11:00:00Z"})
        for i in range(100):  # the window: 100 unscored stories on one day
            rows.append({"event_id": f"news:b{i}", "event_date": "2026-10-27T10:00:00Z", "cluster_id": f"news:b{i}",
                         "sector": "", "significance": "", "scored_at": ""})
        pd.DataFrame(rows).to_csv(os.path.join(d, "news_stories.csv"), index=False)
        days, shares = bf.estimate("2026-10-27", "2026-10-28", out_dir=d)
        self.assertEqual(int(days["unscored"].sum()), 100)
        self.assertAlmostEqual(shares["deal_share"], 0.15)   # the deal extractor takes datacenter_power too
        self.assertEqual(list(days.loc[days["stories"] == 0, "day"]), ["2026-10-28"])
        p = bf.plan(days, shares, {"score": (0.02, 0.001, 5), "deals": (0.05, None, 5), "datacenters": (0.03, None, 5)})
        by = p.set_index("step")
        self.assertEqual(by.loc["score", "calls"], 4)          # 100 stories, 25 a call
        self.assertAlmostEqual(by.loc["score", "usd"], 0.1)    # 100 stories at USD 0.001
        self.assertEqual(by.loc["deals", "calls"], 2)          # 15 stories, one cluster each, 12 a call

    def test_the_costs_are_read_from_the_runs(self):
        c = bf.step_costs(os.path.join(ROOT, "warehouse", "metadata", "run_status.csv"))
        for step in ("score", "deals", "datacenters"):
            self.assertIsNotNone(c[step][0], step)


class ARateIsNotASize(unittest.TestCase):
    def test_a_target_a_year_is_not_compared(self):
        t = "Return secures 835 million first-of-its-kind financing for Germany BESS rollout, targets 1GW annually"
        self.assertEqual(crosscheck.stated(t)["mw"], [])
        self.assertEqual(crosscheck.stated("Amazon and AEP to explore deployment of up to 960MW of X-energy SMRs")["mw"], [960.0])


if __name__ == "__main__":
    unittest.main()
