"""Session 30: the cost ledger's pricing and spend cap, the shadow scorer's switches, the story caps, and the price
board's calendar rules.

Energy Research Warehouse (ERW). No test calls the Anthropic API: the ledger is exercised with a fake client, and
every file is written under a temporary directory.

    python -m unittest discover -s tests -v
"""

import datetime as dt
import os
import shutil
import sys
import tempfile
import types
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/news", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, p))

import iso_prices as ip  # noqa: E402
import llm  # noqa: E402
import price_board  # noqa: E402


def usage(i=1000, o=100, cr=0, cw=0):
    return types.SimpleNamespace(input_tokens=i, output_tokens=o, cache_read_input_tokens=cr,
                                 cache_creation_input_tokens=cw, cache_creation=None, server_tool_use=None)


class FakeMessages:
    def __init__(self, model):
        self.model = model

    def create(self, **kwargs):
        return types.SimpleNamespace(model=self.model, usage=usage(), _request_id=f"req_{id(kwargs)}")


class Fake:
    def __init__(self, model):
        self.messages = FakeMessages(model)


class TestLedger(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old = ip.OUT_DIR, ip.LOG_DIR, ip.METADATA_DIR, ip.STATUS_DIR, ip.RAW_DIR
        ip.set_out_dir(self.tmp)
        os.environ["ERW_SESSION"] = "test30"
        llm._REGISTERED = False

    def tearDown(self):
        ip.OUT_DIR, ip.LOG_DIR, ip.METADATA_DIR, ip.STATUS_DIR, ip.RAW_DIR = self.old
        for k in ("ERW_SESSION", "ERW_SPEND_CAP_USD"):
            os.environ.pop(k, None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_dated_model_id_is_priced_as_its_alias(self):
        self.assertEqual(llm.price_of("claude-haiku-4-5-20251001"), llm.price_of("claude-haiku-4-5"))
        self.assertIsNone(llm.price_of("no-such-model"))

    def test_cache_prices(self):
        n = llm.usage_numbers(usage(i=1000, o=100, cr=5000, cw=2000))
        # Sonnet 5.5: 1000 x 2 + 100 x 10 + 5000 x 0.2 + 2000 x 2.5, per million
        self.assertAlmostEqual(llm.usd("claude-sonnet-5-5", n), (2000 + 1000 + 1000 + 5000) / 1e6)
        self.assertAlmostEqual(llm.uncached_usd("claude-sonnet-5-5", n), (8000 * 2 + 1000) / 1e6)

    def test_every_call_is_a_ledger_row_and_the_cap_stops_calls(self):
        c = llm.wrap(Fake("claude-sonnet-5-5"), "test_step")
        c.messages.create(model="claude-sonnet-5-5", max_tokens=10, messages=[])
        c.messages.create(model="claude-sonnet-5-5", max_tokens=10, messages=[])
        led = llm.read_ledger()
        self.assertEqual(len(led), 2)
        self.assertEqual(set(led["step"]), {"test_step"})
        self.assertAlmostEqual(llm.session_total(), 2 * (1000 * 2 + 100 * 10) / 1e6)
        os.environ["ERW_SPEND_CAP_USD"] = "0.000001"
        with self.assertRaises(llm.SpendCapReached):
            c.messages.create(model="claude-sonnet-5-5", max_tokens=10, messages=[])
        self.assertEqual(len(llm.read_ledger()), 2)  # the refused call sent nothing and wrote nothing


class TestShadowSwitches(unittest.TestCase):
    def test_kill_switch_and_expiry(self):
        import shadow
        old = os.environ.pop("SHADOW_MODEL", None)
        try:
            model, why = shadow.gate(print)
            self.assertIsNone(model)
            self.assertIn("kill switch", why)
            os.environ["SHADOW_MODEL"] = "claude-haiku-4-5"
            expires = shadow.config()["expires"]
            model, why = shadow.gate(print)
            today = dt.datetime.now(dt.timezone.utc).date().isoformat()
            self.assertEqual(model is None, today >= expires)
        finally:
            os.environ.pop("SHADOW_MODEL", None)
            if old is not None:
                os.environ["SHADOW_MODEL"] = old


class TestStoryCaps(unittest.TestCase):
    def test_caps_cut_by_source_then_run_and_keep_priority(self):
        import score
        now = pd.Timestamp.now(tz="UTC")
        past = pd.DataFrame({"event_id": [f"p{i}" for i in range(6)], "source": ["A"] * 3 + ["B"] * 3,
                             "significance": ["8"] * 3 + ["2"] * 3, "scored_at": ["x"] * 6,
                             "event_date": [ip.utc_iso(now - pd.Timedelta(days=1))] * 6})
        todo = pd.DataFrame({"event_id": [f"t{i}" for i in range(10)], "source": ["A"] * 5 + ["B"] * 5,
                             "significance": [""] * 10, "scored_at": [""] * 10,
                             "event_date": [ip.utc_iso(now - pd.Timedelta(hours=i)) for i in range(10)]})
        todo["_when"] = pd.to_datetime(todo["event_date"], utc=True)
        df = pd.concat([past, todo.drop(columns="_when")], ignore_index=True)
        kept, cut = score.apply_caps(todo, df, lambda m: None, per_run=5, per_source=3)
        self.assertEqual(len(kept), 5)
        self.assertEqual((kept["source"] == "A").sum(), 3)  # A has the higher mean significance
        self.assertEqual(len(cut), 5)


class TestBoardCalendar(unittest.TestCase):
    def test_nerc_holidays(self):
        h = price_board.nerc_holidays([2026, 2027])
        self.assertIn(dt.date(2026, 9, 7), h)    # Labor Day
        self.assertIn(dt.date(2026, 11, 26), h)  # Thanksgiving
        self.assertIn(dt.date(2026, 5, 25), h)   # Memorial Day
        self.assertIn(dt.date(2027, 7, 5), h)    # Independence Day, a Sunday, moves to Monday
        self.assertNotIn(dt.date(2026, 7, 3), h)  # a Saturday holiday is not moved to Friday

    def test_peak_days_by_iso(self):
        local = pd.Series(pd.to_datetime(["2026-09-26 12:00", "2026-09-28 12:00", "2026-09-28 05:00",
                                          "2026-09-07 12:00"]).tz_localize("America/Chicago"))
        hol = price_board.nerc_holidays([2026])
        self.assertEqual(list(price_board.is_peak(local, "ercot", hol)), [False, True, False, False])
        self.assertEqual(list(price_board.is_peak(local, "caiso", hol)), [True, True, False, False])


if __name__ == "__main__":
    unittest.main()
