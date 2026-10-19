"""Session 296: the battery page's pass 1 (the owner's ten rulings of 15 October 2026). What is held to:

  the 8-hour defaults are NREL's Annual Technology Baseline 2025, as its cost report states them: a capital cost of
    USD 2,300 per kW (241 per kWh times 8 hours plus 372 per kW, 2024 dollars) and fixed O&M of 92 (4 percent of it),
    the same figures in the stack library and the finance library, each naming the report; 2 and 4 hours stay Lazard's;
  the sourced ranges are typed with their sources, six assumptions have one, and the other six are named with why;
  the view (lib/battery/view.ts) defaults to the page as it was: the three headline figures, the one chart, the
    adjusted scale, this battery, the sourced range in NPV, no window, nothing left out; every parameter is omitted at
    its default, and a shared address reads back to the same view;
  the box: five sections in order, two open; the twelve assumptions are the shared panel, drawn once, with the
    contract as a sub-group; the second question draws the table alone;
  the income table's columns: the last twelve months, the calendar years and the reader's window; the ERW's own
    windows (the last three full years, without the one month) are gone from the page, and the window at its default
    keeps the old key;
  every chart and the income table have a Chart | Table toggle; the year chart, the income table, the units, the
    scale and the sensitivity carry a hover tip; the duration and each strategy carry a one-line hover;
  the methods note and the review pack state the session's changes; no em dash in any file the session wrote.

No request, no model call; the environment is read, never set."""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
FILES = [
    "site/lib/battery/finance.ts", "site/lib/battery/view.ts", "site/lib/batterystack.ts",
    "site/app/cost-of-power/battery/page.tsx", "site/app/cost-of-power/battery/Scenarios.tsx", "site/app/cost-of-power/battery/Settings.tsx",
    "site/app/cost-of-power/battery/Income.tsx", "site/app/cost-of-power/battery/ViewState.tsx", "site/app/cost-of-power/battery/BatteryForm.tsx",
    "site/components/tool/SeriesChart.tsx", "site/components/tool/ToolPage.tsx", "site/components/decisions/ScenarioBlock.tsx", "site/app/tokens.css",
    "site/scripts/test-battery-finance.mjs", "site/scripts/check-battery-scenarios.mjs", "site/scripts/check-decisions-face.mjs",
    "docs/methods/battery_earns_algorithm.md", "docs/reviews/packs/battery.md", "tests/test_session296.py",
]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_eval(expr):
    """A value from the finance library, through Node (skipped when node is absent)."""
    script = f"const F = await import('./lib/battery/finance.ts'); const B = await import('./lib/batterystack.ts'); process.stdout.write(JSON.stringify({expr}));"
    try:
        out = subprocess.run(["node", "--input-type=module", "-e", script], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise unittest.SkipTest(f"node did not answer: {exc}")
    if out.returncode != 0:
        raise AssertionError(out.stderr[-800:])
    return json.loads(out.stdout)


class TheEightHourDefaults(unittest.TestCase):
    def test_the_stack_library_names_the_atb_and_its_figures(self):
        s = src("site", "lib", "batterystack.ts")
        self.assertIn("8: { capex: 2300, fom: 92,", s)
        self.assertIn("2: { capex: 610, fom: 11.2,", s)
        self.assertIn("4: { capex: 1110, fom: 22,", s)
        self.assertIn("NREL, Annual Technology Baseline 2025, utility-scale battery storage (Cole, Karmakar and Mann, NREL/TP-6A40-93281, June 2025, section 2.2)", s)
        self.assertIn("source: ATB_SOURCE", s)
        self.assertEqual(s.count("source: LAZARD_SOURCE"), 2)

    def test_the_finance_library_states_the_atb_and_computes_the_same(self):
        f = src("site", "lib", "battery", "finance.ts")
        self.assertIn("energy: 241, power: 372, fomShare: 0.04, rte: 85, life: 15,", f)
        self.assertIn("NREL/TP-6A40-93281", f)
        self.assertIn("https://atb.nlr.gov/electricity/2025/utility-scale_battery_storage", f)
        v = node_eval("[F.atbCapex(8), F.atbFom(8), F.atbCapex(2), F.atbCapex(4), B.COSTS[8].capex, B.COSTS[8].fom]")
        self.assertEqual(v, [2300, 92, 854, 1336, 2300, 92])

    def test_the_notes_state_the_change_and_what_moved(self):
        note = src("docs", "methods", "battery_earns_algorithm.md")
        self.assertIn("| Capital cost | 610, 1,110, 2,300 USD per kW (2, 4, 8 hours) |", note)
        self.assertIn("| Fixed O&M | 11.2, 22, 92 USD per kW a year |", note)
        self.assertIn("#### Session 296: the box, the figures, the charts and the two sensitivity modes", note)
        pack = src("docs", "reviews", "packs", "battery.md")
        self.assertIn("| Capital cost | 610, 1,110, 2,300 USD per kW (2, 4, 8 hours) |", pack)
        self.assertIn("| Fixed O&M | 11.2, 22, 92 USD per kW a year |", pack)
        self.assertIn("| Sensitivity mode |", pack)


class TheSourcedRanges(unittest.TestCase):
    def test_six_assumptions_have_a_range_with_a_source_and_six_are_named_without(self):
        r = node_eval("[F.rangesOf(4), F.rangesOf(8), F.NO_RANGE]")
        r4, r8, none = r
        self.assertEqual(sorted(r4), ["capex", "deg", "fom", "life", "rte", "share"])
        for k, rng in r4.items():
            self.assertLess(rng["low"], rng["high"], k)
            self.assertRegex(rng["source"], r"Lazard|Annual Technology Baseline", k)
        self.assertEqual((r4["capex"]["low"], r4["capex"]["high"]), (620, 1600))
        self.assertEqual((r4["life"]["low"], r4["life"]["high"]), (15, 20))
        self.assertEqual((r4["deg"]["low"], r4["deg"]["high"]), (0, 2.6))
        self.assertEqual((r4["rte"]["low"], r4["rte"]["high"]), (85, 92))
        self.assertEqual((r4["share"]["low"], r4["share"]["high"]), (20, 60))
        # session 314 (the owner's ruling of 19 October 2026): 8 hours takes the ATB's figure alone, no range for its
        # capital cost and fixed O&M (session 296 drew the lines through Lazard's 2- and 4-hour cases, 1180 to 3040)
        self.assertEqual(sorted(r8), ["deg", "life", "rte", "share"])
        # session 297: its six keys have no published range either
        self.assertEqual(sorted(none), ["aug", "augcost", "cprice", "cshare", "cycles", "fade", "hurdle", "itc", "method", "rate", "stress", "term"])

    def test_the_finance_hand_cases_pass(self):
        try:
            out = subprocess.run(["node", "scripts/test-battery-finance.mjs"], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise unittest.SkipTest(f"node did not answer: {exc}")
        self.assertEqual(out.returncode, 0, out.stdout[-1500:])
        self.assertIn("the ATB's cost: 241 per kWh times the hours plus 372 per kW", out.stdout)
        self.assertIn("the sourced range draws the six rows with a range and no other", out.stdout)


class TheView(unittest.TestCase):
    def test_the_defaults_are_the_page_as_it_was_and_the_address_is_round_trip(self):
        v = node_eval("await (async () => { const V = await import('./lib/battery/view.ts'); const d = V.parseView({}); const q = V.viewQuery(d); const w = V.parseView({ u: 'kw', hf: 'l12+npv+irr', ch: 'revenue+debt', sc: 'log', wf: '2020', wt: '2024', lo: 'uri_2021+elliott_2022', it: 'chart', sm: 'pct', sp: '25', sx: 'irr' }); return { d, q, w, back: V.parseView(Object.fromEntries(V.viewQuery(w))), many: V.parseView({ hf: 'l12+bad+cover+npv+irr+toll+payback+npveq', ch: 'revenue+after_costs+after_debt+debt', sp: '500' }) }; })()")
        self.assertEqual(v["d"], {"units": "battery", "heads": ["l12", "bad", "cover"], "charts": ["revenue"], "scale": "adjusted", "from": None, "to": None, "out": [], "income": "table", "mode": "range", "pct": 10, "measure": "npv"})
        self.assertEqual(v["q"], [])
        self.assertEqual(v["w"]["units"], "kw")
        self.assertEqual(v["w"]["heads"], ["l12", "npv", "irr"])
        self.assertEqual(v["w"]["out"], ["elliott_2022", "uri_2021"])
        self.assertEqual(v["w"]["pct"], 25)
        self.assertEqual(v["back"], v["w"])
        self.assertEqual(len(v["many"]["heads"]), 6)
        self.assertEqual(len(v["many"]["charts"]), 3)
        self.assertEqual(v["many"]["pct"], 100)

    def test_the_view_file_is_pure(self):
        v = src("site", "lib", "battery", "view.ts")
        self.assertNotIn("import ", v)
        self.assertNotIn("use client", v)


class TheBox(unittest.TestCase):
    def test_five_sections_in_order_two_open(self):
        s = src("site", "app", "cost-of-power", "battery", "Settings.tsx")
        ids = re.findall(r'<SettingsFold id="([a-z]+)" title="([^"]+)" open=\{(true|false)\}', s)
        self.assertEqual(ids, [("battery", "Assumptions", "true"), ("heads", "Headline figures", "true"), ("charts", "Charts", "false"), ("financing", "Financing", "false"), ("sensitivity", "Sensitivity", "false")])
        self.assertIn('<section className="mb-4 bg-paper px-4 py-4" aria-label="Assumptions" data-settings="1">', s)
        self.assertIn("<BatteryFinancing ", s)
        self.assertIn('data-costs-in-a="1"', s)
        self.assertIn("scenario A gives the headline", s)

    def test_the_panel_is_the_shared_one_drawn_once_with_the_contract_as_a_sub_group(self):
        block = src("site", "components", "decisions", "ScenarioBlock.tsx")
        self.assertIn("export function ScenarioPanel(", block)
        self.assertIn("panel = true", block)
        self.assertIn('data-assumptions={s.view}', block)
        self.assertEqual(block.count("data-assumptions="), 1)
        sc = src("site", "app", "cost-of-power", "battery", "Scenarios.tsx")
        # session 297: the degradation method's sub-group joins the contract's
        self.assertIn('groups={[{ key: "degradation", title: "Degradation and augmentation", keys: ["method", "fade", "aug", "augcost"] }, { key: "contract", title: "The contract", keys: ["cshare", "cprice"] }]}', sc)
        self.assertIn("panel={false}", sc)
        self.assertNotIn("useRef", sc)
        form = src("site", "app", "cost-of-power", "battery", "BatteryForm.tsx")
        self.assertNotIn('data-costs-in-a="1"', form)
        self.assertIn("export const STRATEGY_WORDS", form)
        self.assertIn("Perfect foresight", form)

    def test_the_headline_offers_eight_figures_and_the_charts_four(self):
        v = src("site", "lib", "battery", "view.ts")
        self.assertEqual(re.findall(r'key: "(\w+)", label: "([^"]+)", words:', v)[:8],
                         [("l12", "Last twelve months, all streams"), ("bad", "A bad month: the 10th percentile, last 36 months"), ("cover", "Debt coverage, last twelve months"),
                          ("npv", "NPV at the hurdle rate"), ("irr", "IRR"), ("toll", "Breakeven toll"), ("payback", "Payback year"), ("npveq", "NPV per dollar of equity")])
        self.assertIn('{ key: "revenue", label: "Revenue by stream"', v)
        self.assertIn('{ key: "debt", label: "Debt"', v)
        self.assertIn("HEADS_MAX = 6, CHARTS_MAX = 3", v)


class TheIncomeTable(unittest.TestCase):
    def test_the_columns_are_the_years_the_last_twelve_months_and_the_readers_window(self):
        inc = src("site", "app", "cost-of-power", "battery", "Income.tsx")
        for words in ("usd: (s) => `l12:${s}`", "usd: (s) => `yr:${y.y}:${s}`", "usd: (s) => (whole ? `avg:${s}` : `win:${wk}:${s}`)", 'data-window-from="1"', 'data-window-to="1"', "data-leave-out={e.event}", 'data-chart-table="income"'):
            self.assertIn(words, inc)
        page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        for gone in ("y3:", "avg_without", "lastThreeYears", "Last three full years"):
            self.assertNotIn(gone, page, gone)
        self.assertIn("<Income ", page)
        self.assertIn("<BatteryCharts ", page)
        self.assertNotIn("function YearBars", page)

    def test_the_stat_recomputes_the_new_keys_from_months(self):
        v = node_eval("""await (async () => {
          const mk = (m, e, a) => [{ variable: 'foresight_4h_revenue_energy_usd_per_mw', ts_utc: m + '-01T00:00:00Z', value: e }, { variable: 'foresight_4h_revenue_ancillary_usd_per_mw', ts_utc: m + '-01T00:00:00Z', value: a },
            { variable: 'foresight_4h_revenue_total_usd_per_mw', ts_utc: m + '-01T00:00:00Z', value: e + a }, { variable: 'foresight_4h_days_held', ts_utc: m + '-01T00:00:00Z', value: 30 }, { variable: 'foresight_4h_days_in_month', ts_utc: m + '-01T00:00:00Z', value: 30 }, { variable: 'foresight_4h_days_left_out', ts_utc: m + '-01T00:00:00Z', value: 0 }];
          const rows = [];
          for (const y of ['2023', '2024']) for (let k = 1; k <= 12; k++) rows.push(...mk(y + '-' + String(k).padStart(2, '0'), 1000 + k, 100));
          const stress = [{ variable: 'foresight_4h_revenue_energy_usd_per_mw', ts_utc: '2024-02-15T00:00:00Z', value: 400, event: 'x' }, { variable: 'foresight_4h_revenue_ancillary_usd_per_mw', ts_utc: '2024-02-15T00:00:00Z', value: 50, event: 'x' }, { variable: 'foresight_4h_revenue_total_usd_per_mw', ts_utc: '2024-02-15T00:00:00Z', value: 450, event: 'x' }];
          const x = B.inputsOf({ grid: 'ercot', dur: '4', strat: 'foresight', mw: '10' });
          const st = (w) => B.stat(rows, stress, x, w);
          return { yr: st('yr:2023:energy'), yrkw: st('yr_kw:2024:total'), avg: st('avg:energy'), winAll: st('win:2023:2024:none:energy'), winOut: st('win:2023:2024:x:energy'), winOutProduct: st('win:2023:2024:x:regup'), win2024: st('win:2024:2024:none:total'), kw: st('win_kw:2024:2024:x:total') };
        })()""")
        self.assertEqual(v["yr"], 10 * sum(1000 + k for k in range(1, 13)))
        self.assertAlmostEqual(v["yrkw"], sum(1100 + k for k in range(1, 13)) / 1000)
        self.assertEqual(v["avg"], v["winAll"])
        # the window's average year is the mean of each calendar month over its two years: February's mean falls by 400 / 2
        self.assertEqual(v["winOut"], v["winAll"] - 10 * 400 // 2)
        self.assertIsNone(v["winOutProduct"])
        self.assertEqual(v["win2024"], 10 * sum(1100 + k for k in range(1, 13)))
        self.assertAlmostEqual(v["kw"], (sum(1100 + k for k in range(1, 13)) - 450) / 1000)


class TheSharedPieces(unittest.TestCase):
    def test_the_chart_and_the_tip_and_the_fold(self):
        tp = src("site", "components", "tool", "ToolPage.tsx")
        self.assertIn("export function SettingsFold(", tp)
        self.assertIn("export function Tip(", tp)
        self.assertIn('role="tooltip"', tp)
        chart = src("site", "components", "tool", "SeriesChart.tsx")
        self.assertIn('data-direct-labels="1"', chart)
        self.assertIn("data-chart-table={id}", chart)
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{3,8}\b(?![\w-])", re.sub(r"//.*", "", chart)))
        for token in ("var(--color-accent)", "var(--color-ink)", "var(--color-muted)", "var(--color-rule)", "var(--color-surface)"):
            self.assertIn(token, chart + src("site", "app", "cost-of-power", "battery", "Scenarios.tsx"))
        css = src("site", "app", "tokens.css")
        self.assertIn(".brand-a details[data-settings-fold][open] > summary [data-fold-summary] {", css)
        self.assertIn('.brand-a .tip:focus-within [role="tooltip"] {', css)
        self.assertEqual(css.count("{"), css.count("}"))

    def test_the_hovers_on_the_duration_and_the_strategies(self):
        form = src("site", "app", "cost-of-power", "battery", "BatteryForm.tsx")
        self.assertIn('<Tip id="duration" label="the duration">', form)
        self.assertIn('<Tip id="strategy" label="the strategy">', form)
        self.assertIn("title={STRATEGY_WORDS[s]}", form)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    sys.exit(unittest.main())
