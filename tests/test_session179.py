"""Session 179: "What a battery earns", decisions. What is held to:

  the finance of the two scenarios (site/lib/battery/finance.ts) equals a Python mirror written here from the Method
    note's formulas, on hand cases and on 300 seeded cases, to 1e-6: the debt payment, the flows to equity, the net
    present value, the internal rate of return by bisection, coverage, the breakeven toll and the merchant tail;
  the file of steps (site/data/battery_scenario_steps.json) holds the twelve cases the page opens to a visitor, each
    with twelve cells (round trip 86, 89, 92; cycle limit 0.5, 1, 1.5, 2), its default cell equal to the table as it
    stood at the build, and more revenue at a looser cycle limit in every month (a looser limit can never earn less);
  with the tables on the machine, the file still describes battery_stack_monthly over the page's window; when it does
    not, the test fails with the command that rebuilds it (the page meanwhile offers the default step alone and says so);
  the builder changes one bound of the model's own program and nothing else: at the model's values it returns the
    model's day exactly, and it leaves the model's function in place;
  the page: ten assumptions and no others, a Reset each, the seven rows in order, "Copy A to B", no request and no
    storage in the scenarios' code, no word of recommendation, no colour that judges, and the marked place for the
    usage event; the Method note states every formula.

No request, no model call; the environment is read, never set. Tests that need the tables, node or scipy skip when
they are absent. ERW_TABLES_DIR may name another copy's warehouse/output (read only)."""
import importlib.util
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
STEPS = os.path.join(ROOT, "site", "data", "battery_scenario_steps.json")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
EM = chr(0x2014)
KEYS = ["capex", "share", "rate", "term", "fom", "rte", "cycles", "deg", "life", "hurdle"]
FILES = ["warehouse/derived/battery_scenario_steps.py", "site/lib/battery/finance.ts", "site/app/cost-of-power/battery/Scenarios.tsx",
         "site/app/cost-of-power/battery/page.tsx", "site/app/cost-of-power/battery/BatteryForm.tsx",
         "site/scripts/test-battery-finance.mjs", "site/scripts/check-battery-scenarios.mjs", "docs/methods/battery_earns_algorithm.md",
         "tests/test_session179.py", "archive/sessions/SESSION_179_REPORT.md"]
REBUILD = "python warehouse/derived/battery_scenario_steps.py --in-dir warehouse/output"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


# ----------------------------------------------------------------------------------------------------------------------
# The mirror: docs/methods/battery_earns_algorithm.md, section 11.1, written again in Python. USD per kW; rates in percent.

def crf(rate, years):
    return 1 / years if rate == 0 else rate / (1 - (1 + rate) ** -years)


def debt_years(a):
    return min(a["term"], a["life"])


def debt_service(a):
    return a["capex"] * (a["share"] / 100) * crf(a["rate"] / 100, debt_years(a))


def flows(a, rev):
    ds, dy = debt_service(a), debt_years(a)
    out = [-a["capex"] * (1 - a["share"] / 100)]
    for t in range(1, a["life"] + 1):
        out.append(rev * (1 - a["deg"] / 100) ** (t - 1) - a["fom"] - (ds if t <= dy else 0))
    return out


def npv(rate_pct, fl):
    r = rate_pct / 100
    return sum(f / (1 + r) ** t for t, f in enumerate(fl))


def irr(fl):
    lo, hi = -99.0, 1000.0
    flo, fhi = npv(lo, fl), npv(hi, fl)
    if flo == 0:
        return lo
    if fhi == 0:
        return hi
    if (flo > 0) == (fhi > 0):
        return None
    for _ in range(200):
        if hi - lo <= 1e-10:
            break
        mid = (lo + hi) / 2
        fm = npv(mid, fl)
        if fm == 0:
            return mid
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


def coverage(a, rev):
    ds = debt_service(a)
    return (rev - a["fom"]) / ds if ds > 0 else None


def toll(a, target=1.25):
    ds = debt_service(a)
    return (target * ds + a["fom"]) / 12 if ds > 0 else None


