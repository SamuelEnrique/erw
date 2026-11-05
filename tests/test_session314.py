"""Session 314: the battery chart fault, and the open items of sessions 296, 298 and 302 at the defaults the owner ruled
on 19 October 2026 (the chain of 19 October, daytime, CHAIN_OCT19B_PROMPT.md). What is held to:

  the shared chart (site/components/tool/SeriesChart.tsx) chooses its axis step by magnitude (five steps at most on any
    span, so a dollar axis in the tens of millions draws a handful of ticks, not thousands), is drawn for the width it
    measures, wraps a column's label by words, thins the labels when a line is wider than a column, and writes a
    sub-label and a bar's figure only where they fit; the phone's sideways scroll of app/tokens.css leaves it out;
  the year chart alone is the default chart; the contract's two assumptions take no sourced range and say the percent
    step moves them; 8 hours takes the ATB's figure alone with no range for its capital cost and fixed O&M, and the
    line under the chart says why;
  an evaluation of /ask spends through a ledger step of its own, site_ask_eval, under its own day ceiling: the route
    knows it by ASK_EVAL_TOKEN, admits it by ASK_EVAL_DAILY_USD against the step's spend, writes its calls strictly
    under the step, and migration 035 (written, not applied) widens the step check and keeps the public ceilings'
    sums to the public steps;
  a grid's scoped chat takes its tables from the rule of warehouse/chat/grid_tables.py (the entity-prefix probe
    session 302 ran by hand, with the ba, market, name and queue rules beside it), written to docs/grids/grid_tables.json,
    and the rule reproduces the hand-kept lists of docs/grids/grids.json on the day it was run;
  the screenshots of the chart before and after at 1280 and 390 are in docs/brand/review-314/ with a README; the
    methods note carries the session; no em dash in any file the session wrote.

No request, no model call; the environment is read, never set."""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
FILES = [
    "site/components/tool/SeriesChart.tsx", "site/app/tokens.css", "site/lib/battery/finance.ts", "site/app/cost-of-power/battery/Scenarios.tsx",
    "site/scripts/test-battery-finance.mjs", "site/lib/chat/ledger.ts", "site/lib/chat/ask.ts", "site/lib/chat/limits.ts", "site/app/api/ask/route.ts",
    "warehouse/supabase/migrations/035_ask_eval_step.sql", "warehouse/supabase/rollbacks/035_ask_eval_step.sql", "site/README.md",
    "warehouse/chat/grid_tables.py", "docs/grids/grid_tables.json", "site/lib/chat/tools.ts", "warehouse/chat/tools.py",
    "docs/methods/battery_earns_algorithm.md", "docs/brand/review-314/README.md", "tests/test_session314.py",
]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def nice(span):
    """The chart's axis step, as SeriesChart.tsx states it: 1, 2, 2.5 or 5 times a power of ten, five steps at most."""
    if not span > 0:
        return 1
    p = 10 ** math.floor(math.log10(span / 5))
    for m in (1, 2, 2.5, 5, 10):
        if span / (m * p) <= 5:
            return m * p
    return 10 * p


