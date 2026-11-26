"""Session 10234 (chain 710, part D): the chat's number check, exercised on crafted answers with no model.

docs/reviews/ask-model-audit-2026-11-26.md, finding 1. The check (warehouse/chat/ask.py unverified, unit_mismatches;
the same in site/lib/chat/ask.ts, held equal by tests/test_session1309.py) is run on drafts written by hand against
tool results stored by the evaluation (warehouse/chat/eval/eval_s5275_site_trader_run.json: the trader's tr02, a
maximum with its hour, and tr19, the held answer to a question about NYISO's Zone J, which carries the public grids'
figures and no NYISO figure). The first class passes what it should; the second stops what it should; the third is the
finding: drafts a reader would be misled by that the check lets through, because it asks only whether a figure's
magnitude, at the precision written, lies within half a unit of ANY number of ANY source (every tool result, every tool
argument, the question), never which row, grid, day or sign the number belongs to.

No model, no network, no environment set at import. Passes on main: it shows the finding, it does not fix it.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAT = os.path.join(ROOT, "warehouse", "chat")
RUN = os.path.join(CHAT, "eval", "eval_s5275_site_trader_run.json")


def ask_module():
    if CHAT not in sys.path:
        sys.path.insert(0, CHAT)
    import ask  # noqa: E402
    return ask


def stored(qid, call):
    with open(RUN, encoding="utf-8") as f:
        run = json.load(f)
    q = next(x for x in run["questions"] if x["id"] == qid)
    t = q["trace"][call]
    return q["question"], t["input"], t["out"]


def pool(question, *calls):
    """The sources as both loops build them: the question, then each call's result and its arguments."""
    out = [question]
    for inp, res in calls:
        out += [json.dumps(res), json.dumps(inp)]
    return out


class Fixtures:
    @classmethod
    def setUpClass(cls):
        cls.A = ask_module()
        q2, i2, o2 = stored("tr02", 0)      # HB_NORTH day-ahead maximum, 3 November 2026: 150 at 2026-11-04T03:00:00Z (9 pm Central, 3 November)
        cls.max_src = pool(q2, (i2, o2))
        q19, i19, o19 = stored("tr19", 1)   # the held answer: NYISO named, the public grids' figures, no NYISO figure
        assert o19.get("held") is True and o19.get("grid") == "NYISO"
        cls.held_src = pool(q19, (i19, o19))
        cls.held_out = o19
        # a mean and a compare as the tools return them (the shapes of tr01 and tr12 of the same run)
        cls.mean = {"aggregation": "mean", "rows_matched": 24, "units": ["USD/MWh"], "table": "iso_dam_hub_prices",
                    "result": [{"value": 50.795417, "entity": "ercot:HB_NORTH", "unit": "USD/MWh"}]}
        cls.diff = {"a": {"result": [{"value": 54.9369, "entity": "caiso:TH_NP15_GEN-APND"}], "units": ["USD/MWh"]},
                    "b": {"result": [{"value": 44.6725, "entity": "caiso:TH_SP15_GEN-APND"}], "units": ["USD/MWh"]},
                    "difference_b_minus_a": -10.264308, "ratio_b_over_a": 0.813}
        cls.bat = {"aggregation": "sum", "units": ["USD/MW"], "table": "battery_stack_monthly",
                   "result": [{"value": 81402.19, "entity": "ercot:HB_WEST"}]}

    def ok(self, answer, sources):
        return not self.A.unverified(answer, sources) and not self.A.unit_mismatches(answer, sources)


class PassesWhatItShould(Fixtures, unittest.TestCase):
    def test_the_figure_as_returned_and_rounded_coarser(self):
        src = pool("What was the mean?", ({"table": "iso_dam_hub_prices"}, self.mean))
        for a in ("50.795417 USD/MWh", "50.80 USD/MWh", "50.8 USD/MWh", "51 USD/MWh"):
            self.assertTrue(self.ok(f"HB_NORTH averaged {a} (iso_dam_hub_prices).", src), a)

    def test_thousands_separators_and_a_magnitude_with_its_sign_in_words(self):
        src = pool("q", ({"table": "battery_stack_monthly"}, self.bat), ({"a": {}, "b": {}}, self.diff))
        self.assertTrue(self.ok("The battery earned 81,402.19 USD/MW.", src))
        self.assertTrue(self.ok("SP15 was 10.26 USD/MWh below NP15.", src))

    def test_the_hour_and_day_as_the_tool_wrote_them_locally(self):
        self.assertTrue(self.ok("The highest was 150 USD/MWh, in the hour starting 9 pm Central, 3 November 2026.", self.max_src))

    def test_the_held_answer_as_designed(self):
        self.assertTrue(self.ok("NYISO's rows are held for a license (license needed). For the public grids: ERCOT HB_HOUSTON 64.27 USD/MWh, "
                                "CAISO TH_SP15_GEN-APND 44.67 USD/MWh (iso_trader_daily).", self.held_src))


