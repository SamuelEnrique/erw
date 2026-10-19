"""Session 263: "What a battery earns" (/cost-of-power/battery), deep, for the owner's technical review (the chain of 14
October 2026).

Energy Research Warehouse (ERW). What is held here:
- the edge cases at the library: an address that asks for what the page does not show (a grid not held, a duration or
  strategy the model was not run at, a size outside 1 to 5,000 MW, a scenario value outside its field's bounds or not a
  step) is said in one line, never replaced in silence (typedNotes in site/lib/batterystack.ts, scenarioNotes and
  clampWords in site/lib/battery/finance.ts); a leap February counts on the 90 percent rule over 29 days; a month with
  one day held never counts; a debt term or a contract longer than the project is cut to the project's life;
- the page draws the one status line and the field's note, and CAISO's line beside its market monitor says in one
  sentence why the two differ, quoting the monitor's reason as docs/methods/battery_stack.md quotes it;
- the replication files take the page's defaults (20 percent debt, a hurdle rate of 12) and rebuild scenario A's column:
  the Python mirror run on the committed CSV gives the page's library's values, and the do-file mirrors it display for
  display;
- the figures once marked [c] are in the methods note's section 11.2 and in site/scripts/check-battery-figures.mjs, each
  value printed in both, and the review pack carries no [c];
- no em dash in what the session wrote.
Nothing here sets the environment at import, reads a table or makes a request. Node runs the libraries (skipped when
node is not on the machine).
"""