class TheSharedChart(unittest.TestCase):
    def test_the_axis_step_is_chosen_by_magnitude_five_steps_at_most(self):
        chart = src("site", "components", "tool", "SeriesChart.tsx")
        self.assertIn("const p = 10 ** Math.floor(Math.log10(span / 5));", chart)
        self.assertIn("for (const m of [1, 2, 2.5, 5, 10]) if (span / (m * p) <= 5) return m * p;", chart)
        self.assertNotIn("20000].find(", chart)   # the fixed list that ended at 20,000 (the fault)
        # the Python mirror of the rule: the income chart's span (about 70 million) draws four steps, not 3,500
        self.assertEqual(nice(70.7e6), 2e7)
        self.assertEqual(math.ceil(70.7e6 / nice(70.7e6)), 4)
        self.assertEqual(nice(468), 100)      # the year chart, USD per kW
        self.assertEqual(nice(4.2), 1)
        for span in (0.3, 7, 99, 1234, 56789, 3.3e6, 9.9e8):
            self.assertLessEqual(span / nice(span), 5, span)
            self.assertGreater(span / nice(span), 1, span)

    def test_the_chart_is_drawn_for_its_measured_width_and_its_labels_fit_their_columns(self):
        chart = src("site", "components", "tool", "SeriesChart.tsx")
        self.assertIn("new ResizeObserver(", chart)
        self.assertIn("const W = Math.max(280, width);", chart)
        self.assertIn('data-chart-width={W}', chart)
        self.assertIn("export function wrapLabel(label: string, width: number, size = 11): string[] {", chart)
        self.assertIn("const lines = categories.map((c) => wrapLabel(c.label, bw - 4));", chart)
        self.assertIn("Math.max(1, Math.ceil(widest / bw))", chart)           # the labels thinned to every k-th column
        self.assertIn("textWidth(c.sub, 10) <= bw - 2", chart)                 # a sub-label only where it fits
        self.assertIn("textWidth(figure) <= bw * 1.5", chart)                  # a bar's figure where it (nearly) fits
        self.assertIn("right -= textWidth(s.name, 12) + 16;", chart)           # the names spaced by their length
        self.assertNotIn("(series.length - 1 - k) * 150", chart)
        # what the checks and the tests of sessions 296 and 303 read stays
        for keep in ('data-direct-labels="1"', "data-chart-table={id}", "data-chart-as-table={id}", "data-series-chart={id}", 'data-log-refused="1"'):
            self.assertIn(keep, chart)
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{3,8}\b(?![\w-])", re.sub(r"//.*", "", chart)))

    def test_the_phones_sideways_scroll_leaves_the_measured_chart_out(self):
        css = src("site", "app", "tokens.css")
        self.assertIn('.brand-a figure:not([data-chart-width]) > svg[role="img"] {', css)
        self.assertIn('.brand-a figure:not([data-chart-width]):has(> svg[role="img"]) {', css)
        self.assertEqual(css.count("{"), css.count("}"))

    def test_the_screenshots_before_and_after_at_both_widths_with_a_readme(self):
        d = os.path.join(ROOT, "docs", "brand", "review-314")
        names = set(os.listdir(d))
        for n in ("chart_before_default_1280.png", "chart_before_default_390.png", "chart_after_default_1280.png", "chart_after_default_390.png",
                  "chart_before_2y_1280.png", "chart_before_2y_390.png", "chart_after_2y_1280.png", "chart_after_2y_390.png", "README.md"):
            self.assertIn(n, names, n)
        readme = src("docs", "brand", "review-314", "README.md")
        self.assertIn("twelve thin bars", readme)


class TheThreeDefaults(unittest.TestCase):
    def test_the_year_chart_alone_is_the_default(self):
        self.assertIn('charts: ["revenue"]', src("site", "lib", "battery", "view.ts"))

    def test_the_contract_and_eight_hours_take_no_sourced_range(self):
        fin = src("site", "lib", "battery", "finance.ts")
        self.assertIn('cshare: "the reader\'s own term, no published case; the percent step moves it"', fin)
        self.assertIn('cprice: "the reader\'s own term, no published case; the percent step moves it"', fin)
        self.assertIn("the sourced range draws no row for it and the sensitivity's percent step moves it", fin)
        self.assertIn("export function noRangeOf(hours: number): Partial<Record<Key, string>> {", fin)
        self.assertNotIn("an extrapolation", fin.split("export function rangesOf")[1].split("export const NO_RANGE")[0])
        sc = src("site", "app", "cost-of-power", "battery", "Scenarios.tsx")
        self.assertIn("const noRange = noRangeOf(x.dur);", sc)
        self.assertNotIn("NO_RANGE[k]", sc)
        out = node("const F = await import('./lib/battery/finance.ts'); console.log(JSON.stringify([Object.keys(F.rangesOf(8)).sort(), Object.keys(F.rangesOf(4)).sort(), F.noRangeOf(8).capex, F.noRangeOf(8).fom, F.noRangeOf(4).capex ?? null]));")
        self.assertEqual(out[0], ["deg", "life", "rte", "share"])
        self.assertEqual(out[1], ["capex", "deg", "fom", "life", "rte", "share"])
        self.assertIn("2,300", out[2])
        self.assertIn("no extrapolation", out[2])
        self.assertIn("92", out[3])
        self.assertIsNone(out[4])


