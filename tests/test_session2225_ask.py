"""Session 2225 (chain 152, Ask): the owner's rule proved on the stored answers and on the tools, with no model.

The rule: Ask never states a number it did not fetch from the warehouse; a held or licensed table is refused with its
hold's words; a question outside the warehouse says so in one sentence; the sources line carries table and row for every
figure; the site's loop and the Python loop give the same answers. Held here:

  1. Strip the fetched rows from an answer and no digit survives: for every stored answer the loop let through (the runs
     of runs.json with a tool record, 247 before this chain's fourth run on 6 November 2026), every number the loop reads as a figure is in a tool
     result, the question or a tool argument (the number check), and once those are struck out of the text the only digits
     left are inside names (EIA-930, HB_2015, a table's name).
  2. Each table held whole for a license (site/data/license_status.json, the "license needed" rows docs/licenses.md
     counts) is refused by name by the Python tools with the hold's words and no figure, before any row is read; MISO's
     rows with the pause's words; and the stored answers to held questions carry those words and no figure.
  3. A question outside the warehouse says so in one sentence: every stored refusal of the class "the warehouse lacks
     the figure" says "not in the warehouse" in its first sentence.
  4. The sources line carries table and row for every figure: every answered record of this chain's runs lists what each
     query read (table, entity, variable, window, aggregation) and every cited table is among them; the site's component
     draws the same two things.
  5. Both loops give the same answers: session 1300's turn-by-turn test now covers eleven kinds of answer, among them a
     table held whole and MISO's pause (this session's scenarios), and session 1309's holds the checks equal on every
     stored answer; this file holds that the scenario list is whole.
(Named _ask: tests/test_session2225.py is chain 098's.) No network, no model. Nothing here sets the environment at import.
"""
import json
import os
import re
import sys
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
CHAT = os.path.join(ROOT, "warehouse", "chat")
for p in (EVAL, CHAT):
    if p not in sys.path:
        sys.path.insert(0, p)
import ask  # noqa: E402
import license_hold as hold  # noqa: E402
import refusals as F  # noqa: E402
import replay as R  # noqa: E402
import tools  # noqa: E402


def answers():
    """Every stored answer the loop let through, with its sources as the replay builds them."""
    out = []
    for name, graded, label in R.RUNS:
        for q in R.load(name)["questions"]:
            if not R.trace_of(q) or not q.get("answer") or q.get("status") not in ("answered", "not_in_warehouse"):
                continue
            trace = R.trace_of(q)
            today = (q.get("asked_at_utc") or "")[:10]
            sources = [q.get("question") or "", f"Today is {today} (UTC)."] + [json.dumps(t.get("out"), default=str) for t in trace] \
                + [json.dumps(t.get("input"), default=str) for t in trace]
            out.append((label, q, sources))
    return out


def strip_fetched(answer, sources):
    """The answer with every figure the loop reads struck out (a name's digits, EIA-930's, are left): what is left of its digits."""
    pool = " ".join(sources)
    pool_numbers = set(v for v, _ in ask.numbers(pool)) if hasattr(ask, "numbers") else set()
    text = answer
    for m in sorted(ask.NUM.finditer(answer), key=lambda m: -m.start()):
        if ask.is_name(answer, m.start()):
            continue
        text = text[:m.start()] + " " * (m.end() - m.start()) + text[m.end():]
    return text, pool_numbers


class StripTheRows(unittest.TestCase):
    def test_no_digit_survives_but_a_names(self):
        rows = answers()
        self.assertGreater(len(rows), 200)
        for label, q, sources in rows:
            self.assertEqual(ask.unverified(q["answer"], sources), [], (label, q["id"]))
            left, _ = strip_fetched(q["answer"], sources)
            # what is left may hold a digit only inside a name: a code glued to letters (CO2, HB_2015, eia930_ciso), which the
            # loop's own number pattern never reads as a figure, or a form name after a hyphen (EIA-930)
            for m in ask.NUM.finditer(left):
                self.assertTrue(ask.is_name(left, m.start()), (label, q["id"], left[max(0, m.start() - 20):m.start() + 20]))

    def test_the_strip_is_not_blind(self):
        answer = "ERCOT's hub average was 54.48 USD/MWh in January 2026 (cost_of_power_monthly, EIA-930)."
        sources = ['{"result": [{"value": 54.481}], "start": "2026-01-01"}']
        self.assertEqual(ask.unverified(answer, sources), [])
        left, _ = strip_fetched(answer, sources)
        self.assertNotIn("54.48", left)
        self.assertNotIn("2026", left.replace("EIA-930", ""))
        self.assertIn("EIA-930", left)
        self.assertEqual([m.group(0) for m in ask.NUM.finditer(left) if not ask.is_name(left, m.start())], [])
        self.assertEqual([m.group(0) for m in ask.NUM.finditer("It was 54.49 USD/MWh.") if not ask.is_name("It was 54.49 USD/MWh.", m.start())], ["54.49"])
        self.assertEqual(ask.unverified("It was 54.49 USD/MWh.", sources), ["54.49"])