import importlib.util
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
PUBLIC = os.path.join(SITE, "public", "battery")
CSV_PATH = os.path.join(PUBLIC, "erw_2026_battery_dispatch.csv")
PACK = os.path.join(ROOT, "docs", "reviews", "packs", "battery.md")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    out = subprocess.run([exe, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise AssertionError(out.stderr[-2000:])
    return json.loads(out.stdout.strip().split("\n")[-1])


def load_mirror():
    spec = importlib.util.spec_from_file_location("erw_battery_replication_263", os.path.join(PUBLIC, "erw_2026_battery_replication.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TheEdgeCasesAtTheLibrary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.got = node(r"""
const B = await import("./lib/batterystack.ts");
const F = await import("./lib/battery/finance.ts");
const notes = (q) => B.typedNotes(q, B.inputsOf(q, false));
const d = F.defaultsOf(B.COSTS[4]);
const steps = { rte: [86, 89, 92], cycles: [0.5, 1, 1.5, 2] };
const month = (m, held, days) => [
  { variable: "foresight_4h_days_held", ts_utc: m + "-01T00:00:00Z", value: held },
  { variable: "foresight_4h_days_in_month", ts_utc: m + "-01T00:00:00Z", value: days },
  { variable: "foresight_4h_days_left_out", ts_utc: m + "-01T00:00:00Z", value: 0 },
  { variable: "foresight_4h_revenue_total_usd_per_mw", ts_utc: m + "-01T00:00:00Z", value: 1000 },
  { variable: "foresight_4h_revenue_energy_usd_per_mw", ts_utc: m + "-01T00:00:00Z", value: 600 },
  { variable: "foresight_4h_revenue_ancillary_usd_per_mw", ts_utc: m + "-01T00:00:00Z", value: 400 },
];
const year = ["2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"];
const leap = (held) => B.monthsOf(year.flatMap((m) => month(m, m === "2024-02" ? held : 30, m === "2024-02" ? 29 : 30)), "foresight", 4);
const withOne = B.monthsOf([...year.flatMap((m) => month(m, m === "2024-02" ? 29 : 30, m === "2024-02" ? 29 : 30)), ...month("2025-01", 1, 31)], "foresight", 4);
const long = { ...d, term: 30 }, contract = { ...d, term: 30, cshare: 50, cprice: 10 };
console.log(JSON.stringify({
  none: notes({ grid: "ercot", dur: "4", strat: "foresight", mw: "100" }),
  pjm: notes({ grid: "pjm" }), xyz: notes({ grid: "xyz" }), nyiso: notes({ grid: "nyiso" }),
  nyisoInternal: B.typedNotes({ grid: "nyiso" }, B.inputsOf({ grid: "nyiso" }, true)),
  dur3: notes({ dur: "3" }), strat: notes({ strat: "other" }),
  mw0: notes({ mw: "0" }), mwBig: notes({ mw: "99999" }), mwText: notes({ mw: "abc" }), mw1: notes({ mw: "1" }), mw1000: notes({ mw: "1000" }),
  mwOf: [B.inputsOf({ mw: "0" }).mw, B.inputsOf({ mw: "99999" }).mw, B.inputsOf({ mw: "abc" }).mw, B.inputsOf({ mw: "1000" }).mw],
  scen: F.scenarioNotes({ ac: "99999", bt: "20.5", ae: "90", af: "abc", ah: "12" }, d, steps),
  scenOk: F.scenarioNotes({ ac: "1200", at: "25", ae: "92" }, d, steps),
  clamp: [F.clampWords("capex", 99999, 10000), F.clampWords("term", 20.5, 21), F.clampWords("fom", -3, 0)],
  leap26: leap(26).find((r) => r.m === "2024-02").held, leap27: leap(27).find((r) => r.m === "2024-02").held,
  oneDay: withOne.find((r) => r.m === "2025-01").held, oneDayWhole: withOne.find((r) => r.m === "2025-01").whole,
  l12: (() => { const t = B.lastTwelve(withOne); return t ? [t[0].m, t[11].m] : null; })(),
  bad: B.badMonth(withOne).m,
  debtYears: F.debtYears(long), tail: F.merchantTail(long, 81.4).years,
  contractYears: [1, 20, 21].map((t) => F.incomeInYear(contract, 81.4, t)),
  flowsLength: F.flows(long, 81.4).length,
  debtLong: F.debtUsd(long, 100), debtTwenty: F.debtUsd(d, 100),
}));
""")

    def test_an_address_read_as_given_says_nothing(self):
        self.assertEqual(self.got["none"], [])
        self.assertEqual(self.got["mw1"], [])
        self.assertEqual(self.got["mw1000"], [])
        self.assertEqual(self.got["scenOk"], [])
        self.assertEqual(self.got["nyisoInternal"], [])  # a grid in review opens in the internal view as asked

    def test_a_grid_the_tool_does_not_show_is_said(self):
        self.assertEqual(self.got["pjm"], ["PJM is not built for this tool (license needed): ERCOT is shown."])
        self.assertEqual(self.got["xyz"], ["The grid asked for is not a grid this tool holds: ERCOT is shown."])
        self.assertEqual(self.got["nyiso"], ["NYISO is in review and opens in the internal view only: ERCOT is shown."])
        self.assertEqual(self.got["dur3"], ["The model is run at 2, 4 and 8 hours: 4 hours is shown."])
        self.assertEqual(self.got["strat"], ["The strategy asked for is not one of the two: perfect foresight is shown."])

    def test_a_size_outside_its_bounds_is_brought_to_them_and_said(self):
        self.assertEqual(self.got["mwOf"], [1, 5000, 100, 1000])
        self.assertEqual(self.got["mw0"], ["0 MW is outside the size field's bounds, 1 to 5,000 MW: 1 MW is shown."])
        self.assertEqual(self.got["mwBig"], ["99,999 MW is outside the size field's bounds, 1 to 5,000 MW: 5,000 MW is shown."])
        self.assertEqual(self.got["mwText"], ["The size asked for is not a number: 100 MW is shown."])

    def test_a_scenario_value_outside_its_field_is_said(self):
        self.assertEqual(self.got["scen"], [
            "Capital cost, scenario A: 99,999 is outside the field's bounds, 0 to 10,000 USD per kW, so 10,000 is used.",
            "Fixed O&M, scenario A: the value asked for is not a number, so the default 22 is used.",
            "Round-trip efficiency, scenario A: 90 is not a step the model was run at, so 86 is used.",
            "Term of the debt, scenario B: 20.5 is not a whole number of years, so 21 is used.",
        ])
        self.assertEqual(self.got["clamp"], [
            "99,999 was typed: the field runs from 0 to 10,000, so 10,000 is used.",
            "20.5 was typed: the field takes whole years, so 21 is used.",
            "-3 was typed: the field runs from 0 to 500, so 0 is used.",
        ])

    def test_a_leap_february_counts_on_its_29_days(self):
        self.assertFalse(self.got["leap26"])   # 26 of 29 is 89.7 percent
        self.assertTrue(self.got["leap27"])    # 27 of 29 is 93.1 percent

    def test_a_month_with_one_day_held_never_counts(self):
        self.assertFalse(self.got["oneDay"])
        self.assertFalse(self.got["oneDayWhole"])
        self.assertEqual(self.got["l12"], ["2024-01", "2024-12"])
        self.assertNotEqual(self.got["bad"], "2025-01")

    def test_a_debt_or_a_contract_longer_than_the_project_is_cut_to_its_life(self):
        self.assertEqual(self.got["debtYears"], 20)
        self.assertEqual(self.got["tail"], 0)
        self.assertEqual(self.got["flowsLength"], 21)          # year 0 and the twenty years of the life, never more
        self.assertEqual(self.got["debtLong"], self.got["debtTwenty"])
        y1, y20, y21 = self.got["contractYears"]
        self.assertAlmostEqual(y1, 0.5 * 10 * 12 + 0.5 * 81.4, places=9)
        self.assertLess(y21, y1)   # year 21 does not exist in the cash flows; incomeInYear past the debt is the market alone


class ThePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        cls.scen = src("site", "app", "cost-of-power", "battery", "Scenarios.tsx")

    def test_one_status_line_for_what_the_address_did_not_get(self):
        self.assertIn("const asItWas = [...typedNotes(q, asked), ...scenarioNotes(q, defaultsOf(COSTS[asked.dur]), offered)];", self.page)
        self.assertIn('role="status" data-typed-notes={asItWas.length}>{asItWas.join(" ")}</p>', self.page)
        self.assertEqual(self.page.count("data-typed-notes="), 1)

    def test_a_typed_value_brought_inside_its_bounds_says_so_under_the_field(self):
        # session 296: the field draws the line itself from the value typed and the value used (no ref is read in render);
        # the page hands it the words
        self.assertIn("clamp: (t: number, u: number) => clampWords(k, t, u) };", self.scen)
        self.assertIn("note: <>Default {sp.plain(d[k])}. {sourceOf(k)}.</>, clamp:", self.scen)   # session 297: a choice's default is words
        block = src("site", "components", "decisions", "ScenarioBlock.tsx")
        self.assertIn("bound: (key: string, v: number) => number;", block)   # the shared block's bound is not changed
        self.assertIn('<span className="mt-1 block text-xs leading-snug text-muted" data-clamped={f.key}>{clamped}</span>', block)
        # session 298 (ruling 8a): a field without its page's own words takes the shared component's
        self.assertIn("const clamped = typed !== null && read(typed) === value ? words(typed, value) : null;", block)
        self.assertIn("const words = f.clamp ?? ((t: number, u: number) =>", block)

    def test_no_debt_and_a_term_above_the_life_are_said_as_they_are(self):
        # fixed on the local build of 14 October 2026: "covered its debt not held times", and a tail note that called a
        # term of 30 years "both 20 years"
        self.assertIn("const noDebt = total !== null && cover === null;", self.scen)
        self.assertEqual(self.scen.count('<span data-no-debt="1">has no debt to cover.</span>'), 2)
        self.assertIn('<span data-no-debt="2">No debt</span>', self.scen)
        self.assertIn("c.y.term > c.y.life ? `0 years: the term of ${plain(c.y.term)} years is cut to the life, ${plain(c.y.life)} years`", self.scen)

    def test_caisos_line_says_why_the_two_differ(self):
        line = self.page[self.page.index("data-fleet-beside="):]
        line = line[:line.index("</p>")]
        self.assertIn('<span data-fleet-why="1">The two differ in regulation: this model sells it as if the market had no size, and the monitor writes that '
                      "&ldquo;there is a large amount of battery capacity competing to provide a relatively low amount of required regulation&rdquo;.</span>", line)
        note = src("docs", "methods", "battery_stack.md")
        self.assertIn("there is a large amount of battery capacity competing to provide a relatively low amount of required regulation", note)
        self.assertIn("it sells as if the market had no size", note)


class TheReplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.do = src("site", "public", "battery", "erw_2026_battery_replication.do")
        cls.mirror = load_mirror()
        cls.n = cls.mirror.numbers(cls.mirror.read(CSV_PATH))

    def test_the_first_line_is_a_comment_in_the_house_form(self):
        self.assertTrue(self.do.split("\n", 1)[0].startswith("* ERW, What a battery earns (/cost-of-power/battery): the headline numbers of the default case"))

    def test_the_defaults_are_the_pages(self):
        for line in ("scalar s_debt_share = 0.2", "scalar s_debt_rate = 0.08", "scalar s_debt_years = 20", "scalar s_life_years = 20",
                     "scalar s_degradation = 0.026", "scalar s_hurdle_pct = 12", "scalar s_toll_target = 1.25"):
            self.assertIn(line + "\n", self.do)
        m = self.mirror
        self.assertEqual((m.DEBT_SHARE, m.DEBT_RATE, m.DEBT_YEARS, m.LIFE_YEARS, m.DEGRADATION, m.HURDLE_PCT, m.TOLL_TARGET), (0.2, 0.08, 20, 20, 0.026, 12, 1.25))
        fin = src("site", "lib", "battery", "finance.ts")
        self.assertIn("export const SHARE = 20;", fin)
        self.assertIn("export const HURDLE = 12;", fin)
        self.assertIn("export const DEG = 2.6;", fin)
        self.assertIn("export const IRR_LOW = -99, IRR_HIGH = 1000;", fin)

    def test_the_mirror_rebuilds_the_default_case_on_the_committed_csv(self):
        n = self.n
        self.assertEqual((n["l12_first"], n["l12_last"]), ("2025-10", "2026-09"))
        self.assertEqual(f"{n['l12_kw_total']:.2f}", "81.40")
        self.assertEqual(n["l12_total_usd"], 8140219)
        self.assertEqual(n["l12_share_ancillary"], 33)
        self.assertEqual(n["debt_service"], 2261119)
        self.assertEqual(f"{n['cover']:.2f}", "2.63")
        self.assertEqual(f"{n['a_coverage']:.2f}", "2.63")
        self.assertEqual(f"{n['npv_kw']:.2f}", "-697.80")
        self.assertEqual(n["npv_usd"], -69779883)
        self.assertEqual(f"{n['irr']:.1f}", "-8.8")
        self.assertEqual(f"{n['toll']:.2f}", "4.19")
        self.assertEqual((n["tail_years"], n["tail_usd"]), (0, 0))
        self.assertEqual((n["bad_month"], n["p10_36_usd"], n["n36"]), ("2024-12", 475477, 36))

    def test_the_mirror_equals_the_library_on_the_same_months(self):
        js = r"""
import fs from "node:fs";
const B = await import("./lib/batterystack.ts");
const F = await import("./lib/battery/finance.ts");
const lines = fs.readFileSync("public/battery/erw_2026_battery_dispatch.csv", "utf-8").split("\n").filter((l) => l && !l.startsWith("#"));
const head = lines[0].split(","), col = (n) => head.indexOf(n);
const by = new Map();
for (const l of lines.slice(1)) {
  const c = l.split(","), m = c[col("local_month")];
  if (!by.has(m)) by.set(m, { days: new Set(), sums: {} });
  const o = by.get(m); o.days.add(c[col("local_day")]);
  for (const k of ["energy", "regup", "regdn", "rrs", "ecrs", "nspin", "ancillary", "total"]) { const v = Number(c[col("revenue_" + k + "_usd")]); o.sums[k] = (o.sums[k] ?? 0) + (v === -999 ? 0 : v); }
}
const rows = [];
for (const [m, o] of by) {
  const [y, mo] = m.split("-").map(Number), dim = new Date(Date.UTC(y, mo, 0)).getUTCDate(), ts = m + "-01T00:00:00Z";
  rows.push({ variable: "foresight_4h_days_held", ts_utc: ts, value: o.days.size }, { variable: "foresight_4h_days_in_month", ts_utc: ts, value: dim },
    { variable: "foresight_4h_days_left_out", ts_utc: ts, value: dim - o.days.size });
  for (const [k, v] of Object.entries(o.sums)) rows.push({ variable: "foresight_4h_revenue_" + k + "_usd_per_mw", ts_utc: ts, value: v });
}
const d = F.defaultsOf(B.COSTS[4]), x = { ...B.inputsOf({}), fom: d.fom, ds: F.debtUsd(d, 100) };
const st = (s) => B.stat(rows, [], x, s), r = F.resultOf(d, st("l12_kw:total"));
console.log(JSON.stringify({ kw: st("l12_kw:total"), usd: st("l12:total"), share: st("l12_share:ancillary"), ds: st("ds"), cover: st("cover"), p10: st("p10_36"), n36: st("n36"),
  npv: r.npv, irr: r.irr, toll: r.toll, tail: r.tail.pv, coverage: r.coverage }));
"""
        lib, n = node(js), self.n
        self.assertAlmostEqual(lib["kw"], n["l12_kw_total"], places=9)
        self.assertEqual(lib["usd"], n["l12_total_usd"])
        self.assertEqual(lib["share"], n["l12_share_ancillary"])
        self.assertEqual(lib["ds"], n["debt_service"])
        self.assertAlmostEqual(lib["cover"], n["cover"], places=9)
        self.assertAlmostEqual(lib["coverage"], n["a_coverage"], places=9)
        self.assertEqual(lib["p10"], n["p10_36_usd"])
        self.assertEqual(lib["n36"], n["n36"])
        self.assertAlmostEqual(lib["npv"], n["npv_kw"], places=8)
        self.assertAlmostEqual(lib["irr"], n["irr"], places=8)
        self.assertAlmostEqual(lib["toll"], n["toll"], places=9)
        self.assertEqual(round(lib["tail"] * 1000 * 100), n["tail_usd"])

    def test_the_do_file_mirrors_the_finance(self):
        for words in ("program define erw_npv", "scalar s_debt_years_used = min(s_debt_years, s_life_years)",
                      "cond(`t' <= s_debt_years_used, s_debt_kw, 0)", "forvalues i = 1/200 {", "if s_go == 1 & s_done == 0 & s_hi - s_lo > 1e-10 {",
                      "scalar s_lo = -99", "scalar s_hi = 1000", "(s_toll_target * s_debt_kw + s_fom_usd_kw_year) / 12",
                      "Not run: Stata is not on the machine that wrote it"):
            self.assertIn(words, self.do, words)
        shown = [re.search(r'display "([^"`:]*)', line).group(1) for line in self.do.split("\n") if re.search(r'(^|\s)display "', line)]
        out = "\n".join(self.mirror.report(self.n))
        for words in shown:
            self.assertIn(words.strip(), out, words)
        for words in ("scenario A, NPV at the hurdle rate, USD per kW", "scenario A, IRR, percent a year", "scenario A, breakeven toll", "scenario A, merchant tail"):
            self.assertIn(words, "\n".join(shown))
        self.assertNotIn("\t", self.do)


class TheComputedFigures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = src("site", "scripts", "check-battery-figures.mjs")
        cls.note = src("docs", "methods", "battery_earns_algorithm.md")
        cls.pack = src("docs", "reviews", "packs", "battery.md")
        cls.expected = re.findall(r'^\s*\["([^"]+)", (-?[\d.]+|"[^"]+"), (\d|null)\],', cls.script, re.M)

    def test_the_script_checks_every_figure_and_exits_on_a_difference(self):
        self.assertEqual(len(self.expected), 32)
        self.assertIn("process.exit(bad ? 1 : 0);", self.script)
        self.assertIn('await import("../lib/batterystack.ts")', self.script)
        self.assertIn('await import("../lib/battery/finance.ts")', self.script)
        self.assertNotIn("SERVICE", self.script)          # the anon key only

    def test_each_figure_is_printed_in_the_note_and_the_pack(self):
        section = self.note.split("### 11.2 The figures no check key carries (session 263)", 1)[1].split("\n## ", 1)[0]
        for name, value, dp in self.expected:
            if value.startswith('"'):
                words = value.strip('"')
                self.assertIn(words, section, name)
                self.assertIn(words, self.pack, name)
                continue
            v = float(value)
            shown = f"{v:,.{int(dp)}f}"
            self.assertTrue(shown in self.pack or shown.replace(",", "") in self.pack, f"{name}: {shown} not in the pack")
            if "ercot 4h foresight" not in name:
                self.assertTrue(shown in section or shown.replace(",", "") in section, f"{name}: {shown} not in section 11.2")

    def test_no_figure_of_the_pack_needs_the_mark(self):
        self.assertNotIn("[c]", self.pack)
        self.assertFalse(os.path.exists(os.path.join(ROOT, "docs", "howitworks", "battery.md")))

    def test_no_em_dash(self):
        for parts in (("docs", "reviews", "packs", "battery.md"), ("docs", "methods", "battery_earns_algorithm.md"), ("site", "scripts", "check-battery-figures.mjs"),
                      ("site", "public", "battery", "erw_2026_battery_replication.do"), ("site", "public", "battery", "erw_2026_battery_replication.py"),
                      ("site", "lib", "batterystack.ts"), ("site", "lib", "battery", "finance.ts"), ("site", "app", "cost-of-power", "battery", "page.tsx"),
                      ("site", "app", "cost-of-power", "battery", "Scenarios.tsx"), ("docs", "howitworks", "README.md"), ("tests", "test_session263.py")):
            self.assertEqual(src(*parts).count(EM), 0, "/".join(parts))


if __name__ == "__main__":
    unittest.main()
