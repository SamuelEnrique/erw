"""Session 143: Ask ERCOT, from 17 seconds toward 5. Where the seconds of an answer go (stage timings that sum to the
whole); the cuts (the tables' summaries held ready, one reading turn with a writing turn that streams, a call never
made twice, a grouped result that carries its own summary, the words before the chart); every guard as it was (the
number check, a series equal to the rows fetched, the refusals, the ceilings, the per-visitor limit); the measured
record. No model call and no request: the sources are read, and the session's own tests run in node on recorded reads."""
import csv
import io
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STAGES = ["planning", "fetching", "drawing", "writing", "other"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class StageTimings(unittest.TestCase):
    def test_every_answer_records_its_stages_and_they_sum_to_the_whole(self):
        stages = src("site", "lib", "chat", "stages.ts")
        for words in ('export type Stage = "planning" | "fetching" | "drawing" | "writing" | "other";', "out.other = out.total - named;", "sumStages(steps, Math.max(0, Math.round(end - t0)))"):
            self.assertIn(words, stages, words)
        loop = src("site", "lib", "chat", "ask.ts")
        for words in ("const clock = stageClock(t0);", "const stages_ms = clock.done();", 'clock.add("planning", "model", ms, note);', 'clock.add("fetching", "tools", Date.now() - tTools',
                      'clock.add("drawing", "series", Date.now() - tDraw);', 'clock.add("writing", "check", Date.now() - tCheck);'):
            self.assertIn(words, loop, words)

    def test_the_stages_go_to_the_record_and_the_log_and_not_to_the_page(self):
        route = src("site", "app", "api", "ask", "route.ts")
        self.assertIn("stages_ms: r.stages_ms ?? null", route)                       # the server's log line
        self.assertIn('before: [{ stage: "other" as const, what: "admit", ms: Date.now() - now }]', route)   # the admission is the first step
        page = src("site", "components", "ask", "AskPanel.tsx")
        for words in ("stages_ms", "seconds_words", "steps", "planning", "fetching"):
            self.assertNotIn(words, page, words)
        for path in (("site", "app", "ask", "ercot", "page.tsx"), ("site", "app", "grid", "[slug]", "page.tsx")):
            if os.path.exists(os.path.join(ROOT, *path)):
                self.assertNotIn("stages_ms", src(*path))

    def test_the_measured_record_holds_the_stages_of_every_answer_before_and_after(self):
        text = src("warehouse", "chat", "eval_ercot_speed_results.csv")
        head = [l for l in text.split("\n") if l.startswith("#")]
        self.assertTrue(any("session 143" in l for l in head))
        rows = list(csv.DictReader(io.StringIO("\n".join(l for l in text.split("\n") if not l.startswith("#")))))
        self.assertEqual(len(rows), 100)
        self.assertEqual(len({r["id"] for r in rows}), 100)
        before = [r for r in rows if r["before_total_ms"]]
        after = [r for r in rows if r["after_total_ms"]]
        self.assertEqual(len(before), 20)                                             # the stratified sample: five of each kind
        self.assertEqual(sorted({r["kind"] for r in before}), ["chart", "conceptual", "refuse", "sentence"])
        self.assertGreaterEqual(len(after), 20)
        for when, part in (("before", before), ("after", after)):
            for r in part:
                self.assertEqual(sum(int(r[f"{when}_{s}_ms"]) for s in STAGES), int(r[f"{when}_total_ms"]), r["id"])
                self.assertIn(r[f"{when}_pass"], ("0", "1"))
        # a question not asked after the change says so: it has no figure, never a filled one
        for r in rows:
            if not r["after_total_ms"]:
                self.assertEqual((r["after_pass"], r["after_usd"], r["after_seconds_words"]), ("", "", ""), r["id"])


class TheCuts(unittest.TestCase):
    def test_the_summaries_are_held_ten_minutes_and_a_query_still_governs(self):
        s = src("site", "lib", "chat", "summaries.ts")
        self.assertIn("export const LIFE_MS = 600_000;", s)
        self.assertIn("a query's own rows govern", s)
        self.assertIn("value.catch(() => { if (held.get(key) === entry) held.delete(key); });", s)       # a failed read is never kept as an answer
        panel = src("site", "lib", "chat", "panel.ts")
        self.assertIn("Never say that a recent day, yesterday or this week is not held without a query that came back empty", panel)   # session 137's rule stands
        tools = src("site", "lib", "chat", "tools.ts")
        self.assertIn("const summaries = keep<Held>(LIFE_MS,", tools)
        self.assertIn("const described = keep<Json>(LIFE_MS,", tools)                  # describe_table is answered from memory within its life

    def test_one_reading_turn_then_a_writing_turn_that_can_call_no_tool(self):
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertIn('const w = await call(writer, "absent", asked, "answered");', loop)
        self.assertIn('if (tools === "absent") { delete params.tools; delete params.tool_choice; }', loop)
        self.assertIn("if (!draft || draft.not_in_warehouse || !draft.answer.trim()) break;", loop)     # what the fast path does not settle goes to the loop
        self.assertIn("ONE READING TURN", src("site", "lib", "chat", "panel.ts"))

    def test_the_calls_of_one_turn_are_read_together_and_none_is_made_twice(self):
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertIn("const outs = await Promise.all(blocks.map((b, i) => (slots[i] ? runTool(b.name, b.input, scope) : null)));", loop)
        self.assertIn("const repeat = k !== null && ran.has(k);", loop)
        self.assertIn("if (profile && blocks.length && fresh === 0) forceWrite = true;", loop)

    def test_a_grouped_result_carries_its_summary_and_no_table_was_added(self):
        tools = src("site", "lib", "chat", "tools.ts")
        self.assertIn("export function groupSummary(", tools)
        self.assertIn("if (summary) out.summary = summary;", tools)
        # nothing was loaded and no table was added to the live set: the session wrote no migration and no loader change
        self.assertNotIn("143", " ".join(os.listdir(os.path.join(ROOT, "warehouse", "supabase", "migrations"))))

    def test_the_models_are_the_ones_before_the_session(self):
        e = src("site", "lib", "chat", "ercot.ts")
        self.assertIn('export const PLANNER = "writer";', e)                           # the smaller model was tried and not kept
        self.assertNotIn("thinking:", e.split("export function ercotProfile()")[1].split("opening:")[0])
        self.assertEqual(json.loads(src("site", "lib", "chat", "spec_ercot.json"))["effort"], "medium")
        self.assertIn('if (m.id.toLowerCase().includes("sonnet")) sonnets.push(m);', src("site", "lib", "chat", "ask.ts"))

    def test_the_words_come_before_the_chart_and_only_once_checked(self):
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertIn("if (unverified(words, sources).length || profile.early(head as Draft, records, given).length) return;", loop)
        self.assertLess(loop.index("if (unverified(words, sources).length || profile.early("), loop.index('opts.onEvent({ type: "words"'))
        self.assertIn('opts.onEvent?.({ type: "withdrawn" });', loop)
        e = src("site", "lib", "chat", "ercot.ts")
        self.assertIn('export const FIELD_ORDER = ["form", "not_in_warehouse", "series", "premise", "answer", "citations", "nearest", "followups"];', e)
        spec = json.loads(src("site", "lib", "chat", "spec_ercot.json"))
        self.assertEqual(list(spec["answer_schema"]["properties"])[0], "answer")       # the Python export is untouched: the order is the site's
        page = src("site", "components", "ask", "AskPanel.tsx")
        self.assertIn('else if (e.type === "words" && typeof e.answer === "string") setEarly(', page)
        self.assertIn('else if (e.type === "withdrawn") setEarly(null);', page)
        self.assertIn("The answer itself is never sent in pieces: it is checked whole first.", src("site", "app", "api", "ask", "route.ts"))


class TheGuards(unittest.TestCase):
    def test_the_whole_draft_is_still_checked_as_it_was(self):
        loop = src("site", "lib", "chat", "ask.ts")
        for words in ("const bad = unverified(draft.answer, sources);", "const uncited = draft.citations.map((c) => c.table).filter((t) => !tablesRead.has(t));",
                      "const noCite = !draft.not_in_warehouse && (!draft.citations.length || !draft.answer.trim());", "const more = profile ? profile.extraProblems(draft, records, given) : [];",
                      'status: "refused_unverified" as const'):
            self.assertIn(words, loop, words)
        e = src("site", "lib", "chat", "ercot.ts")
        self.assertIn("series: all.filter((s) => s.check.same)", e)                    # a series that is not the rows fetched is not shown

    def test_the_ceilings_and_the_visitor_limit_are_untouched(self):
        limits = json.loads(src("site", "lib", "chat", "limits.json"))
        self.assertEqual((limits["daily_usd"], limits["monthly_usd"], limits["per_visitor_per_day"]), (3, 30, 15))
        route = src("site", "app", "api", "ask", "route.ts")
        self.assertLess(route.index("const admitted = await admit("), route.index("await ask(asked"))
        self.assertLess(route.index("if (!admitted.ok) {"), route.index("const timing = {"))
        lim = src("site", "lib", "chat", "limits.ts")
        self.assertIn("if (!salt) return refuse(\"closed\"", lim)

    def test_every_model_call_still_goes_to_the_ledger_with_its_own_model(self):
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertEqual(loop.count('ledger.push(recordCall(model, resp, raw.request_id, profile ? "site_ask_ercot" : "site_ask", opts.questionId));'), 1)
        self.assertEqual(loop.count("client.messages.stream("), 1)                     # one place calls the model, and it records the call
        self.assertNotIn("client.messages.create(", loop)
        self.assertIn("const c = cost(model, u);", loop)

    def test_both_pages_stay_in_review_and_the_question_set_is_as_it_was(self):
        release = src("site", "lib", "release.ts")
        self.assertIn('"/ask/ercot": "review"', release)
        self.assertNotIn('"/grid/ercot": "live"', release)
        self.assertNotIn('"/ask/ercot": "live"', release)
        q = json.loads(src("warehouse", "chat", "eval_ercot_panel.json"))["questions"]
        self.assertEqual(len(q), 100)

    def test_the_runner_stops_before_a_question(self):
        run = src("site", "scripts", "eval-ask-speed.mjs")
        self.assertLess(run.index("if (!mayAsk(sessionSpend(spend), reserve, stop))"), run.index("a = await one(q,"))
        self.assertIn("export function mayAsk(spentSoFar, reserveUsd, stopUsd) { return spentSoFar + reserveUsd <= stopUsd; }", src("site", "scripts", "eval-spend.mjs"))


class TheNote(unittest.TestCase):
    def test_how_answers_are_made_fast_is_in_the_method_note(self):
        note = src("docs", "methods", "ask_ercot.md")
        for words in ("## How long an answer takes", "Planning", "Fetching", "Writing", "A smaller model"):
            self.assertIn(words, note, words)

    def test_no_em_dash_in_what_the_session_wrote(self):
        dash = chr(0x2014)
        for parts in (("site", "lib", "chat", "stages.ts"), ("site", "lib", "chat", "summaries.ts"), ("site", "lib", "chat", "ask.ts"), ("site", "lib", "chat", "ercot.ts"), ("site", "lib", "chat", "panel.ts"),
                      ("site", "lib", "chat", "tools.ts"), ("site", "app", "api", "ask", "route.ts"), ("site", "components", "ask", "AskPanel.tsx"), ("site", "scripts", "eval-ask-speed.mjs"),
                      ("site", "scripts", "eval-spend.mjs"), ("site", "scripts", "test-ask-speed.mjs"), ("site", "scripts", "probe-ask-ercot.mjs"), ("site", "scripts", "record-ask-fixture.mjs"),
                      ("docs", "methods", "ask_ercot.md"), ("warehouse", "chat", "eval_ercot_speed_results.csv"), ("tests", "test_session143.py"), ("tests", "fixtures", "session143", "tool_reads.json")):
            self.assertNotIn(dash, src(*parts), parts)


class TheNodeTests(unittest.TestCase):
    def test_the_sessions_own_tests_pass_with_no_request(self):
        node = shutil.which("node")
        if not node or not os.path.isdir(os.path.join(ROOT, "site", "node_modules")):
            self.skipTest("node or the site's packages are not here")
        r = subprocess.run([node, "--import", "./scripts/alias-register.mjs", "scripts/test-ask-speed.mjs"], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0, r.stdout[-1200:] + r.stderr[-1200:])
        self.assertIn("13 tests pass", r.stdout)


if __name__ == "__main__":
    unittest.main()