class StopsWhatItShould(Fixtures, unittest.TestCase):
    def setUp(self):
        self.src = pool("What was the mean?", ({"table": "iso_dam_hub_prices"}, self.mean), ({"a": {}, "b": {}}, self.diff),
                        ({"table": "battery_stack_monthly"}, self.bat))

    def test_a_figure_in_no_result(self):
        self.assertEqual(self.A.unverified("HB_NORTH averaged 71.23 USD/MWh.", self.src), ["71.23"])

    def test_a_truncation_is_not_a_rounding(self):
        self.assertEqual(self.A.unverified("HB_NORTH averaged 50.79 USD/MWh.", self.src), ["50.79"])

    def test_a_sum_the_model_made(self):
        self.assertEqual(self.A.unverified("Together the two hubs come to 99.61 USD/MWh.", self.src), ["99.61"])

    def test_a_percent_the_model_made(self):
        self.assertEqual(self.A.unverified("SP15 was 18.7 percent below NP15.", self.src), ["18.7"])

    def test_a_unit_changed_by_the_model(self):
        self.assertEqual(self.A.unverified("The battery earned 81.40 USD/kW.", self.src), ["81.40"])
        self.assertEqual(len(self.A.unit_mismatches("The battery earned 81,402.19 USD/kW.", self.src)), 1)
        self.assertEqual(len(self.A.unit_mismatches("HB_NORTH averaged 50.80 USD/MW.", self.src)), 1)

    def test_a_held_grid_figure_at_two_decimals_that_no_public_grid_has(self):
        self.assertEqual(self.A.unverified("NYISO's Zone J averaged 61.15 USD/MWh.", self.held_src), ["61.15"])


class LetsThroughWhatItShouldNot(Fixtures, unittest.TestCase):
    """The finding: each of these passes both checks."""

    def test_a_public_figure_pinned_on_the_held_grid(self):
        # HB_HOUSTON's 64.2746 written as NYISO's: the check never asks whose figure it is
        self.assertTrue(self.ok("NYISO's Zone J averaged 64.27 USD/MWh on 3 November 2026 (iso_trader_daily).", self.held_src))

    def test_a_whole_number_for_the_held_grid_passes_on_any_public_figure_within_half_a_unit(self):
        self.assertTrue(self.ok("NYISO's Zone J averaged 64 USD/MWh on 3 November 2026.", self.held_src))
        self.assertTrue(self.ok("NYISO's Zone J averaged 57 USD/MWh on 3 November 2026.", self.held_src))
        self.assertNotIn("64", json.dumps(self.held_out).replace("64.2746", ""))   # 64 stands in the result only as HB_HOUSTON's

    def test_the_utc_day_and_hour_written_as_the_local_ones(self):
        # the maximum's hour began 2026-11-04T03:00:00Z, which is 9 pm Central on 3 November; both wrong forms pass
        self.assertTrue(self.ok("The highest was 150 USD/MWh, in the hour starting 9 pm Central, 4 November 2026.", self.max_src))
        self.assertTrue(self.ok("The highest was 150 USD/MWh, in the hour starting 3 am Central, 4 November 2026.", self.max_src))

    def test_the_wrong_direction(self):
        src = pool("SP15 minus NP15?", ({"a": {}, "b": {}}, self.diff))
        self.assertTrue(self.ok("SP15 was 10.26 USD/MWh above NP15.", src))

    def test_a_number_the_question_supplies_is_stated_as_a_fact(self):
        q = "Did ERCOT's North hub average 200 USD/MWh on 3 November 2026?"
        src = pool(q, ({"table": "iso_dam_hub_prices"}, self.mean))
        self.assertTrue(self.ok("Yes: HB_NORTH averaged 200 USD/MWh on 3 November 2026 (iso_dam_hub_prices).", src))

    def test_a_number_the_model_put_in_its_own_tool_argument(self):
        # a threshold the model chose counts as a source: written back as a price, it passes
        arg = {"table": "iso_rtm_hub_prices", "aggregation": "count", "threshold": {"above": 512.33}}
        res = {"aggregation": "count", "result": [{"count": 0}], "units": ["USD/MWh"], "threshold": {"above": 512.33, "rows_kept": 0}}
        src = ["How high did HB_WEST go?"] + [json.dumps(res), json.dumps(arg)]
        self.assertTrue(self.ok("HB_WEST peaked at 512.33 USD/MWh (iso_rtm_hub_prices).", src))

    def test_a_money_unit_written_without_a_money_word_is_not_judged(self):
        src = pool("q", ({"table": "battery_stack_monthly"}, self.bat))
        self.assertEqual(self.A.unit_mismatches("The battery earned 81,402.19 USD per kW.", src), ["81402.19 USD/kW (the tools gave it in USD/MW)"])
        self.assertEqual(self.A.unit_mismatches("The battery earned 81,402.19 per kW.", src), [])
        self.assertEqual(self.A.unit_mismatches("The battery earned 81,402.19 a kW.", src), [])

    def test_a_small_whole_number_passes_on_a_date_or_a_count_of_the_result(self):
        # the result's own stamps, local times and counts put 0, 3, 4, 9, 11, 12, 24 and 2026 in the pool: a count of 3
        # hours, 11 intervals or 12 days that the tool never returned passes
        for n in ("3 hours", "11 intervals", "12 days"):
            self.assertTrue(self.ok(f"The price stood at its high for {n}.", self.max_src), n)
        self.assertFalse(self.ok("The price stood at its high for 7 hours.", self.max_src))


