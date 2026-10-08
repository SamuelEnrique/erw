"""Session 137: Ask ERCOT as the answer panel. The 100 test questions and their rule; the one component and where it
is placed; the form of an answer and the rule that a chart is never shown for its own sake; the sources added; the
ceilings of session 128 untouched. No model call: the sources are read, and the panel's own tests run in node."""
import collections
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Questions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.set = json.loads(src("warehouse", "chat", "eval_ercot_panel.json"))
        cls.q = cls.set["questions"]

    def test_one_hundred_new_questions_25_of_each_kind(self):
        self.assertEqual(len(self.q), 100)
        self.assertEqual(collections.Counter(x["kind"] for x in self.q), {"conceptual": 25, "chart": 25, "sentence": 25, "refuse": 25})
        self.assertEqual(len({x["id"] for x in self.q}), 100)
        self.assertEqual(len({x["q"].lower() for x in self.q}), 100)
        self.assertTrue(all(len(x["q"]) <= 500 for x in self.q))

    def test_the_refusals_cover_other_grids_licensed_data_and_named_companies(self):
        why = collections.Counter(x["why"] for x in self.q if x["kind"] == "refuse")
        self.assertGreaterEqual(sum(n for k, n in why.items() if k.startswith("other grid")), 8)
        self.assertGreaterEqual(why["licensed data"], 5)
        self.assertGreaterEqual(sum(n for k, n in why.items() if k.startswith("a named company")), 6)
        for x in self.q:
            if x["kind"] == "refuse":
                re.compile(x["say"])

    def test_some_questions_need_the_tables_landed_today(self):
        new = collections.Counter(x.get("new") for x in self.q if x.get("new"))
        self.assertEqual(set(new), {"board", "supply", "mix"})
        self.assertGreaterEqual(sum(new.values()), 10)

    def test_the_two_questions_the_owner_named_are_in_the_set(self):
        asked = [x["q"] for x in self.q if x["kind"] == "conceptual"]
        self.assertIn("Teach me how ERCOT sets prices.", asked)
        self.assertIn("What is a hub?", asked)

    def test_no_question_was_asked_before(self):
        old = src("site", "scripts", "time-ask-ercot.mjs") + src("site", "scripts", "check-ask-conversation.mjs")
        for x in self.q:
            self.assertNotIn(x["q"], old, x["id"])

    def test_one_rule_a_kind_and_the_runner_stops_before_its_budget(self):
        self.assertEqual(set(self.set["rules"]), {"conceptual", "chart", "sentence", "refuse"})
        judge = src("site", "scripts", "eval-judge.mjs")
        for words in ('q.kind === "conceptual"', 'q.kind === "chart"', 'q.kind === "sentence"', 'q.kind === "refuse"', "a series does not equal the rows fetched", "series shown for one figure"):
            self.assertIn(words, judge, words)
        run = src("site", "scripts", "eval-ask-panel.mjs")
        self.assertIn("if (spent + reserve > budget) { stopped = true;", run)
        self.assertLess(run.index("if (spent + reserve > budget)"), run.index("a = await one(q,"))       # asked before the question, never after
        self.assertIn("cost_usd: cost", run)
        self.assertIn("seconds_first_sign", run)