def tail(a, rev):
    dy = debt_years(a)
    pv = sum((rev * (1 - a["deg"] / 100) ** (t - 1) - a["fom"]) / (1 + a["hurdle"] / 100) ** t for t in range(dy + 1, a["life"] + 1))
    return max(0, a["life"] - dy), pv


DEFAULT_4H = dict(capex=1110, share=60, rate=8, term=20, fom=22, rte=86, cycles=1, deg=0, life=20, hurdle=8)


def cases():
    """The default case, the edges, and 300 seeded cases."""
    out = [(DEFAULT_4H, 81.40219), (dict(DEFAULT_4H, term=10), 81.40219), (dict(DEFAULT_4H, capex=600, deg=2, hurdle=12), 140.0),
           (dict(DEFAULT_4H, share=0), 90.0), (dict(DEFAULT_4H, share=100), 90.0), (dict(DEFAULT_4H, rate=0), 120.0),
           (dict(DEFAULT_4H, term=40, life=5), 300.0), (dict(DEFAULT_4H, hurdle=0, life=1, term=1), 2000.0)]
    rng = random.Random(179)
    for _ in range(300):
        a = dict(capex=round(rng.uniform(100, 3000), 2), share=round(rng.uniform(0, 100), 1), rate=round(rng.uniform(0, 15), 2),
                 term=rng.randint(1, 40), fom=round(rng.uniform(0, 80), 2), rte=86, cycles=1, deg=round(rng.uniform(0, 6), 2),
                 life=rng.randint(1, 40), hurdle=round(rng.uniform(0, 25), 2))
        out.append((a, round(rng.uniform(0, 600), 4)))
    return out