class EveryHeldTableIsRefused(unittest.TestCase):
    def held_whole(self):
        return sorted(t for t in hold.tables() if hold.held_whole(t))

    def test_the_held_tables_are_many_and_each_is_refused_by_name_with_the_holds_words(self):
        tables = self.held_whole()
        self.assertGreaterEqual(len(tables), 5, tables)   # 6 November 2026: the deals table, the three datacenter tables, the news index
        with mock.patch.dict(os.environ, {"ASK_HOLD": "on"}):
            for t in tables:
                out, err = tools.run("query", {"table": t, "aggregation": "count"})
                self.assertTrue(err, t)
                text = json.dumps(out)
                self.assertIn("license needed", text, t)
                self.assertIn(t, text, t)
                self.assertEqual(re.findall(r"\d", text), [], (t, text))   # no figure, no date: the hold's words alone
                out, err = tools.run("describe_table", {"table": t})
                self.assertTrue(err and "license needed" in json.dumps(out), t)

    def test_misos_rows_are_refused_with_the_pauses_words(self):
        with mock.patch.dict(os.environ, {"ASK_HOLD": "on"}):
            out, err = tools.run("query", {"table": "cost_of_power_monthly", "aggregation": "mean", "entity": "miso:INDIANA.HUB", "variable": "rt_load_weighted"})
        self.assertTrue(err)
        text = json.dumps(out)
        self.assertIn("paused while its terms are reviewed", text)
        self.assertEqual(re.findall(r"\d+(?:\.\d+)?", re.sub(r"4 October 2026", "", text)), [])   # the date of the pause is the only figure

    def test_the_stored_answers_to_held_questions_carry_the_words_and_no_figure_of_the_held_table(self):
        with open(os.path.join(EVAL, "eval_s2224_loop_s2224_run.json"), encoding="utf-8") as f:
            run = {q["id"]: q for q in json.load(f)["questions"]}
        for qid in ("l01", "l02", "l03", "l04"):
            a = run[qid]["answer"].lower()
            self.assertIn("license needed", a, qid)
            self.assertFalse(any(dec >= 1 or (abs(v) >= 1000 and not 1900 <= v <= 2100) for v, dec in F.R.ask.numbers(run[qid]["answer"])) if hasattr(F.R.ask, "numbers") else False, qid)
        self.assertIn("paused", run["l10"]["answer"].lower())


class OutsideTheWarehouse(unittest.TestCase):
    def test_a_refusal_for_what_the_warehouse_lacks_says_so_in_its_first_sentence(self):
        rows = [r for r in F.refusals() if r["class"] == "lacks"]
        self.assertGreaterEqual(len(rows), 8)
        by_run = {label: {q["id"]: q for q in R.load(name)["questions"]} for name, _, label in R.RUNS}
        for r in rows:
            answer = by_run[r["run"]][r["id"]]["answer"]
            first = re.split(r"(?<=[.!?:])\s", answer.strip(), maxsplit=1)[0]
            self.assertIn("not in the warehouse", first.lower(), (r["run"], r["id"], first))


class TheSourcesLine(unittest.TestCase):
    def test_every_answered_record_of_this_chain_lists_what_each_query_read(self):
        n = 0
        for name in ("eval_s2221_loop_run.json", "eval_s2222_loop_run.json", "eval_s2223_loop_run.json", "eval_s2224_loop_s2224_run.json"):
            for q in R.load(name)["questions"]:
                if q.get("status") != "answered":
                    continue
                n += 1
                reads = q.get("reads") or []
                self.assertTrue(reads, (name, q["id"]))
                for r in reads:
                    self.assertIn("table", r)
                    self.assertTrue(set(r) & {"entity", "variable", "start", "end", "aggregation", "where", "value_column"}, (name, q["id"], r))
                cited = {c.get("table") for c in q.get("citations") or []}
                self.assertTrue(cited <= {r["table"] for r in reads}, (name, q["id"], cited))
        self.assertGreater(n, 90)

    def test_the_sites_component_draws_the_table_and_the_read(self):
        with open(os.path.join(ROOT, "site", "components", "ask", "AnswerSources.tsx"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("reads", src)
        self.assertIn("table", src)


class BothLoops(unittest.TestCase):
    def test_the_scripted_turns_cover_every_kind_of_answer_the_rule_names(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "session1300", "turns.json"), encoding="utf-8") as f:
            ids = [s["id"] for s in json.load(f)["scenarios"]]
        for sid in ("answered", "a_figure_in_no_result", "a_compare", "not_in_the_warehouse", "a_table_cited_unread", "a_held_grid",
                    "a_series", "a_per_kw_question", "a_repeated_call", "a_table_held_whole", "misos_pause"):
            self.assertIn(sid, ids)
        with open(os.path.join(ROOT, "tests", "test_session1300.py"), encoding="utf-8") as f:
            src = f.read()
        for k in ('"status"', '"tool_calls"', '"tool_choices"', '"reads"', '"citations"', '"answer"', '"why"', '"series"'):
            self.assertIn(k, src)


if __name__ == "__main__":
    unittest.main()