class TheComponent(unittest.TestCase):
    def test_one_component_with_the_grid_as_a_parameter(self):
        c = src("site", "components", "ask", "AskPanel.tsx")
        self.assertIn("export function AskPanel({ grid,", c)
        self.assertIn('const PROFILES = new Set(["ercot"]);', c)
        self.assertIn("profile: grid, stream: true", c)
        self.assertIn(": { question, grid }", c)                        # a grid without a profile is asked of the general chat for that grid

    def test_the_answer_sits_right_below_the_box(self):
        c = src("site", "components", "ask", "AskPanel.tsx")
        body = c.split("return (\n    <div className=\"max-w-3xl\" data-ask-panel={grid}>")[1]
        self.assertLess(body.index("<form onSubmit"), body.index("{order.map(({ t, n }) => <Answer"))
        self.assertIn("const order = turns.map((t, i) => ({ t, n: i + 1 })).reverse();", c)       # the newest answer first

    def test_it_is_used_on_both_pages_and_nothing_else_of_the_grid_page_moved(self):
        self.assertIn('return <AskPanel grid="ercot" initial={initial} context={context} />;', src("site", "app", "ask", "ercot", "AskErcot.tsx"))
        page = src("site", "app", "grid", "[iso]", "page.tsx")
        self.assertEqual(page.count("<AskPanel "), 1)
        self.assertIn('{g.slug === "ercot" ? <div className="mb-8"><AskPanel grid="ercot" inputId="ask-grid" showContext={false}', page)
        self.assertIn('<form action="/ask" method="get"', page)          # the six other grids keep their form
        # the page's sections, in the order they were
        titles = re.findall(r'<Section title="([^"]+)"', page)
        self.assertEqual(titles[:2], ["Who runs this grid", "Right now: demand"])
        self.assertLess(page.index('<Section title="Who runs this grid"'), page.index("<AskPanel "))
        self.assertLess(page.index("<AskPanel "), page.index('<Section title="Right now: demand"'))
        self.assertIn("<AskErcotLink context=", page)

    def test_a_chart_is_drawn_only_for_the_forms_that_call_for_one(self):
        c = src("site", "components", "ask", "AskPanel.tsx")
        self.assertIn('const chart = form !== "table" && isDrawn(s.kind, drawn);', c)
        self.assertIn("chartPoints(s.rows, s.group_by)", c)   # session 161: the group says whether a key is a time or an hour of the day
        e = src("site", "lib", "chat", "ercot.ts")
        self.assertIn('const shows = legacy || form === "chart" || form === "table";', e)      # legacy: the reference loop's draft, which names no form
        self.assertIn("let ids = shows ? (", e)
        self.assertIn("if (shows && !ids.length) {", e)
        self.assertIn("series: all.filter((s) => s.check.same), series_not_shown:", e)     # each series still set against the rows fetched
        for words in ('form "${form}" carries no series', 'form "${form}" needs the result it shows named in series'):
            self.assertIn(words, e, words)

    def test_no_method_prose_on_the_face(self):
        c = src("site", "components", "ask", "AskPanel.tsx")
        face = c.split("export function AskPanel(")[1] + c.split("function Answer(")[1].split("export function AskPanel(")[0] + c.split("function SeriesBlock(")[1].split("function Answer(")[0]
        for words in ("nothing is drawn between them", "appears whole once every number", "warehouse queries by", "model cost USD", "are sent with the next question"):
            self.assertNotIn(words, face, words)
        self.assertIn("<Link href={methodHref}>Method note</Link>", c)
        page = src("site", "app", "ask", "ercot", "page.tsx")
        for words in ("Every number in an answer comes from a query", "At most 10 questions per hour", "live\n        set"):
            self.assertNotIn(words, page, words)
        note = src("docs", "methods", "ask_ercot.md")
        for words in ("Every number comes from a query", "never added for its own sake", "Every chart is set against the rows fetched", "speaks for ERCOT only", "Licensed data", "live set"):
            self.assertIn(words, note, words)
        self.assertNotIn(chr(0x2014), note + c + src("site", "lib", "chat", "panel.ts"))


class Sources(unittest.TestCase):
    def test_the_profile_takes_the_panels_additions_and_the_exported_spec_is_untouched(self):
        e = src("site", "lib", "chat", "ercot.ts")
        for words in ("system: spec.system + addendum(base.slug, base.iso),", "tools: [PAGE_TOOL],", "preRead: [NOTES_TABLE(base.slug)],", "tables: [...spec.tables, ...MIX_TABLES]",
                      "preSources: [notesOf(base.slug)],", 'form: FORM_SCHEMA }, required: ['):
            self.assertIn(words, e, words)
        spec = json.loads(src("site", "lib", "chat", "spec_ercot.json"))
        self.assertNotIn("form", spec["answer_schema"]["properties"])     # the Python export is as it was: the panel is the site's addition
        self.assertNotIn("page_figures", spec["system"])

    def test_the_shared_loop_gained_hooks_a_profile_must_set(self):
        a = src("site", "lib", "chat", "ask.ts")
        for words in ("tools: profile?.tools ? [...TOOLS, ...profile.tools] : TOOLS,", "profile?.ownTool?.(name, input) ?? runWarehouseTool(name, input, sc)", "...(profile?.preRead ?? [])"):
            self.assertIn(words, a, words)
        self.assertIn("const outs = await Promise.all(blocks.map((b, i) => (slots[i] ? runTool(b.name, b.input, scope) : null)));", a)

    def test_the_panels_own_tests_pass(self):
        node = shutil.which("node")
        if not node or not os.path.isdir(os.path.join(ROOT, "site", "node_modules")):
            self.skipTest("node or the site's packages are not here")
        r = subprocess.run([node, "--import", "./scripts/alias-register.mjs", "scripts/test-ask-panel.mjs"], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout[-800:] + r.stderr[-800:])
        self.assertIn("8 tests pass", r.stdout)


class Ceilings(unittest.TestCase):
    def test_session_128s_ceilings_and_per_visitor_limit_are_as_they_were(self):
        limits = json.loads(src("site", "lib", "chat", "limits.json"))
        self.assertEqual((limits["daily_usd"], limits["monthly_usd"], limits["per_visitor_per_day"]), (3, 30, 15))
        route = src("site", "app", "api", "ask", "route.ts")
        self.assertLess(route.index("const admitted = await admit("), route.index("await ask(asked"))     # admitted by the database before any model call
        self.assertIn("if (!admitted.ok) {", route)
        self.assertIn('opts.questionId', src("site", "lib", "chat", "ask.ts"))

    def test_both_pages_stay_in_review(self):
        release = src("site", "lib", "release.ts")
        self.assertIn('"/ask/ercot": "review"', release)
        self.assertNotIn('"/grid/ercot": "live"', release)
        self.assertNotIn('"/grid": "live"', release)


if __name__ == "__main__":
    unittest.main()