def node_results(cs):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    d = tempfile.mkdtemp(prefix="erw179_")
    try:
        p = os.path.join(d, "cases.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump([dict(a=a, rev=rev) for a, rev in cs], f)
        r = subprocess.run([exe, os.path.join("scripts", "test-battery-finance.mjs"), "--cases", p], cwd=os.path.join(ROOT, "site"),
                           capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            raise AssertionError(r.stderr[-2000:])
        return json.loads(r.stdout)
    finally:
        shutil.rmtree(d, ignore_errors=True)


class TheFinanceByHand(unittest.TestCase):
    def test_the_default_debt_payment_is_the_pages(self):
        self.assertAlmostEqual(crf(0.08, 20), 0.101852209, places=9)
        self.assertEqual(round(debt_service(DEFAULT_4H) * 1000 * 100), 6783357)

    def test_coverage_of_the_default_case(self):
        self.assertEqual(f"{coverage(DEFAULT_4H, 81.40219):.2f}", "0.88")

    def test_flows_by_hand(self):
        a = dict(capex=1000, share=60, rate=0, term=10, fom=10, rte=86, cycles=1, deg=0, life=10, hurdle=0)
        fl = flows(a, 100)
        self.assertEqual(fl[0], -400)
        self.assertTrue(all(abs(v - 30) < 1e-12 for v in fl[1:]))
        self.assertAlmostEqual(npv(0, fl), -100)
        self.assertAlmostEqual(flows(dict(a, deg=10), 100)[3], 81 - 10 - 60)

    def test_the_rate_of_return_by_hand(self):
        self.assertAlmostEqual(irr([-100, 110]), 10, places=6)
        self.assertAlmostEqual(irr([-100, 0, 121]), 10, places=6)
        self.assertIsNone(irr([-100, -5, -5]))
        self.assertIsNone(irr([100, 5]))

    def test_the_toll_sets_coverage_to_one_and_a_quarter(self):
        t = toll(DEFAULT_4H)
        self.assertAlmostEqual((12 * t - DEFAULT_4H["fom"]) / debt_service(DEFAULT_4H), 1.25, places=12)
        self.assertEqual(f"{t:.2f}", "8.90")

    def test_the_tail_by_hand(self):
        a = dict(capex=1000, share=60, rate=0, term=10, fom=10, rte=86, cycles=1, deg=0, life=12, hurdle=10)
        years, pv = tail(a, 100)
        self.assertEqual(years, 2)
        self.assertAlmostEqual(pv, 90 / 1.1 ** 11 + 90 / 1.1 ** 12)
        self.assertEqual(tail(DEFAULT_4H, 81.4), (0, 0))


class ThePageLibraryIsTheMirror(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = cases()
        cls.got = node_results(cls.cases)

    def test_every_number_to_one_in_a_million(self):
        self.assertEqual(len(self.got), len(self.cases))
        for (a, rev), g in zip(self.cases, self.got):
            want_tail = tail(a, rev)
            pairs = [("debt", debt_service(a)), ("coverage", coverage(a, rev)), ("npv", npv(a["hurdle"], flows(a, rev))),
                     ("irr", irr(flows(a, rev))), ("toll", toll(a)), ("tail_years", want_tail[0]), ("tail_pv", want_tail[1])]
            for k, want in pairs:
                if want is None:
                    self.assertIsNone(g[k], f"{k} {a}")
                else:
                    self.assertIsNotNone(g[k], f"{k} {a}")
                    self.assertLessEqual(abs(g[k] - want), 1e-6 * max(1.0, abs(want)), f"{k} {a} {rev}: {g[k]} against {want}")
            fl = flows(a, rev)
            self.assertEqual(len(g["flows"]), len(fl))
            self.assertTrue(all(abs(x - y) <= 1e-6 * max(1.0, abs(y)) for x, y in zip(g["flows"], fl)), str(a))

    def test_the_cases_reach_both_outcomes_of_the_rate_of_return(self):
        got = [g["irr"] for g in self.got]
        self.assertGreater(sum(v is None for v in got), 10)
        self.assertGreater(sum(v is not None for v in got), 10)

    def test_the_hand_cases_of_the_node_script_pass(self):
        exe = shutil.which("node")
        r = subprocess.run([exe, os.path.join("scripts", "test-battery-finance.mjs")], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertNotIn("FAIL", r.stdout)


class TheStepsFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(STEPS):
            raise unittest.SkipTest("the file of steps is not on this machine")
        cls.doc = json.loads(src("site", "data", "battery_scenario_steps.json"))

    def test_the_cases_and_the_steps(self):
        d = self.doc
        self.assertEqual(d["rte_steps"], [86, 89, 92])
        self.assertEqual(d["cycle_steps"], [0.5, 1, 1.5, 2])
        self.assertEqual(d["default"], {"rte": 86, "cycles": 1})
        self.assertEqual(sorted(d["cases"]), sorted(f"{g}|{s}|{h}" for g in ("ercot", "caiso") for s in ("foresight", "dayahead") for h in (2, 4, 8)))
        self.assertRegex(d["built"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertRegex(d["model"]["sha256"], r"^[0-9a-f]{64}$")
        for k, c in d["cases"].items():
            n = len(c["months"])
            self.assertEqual(sorted(c["cells"]), sorted(f"{r}|{y:g}" for r in (86, 89, 92) for y in (0.5, 1, 1.5, 2)), k)
            self.assertTrue(all(len(v) == n for v in c["cells"].values()) and len(c["days"]) == n and len(c["table"]) == n, k)
            self.assertEqual(c["months"], sorted(c["months"]), k)
            self.assertEqual((c["first"] <= c["months"][0], c["last"]), (True, c["months"][-1]), k)

    def test_the_default_cell_is_the_table_as_built(self):
        for k, c in self.doc["cases"].items():
            for m, a, b in zip(c["months"], c["cells"]["86|1"], c["table"]):
                self.assertLessEqual(abs(a - b), self.doc["tolerance_usd_per_mw"], f"{k} {m}")

    def test_a_looser_cycle_limit_never_earns_less(self):
        for k, c in self.doc["cases"].items():
            for r in (86, 89, 92):
                for lo, hi in (("0.5", "1"), ("1", "1.5"), ("1.5", "2")):
                    for m, a, b in zip(c["months"], c["cells"][f"{r}|{lo}"], c["cells"][f"{r}|{hi}"]):
                        self.assertGreaterEqual(b, a - 0.01, f"{k} {m} round trip {r}: {hi} cycles {b}, {lo} cycles {a}")

    def test_the_default_case_is_the_pages_headline(self):
        c = self.doc["cases"]["ercot|foresight|4"]
        if c["last"] != "2026-09":
            self.skipTest("the file has been rebuilt for a later window; the dated figure no longer applies")
        self.assertEqual(f"{sum(c['cells']['86|1'][-12:]) / 1000:.2f}", "81.40")

    def test_the_file_still_describes_the_table(self):
        path = os.path.join(TABLES, "battery_stack_monthly.csv")
        if not os.path.exists(path):
            self.skipTest("battery_stack_monthly is not on this machine")
        sys.path.insert(0, DERIVED)
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
        try:
            import pandas  # noqa: F401
            import battery_dispatch_export as ex
        except ImportError as e:
            self.skipTest(f"the table's readers are not on this machine: {e}")
        monthly = ex.read_monthly(TABLES)
        hub = {"ercot": "ercot:HB_HUBAVG", "caiso": "caiso:TH_SP15_GEN-APND"}
        for k, c in self.doc["cases"].items():
            grid, strat, dur = k.split("|")
            months = ex.months_of(monthly, hub[grid], strat, int(dur))
            first, last, held = ex.last_36(months)
            at = {m: i for i, m in enumerate(c["months"])}
            why = f"{k}: the file of steps no longer describes battery_stack_monthly; rebuild it with: {REBUILD}"
            self.assertTrue(all(m in at for m in held), f"{why} (the table's window is {first} to {last}, the file's {c['first']} to {c['last']})")
            for m in held:
                self.assertEqual(c["days"][at[m]], months[m]["days_held"], f"{why} ({m}: days)")
                self.assertLessEqual(abs(c["cells"]["86|1"][at[m]] - months[m]["revenue_total_usd_per_mw"]), self.doc["tolerance_usd_per_mw"], f"{why} ({m})")


class TheBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, DERIVED)
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
        try:
            import numpy as np
            import battery_scenario_steps as st
        except ImportError as e:
            raise unittest.SkipTest(f"the model's packages are not on this machine: {e}")
        cls.st, cls.bs, cls.np = st, st.bs, np
        rng = random.Random(1790)
        cls.energy = [round(20 + 60 * math.sin(t / 24 * 2 * math.pi - 2) + rng.uniform(-8, 8), 2) for t in range(24)]
        cls.reserves = [[round(rng.uniform(0, 12), 2) for _ in range(24)], [round(rng.uniform(0, 6), 2) for _ in range(24)]]
        cls.spec = ((True, 1.0), (False, 1.0))

    def test_at_the_models_values_it_is_the_models_day(self):
        own = self.bs.solve_day(self.energy, self.reserves, self.spec, 4)
        got = self.st.solve(self.energy, self.reserves, self.spec, 4, self.bs.RTE, 1.0)
        self.assertAlmostEqual(got["total"], own["total"], places=9)
        self.assertTrue(self.np.allclose(got["discharge"], own["discharge"]))

    def test_the_cycle_limit_binds_at_its_step_and_looser_earns_no_less(self):
        totals = []
        for c in (0.5, 1.0, 1.5, 2.0):
            sol = self.st.solve(self.energy, self.reserves, self.spec, 4, 0.86, c)
            self.assertLessEqual(float((sol["discharge"] / math.sqrt(0.86)).sum()), c * 4 + 1e-6)
            totals.append(sol["total"])
        self.assertEqual(totals, sorted(totals))
        self.assertLess(totals[0], totals[1])

    def test_the_models_function_is_left_in_place(self):
        before = self.bs.structure
        self.st.solve(self.energy, self.reserves, self.spec, 2, 0.92, 2.0)
        self.assertIs(self.bs.structure, before)
        self.assertIs(self.bs.structure, self.st._model_structure)

    def test_it_writes_a_site_file_and_nothing_in_the_warehouse(self):
        text = src("warehouse", "derived", "battery_scenario_steps.py")
        for word in ("write_table", "write_csv", "_require_lock", "update_sources", "write_status", "set_out_dir"):
            self.assertNotIn(word, text, word)
        for word in ("anthropic", "requests.", "urlopen", "http.client"):
            self.assertNotIn(word, text.lower(), word)
        self.assertIn('os.path.join(ROOT, "site", "data", "battery_scenario_steps.json")', text)

    def test_the_model_file_is_not_changed_by_this_session(self):
        text = src("warehouse", "derived", "battery_stack.py")
        self.assertIn("def solve_day(energy, reserves, spec, duration, rte=RTE, force_switch=False, caps=None):", text)
        self.assertIn("rows.append(cyc); b.append(duration)             # at most one full cycle a day", text)


class ThePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.block = src("site", "app", "cost-of-power", "battery", "Scenarios.tsx")
        cls.lib = src("site", "lib", "battery", "finance.ts")
        cls.page = src("site", "app", "cost-of-power", "battery", "page.tsx")

    def test_ten_assumptions_and_no_others(self):
        hit = re.search(r"export const KEYS: Key\[\] = \[(.*?)\];", self.lib)
        self.assertEqual(re.findall(r'"(\w+)"', hit.group(1)), KEYS)
        for k in KEYS:
            self.assertEqual(self.lib.count(f'  {k}: {{ key: "{k}", letter: "'), 1, k)
        self.assertEqual(self.lib.count('{ key: "'), 10)
        self.assertEqual(self.lib.count(", source: "), 10)

    def test_the_defaults_and_what_they_cite(self):
        self.assertIn("return { capex: costs.capex, share: 60, rate: 8, term: 20, fom: costs.fom, rte: MODEL.rte, cycles: MODEL.cycles, deg: 0, life: 20, hurdle: 8 };", self.lib)
        self.assertIn("export const MODEL = { rte: 86, cycles: 1 };", self.lib)
        stack = src("site", "lib", "batterystack.ts")
        self.assertIn("export const DEBT = { share: 0.6, rate: 0.08, life: 20 };", stack)   # the page's own, cited to Lazard
        self.assertIn("export const RTE = 0.86;", stack)
        note = src("docs", "methods", "cost_of_power.md")
        self.assertIn("86 percent, the low end of Lazard's 92 to 86 percent", note)           # the efficiency steps' range
        self.assertIn('"60% debt at an 8% interest rate"', note)
        # the two defaults no source in the repository gives say so on the page, and are not dressed as cited
        self.assertIn("No cited rate is held. The default is set equal to the interest rate", self.lib)
        self.assertIn("The model has no capacity fade. No cited rate is held, so the default is none", self.lib)

    def test_a_reset_each_one_for_all_and_copy_a_to_b(self):
        self.assertIn("data-reset={k}", self.block)
        self.assertIn(">Reset</button>", self.block)
        self.assertIn("data-reset-all", self.block)
        self.assertIn(">Copy A to B</button>", self.block)

    def test_the_seven_rows_in_order_and_the_last_in_words(self):
        keys = re.findall(r'\{ key: "(\w+)", label: "', self.block)
        self.assertEqual(keys, ["revenue", "p10", "coverage", "npv", "irr", "toll", "tail"])
        self.assertLess(self.block.index('data-row={r.key}'), self.block.index('data-row="differs"'))
        self.assertIn("differenceWords(s.a, s.b)", self.block)

    def test_it_computes_in_the_browser_and_asks_for_nothing(self):
        self.assertTrue(self.block.startswith('"use client";'))
        for word in ("fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "sessionStorage", "document.cookie", "router.", "useRouter"):
            self.assertNotIn(word, self.block, word)
        self.assertIn("window.history.replaceState(", self.block)
        self.assertNotRegex(self.lib, r"(?m)^import ")
        self.assertNotIn('from "react"', self.lib)

    def test_no_word_of_recommendation_and_no_colour_that_judges(self):
        text = re.sub(r"(?m)^\s*//.*$", "", self.block)
        for word in ("better", "worse", "attractive", "should", "recommend", "best", "worst", "good", "poor", "prefer", "favou", "favor"):
            self.assertNotRegex(text.lower(), rf"\b{word}", word)
        for colour in ("color-up", "color-down", "#175E54", "green", "red-", "#8C1515"):
            self.assertNotIn(colour, text, colour)
        self.assertIn('const DOWN = "#2a78d6", UP = "#eb6834";', self.block)
        tokens = src("site", "app", "tokens.css")
        self.assertIn("--color-fuel-gas: #2a78d6;", tokens)
        self.assertIn("--color-fuel-coal: #eb6834;", tokens)

    def test_the_place_for_the_usage_event_is_marked_once(self):
        line = '// session 179: track("scenario compared") goes here once site/lib/usage.ts is on main'
        self.assertEqual(self.block.count(line), 1)
        self.assertNotIn("lib/usage\"", self.block)
        self.assertNotIn("import(", self.block)

    def test_the_page_draws_the_block_once_after_the_contract(self):
        self.assertEqual(self.page.count("<Scenarios "), 1)
        self.assertLess(self.page.index("<ContractResult "), self.page.index("<Scenarios "))
        self.assertLess(self.page.index("<Scenarios "), self.page.index('<ToolSection title="Other grids"'))
        self.assertIn('"/cost-of-power/battery": "review",', src("site", "lib", "release.ts"))

    def test_the_other_links_carry_the_scenarios(self):
        form = src("site", "app", "cost-of-power", "battery", "BatteryForm.tsx")
        self.assertEqual(form.count("carry("), 3)
        self.assertIn('for (const k of ["grid", "dur", "strat", "mw", "fom", "ds"])', form)   # the six the page had, unchanged


class TheNote(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.note = src("docs", "methods", "battery_earns_algorithm.md")

    def test_every_formula_is_stated(self):
        self.assertIn("### 11.1 Scenarios A and B", self.note)
        part = self.note[self.note.index("### 11.1 Scenarios A and B"):]
        for words in ("capex x share x crf(rate, n)", "n = min(term, life)", "R_t = R x (1 - deg)^(t - 1)", "F_0 = -capex x (1 - share)",
                      "NPV = sum over t = 0 to life of F_t / (1 + hurdle)^t", "bisection", "-99", "1,000", "(R - fom) / debt",
                      "toll = (1.25 x debt + fom) / 12", "t = n + 1 to life", "battery_scenario_steps.py", "86, 89 and 92", "0.5, 1, 1.5 and 2",
                      "replaceState", "to be confirmed"):
            self.assertIn(words, part, words)
        for k in ("ac", "as", "ar", "at", "af", "ae", "ay", "ad", "al", "ah"):
            self.assertIn(f"`{k}`", part, k)


class House(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            p = os.path.join(ROOT, *f.split("/"))
            if os.path.exists(p):
                self.assertNotIn(EM, src(*f.split("/")), f)

    def test_the_new_modules_names_are_their_own(self):
        names = {}
        for top in ("warehouse", "scripts", "tests"):
            for d, dirs, files in os.walk(os.path.join(ROOT, top)):
                dirs[:] = [x for x in dirs if x not in ("output", "__pycache__", "node_modules", "raw")]
                for f in files:
                    if f.endswith(".py"):
                        names.setdefault(f, []).append(os.path.relpath(os.path.join(d, f), ROOT))
        for f in ("battery_scenario_steps.py", "test_session179.py"):
            self.assertEqual(len(names.get(f, [])), 1, names.get(f))

    def test_the_file_of_steps_keeps_its_line_ends(self):
        self.assertIn("site/data/battery_scenario_steps.json text eol=lf", src(".gitattributes"))


if __name__ == "__main__":
    unittest.main()
