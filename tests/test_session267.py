"""Session 267 (14 October 2026): Research, deep, and Ask accuracy.

Part A, held here:
  1. The charts in the brand's colors: warehouse/analysis/style.py (series_colors: the five of docs/brand.md section 2,
     the eight of "Many series" past five, cardinal kept for the highlight), card_image.py (today's chart), and the
     site's literal-to-token table (site/components/echarts.ts), so a site chart reads the CSS variables.
  3. The daily chart's guard (warehouse/analysis/findings/daily_chart.py: record_jump, must_wait, held_before,
     keep_held, choose): a record more than 25 percent past the old one waits a day.
  4. The plain-names file (warehouse/analysis/plain_names.json).
  5. The six do-files that read varnames(1) over a CSV whose first four lines are comments.
Part B, held here: the 30 questions of warehouse/chat/eval/questions_s267.yaml, their answers through /api/ask as
fixtures (eval_s267_fixtures.json) replayed without a model (eval_s267.py grades them; ask.py's number check), and the
fixes of the three wrong answers (MISO held in site/lib/chat/tools.ts; two rows of package/llms.txt).
No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, "warehouse", "analysis")
FIND = os.path.join(ANALYSIS, "findings")
for p in (FIND, ANALYSIS):
    if p not in sys.path:
        sys.path.insert(0, p)
import daily_chart  # noqa: E402
import style  # noqa: E402

EM = chr(0x2014)
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "session232", "candidates.json")
SIX = ["batteries_lunch", "gas_sets_price", "negative_prices_west", "peak_hour_moved", "queue_divorce", "who_rescues_whom"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def candidates():
    with open(FIXTURE, encoding="utf-8") as f:
        return json.load(f)["candidates"]


def record(value, old, key="scan-record-test"):
    return {"source": "scanner", "key": key, "rank": 1, "fact": "f", "table": "t", "series_key": "s",
            "flag": {"rule": "record", "strength": 1.0, "value": value, "compared": {"old_record": old}}, "card": {}}


class TheGuard(unittest.TestCase):
    def test_the_fixture_record_is_34_percent_past_the_old_one(self):
        rec = candidates()[0]
        self.assertEqual(rec["flag"]["rule"], "record")
        self.assertAlmostEqual(daily_chart.record_jump(rec), (1028747.26 - 765381.4) / 765381.4, places=9)
        self.assertGreater(daily_chart.record_jump(rec), daily_chart.RECORD_JUMP)
        self.assertEqual(daily_chart.RECORD_JUMP, 0.25)

    def test_only_a_record_past_25_percent_waits(self):
        self.assertFalse(daily_chart.must_wait(record(125.0, 100.0), set()))       # exactly 25 percent: shown
        self.assertTrue(daily_chart.must_wait(record(125.5, 100.0), set()))        # past it: waits
        self.assertTrue(daily_chart.must_wait(record(-130.0, -100.0), set()))      # a low record, by its size
        self.assertTrue(daily_chart.must_wait(record(5.0, 0.0), set()))            # past a record of zero
        self.assertFalse(daily_chart.must_wait(record(200.0, 100.0), {"scan-record-test"}))   # held on an earlier run
        spike = dict(candidates()[1])
        self.assertIsNone(daily_chart.record_jump(spike))
        self.assertFalse(daily_chart.must_wait(spike, set()))

    def test_choose_passes_over_a_held_record_and_says_so(self):
        c = candidates()
        got, why = daily_chart.choose(c, set())
        self.assertEqual(got["key"], c[1]["key"])
        self.assertIn("held a day by the guard", why)
        got, why = daily_chart.choose(c, set(), waited={c[0]["key"]})
        self.assertEqual(got["key"], c[0]["key"])
        self.assertNotIn("held", why)

    def test_held_today_shown_on_the_next_run(self):
        c = candidates()
        with tempfile.TemporaryDirectory() as d:
            said = []
            daily_chart.section("2026-10-13", said.append, chart_dir=d, candidates=c)
            with open(os.path.join(d, "2026-10-13.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f)["key"], c[1]["key"])
            with open(os.path.join(d, daily_chart.HELD_FILE), encoding="utf-8") as f:
                held = json.load(f)
            self.assertEqual(list(held), [c[0]["key"]])
            self.assertEqual(held[c[0]["key"]]["held_on"], "2026-10-13")
            self.assertEqual(held[c[0]["key"]]["jump_pct"], 34.4)
            self.assertTrue(any("held a day" in m for m in said))
            self.assertEqual(daily_chart.held_before("2026-10-13", d), set())          # a rerun of the day holds it again
            self.assertEqual(daily_chart.held_before("2026-10-14", d), {c[0]["key"]})
            daily_chart.section("2026-10-14", lambda m: None, chart_dir=d, candidates=c)
            with open(os.path.join(d, "2026-10-14.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f)["key"], c[0]["key"])
            with open(os.path.join(d, daily_chart.HELD_FILE), encoding="utf-8") as f:
                self.assertEqual(json.load(f)[c[0]["key"]]["held_on"], "2026-10-13")   # the first day it was held is kept

    def test_a_record_not_raised_again_is_never_shown(self):
        c = candidates()
        with tempfile.TemporaryDirectory() as d:
            daily_chart.section("2026-10-13", lambda m: None, chart_dir=d, candidates=c)
            daily_chart.section("2026-10-14", lambda m: None, chart_dir=d, candidates=c[1:])
            with open(os.path.join(d, "2026-10-14.json"), encoding="utf-8") as f:
                self.assertNotEqual(json.load(f)["key"], c[0]["key"])

    def test_a_proof_holds_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            daily_chart.section("2026-10-12", lambda m: None, chart_dir=d, candidates=candidates(), proof=True)
            self.assertFalse(os.path.exists(os.path.join(d, daily_chart.HELD_FILE)))

    def test_the_shadow_copy_reads_the_real_memory_and_the_site_ignores_the_file(self):
        self.assertIn("waited=daily_chart.held_before(digest_date)", src("warehouse", "news", "brief.py"))
        build = src("site", "scripts", "build-content.mjs")
        self.assertIn(r"/^\d{4}-\d{2}-\d{2}\.png$/", build)
        self.assertIn(r"/^(\d{4}-\d{2}-\d{2})\.json$/", build)


class ThePalette(unittest.TestCase):
    def test_the_five_are_the_brands_in_its_order(self):
        brand = src("docs", "brand.md")
        line = next(ln for ln in brand.splitlines() if ln.startswith("In this order: ink"))
        self.assertEqual(re.findall(r"#[0-9A-F]{6}", line), style.BRAND_SERIES)
        self.assertEqual(style.BRAND_SERIES, ["#2E2D29", "#8C1515", "#3C6E9E", "#6B675F", "#8F8A80"])
        self.assertEqual(style.PALETTE, style.BRAND_SERIES)

    def test_the_eight_are_the_tokens_of_session_268(self):
        css = src("site", "app", "tokens.css")
        got = [re.search(rf"--chart-series-{i}: (#[0-9A-F]{{6}});", css).group(1) for i in range(1, 9)]
        self.assertEqual(got, style.MANY_SERIES)
        for tok, val in (("--chart-ink", style.INK), ("--chart-blue", style.BLUE), ("--chart-grey", style.GREY), ("--chart-light", style.LIGHT),
                         ("--color-accent", style.ACCENT), ("--color-rule", style.RULE), ("--color-muted", style.MUTED), ("--color-paper", style.PANEL)):
            block = css[css.index(".brand-a,\nbody:has(.brand-a) {"):]
            self.assertIn(f"{tok}: {val};", block, tok)

    def test_series_colors(self):
        self.assertEqual(style.series_colors(2), ["#2E2D29", "#8C1515"])
        self.assertEqual(style.series_colors(5), style.BRAND_SERIES)
        six = style.series_colors(6)
        self.assertEqual(six, style.MANY_SERIES[:6])
        self.assertNotIn(style.ACCENT, six)
        ten = style.series_colors(10)
        self.assertEqual(ten[8:], style.MANY_SERIES[:2])
        marked = style.series_colors(7, highlight=2)
        self.assertEqual(marked[2], style.ACCENT)
        self.assertEqual(marked.count(style.ACCENT), 1)
        self.assertNotIn("#AA3377", marked)

    def test_every_color_the_option_writes_is_read_from_a_token_on_the_site(self):
        hook = src("site", "components", "echarts.ts")
        table = hook[hook.index("const LITERAL_TOKENS"):hook.index("function inTokens")]
        mapped = dict(re.findall(r'"(#[0-9a-f]{6})": "(--[a-z0-9-]+)"', table))
        css = src("site", "app", "tokens.css")
        brand = css[css.index("body:has(.brand-a) {"):]
        for tok in set(mapped.values()):
            self.assertIn(tok + ":", brand, tok)
        for n in (1, 3, 5, 6, 8):
            spec = {"kind": "line", "title": "t", "subtitle": "s", "source": "s", "x": ["a", "b"], "x_label": "", "y_label": "",
                    "series": [{"name": f"s{i}", "values": [1, 2]} for i in range(n)]}
            text = json.dumps(style.echarts(spec))
            for lit in set(re.findall(r"#[0-9A-Fa-f]{6}", text)):
                self.assertIn(lit.lower(), mapped, f"{lit} in an option of {n} series has no token")

    def test_the_picture_takes_the_brand(self):
        ci = src("warehouse", "analysis", "findings", "card_image.py")
        self.assertNotIn("PALETTE[7]", ci)
        self.assertNotIn("% len(style.PALETTE)", ci)
        self.assertIn('serif, style.INK, y, 1.18, "bold"', ci)                      # the title in ink, not cardinal
        self.assertEqual(style.PAPER, "#FFFFFF")


class ThePlainNames(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ANALYSIS, "plain_names.json"), encoding="utf-8") as f:
            self.doc = json.load(f)

    def test_the_form(self):
        names = self.doc["names"]
        self.assertEqual(self.doc["count"], len(names))
        self.assertEqual(self.doc["drafts"], sum(1 for e in names if e["status"] == "draft"))
        self.assertGreaterEqual(len(names), 60)
        self.assertEqual(len({e["key"] for e in names}), len(names))
        for e in names:
            self.assertIn(e["status"], ("label", "draft", "note"), e["key"])   # session 315: "note", a name taken from a methods note (ruling 5b)
            self.assertTrue(e["name"].strip() and e["unit"].strip() and e["from"].strip(), e["key"])
            self.assertNotIn(EM, e["name"])
        self.assertNotIn(EM, json.dumps(self.doc, ensure_ascii=False))

    def test_every_watch_measure_and_hunt_pattern_is_named(self):
        import hunt
        import watch
        keys = {e["key"]: e for e in self.doc["names"]}
        for w in watch.WATCH:
            self.assertEqual(keys[f"watch:{w['name']}"]["unit"], w.get("unit", ""), w["name"])
        for p in hunt.PATTERNS:
            self.assertEqual(keys[f"hunt:{p['name']}"]["unit"], p["unit"], p["name"])

    def test_a_label_entry_is_what_the_code_writes(self):
        for e in self.doc["names"]:
            if e["key"].startswith("series:") and e["status"] == "label":
                self.assertEqual(daily_chart.plain_name(e["table"], {"entity": e["entity"], "variable": e["variable"],
                                                                    "node": "CLEVELAND" if "EPMR" in e["entity"] else ""}, "x"), e["name"])


class TheSixDoFiles(unittest.TestCase):
    def test_every_findings_do_file_reads_past_the_csvs_comment_lines(self):
        down = os.path.join(ROOT, "site", "public", "findings")
        dos = sorted(f for f in os.listdir(down) if f.endswith(".do"))
        self.assertGreaterEqual(len(dos), 11)
        for name in dos:
            text = src("site", "public", "findings", name)
            for csv, n in re.findall(r'import delimited "([^"]+)", varnames\((\d+)\)', text):
                if not os.path.exists(os.path.join(down, csv)):
                    continue                                                       # a draft's CSV, written per request
                with open(os.path.join(down, csv), encoding="utf-8") as f:
                    lines = f.read().splitlines()
                comments = next(i for i, ln in enumerate(lines) if not ln.startswith("#"))
                self.assertEqual(int(n), comments + 1, f"{name}: the names are on line {comments + 1}")
                self.assertIn(f"varnames({comments + 1}) rowrange({comments + 2})", text, name)
            self.assertNotIn("varnames(1)", text, name)

    def test_the_six_are_written_by_their_module_and_the_python_copy_matches(self):
        import importlib
        for name in SIX:
            mod = importlib.import_module(name)
            self.assertEqual(mod.stata({}), src("site", "public", "findings", name + ".do"), name)
            self.assertIn("varnames(5) rowrange(6) stringcols(_all) clear", mod.stata({}), name)
            self.assertEqual(src("site", "public", "findings", name + ".py"), src("warehouse", "analysis", "findings", name + ".py"), name)
            self.assertTrue(mod.stata({}).startswith("* ERW "), name)



# ---------------------------------------------------------------------------------------------------------------------
# Part B, Ask accuracy (items 7 to 10): the 30 questions, their answers as fixtures replayed without a model, and the
# fixes of the three wrong answers. The modules of warehouse/chat are loaded under names of their own (no clash with a
# module of the same name another test loads).
# ---------------------------------------------------------------------------------------------------------------------
import importlib.util  # noqa: E402

CHAT = os.path.join(ROOT, "warehouse", "chat")
EVAL = os.path.join(CHAT, "eval")


def _load(name, path):
    if CHAT not in sys.path:
        sys.path.insert(0, CHAT)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fixtures():
    with open(os.path.join(EVAL, "eval_s267_fixtures.json"), encoding="utf-8") as f:
        return json.load(f)


class TheThirtyQuestions(unittest.TestCase):
    def test_thirty_across_every_public_grid(self):
        import yaml
        with open(os.path.join(EVAL, "questions_s267.yaml"), encoding="utf-8") as f:
            qs = yaml.safe_load(f)["questions"]
        self.assertEqual(len(qs), 30)
        self.assertEqual(len({q["id"] for q in qs}), 30)
        grids = {q["grid"] for q in qs}
        for g in ("ERCOT", "CAISO", "NYISO", "SPP", "ISO-NE", "MISO", "PJM", "US48"):
            self.assertIn(g, grids)
        for q in qs:
            self.assertTrue(q["note"], q["id"])
            self.assertEqual(bool(q["refuse"]), not q["expected"], q["id"])
        self.assertNotIn(EM, src("warehouse", "chat", "eval", "questions_s267.yaml"))


class TheFixtures(unittest.TestCase):
    """Item 10: every answer as asked through /api/ask, replayed offline."""

    @classmethod
    def setUpClass(cls):
        cls.fx = fixtures()
        cls.ev = _load("erw_eval_s267", os.path.join(EVAL, "eval_s267.py"))
        cls.ask = _load("erw_chat_ask_s267", os.path.join(CHAT, "ask.py"))

    def test_thirty_recorded_with_their_tool_calls(self):
        qs = self.fx["questions"]
        self.assertEqual(len(qs), 30)
        self.assertIn("/api/ask", self.fx["route"])
        for q in qs:
            self.assertTrue(q["trace"], q["id"])
            self.assertGreaterEqual(q["tool_calls"], 1, q["id"])
            for t in q["trace"]:
                self.assertIn(t["tool"], ("list_tables", "describe_table", "query", "compare", "grid_notes"), q["id"])
            self.assertIsNotNone(q["cost_usd"], q["id"])

    def test_the_grades_replay(self):
        for q in self.fx["questions"]:
            g = self.ev.grade(q, q)
            self.assertEqual(g, q["grade"], q["id"])
            self.assertEqual(g["ok"], q["right"], q["id"])
        right = [q["id"] for q in self.fx["questions"] if q["right"]]
        self.assertEqual(len(right), 27)
        self.assertEqual(sorted(q["id"] for q in self.fx["questions"] if not q["right"]), ["q04", "q10", "q28"])

    def test_a_wrong_answer_names_its_cause_and_its_fix(self):
        for q in self.fx["questions"]:
            if not q["right"]:
                self.assertTrue(q["cause"] and q["fix"], q["id"])
                self.assertIn("Not verified with a call", q["fix"], q["id"])

    def test_every_number_of_an_answer_is_in_a_tool_result(self):
        """The number check (warehouse/chat/ask.py unverified, the Python twin of lib/chat/ask.ts's) on the recorded
        results: every number of every answer is one a tool returned, the question gave, or the day."""
        for q in self.fx["questions"]:
            if q["status"] != "answered":
                continue
            sources = [q["question"], self.fx.get("today", "2026-10-14")]
            sources += [json.dumps(t["out"]) for t in q["trace"]] + [json.dumps(t["input"]) for t in q["trace"]]
            self.assertEqual(self.ask.unverified(q["answer"], sources), [], q["id"])

    def test_a_right_number_came_from_a_tool(self):
        for q in self.fx["questions"]:
            if not q["right"] or not q["expected"]:
                continue
            pool = self.ev.numbers(" ".join(json.dumps(t["out"]) for t in q["trace"]))
            for e in q["expected"]:
                self.assertTrue(self.ev.matches(e, pool, q["tolerance"]), (q["id"], e))

    def test_the_grader_reads_precision_and_separators(self):
        self.assertTrue(self.ev.matches(106.3204, self.ev.numbers("106.3 kgCO2/MWh"), 0.01))
        self.assertFalse(self.ev.matches(106.3204, self.ev.numbers("106.4 kgCO2/MWh"), 0.01))
        self.assertTrue(self.ev.matches(1361345.63, self.ev.numbers("1,361,345.63 MWh"), 1))
        self.assertTrue(self.ev.matches(3699, self.ev.numbers("3699 intervals"), 0.5))
        self.assertNotIn(EM, src("warehouse", "chat", "eval", "eval_s267_fixtures.json"))


class TheFixes(unittest.TestCase):
    """Item 9: each wrong answer fixed at its cause."""

    def test_miso_held_in_the_query_tool(self):
        ts = src("site", "lib", "chat", "tools.ts")
        self.assertIn("export const MISO_PAUSED", ts)
        self.assertIn('paused while terms are reviewed', ts)
        self.assertIn("export const misoOwn = (v: unknown): boolean => typeof v === \"string\" && /^miso[:_]/i.test(v);", ts)
        self.assertIn("if (misoOwn(a.table) || misoOwn(a.entity) || Object.values(a.where ?? {}).flat().some(misoOwn)) throw new ToolError(MISO_PAUSED);", ts)
        self.assertIn("const out = rows.filter((r) => !misoOwn(r.entity)); if (rows.length && !out.length) throw new ToolError(MISO_PAUSED);", ts)
        # EIA's figures for the MISO balancing authority are kept: the rule reads "miso:" and "miso_", never "eia930:MISO"
        rx = re.compile(r"^miso[:_]", re.I)
        self.assertTrue(rx.match("miso:INDIANA.HUB") and rx.match("miso_interconnection_queue"))
        self.assertFalse(rx.match("eia930:MISO") or rx.match("iso:miso"))

    def test_the_briefing_names_the_two_tables(self):
        llms = src("package", "llms.txt")
        self.assertIn("| `ercot_hub_prices_daily` (variables rt_ and da_ mean, min, max, offpeak_mean, hours_below_zero, hours_above_200; a year's hours below zero is the sum of the days) |", llms)
        self.assertIn("| `merchant_revenue_monthly` (energy only; a battery's energy and ancillary services together, by strategy: `battery_stack_monthly`) |", llms)
        spec = json.loads(src("site", "lib", "chat", "spec.json"))
        self.assertIn("ercot_hub_prices_daily", spec["system"])
        self.assertIn("merchant_revenue_monthly", spec["system"])

    def test_the_trace_is_off_unless_asked(self):
        ts = src("site", "lib", "chat", "ask.ts")
        # session 1111: or an evaluation admitted by its own token (the route sets opts.record); a visitor never
        self.assertIn('const tracing = process.env.ASK_RECORD_TOOLS === "1" || opts.record === true;', ts)
        self.assertIn("...(tracing ? { trace: traced } : {})", ts)


if __name__ == "__main__":
    unittest.main()