class TheWholeLoopWithAStubbedModel(Fixtures, unittest.TestCase):
    """The Python loop (ask.Asker) end to end: a stub stands for the model (no client is built, no request is sent) and
    for the tools (the stored held result of tr19 is handed back). A draft that pins a public grid's figure on the held
    grid is let through as an answer, at the first draft, with no retry."""

    def test_a_held_grid_draft_with_a_public_figure_is_answered(self):
        from types import SimpleNamespace as NS
        A = self.A
        held = self.held_out
        draft = {"answer": "NYISO's rows are held for a license (license needed). NYISO's Zone J averaged 64 USD/MWh on 3 November 2026.",
                 "citations": [{"table": "iso_trader_daily", "source_report": "erw:trader_view", "data_version": "x", "tier": "derived"}],
                 "not_in_warehouse": False}
        usage = NS(input_tokens=10, output_tokens=5, cache_creation_input_tokens=0, cache_read_input_tokens=0)
        turns = [NS(stop_reason="tool_use", usage=usage, _request_id="r1",
                    content=[NS(type="tool_use", id="t1", name="query",
                                input={"table": "iso_trader_daily", "aggregation": "mean", "entity": "nyiso:N.Y.C.", "variable": "da_mean_usd",
                                       "start": "2026-11-03", "end": "2026-11-04"})]),
                 NS(stop_reason="end_turn", usage=usage, _request_id="r2", content=[NS(type="text", text=json.dumps(draft))])]
        sent = []

        class Messages:
            def create(self, **kw):
                sent.append(kw)
                return turns[len(sent) - 1]

        saved = {k: getattr(A.tools, k) for k in ("run", "live_only", "provenance", "nearest_for", "set_scope")}
        try:
            A.tools.run = lambda name, args: (held, False)
            A.tools.live_only = lambda: False
            A.tools.provenance = lambda t: {"tier": "derived"}
            A.tools.nearest_for = lambda tables: []
            A.tools.set_scope = lambda slug: None
            rec = A.Asker(model="stub-model", client=NS(messages=Messages())).ask("What was the day-ahead average in NYISO's Zone J on 3 November 2026?", today="2026-11-14")
        finally:
            for k, v in saved.items():
                setattr(A.tools, k, v)
        self.assertEqual(len(sent), 2)
        self.assertEqual(rec["status"], "answered")
        self.assertFalse(rec["retried"])
        self.assertIn("Zone J averaged 64 USD/MWh", rec["answer"])


if __name__ == "__main__":
    unittest.main()
