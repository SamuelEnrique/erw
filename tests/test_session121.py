"""Session 121: Ask ERCOT, to user-ready.

Energy Research Warehouse (ERW). No model is called and no request leaves the machine: the loop is driven by a
stand-in client that replies from a script. What these tests hold:

- a conversation: the turns before a question are in its first message (question, answer, queries), the numbers of an
  earlier answer count as given, and a question without a conversation opens exactly as it did;
- a refusal names the nearest thing held: a refusal that names no table of the guide, or a table that is not in it,
  is sent back; what the reader is shown beside each table is written by code from the guide, never by the model;
- a premise: the sentence that says what the question assumed is checked number by number as the answer is;
- time: every record says when the first thing could be shown and when the answer was whole;
- a chart: the series is set against the rows the tool returned, and the points a chart draws against the series;
- the guide's two faults the second evaluation set found (a year's demand, ERCOT's total net imports);
- the second evaluation set and its scorer;
- the site says the same things (run in Node where the site's packages are installed).

    python -m unittest tests.test_session121 -v
"""
import json
import os
import shutil
import subprocess
import sys
import types
import unittest

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
for p in ("warehouse/chat", "warehouse/chat/eval", "warehouse"):
    sys.path.insert(0, os.path.join(ROOT, *p.split("/")))
import ask  # noqa: E402
import ercot  # noqa: E402
import ercot_eval_s121 as ev  # noqa: E402
import tools  # noqa: E402