class TheEvaluationsOwnLedgerStep(unittest.TestCase):
    def test_the_route_knows_an_evaluation_by_its_secret_and_admits_it_by_its_own_ceiling(self):
        r = src("site", "app", "api", "ask", "route.ts")
        self.assertIn('const evaluation = evalToken !== null && sameSecret(req.headers.get("x-erw-ask-eval") ?? "", evalToken);', r)
        self.assertIn('? await admitEvaluation(now, readEvalCap(), () => rpc("internal_ask_spend", { p_token: process.env.INTERNAL_COSTS_TOKEN ?? "" }, { privileged: true }))', r)
        # session 1111: an evaluation also records its tool calls (record: true); a visitor's request gets none of these
        self.assertIn("const ledgerOpts = evaluation ? { step: EVAL_STEP, strictLedger: true, record: true } : {};", r)
        self.assertEqual(r.count("...ledgerOpts"), 3)          # the stream, Ask ERCOT and the general chat
        self.assertIn("if (gate.ok && !evaluation) {", r)       # the hourly limit is the visitor's, not the runner's
        lim = src("site", "lib", "chat", "limits.ts")
        self.assertIn('export const EVAL_STEP = "site_ask_eval";', lim)
        self.assertIn("return s.length >= 24 ? s : null;", lim)
        a = src("site", "lib", "chat", "ask.ts")
        self.assertIn('opts.step ?? (profile ? "site_ask_ercot" : "site_ask")', a)
        self.assertIn("if (opts.strictLedger) await row; else ledger.push(row);", a)
        self.assertIn("if (strict) throw new Error(`the cost ledger refused the ${step} row", src("site", "lib", "chat", "ledger.ts"))

    def test_the_evaluations_admission_holds_its_own_ceiling_and_fails_closed(self):
        out = node("""const L = await import('./lib/chat/limits.ts');
          const now = Date.UTC(2026, 9, 19, 20);
          const rows = { days: [{ day: '2026-10-19', step: 'site_ask', usd: 2.9 }, { day: '2026-10-19', step: 'site_ask_eval', usd: '3.25' }, { day: '2026-10-18', step: 'site_ask_eval', usd: 4 }] };
          const res = {
            under: (await L.admitEvaluation(now, 5, async () => rows)).ok,
            over: (await L.admitEvaluation(now, 3, async () => rows)).reason,
            noCap: (await L.admitEvaluation(now, null, async () => rows)).reason,
            failed: (await L.admitEvaluation(now, 5, async () => { throw new Error('no'); })).reason,
            empty: (await L.admitEvaluation(now, 5, async () => ({}))).ok,
            token: [L.readEvalToken({ ASK_EVAL_TOKEN: 'short' }), L.readEvalToken({ ASK_EVAL_TOKEN: 'a-secret-of-at-least-24-characters' })],
            cap: [L.readEvalCap({}), L.readEvalCap({ ASK_EVAL_DAILY_USD: '5' }), L.readEvalCap({ ASK_EVAL_DAILY_USD: 'five' })],
          };
          console.log(JSON.stringify(res));""")
        self.assertTrue(out["under"])
        self.assertEqual(out["over"], "day")          # the public chat's 2.9 does not count; the step's own 3.25 does
        self.assertEqual(out["noCap"], "closed")
        self.assertEqual(out["failed"], "closed")
        self.assertTrue(out["empty"])
        self.assertEqual(out["token"], [None, "a-secret-of-at-least-24-characters"])
        self.assertEqual(out["cap"], [None, 5, None])

    def test_migration_035_widens_the_step_check_and_keeps_the_public_sums_to_the_public_steps(self):
        m = src("warehouse", "supabase", "migrations", "035_ask_eval_step.sql")
        self.assertIn("check (step in ('site_ask', 'site_ask_ercot', 'site_ask_eval'))", m)
        self.assertEqual(m.count("and step <> 'site_ask_eval'"), 2)       # the month's sum and the day's sum
        self.assertIn("create or replace function public.site_ask_admit(", m)
        rb = src("warehouse", "supabase", "rollbacks", "035_ask_eval_step.sql")
        self.assertIn("check (step in ('site_ask', 'site_ask_ercot'))", rb)
        self.assertIn("update public.site_api_calls set step = 'site_ask' where step = 'site_ask_eval';", rb)
        self.assertIn("ASK_EVAL_TOKEN", src("site", "README.md"))
        self.assertIn("ASK_EVAL_DAILY_USD", src("site", "README.md"))


