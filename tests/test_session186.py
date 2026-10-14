"""Session 186: "What a generator earns", decisions, as session 179 built them for the battery. What is held to:

  the finance of the two scenarios (site/lib/seller/finance.ts) equals a Python mirror written here from the Method
    note's formulas, on hand cases and on 300 seeded cases, to 1e-6: the debt payment, the flows to equity, the net
    present value, the internal rate of return by bisection, coverage, a month's coverage, the contract price for the
    whole of the energy and the toll that each set coverage to 1.25, and every bar of the sensitivity chart;
  the default case from the snapshot the page reads: the scenario's debt payment and coverage are the page's own;
  the page: eight assumptions and no others, a Reset each, the eight rows in order, "Copy A to B", no request and no
    storage in the scenarios' code, no word of recommendation, no colour that judges, the block drawn once after the
    contract, the page still in review, and the form carrying the scenarios; the Method note states every formula;
  the battery page's block is not touched by this session.

No request, no model call; the environment is read, never set. Tests that need node skip when it is absent."""
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
KEYS = ["capex", "share", "rate", "term", "fom", "deg", "life", "hurdle"]
SWING = dict(capex=100, share=10, rate=1, term=5, fom=5, deg=1, life=5, hurdle=1)
BOUNDS = dict(capex=(0, 10000), share=(0, 100), rate=(0, 30), term=(1, 40), fom=(0, 500), deg=(0, 20), life=(1, 40), hurdle=(0, 40))
FILES = ["site/lib/seller/finance.ts", "site/app/cost-of-power/seller/SellerScenarios.tsx", "site/app/cost-of-power/seller/page.tsx",
         "site/app/cost-of-power/seller/SellerForm.tsx", "site/scripts/test-seller-finance.mjs", "site/scripts/check-seller-scenarios.mjs",
         "docs/methods/generator_earns_algorithm.md", "docs/tools.md", "tests/test_session186.py", "archive/sessions/SESSION_186_REPORT.md"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


# ----------------------------------------------------------------------------------------------------------------------
# The mirror: docs/methods/generator_earns_algorithm.md, section 11.3, written again in Python. USD per kW; rates in percent.

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


def month_coverage(a, month):
    ds = debt_service(a)
    return (month - a["fom"] / 12) / (ds / 12) if ds > 0 else None


def contract_price(a, energy, target=1.25):
    ds = debt_service(a)
    return (target * ds + a["fom"]) / energy if ds > 0 and energy > 0 else None


def toll(a, target=1.25):
    ds = debt_service(a)
    return (target * ds + a["fom"]) / 12 if ds > 0 else None


def bars(a, rev):
    """Each assumption moved down and up by its step, the others held; a side outside the bounds is None."""
    out = {}
    for k in KEYS:
        sides = []
        for d in (-1, 1):
            v = round(a[k] + d * SWING[k], 6)
            x = dict(a, **{k: v})
            sides.append(None if v < BOUNDS[k][0] or v > BOUNDS[k][1] else npv(x["hurdle"], flows(x, rev)))
        out[k] = sides
    return out


SOLAR = dict(capex=1375, share=60, rate=8, term=35, fom=12.5, deg=0, life=35, hurdle=8)


def cases():
    """The default case, the edges, and 300 seeded cases: (assumptions, revenue per kW, energy MWh per kW, a month per kW)."""
    out = [(SOLAR, 59.85, 2.58, 1.39), (dict(SOLAR, term=10), 59.85, 2.58, 1.39), (dict(SOLAR, capex=900, deg=0.5, hurdle=12), 140.0, 2.6, 4.0),
           (dict(SOLAR, share=0), 90.0, 2.5, 3.0), (dict(SOLAR, share=100), 90.0, 2.5, 3.0), (dict(SOLAR, rate=0), 120.0, 2.5, 3.0),
           (dict(SOLAR, term=40, life=5), 300.0, 2.5, 3.0), (dict(SOLAR, hurdle=0, life=1, term=1), 2000.0, 2.5, 3.0), (SOLAR, 59.85, 0, 0)]
    rng = random.Random(186)
    for _ in range(300):
        a = dict(capex=round(rng.uniform(100, 3000), 2), share=round(rng.uniform(0, 100), 1), rate=round(rng.uniform(0, 15), 2),
                 term=rng.randint(1, 40), fom=round(rng.uniform(0, 80), 2), deg=round(rng.uniform(0, 6), 2),
                 life=rng.randint(1, 40), hurdle=round(rng.uniform(0, 25), 2))
        out.append((a, round(rng.uniform(0, 600), 4), round(rng.uniform(0.1, 5), 4), round(rng.uniform(-5, 60), 4)))
    return out


def node_results(cs):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    d = tempfile.mkdtemp(prefix="erw186_")
    try:
        p = os.path.join(d, "cases.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump([dict(a=a, rev=rev, energy=e, month=m) for a, rev, e, m in cs], f)
        r = subprocess.run([exe, os.path.join("scripts", "test-seller-finance.mjs"), "--cases", p], cwd=os.path.join(ROOT, "site"),
                           capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            raise AssertionError(r.stderr[-2000:])
        return json.loads(r.stdout)
    finally:
        shutil.rmtree(d, ignore_errors=True)


class TheFinanceByHand(unittest.TestCase):
    def test_the_default_debt_payments_are_the_pages(self):
        # docs/methods/generator_earns_algorithm.md, section 7: the annual debt payment of 100 MW, by asset
        for capex, life, usd in ((1375, 35, 7078769), (2100, 30, 11192257), (610, 20, 3727791), (1110, 20, 6783357), (1300, 30, 6928540)):
            a = dict(SOLAR, capex=capex, term=life, life=life)
            self.assertEqual(round(debt_service(a) * 1000 * 100), usd, capex)

    def test_flows_by_hand(self):
        a = dict(capex=1000, share=60, rate=0, term=10, fom=10, deg=0, life=10, hurdle=0)
        fl = flows(a, 100)
        self.assertEqual(fl[0], -400)
        self.assertTrue(all(abs(v - 30) < 1e-12 for v in fl[1:]))
        self.assertAlmostEqual(npv(0, fl), -100)
        self.assertAlmostEqual(flows(dict(a, deg=10), 100)[3], 81 - 10 - 60)
        self.assertAlmostEqual(flows(dict(a, term=4), 100)[5], 90)

    def test_the_rate_of_return_by_hand(self):
        self.assertAlmostEqual(irr([-100, 110]), 10, places=6)
        self.assertAlmostEqual(irr([-100, 0, 121]), 10, places=6)
        self.assertIsNone(irr([-100, -5, -5]))

    def test_the_contract_price_and_the_toll_set_coverage_to_one_and_a_quarter(self):
        a = dict(capex=1000, share=60, rate=0, term=10, fom=10, deg=0, life=10, hurdle=0)
        self.assertAlmostEqual(contract_price(a, 2.5), 34)                       # (1.25 x 60 + 10) / 2.5
        self.assertAlmostEqual((contract_price(a, 2.5) * 2.5 - 10) / 60, 1.25)
        self.assertAlmostEqual(toll(a), 85 / 12)
        self.assertAlmostEqual((12 * toll(a) - 10) / 60, 1.25)
        self.assertIsNone(contract_price(dict(a, share=0), 2.5))
        self.assertIsNone(contract_price(a, 0))
        for b, rev, e, _ in cases()[9:60]:
            p = contract_price(b, e)
            if p is not None:
                self.assertAlmostEqual((p * e - b["fom"]) / debt_service(b), 1.25, places=9)

    def test_a_months_coverage_sums_to_the_years(self):
        # twelve equal months of a year's revenue give the year's coverage
        self.assertAlmostEqual(month_coverage(SOLAR, 59.85 / 12), coverage(SOLAR, 59.85), places=12)


class ThePageLibraryIsTheMirror(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = cases()
        cls.node = node_results(cls.cases)

    def test_every_number_to_one_in_a_million(self):
        def same(x, y, what):
            if x is None or y is None:
                self.assertEqual(x, y, what)
            else:
                self.assertLessEqual(abs(x - y), 1e-6 * max(1, abs(y)), what)
        self.assertEqual(len(self.node), len(self.cases))
        for i, ((a, rev, e, m), n) in enumerate(zip(self.cases, self.node)):
            fl = flows(a, rev)
            same(n["debt"], debt_service(a), f"{i} debt")
            same(n["coverage"], coverage(a, rev), f"{i} coverage")
            same(n["npv"], npv(a["hurdle"], fl), f"{i} npv")
            same(n["irr"], irr(fl), f"{i} irr")
            same(n["contract"], contract_price(a, e), f"{i} contract")
            same(n["toll"], toll(a), f"{i} toll")
            same(n["month"], month_coverage(a, m), f"{i} month")
            self.assertEqual(len(n["flows"]), len(fl))
            for x, y in zip(n["flows"], fl):
                same(x, y, f"{i} flow")
            mine = bars(a, rev)
            self.assertEqual(sorted(b["key"] for b in n["bars"]), sorted(KEYS))
            sizes = [b["size"] for b in n["bars"]]
            self.assertEqual(sizes, sorted(sizes, reverse=True), f"{i} sorted")
            for b in n["bars"]:
                for side, y in zip((b["down"], b["up"]), mine[b["key"]]):
                    same(None if side is None else side["npv"], y, f"{i} {b['key']}")

    def test_the_cases_reach_both_outcomes_of_the_rate_of_return(self):
        got = [n["irr"] for n in self.node]
        self.assertGreater(sum(1 for v in got if v is None), 10)
        self.assertGreater(sum(1 for v in got if v is not None), 100)

    def test_the_hand_cases_of_the_node_script_pass(self):
        exe = shutil.which("node")
        r = subprocess.run([exe, os.path.join("scripts", "test-seller-finance.mjs")], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:])
        self.assertNotIn("FAIL", r.stdout)
        self.assertIn("equal the battery page's library exactly", r.stdout)


class TheDefaultCaseIsThePages(unittest.TestCase):
    """The snapshot the page reads (site/data/merchant_snapshot.json), ERCOT solar, the last twelve months held."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "site", "data", "merchant_snapshot.json"), encoding="utf-8") as f:
            snap = json.load(f)
        months, near = snap["isos"]["ercot"]["months"], snap["defaults"]["near"]
        held = [m for m in sorted(months) if "solar" in months[m] and months[m]["solar"]["hours"] / months[m]["him"] >= near - 1e-9]

        def before(m, k):
            y, mo = int(m[:4]), int(m[5:7]) - k
            while mo < 1:
                y, mo = y - 1, mo + 12
            return f"{y}-{mo:02d}"
        cls.twelve = None
        for m in reversed(held):
            t = [before(m, k) for k in range(12)]
            if all(x in held for x in t):
                cls.twelve = [months[x]["solar"] for x in t]
                break

    def test_coverage_is_the_pages_formula(self):
        self.assertIsNotNone(self.twelve)
        rev = sum(r["revenue_per_mw"] for r in self.twelve) / 1000
        ds = round(1375 * 1000 * 100 * 0.6 * (0.08 / (1 - 1.08 ** -35)))                 # the page's default debt payment, whole USD
        page = (rev * 1000 * 100 - 12.5 * 1000 * 100) / ds                               # lib/merchant.ts, ttm
        self.assertAlmostEqual(coverage(SOLAR, rev), page, places=6)

    def test_the_contract_price_is_above_zero_and_sets_coverage(self):
        e = sum(r["energy_per_mw"] for r in self.twelve) / 1000
        p = contract_price(SOLAR, e)
        self.assertGreater(p, 0)
        self.assertAlmostEqual((p * e - 12.5) / debt_service(SOLAR), 1.25, places=9)


class ThePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.block = src("site", "app", "cost-of-power", "seller", "SellerScenarios.tsx")
        cls.shared = src("site", "components", "decisions", "ScenarioBlock.tsx")   # session 195: the block the three pages share
        cls.lib = src("site", "lib", "seller", "finance.ts")
        cls.page = src("site", "app", "cost-of-power", "seller", "page.tsx") + src("site", "app", "cost-of-power", "seller", "model.ts")   # session 212: the page's reads are model.ts

    def test_eight_assumptions_and_no_others(self):
        # session 212: ten, the contract's share and price last (0 by default: fully merchant); the eight of this session are FINANCE_KEYS
        hit = re.search(r"export const KEYS: Key\[\] = \[(.*?)\];", self.lib)
        self.assertEqual(re.findall(r'"(\w+)"', hit.group(1)), KEYS + ["cshare", "cprice", "ppa"])   # session 264: the PPA term eleventh
        hit = re.search(r"export const FINANCE_KEYS: Key\[\] = \[(.*?)\];", self.lib)
        self.assertEqual(re.findall(r'"(\w+)"', hit.group(1)), KEYS)
        for k in KEYS + ["cshare", "cprice", "ppa"]:
            self.assertEqual(self.lib.count(f'  {k}: {{ key: "{k}", letter: "'), 1, k)
        self.assertEqual(self.lib.count('{ key: "'), 11)   # session 264: eleven
        self.assertEqual(self.lib.count(", source: "), 11)
        self.assertIn('cshare: { key: "cshare", letter: "n", label: "Contract share", unit: "percent", min: 0, max: 100, whole: false, swing: 10,', self.lib)
        self.assertIn('cprice: { key: "cprice", letter: "p", label: "Contract price", unit: "USD", min: 0, max: 1000, whole: false, swing: 1,', self.lib)
        for k in KEYS:                                                                  # the steps and bounds the mirror uses are the library's
            line = next(x for x in self.lib.splitlines() if x.startswith(f'  {k}: {{ key: "{k}"'))
            self.assertIn(f"min: {BOUNDS[k][0]}, max: {BOUNDS[k][1]},", line, k)
            self.assertIn(f"swing: {SWING[k]},", line, k)

    def test_the_defaults_and_what_they_cite(self):
        # session 196 (the owner's ruling of 11 October 2026): the hurdle rate is Lazard's weighted cost; a battery's degradation is Lazard's
        self.assertIn("return { capex: costs.capex, share: 60, rate: 8, term: costs.life, fom: costs.fom, deg: costs.deg ?? 0, life: costs.life, hurdle: HURDLE, cshare: 0, cprice: 0, ppa: costs.life };", self.lib)   # session 212; session 264: the PPA term
        self.assertIn("export const HURDLE = 12;", self.lib)        # session 208: Lazard's cost of equity (the owner's ruling of 12 October 2026)
        self.assertIn("export const BATTERY_DEG = 2.6;", self.lib)
        merchant = src("site", "lib", "merchant.ts")
        self.assertIn("export const DEBT = { share: 0.6, rate: 0.08 };", merchant)       # the page's own, cited to Lazard
        for line in ("solar: { capex: 1375, life: 35, fom: 12.5,", "wind: { capex: 2100, life: 30, fom: 32.25,", "battery_2h: { capex: 610, life: 20, fom: 11.2,",
                     "battery_4h: { capex: 1110, life: 20, fom: 22,", "peaker: { capex: 1300, life: 30, fom: 13.5,"):
            self.assertIn(line, merchant)
        self.assertIn("costs: { ...costsOf(k), capex: D.capex, fom: D.fom, life: D.life,", self.page)   # the scenarios' defaults are the page's own
        note = src("docs", "methods", "cost_of_power.md")
        self.assertIn('"60% debt at an 8% interest rate"', note)
        self.assertIn('"Economic life sets debt amortization schedule"', note)
        # the two defaults no source in the repository gives say so on the page, and are not dressed as cited
        self.assertIn('"60% debt at an 8% interest rate and 40% equity at a 12% cost". The default is that cost of equity, ${HURDLE} percent', self.lib)   # session 208
        self.assertIn("No cited rate is held, so the default is none", self.lib)

    def test_a_reset_each_one_for_all_and_copy_a_to_b(self):
        # session 195: the panel is the shared block's, which this page's file hands its fields
        self.assertIn("data-reset={k}", self.shared)
        self.assertIn(">Reset</button>", self.shared)
        self.assertIn("data-reset-all", self.shared)
        self.assertIn(">Copy A to B</button>", self.shared)
        self.assertIn("<ScenarioBlock", self.block)

    def test_the_eight_rows_in_order_and_the_last_in_words(self):
        keys = re.findall(r'\n    row\("(\w+)", ', self.block)
        # session 235: a ninth row, the breakeven PPA price, after the contract price at which coverage reaches 1.25
        self.assertEqual(keys, ["revenue", "capture", "month", "coverage", "npv", "irr", "contract", "ppa", "battery"])
        self.assertLess(self.shared.index('data-row={r.key}'), self.shared.index('data-row="differs"'))
        self.assertIn("differenceWords(s.a, s.b)", self.block)
        self.assertIn('row("month", "The worst month"', self.block)

    def test_it_computes_in_the_browser_and_asks_for_nothing(self):
        self.assertTrue(self.block.startswith('"use client";'))
        code = re.sub(r"(?m)^\s*//.*$", "", self.block + self.shared)
        for word in ("fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "sessionStorage", "document.cookie", "router.", "useRouter", "track(", "import("):
            self.assertNotIn(word, code, word)
        self.assertIn("window.history.replaceState(", self.shared)
        self.assertNotRegex(self.lib, r"(?m)^import ")
        self.assertNotIn('from "react"', self.lib)

    def test_no_word_of_recommendation_and_no_colour_that_judges(self):
        # "The worst month" is the row the brief names: the lowest month, a rank and not a verdict
        text = re.sub(r"(?m)^\s*//.*$", "", self.block + self.shared).replace("The worst month", "")
        for word in ("better", "worse", "attractive", "should", "recommend", "best", "worst", "good", "poor", "prefer", "favou", "favor"):
            self.assertNotRegex(text.lower(), rf"\b{word}", word)
        for colour in ("color-up", "color-down", "#175E54", "green", "red-", "#8C1515"):
            self.assertNotIn(colour, text, colour)
        self.assertIn('const DOWN = "#2a78d6", UP = "#eb6834";', self.shared)
        tokens = src("site", "app", "tokens.css")
        self.assertIn("--color-fuel-gas: #2a78d6;", tokens)
        self.assertIn("--color-fuel-coal: #eb6834;", tokens)

    def test_the_page_draws_the_block_once_after_the_contract(self):
        # session 212: the block answers the page's second question, the chart its third; the contract is two of the block's assumptions
        self.assertEqual(self.page.count("<SellerScenarios "), 1)
        self.assertEqual(self.page.count("<SellerSensitivity "), 1)
        self.assertNotIn("<ContractResult ", self.page)
        self.assertLess(self.page.index('<ToolSection title="Is it worth building?"'), self.page.index("<SellerScenarios "))
        self.assertLess(self.page.index("<SellerScenarios "), self.page.index('<ToolSection title="What matters most"'))
        self.assertLess(self.page.index('<ToolSection title="What matters most"'), self.page.index("<SellerSensitivity "))
        self.assertIn('"/cost-of-power/seller": "review",', src("site", "lib", "release.ts"))

    def test_the_form_carries_the_scenarios(self):
        form = src("site", "app", "cost-of-power", "seller", "SellerForm.tsx")
        self.assertEqual(form.count("carry("), 4)                                        # Show, the grid, the asset, "Reset the costs"
        # session 195: the debt payments and the fixed O&M are scenario A's; the other ten are the page's own
        self.assertIn('const KEYS = ["iso", "hub", "asset", "mw", "mwh", "hr", "vom", "bmw", "dur", "strat"] as const;', form)
        self.assertNotIn('name="fom"', form)
        self.assertNotIn('name="ds"', form)

    def test_the_battery_pages_block_is_not_this_sessions(self):
        battery = src("site", "app", "cost-of-power", "battery", "Scenarios.tsx")
        self.assertIn('from "@/lib/battery/finance"', battery)
        self.assertNotIn("lib/seller", battery)
        self.assertNotIn("lib/battery/finance", self.block)


class TheNote(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.note = src("docs", "methods", "generator_earns_algorithm.md")

    def test_every_formula_is_stated(self):
        self.assertIn("## 11. Scenarios A and B", self.note)
        self.assertLess(self.note.index("## 10. What is left"), self.note.index("## 11. Scenarios A and B"))
        part = self.note[self.note.index("## 11. Scenarios A and B"):]
        for words in ("capex x share x crf(rate, n)", "n = min(term, life)", "R_t = R x (1 - deg)^(t - 1)", "F_0 = -capex x (1 - share)",
                      "NPV = sum over t = 0 to life of F_t / (1 + hurdle)^t", "bisection", "-99", "1,000", "(R - fom) / debt",
                      "(M - fom / 12) / (debt / 12)", "price = (1.25 x debt + fom) / E", "toll = (1.25 x debt + fom) / 12",
                      "replaceState", "to be confirmed", "7,078,769"):
            self.assertIn(words, part, words)
        for k in ("ac", "as", "ar", "at", "af", "ad", "al", "ah"):
            self.assertIn(f"`{k}`", part, k)

    def test_the_tools_list_names_the_block(self):
        self.assertIn("since session 186 two scenarios A and B", src("docs", "tools.md"))


class House(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            p = os.path.join(ROOT, *f.split("/"))
            if os.path.exists(p):
                self.assertNotIn(EM, src(*f.split("/")), f)

    def test_the_new_test_modules_name_is_its_own(self):
        names = []
        for top in ("warehouse", "scripts", "tests"):
            for d, dirs, files in os.walk(os.path.join(ROOT, top)):
                dirs[:] = [x for x in dirs if x not in ("output", "__pycache__", "node_modules", "raw")]
                names += [os.path.join(d, f) for f in files if f == "test_session186.py"]
        self.assertEqual(len(names), 1, names)


if __name__ == "__main__":
    unittest.main()