SET = os.path.join(ROOT, "warehouse", "chat", "eval", "questions_ercot_s121.yaml")
B = "storage_buildout_monthly"
BY_YEAR = {"table": B, "entity": "iso:ercot", "variable": "battery_operating_mw", "aggregation": "max", "group_by": "year", "start": "2020-01-01"}
ONE = {"table": B, "entity": "iso:ercot", "variable": "battery_operating_mw", "aggregation": "latest"}
CITE = [{"table": B, "source_report": "x", "data_version": "y", "tier": "source"}]
UPS = ["How long can the fleet run?", "How much is planned?"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def held(*tables):
    return all(os.path.exists(os.path.join(OUT, t + ".csv")) for t in tables)


class Reply:
    """One scripted reply of the stand-in model: tool calls, or a final answer."""
    def __init__(self, calls=None, final=None):
        self.usage = types.SimpleNamespace(input_tokens=10, output_tokens=5, cache_creation_input_tokens=0, cache_read_input_tokens=0)
        self._request_id = "req_test"
        if calls:
            self.stop_reason = "tool_use"
            self.content = [types.SimpleNamespace(type="tool_use", id=f"t{i}", name=n, input=a) for i, (n, a) in enumerate(calls)]
        else:
            self.stop_reason = "end_turn"
            self.content = [types.SimpleNamespace(type="text", text=json.dumps(final))]


class Client:
    def __init__(self, script):
        self.script, self.requests = list(script), []
        self.messages = types.SimpleNamespace(create=self.create)

    def create(self, **kw):
        self.requests.append({**kw, "messages": list(kw["messages"])})
        r = self.script.pop(0)
        return r(kw) if callable(r) else r


def final(answer, missing=False, nearest=None, premise="", series=(), citations=CITE, followups=UPS):
    return Reply(final={"answer": answer, "citations": [] if missing else citations, "not_in_warehouse": missing, "series": list(series), "followups": list(followups),
                        "nearest": list(nearest if nearest is not None else ([B] if missing else [])), "premise": premise})


def run(script, question="How big is the fleet?", **kw):
    c = Client(script)
    rec = ercot.ErcotAsker(model="stand-in", client=c).ask(question, today="2026-10-04", **kw)
    return rec, c


def value(args):
    tools.SCOPE = ercot.SCOPE
    return tools.query(**args)


@unittest.skipUnless(held(B), f"{B} is not on this machine")
class AConversation(unittest.TestCase):
    def test_without_one_the_first_message_is_as_it_was(self):
        _, c = run([final("Not held.", missing=True)])
        self.assertEqual(c.requests[0]["messages"][0]["content"], "Today is 2026-10-04 (UTC).\n\nQuestion: How big is the fleet?")

    def test_the_turns_before_are_in_the_first_message_and_their_numbers_count_as_given(self):
        now = value(ONE)["result"][0]["value"]
        first, _ = run([Reply(calls=[("query", ONE)]), final(f"{now} MW (storage_buildout_monthly).")])
        self.assertEqual(first["status"], "answered")
        # the follow-up repeats the earlier figure and fetches nothing new: allowed only because the conversation carries it
        rec, c = run([final(f"As said, {now} MW (storage_buildout_monthly).")], "And is that the newest?", history=[first])
        opening = c.requests[0]["messages"][0]["content"]
        self.assertIn(ercot.HISTORY_HEAD, opening)
        self.assertIn("Earlier question 1: How big is the fleet?", opening)
        self.assertIn(f"Your answer: {now} MW", opening)
        self.assertIn('Queries you ran: query {"aggregation":"latest","entity":"iso:ercot","table":"storage_buildout_monthly","variable":"battery_operating_mw"}', opening)
        self.assertTrue(opening.endswith("Question: And is that the newest?"))
        self.assertEqual((rec["status"], rec["retried"]), ("answered", False))
        # the same answer with no conversation is a number from nowhere and a table no tool read: sent back, then refused
        bare, _ = run([final(f"As said, {now} MW (storage_buildout_monthly)."), final(f"As said, {now} MW (storage_buildout_monthly).")], "And is that the newest?")
        self.assertEqual(bare["status"], "refused_unverified")

    def test_only_the_newest_turns_are_carried_and_an_answer_is_cut(self):
        hist = [{"question": f"q{i}", "answer": "a" * 5000, "calls": [], "citations": []} for i in range(6)]
        ts = ercot.turns(hist)
        self.assertEqual([t["question"] for t in ts], ["q3", "q4", "q5"])
        self.assertEqual(len(ts[0]["answer"]), ercot.MAX_HISTORY_ANSWER)
        self.assertEqual(ercot.turns([{"question": "q", "answer": ""}, "not a turn", None]), [])
        self.assertEqual(ercot.history_text(None), "")

    def test_a_number_new_to_the_follow_up_is_still_checked(self):
        first, _ = run([Reply(calls=[("query", ONE)]), final("See storage_buildout_monthly.")])
        rec, _ = run([final("It was 123456 MW (storage_buildout_monthly)."), final("It was 123456 MW (storage_buildout_monthly).")], "And a year before?", history=[first])
        self.assertEqual(rec["status"], "refused_unverified")
        self.assertIn("123456", rec["first_violations"])


@unittest.skipUnless(held(B), f"{B} is not on this machine")
class ARefusalNamesWhatIsHeld(unittest.TestCase):
    def test_a_refusal_that_names_no_table_is_sent_back(self):
        rec, c = run([final("Not in the warehouse.", missing=True, nearest=[]), final("Not in the warehouse.", missing=True, nearest=[B])])
        self.assertTrue(rec["retried"])
        self.assertIn("nearest must name one to 3 tables of the guide", " ".join(rec["first_violations"]))
        self.assertEqual(rec["status"], "not_in_warehouse")

    def test_a_table_that_is_not_in_the_guide_is_not_a_table_held(self):
        rec, _ = run([final("Not in the warehouse.", missing=True, nearest=["pjm_capacity_prices"]), final("Not in the warehouse.", missing=True, nearest=["ercot_as_prices", B])])
        self.assertTrue(rec["retried"])
        self.assertEqual([x["table"] for x in rec["nearest"]], ["ercot_as_prices", B])

    def test_what_each_table_holds_is_the_guides_sentence_not_the_models(self):
        rec, _ = run([final("Not in the warehouse.", missing=True, nearest=[B])])
        self.assertEqual(rec["nearest"], [{"table": B, "holds": ercot.HOLDS[B]}])
        self.assertEqual(set(ercot.HOLDS), set(ercot.TABLES))
        for t, h in ercot.HOLDS.items():
            self.assertTrue(h.endswith(".") and 15 < len(h) < 190, (t, h))
            self.assertNotIn("say so", h, t)
            self.assertNotIn(chr(0x2014), h)

    def test_an_answer_has_no_nearest_and_more_than_three_is_too_many(self):
        rec, _ = run([Reply(calls=[("query", ONE)]), final("See storage_buildout_monthly.", nearest=[B])])
        self.assertEqual((rec["status"], rec["nearest"]), ("answered", []))
        four = ["ercot_as_prices", B, "ercot_hub_prices_daily", "storage_capacity"]
        rec, _ = run([final("Not held.", missing=True, nearest=four), final("Not held.", missing=True, nearest=four[:3])])
        self.assertTrue(rec["retried"])
        self.assertEqual(len(rec["nearest"]), 3)

    def test_the_fixed_refusal_names_the_tables_it_read(self):
        bad = final("It was 123456 MW (storage_buildout_monthly).")
        rec, _ = run([Reply(calls=[("query", ONE)]), bad, bad])
        self.assertEqual(rec["status"], "refused_unverified")
        self.assertEqual(rec["nearest"], [{"table": B, "holds": ercot.HOLDS[B]}])

    def test_the_rule_tells_the_model_to_refuse_without_a_query_what_is_plainly_outside(self):
        self.assertIn("refuse at once, without a tool call", ercot.RULES)
        self.assertIn("List in nearest the one to three tables of the guide", ercot.RULES)


@unittest.skipUnless(held(B), f"{B} is not on this machine")
class APremise(unittest.TestCase):
    def test_its_numbers_are_checked_as_the_answers_are(self):
        now = value(ONE)["result"][0]["value"]
        q = "The fleet is over 50000 MW. When did it pass that?"
        ok = final(f"It is {now} MW (storage_buildout_monthly).", premise=f"The question assumes more than 50000 MW; the table shows {now} MW.")
        rec, _ = run([Reply(calls=[("query", ONE)]), ok], q)
        self.assertEqual((rec["status"], rec["retried"]), ("answered", False))
        self.assertIn("50000", rec["premise"])
        invented = final(f"It is {now} MW (storage_buildout_monthly).", premise="The question assumes 50000 MW; the table shows 31337 MW.")
        rec, _ = run([Reply(calls=[("query", ONE)]), invented, ok], q)
        self.assertTrue(rec["retried"])
        self.assertIn("premise contains numbers in no tool result and not in the question: 31337", " ".join(rec["first_violations"]))

    def test_a_refusal_carries_none(self):
        rec, _ = run([final("Not held.", missing=True, premise="The question assumes a thing.")])
        self.assertEqual(rec["premise"], "")

    def test_the_rules_say_what_a_premise_is_and_that_a_loose_question_is_answered(self):
        for words in ("14. A premise.", "do not go along with it", "15. A loose question.", "Never answer with a question", "13. Conversation."):
            self.assertIn(words, ercot.RULES)
        self.assertEqual(ercot.SCHEMA["required"][-2:], ["nearest", "premise"])


@unittest.skipUnless(held(B), f"{B} is not on this machine")
class TimeAndWhatIsShownFirst(unittest.TestCase):
    def test_every_record_says_when_the_first_thing_could_be_shown(self):
        seen = []
        rec, _ = run([Reply(calls=[("query", ONE), ("query", BY_YEAR)]), final("See storage_buildout_monthly.")], on_event=seen.append)
        self.assertIsNotNone(rec["seconds_first"])
        self.assertLessEqual(rec["seconds_first"], rec["seconds"])
        self.assertEqual(seen, [{"type": "reading", "tool": "query", "table": B}] * 2)

    def test_the_model_is_told_that_every_turn_costs_seconds(self):
        self.assertIn("ask for them together in one turn", ercot.RULES)


@unittest.skipUnless(held(B), f"{B} is not on this machine")
class AChartIsTheRowsFetched(unittest.TestCase):
    def test_a_series_is_checked_against_the_tools_rows(self):
        rec, _ = run([Reply(calls=[("query", BY_YEAR)]), final("See storage_buildout_monthly.", series=["r1"])])
        s = rec["series"][0]
        rows = value(BY_YEAR)["result"]
        self.assertEqual(s["check"], {"rows_fetched": len(rows), "rows": len(rows), "same": True, "points": len(rows), "not_drawn": 0})
        self.assertEqual(rec["series_not_shown"], [])

    def test_a_series_that_is_not_the_rows_is_found(self):
        out = value(BY_YEAR)
        s = ercot.series_of("r1", BY_YEAR, out)
        self.assertTrue(ercot.series_check(s, (BY_YEAR, out))["same"])
        moved = dict(s, rows=[dict(r) for r in s["rows"]])
        moved["rows"][0]["value"] += 1
        self.assertFalse(ercot.series_check(moved, (BY_YEAR, out))["same"])
        short = dict(s, rows=s["rows"][:-1])
        c = ercot.series_check(short, (BY_YEAR, out))
        self.assertEqual((c["same"], c["rows_fetched"] - c["rows"]), (False, 1))

    def test_a_row_a_chart_cannot_place_is_counted(self):
        s = {"rows": [{"key": "2021", "value": 1.0}, {"key": "2022", "value": None}, {"key": "HB_WEST", "value": 3.0}, {"key": "2023-05", "value": 2}]}
        out = {"result": [{"year": "2021", "value": 1.0}, {"year": "2022", "value": None}, {"year": "HB_WEST", "value": 3.0}, {"year": "2023-05", "value": 2}]}
        self.assertEqual(ercot.series_check(s, ({"group_by": "year"}, out)), {"rows_fetched": 4, "rows": 4, "same": True, "points": 2, "not_drawn": 2})


class TheGuidesTwoFaults(unittest.TestCase):
    """Found by the second set: the card gave ERCOT's row two variables it does not have, and gave the demand of the held
    days only as "demand"."""

    def test_the_card_names_the_variables_the_table_has(self):
        card = dict(ercot.CARDS)["ba_supply_monthly"]
        for v in ("demand_all_days_mwh", "net_import_pairs_mwh", "net_import_pairs_share_pct", "net_import_total_interchange_share_pct", "net_import_balance_share_pct"):
            self.assertIn(v, card)
        self.assertIn("never read it as the year's demand", card)
        self.assertIn("percent", dict(ercot.CARDS)["merchant_revenue_monthly"])

    @unittest.skipUnless(held("ba_supply_monthly"), "ba_supply_monthly is not on this machine")
    def test_and_the_table_has_them(self):
        import ercot_expected as E
        d = E.rd("ba_supply_monthly", ["entity", "variable", "ts_utc", "value"])
        erco = set(d[d["entity"] == "eia930:ERCO"]["variable"])
        for v in ("demand_all_days_mwh", "demand_mwh", "net_import_pairs_mwh", "net_import_pairs_share_pct", "net_import_total_interchange_mwh", "net_import_balance_mwh", "days_left_out"):
            self.assertIn(v, erco)
        self.assertNotIn("net_import_share_pct", erco)          # the name the card gave ERCOT's row until session 121
        self.assertIn("net_import_share_pct", set(d[d["entity"] == "eia930:ERCO-SWPP"]["variable"]))
        # the trap: summed over the held days, 2025 looks smaller than 2024; over all days it was larger
        y = lambda v, yr: float(d[(d["entity"] == "eia930:ERCO") & (d["variable"] == v) & (d["ts_utc"].str[:4] == yr)]["value"].sum())  # noqa: E731
        if y("days_left_out", "2025") > y("days_left_out", "2024"):
            self.assertGreater(y("demand_all_days_mwh", "2025"), y("demand_all_days_mwh", "2024"))


class TheSecondSet(unittest.TestCase):
    def setUp(self):
        self.spec = yaml.safe_load(open(SET, encoding="utf-8"))
        self.qs = self.spec["questions"]

    def test_a_hundred_questions_twenty_of_each_kind(self):
        kinds = [q["kind"] for q in self.qs]
        self.assertEqual({k: kinds.count(k) for k in ev.KINDS}, {k: 20 for k in ev.KINDS})
        self.assertEqual(len({q["id"] for q in self.qs}), 100)
        self.assertEqual(len({q["question"] for q in self.qs if q["kind"] != "followup"}), 80)

    def test_what_each_kind_must_carry(self):
        for q in self.qs:
            k = q["kind"]
            self.assertEqual(len(q["tolerances"]), len(q["expected"]), q["id"])
            if k == "join":
                self.assertEqual(len(q["tables_all"]), 2, q["id"])
                self.assertFalse(set(q["tables_all"][0]) & set(q["tables_all"][1]), f"{q['id']}: one table could stand for both")
                self.assertGreaterEqual(len(q["expected"]), 2, q["id"])
            if k == "followup":
                self.assertTrue(q["first"].endswith("?") and q["expected"], q["id"])
                self.assertLess(len(q["question"]), 60, f"{q['id']}: a follow-up that stands on its own is not one")
            if k == "premise":
                self.assertTrue(q["expected"] or q["text"] or q.get("text_any"), q["id"])
                self.assertTrue(q["note"], q["id"])
            if k == "outside":
                self.assertTrue(q["refuse"] and not q["expected"] and not q["tables"], q["id"])
                self.assertTrue(set(q["nearest"]) <= set(ercot.TABLES) | {"price_board_peak_offpeak"}, q["id"])
            if k == "vague":
                self.assertTrue(q["tables"] and not q["expected"], q["id"])
        self.assertFalse(any(q["refuse"] for q in self.qs if q["kind"] != "outside"))

    def test_no_question_repeats_the_first_set(self):
        first = {q["question"] for q in yaml.safe_load(open(os.path.join(os.path.dirname(SET), "questions_ercot.yaml"), encoding="utf-8"))["questions"]}
        self.assertFalse(first & {q["question"] for q in self.qs})

    def q(self, qid):
        return next(q for q in self.qs if q["id"] == qid)

    def rec(self, answer, tables=(), status="answered", **kw):
        return {"answer": answer, "status": status, "citations": [{"table": t, "source_report": "s", "data_version": "v"} for t in tables], **kw}

    def test_a_join_needs_both_tables_and_both_numbers(self):
        q = self.q("j01")
        a, b = q["expected"]
        both = self.rec(f"{a} USD/MWh and {b} kg/MWh.", ["cost_of_power_monthly", "carbon_intensity_monthly"])
        self.assertTrue(ev.score(q, both, ercot.TABLES)["correct"])
        one_table = ev.score(q, self.rec(f"{a} and {b}.", ["cost_of_power_monthly"]), ercot.TABLES)
        self.assertEqual((one_table["number"], one_table["citation"], one_table["correct"]), (True, False, False))
        self.assertFalse(ev.score(q, self.rec(f"{a} only.", ["cost_of_power_monthly", "carbon_intensity_monthly"]), ercot.TABLES)["number"])

    def test_each_number_has_its_own_tolerance(self):
        q = self.q("j08")                                        # a count in the thousands and a rate under a hundred
        count, rate = q["expected"]
        tables = ["ercot_peak_premium_annual", "merchant_revenue_monthly"]
        self.assertTrue(ev.score(q, self.rec(f"{count:.0f} intervals; {rate} percent.", tables), ercot.TABLES)["number"])
        self.assertFalse(ev.score(q, self.rec(f"{count:.0f} intervals; {rate + 5} percent.", tables), ercot.TABLES)["number"], "a rate five points off passed beside a large count")
        self.assertFalse(ev.score(q, self.rec(f"{count + 2:.0f} intervals; {rate} percent.", tables), ercot.TABLES)["number"], "a count is checked to the unit")

    def test_a_refusal_must_name_a_table_of_the_guide_and_the_right_one_where_one_is_named(self):
        q = self.q("o03")                                        # a household's bill: the nearest are the hub prices
        ref = lambda text, **kw: ev.score(q, self.rec(text, status="not_in_warehouse", **kw), ercot.TABLES)  # noqa: E731
        self.assertFalse(ref("Not in the warehouse: retail bills are not held.")["nearest"])
        self.assertTrue(ref("Not in the warehouse; ercot_hub_prices_daily holds wholesale hub prices.")["nearest"])
        self.assertTrue(ref("Not in the warehouse.", nearest=[{"table": "ercot_hub_prices_daily", "holds": "x"}])["nearest"])   # as the record holds it
        self.assertFalse(ref("Not in the warehouse; see storage_capacity.")["nearest"], "a table of the guide, and not a near one")
        self.assertFalse(ev.score(q, self.rec("About 14 cents (ercot_hub_prices_daily).", ["ercot_hub_prices_daily"]), ercot.TABLES)["status"])

    def test_a_premise_is_passed_by_what_the_tables_say(self):
        q = self.q("p02")                                        # "the fleet shrank": it grew
        a, b = q["expected"]
        went_along = self.rec("The fleet lost capacity over the year (storage_buildout_monthly).", ["storage_buildout_monthly"])
        self.assertFalse(ev.score(q, went_along, ercot.TABLES)["correct"])
        corrected = self.rec(f"It did not shrink: it grew from {a} MW to {b} MW (storage_buildout_monthly).", ["storage_buildout_monthly"])
        self.assertTrue(ev.score(q, corrected, ercot.TABLES)["correct"])
        q3 = self.q("p03")                                       # a product that began later: an answer or a refusal, with the year
        self.assertTrue(ev.score(q3, self.rec("Not in the warehouse: ECRS begins in June 2023.", status="not_in_warehouse"), ercot.TABLES)["correct"])
        self.assertFalse(ev.score(q3, self.rec("Not in the warehouse.", status="not_in_warehouse"), ercot.TABLES)["correct"])

    def test_a_vague_question_refused_is_wrong(self):
        q = self.q("v02")
        self.assertFalse(ev.score(q, self.rec("Not in the warehouse: please say which measure.", status="not_in_warehouse"), ercot.TABLES)["correct"])
        mw = q["any_of"][0][0]
        self.assertTrue(ev.score(q, self.rec(f"Taking this as operating capacity: {mw} MW (storage_buildout_monthly).", ["storage_buildout_monthly"]), ercot.TABLES)["correct"])


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module"], input=js, cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180, encoding="utf-8")
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2500:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheSite(unittest.TestCase):
    def test_the_chart_draws_the_rows_and_names_the_ones_it_cannot(self):
        rows = [{"key": "2021", "value": 1.5}, {"key": "2022", "value": None}, {"key": "HB_WEST", "value": 3}, {"key": "2023-05", "value": 2}, {"key": "2023-05-09 14:00", "value": -4}]
        r = node(f"""
import {{ chartPoints, pointsAreRows, isDrawn, keySeconds }} from "./lib/chat/series.ts";
const rows = {json.dumps(rows)};
const d = chartPoints(rows);
const moved = {{ points: d.points.map((p, i) => (i ? p : {{ t: p.t, v: p.v + 1 }})), undrawn: d.undrawn }};
const fewer = {{ points: d.points.slice(1), undrawn: d.undrawn }};
console.log(JSON.stringify({{ d, same: pointsAreRows(rows, d), moved: pointsAreRows(rows, moved), fewer: pointsAreRows(rows, fewer), line: isDrawn("line", d), bar: isDrawn("bar", d),
  one: isDrawn("line", chartPoints(rows.slice(0, 1))), t: [keySeconds("2021"), keySeconds("2023-05-09 14:00"), keySeconds("May")] }}));
""")
        self.assertEqual([p["v"] for p in r["d"]["points"]], [1.5, 2, -4])
        self.assertEqual(r["d"]["undrawn"], [{"key": "2022", "why": "no value"}, {"key": "HB_WEST", "why": "not a time"}])
        self.assertEqual((r["same"], r["moved"], r["fewer"]), (True, False, False))
        self.assertEqual((r["line"], r["bar"], r["one"]), (True, False, False))
        self.assertEqual(r["t"], [1609459200, 1683640800, None])
        # the Python check counts the same rows
        out = {"result": [{"month": x["key"], "value": x["value"]} for x in rows]}
        c = ercot.series_check({"rows": rows}, ({"group_by": "month"}, out))
        self.assertEqual((c["points"], c["not_drawn"]), (len(r["d"]["points"]), len(r["d"]["undrawn"])))

    def test_the_spec_carries_the_conversation_and_what_each_table_holds(self):
        spec = json.loads(src("site", "lib", "chat", "spec_ercot.json"))
        self.assertEqual((spec["history_head"], spec["history_turn"], spec["max_history"], spec["max_history_answer"], spec["max_nearest"]),
                         (ercot.HISTORY_HEAD, ercot.HISTORY_TURN, ercot.MAX_HISTORY, ercot.MAX_HISTORY_ANSWER, ercot.MAX_NEAREST))
        self.assertEqual(spec["holds"], ercot.HOLDS)
        self.assertEqual(spec["answer_schema"], ercot.SCHEMA)
        self.assertTrue(spec["system"].startswith(ercot.RULES))

    def test_the_site_writes_the_conversation_as_python_does(self):
        if not os.path.isdir(os.path.join(ROOT, "site", "node_modules", "@anthropic-ai", "sdk")):
            raise unittest.SkipTest("the site's packages are not installed on this machine (npm ci)")
        hist = [{"question": "What was the price in 2023?", "answer": "48.36 USD/MWh (ercot_hub_prices_daily).",
                 "calls": [{"tool": "query", "input": {"table": "ercot_hub_prices_daily", "variable": "rt_mean", "entity": "ercot:HB_HUBAVG", "start": "2023-01-01", "where": {"b": "x", "a": "y"}}},
                           {"tool": "describe_table", "input": {"table": "ercot_as_prices"}}],
                 "citations": [{"table": "ercot_hub_prices_daily"}, {"table": "not_a_table"}]},
                {"question": "", "answer": "dropped"}]
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        js = f"""
import {{ cleanHistory, historyText, ercotProfile }} from "./lib/chat/ercot.ts";
const h = {json.dumps(hist)};
const p = ercotProfile();
console.log(JSON.stringify({{ text: historyText(cleanHistory(h)), opening: p.opening("And in 2022?", "2026-10-04", null, h), known: p.knownTables(h), given: p.extraSources(null, h),
  problems: p.extraProblems({{ answer: "x", citations: [], not_in_warehouse: true, series: [], followups: ["One?", "Two?"], nearest: ["nope"], premise: "It was 77." }}, [], ["Was it 77?"]),
  fine: p.extraProblems({{ answer: "x", citations: [], not_in_warehouse: true, series: [], followups: ["One?", "Two?"], nearest: ["ercot_as_prices"], premise: "" }}, [], []),
  refusal: p.finish("not_in_warehouse", {{ answer: "x", citations: [], not_in_warehouse: true, series: [], followups: ["One?", "Two?"], nearest: ["ercot_as_prices", "nope"], premise: "p" }}, []) }}));
"""
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module"], input=js, cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180, encoding="utf-8")
        if r.returncode != 0:
            raise AssertionError(r.stderr[-2500:])
        j = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(j["text"], ercot.history_text(hist))
        a = ercot.ErcotAsker.__new__(ercot.ErcotAsker)
        self.assertEqual(j["opening"], a.opening("And in 2022?", "2026-10-04", None, hist))
        self.assertEqual(j["known"], sorted(a.known_tables(hist)))
        self.assertEqual(len(j["given"]), len(a.extra_sources(None, hist)))
        self.assertEqual(j["problems"], ["nearest must name one to 3 tables of the guide by their exact names, nearest first (nope given)"])   # 77 is in the question: given
        self.assertEqual(j["fine"], [])
        self.assertEqual((j["refusal"]["nearest"], j["refusal"]["premise"], j["refusal"]["series"]), ([{"table": "ercot_as_prices", "holds": ercot.HOLDS["ercot_as_prices"]}], "", []))

    def test_the_route_streams_for_ask_ercot_only_and_the_other_chats_are_called_as_they_were(self):
        route = src("site", "app", "api", "ask", "route.ts")
        self.assertIn('if (profile === "ercot" && stream === true)', route)
        self.assertIn('await ask(question.trim(), undefined, typeof grid === "string" && grid ? grid : null, null, null, { questionId: qid })', route)   # session 128: the same call, with the question's number for the ledger
        self.assertIn("The answer itself is never sent in pieces: it is checked whole first.", route)
        self.assertIn("cost_usd: r.cost_usd ?? null, seconds: r.seconds ?? null", route)       # the cost and the time of each question, in its log line
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertIn('ledger.push(recordCall(model, resp, raw.request_id, profile ? "site_ask_ercot" : "site_ask", opts.questionId))', loop)   # session 128: with the question's number
        self.assertIn("await Promise.allSettled(ledger);", loop)
        self.assertIn("const outs = await Promise.all(blocks.map((b, i) => (slots[i] ? runTool(b.name, b.input, scope) : null)));", loop)
        self.assertNotIn("await recordCall(", loop)

    def test_the_page_keeps_the_conversation_and_shows_what_the_session_added(self):
        # session 137: the page's component moved to components/ask/AskPanel.tsx, one box and panel for any page
        page = src("site", "components", "ask", "AskPanel.tsx")
        for words in ("stream: true", "history", 'data-premise="1"', "data-nearest=", "data-chart-check=", "data-progress=", 'data-new-conversation="1"',
                      "The nearest thing the warehouse does hold", "The question assumes something the tables do not show.", "chartPoints(s.rows, s.group_by)"):   # session 161: the group says whether a key is a time or an hour of the day
            self.assertIn(words, page)
        self.assertIn('"/ask/ercot": "review"', src("site", "lib", "release.ts"))

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("warehouse", "chat", "ercot.py"), ("warehouse", "chat", "ask.py"), ("warehouse", "chat", "eval", "ercot_eval_s121.py"), ("warehouse", "chat", "eval", "ercot_expected_s121.py"),
                      ("warehouse", "chat", "eval", "questions_ercot_s121.yaml"), ("site", "lib", "chat", "series.ts"), ("site", "lib", "chat", "ercot.ts"), ("site", "lib", "chat", "ask.ts"),
                      ("site", "app", "ask", "ercot", "AskErcot.tsx"), ("site", "app", "api", "ask", "route.ts"), ("site", "lib", "chat", "spec_ercot.json"), ("tests", "test_session121.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts[-1])


if __name__ == "__main__":
    unittest.main()