class TheGridsTablesByRule(unittest.TestCase):
    def test_the_rule_found_every_hand_listed_table_that_holds_the_grids_rows(self):
        ruled = json.load(open(os.path.join(ROOT, "docs", "grids", "grid_tables.json"), encoding="utf-8"))
        hand = {g["slug"]: g for g in json.load(open(os.path.join(ROOT, "docs", "grids", "grids.json"), encoding="utf-8"))["grids"]}
        self.assertEqual(sorted(ruled["grids"]), sorted(hand))
        self.assertEqual(ruled["errors"], {})                      # an unread table is never a finding
        self.assertEqual(ruled["rules"], ["name", "entity", "ba", "isoentity", "queue", "iso"])   # the market rule is a fallback in the tools, not asked; isoentity: session 1142
        for slug, g in ruled["grids"].items():
            self.assertEqual(g["tables"], sorted(g["by"]), slug)
            self.assertEqual(sorted(set(hand[slug]["tables"]) - set(g["tables"])), g["grids_json_not_found"], slug)
            self.assertEqual(sorted(set(g["tables"]) - set(hand[slug]["tables"])), g["not_in_grids_json"], slug)
            # the one hand-listed table the rule does not find: energy_projects for NYISO and MISO, which holds no row of
            # their queues (the hand list claimed it; its filter read no row); every other table of the list is found
            self.assertLessEqual(set(g["grids_json_not_found"]), {"energy_projects"}, slug)
            self.assertTrue(all(t.startswith(slug + "_") for t, by in g["by"].items() if by == "name"), slug)
            self.assertTrue(all(not t.startswith(slug + "_") for t, by in g["by"].items() if by != "name"), slug)
        # session 302's tables, by the entity prefix, in the grids that hold their rows
        for t in ("cost_of_power_monthly", "cost_of_power_hourly_profile", "merchant_revenue_monthly"):
            for slug in ("ercot", "caiso", "nyiso", "isone", "spp", "miso"):
                self.assertEqual(ruled["grids"][slug]["by"].get(t), "entity", (t, slug))
        self.assertEqual(ruled["grids"]["ercot"]["by"].get("battery_stack_monthly"), "entity")
        self.assertEqual(ruled["grids"]["caiso"]["by"].get("iso_curtailment_monthly"), "entity")
        self.assertNotIn("iso_curtailment_monthly", ruled["grids"]["ercot"]["by"])
        self.assertEqual(ruled["grids"]["ercot"]["by"].get("eia930_all_demand"), "ba")
        self.assertEqual(ruled["grids"]["ercot"]["by"].get("ercot_hub_prices_daily"), "name")

    def test_both_tool_sets_read_the_file_and_keep_rows_by_the_rule_that_admitted_the_table(self):
        ts = src("site", "lib", "chat", "tools.ts")
        self.assertIn("const ruled = DOCS.grid_tables?.grids?.[g.slug];", ts)
        self.assertIn("return ruled ? { ...g, tables: [...ruled.tables], by: { ...ruled.by } } : g;", ts)
        self.assertIn("const by = scope.by?.[name];", ts)
        for rule in ("name", "ba", "entity", "market", "queue", "iso"):
            self.assertIn(f'by === "{rule}"', ts)
        self.assertNotIn("HUB_KEYED", ts)
        self.assertNotIn("BA_TABLES", ts)
        self.assertIn('grid_tables: { read_at: gridTables.read_at, grids: gridTables.grids },', src("site", "scripts", "build-content.mjs"))
        py = src("warehouse", "chat", "tools.py")
        self.assertIn('GRID_TABLES_PATH = os.path.join(ROOT, "docs", "grids", "grid_tables.json")', py)
        self.assertIn('GRIDS[_slug] = {**GRIDS[_slug], "tables": list(_ruled["tables"]), "by": dict(_ruled["by"])}', py)
        self.assertIn('by = (g.get("by") or {}).get(name)', py)
        for rule in ("name", "ba", "entity", "market", "queue", "iso"):
            self.assertIn(f'by == "{rule}"', py)
        self.assertNotIn("HUB_KEYED", py)
        self.assertIn('soft_step dm_grid_tables "$PYTHON" warehouse/chat/grid_tables.py', src("warehouse", "run_data_machine_tables.sh"))
        self.assertIn("docs/grids/grid_tables.json", src("warehouse", "run_data_machine.sh"))
        self.assertIn("Session 314", json.load(open(os.path.join(ROOT, "docs", "grids", "grids.json"), encoding="utf-8"))["_about"])

    def test_the_rule_script_is_standard_library_and_asks_the_anon_key_only(self):
        s = src("warehouse", "chat", "grid_tables.py")
        self.assertIn('env("SUPABASE_ANON_KEY")', s)
        self.assertNotIn("SERVICE", s)
        self.assertNotIn("import requests", s)
        self.assertNotIn("import pandas", s)
        self.assertIn('"order": f"{column}.asc", "limit": "1"', s)     # one indexed read, never a like over a partition
        self.assertNotIn('f"like.{slug}:*"', s)


class NoEmDash(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    sys.exit(unittest.main())
