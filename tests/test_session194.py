"""Session 194: "What a datacenter pays", decisions, as session 179 built them for the battery and session 186 for the
generator. What is held to:

  the finance of the two scenarios (site/lib/datacenter/finance.ts) equals a Python mirror written here from the
    note's formulas (docs/methods/datacenter_pays_algorithm.md, section 4.14), on hand cases and on 300 seeded cases,
    to 1e-6: the price, the year's cost, the GPU-hour, the hours off and the breakeven value of a GPU-hour, the costs by
    year, their present value, the fixed price with the same present value, the all-in power per GPU-hour, B set
    against A (the upfront cost at which the two are equal, the rate the dearer one returns) and every bar of the chart;
  the default page from its own files: a scenario at its defaults is the page's headline, and the two ways handed over
    are the flat page's and the flexible page's own;
  the page: eight assumptions and no others, a Reset each, the eight rows in order, "Copy A to B", no request and no
    storage in the scenarios' code, no word of recommendation, no colour that judges, the block drawn once after the
    contract, the page still in review, one page and one address, and the form carrying the scenarios;
  the notes: every formula stated, and session 190's findings 1 and 2 flagged as they stood;
  session 190's work is intact (its own tests hold that; here, that this session changed no line of its files).

No request, no model call; the environment is read, never set. Tests that need node skip when it is absent."""
import json
import math
import os
import random
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
KEYS = ["run", "gpu", "pue", "adder", "growth", "upfront", "life", "hurdle"]
SWING = dict(run=1, gpu=0.1, pue=0.1, adder=5, growth=1, upfront=100, life=5, hurdle=1)
BOUNDS = dict(run=(0, 1), gpu=(0.05, 20), pue=(1, 3), adder=(0, 500), growth=(-20, 20), upfront=(0, 20000), life=(1, 40), hurdle=(0, 40))
FILES = ["site/lib/datacenter/finance.ts", "site/app/cost-of-power/LoadScenarios.tsx", "site/app/cost-of-power/page.tsx", "site/app/cost-of-power/LoadForm.tsx",
         "site/scripts/test-datacenter-finance.mjs", "site/scripts/check-datacenter-scenarios.mjs", "site/scripts/datacenter-ways.mjs",
         "docs/methods/datacenter_pays_algorithm.md", "docs/methods/datacenter_cost.md", "docs/tools.md", "tests/test_session194.py", "archive/sessions/SESSION_194_REPORT.md"]
DEFAULT = dict(run=0, gpu=1.3, pue=1.56, adder=0, growth=0, upfront=0, life=20, hurdle=8)
FLAT = dict(per=40, cost=350400, energy=8760, held=8760, flatCost=350400, down=0, bad=None, of=0)
FLEX = dict(per=38, cost=329080, energy=8660, held=8760, flatCost=350400, down=100, bad=None, of=0)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


# ----------------------------------------------------------------------------------------------------------------------
# The mirror: docs/methods/datacenter_pays_algorithm.md, section 4.14, written again in Python. USD per MW; rates in percent.

def way_of(a, ways):
    return ways[1 if a["run"] == 1 else 0]


def price(a, w):
    return w["cost"] / w["energy"] + a["adder"]


def bill(a, w):
    return w["cost"] + a["adder"] * w["energy"]


def gpu_hour(a, w):
    return price(a, w) * a["gpu"] * a["pue"] / 1000


def gpus_per_mw(a):
    return 1000 / (a["gpu"] * a["pue"])


def gpu_hours_year(a, w):
    return w["energy"] * gpus_per_mw(a)


def off_of(a, w):
    mwh = w["held"] - w["energy"]
    if w["down"] <= 0 or mwh <= 1e-9:
        return None
    per = (w["flatCost"] - w["cost"]) / mwh + a["adder"]
    return dict(hours=w["down"], mwh=mwh, perMwh=per, perGpuHour=per * a["gpu"] * a["pue"] / 1000)


def cost_in_year(a, w, t):
    return bill(a, w) * (1 + a["growth"] / 100) ** (t - 1)


def flows(a, w):
    return [a["upfront"] * 1000] + [cost_in_year(a, w, t) for t in range(1, a["life"] + 1)]


def npv(rate, fl):
    r = rate / 100
    return sum(v / (1 + r) ** t for t, v in enumerate(fl))


def annuity(rate, years):
    r = rate / 100
    return sum(1 / (1 + r) ** t for t in range(1, years + 1))


def present_value(a, w):
    return npv(a["hurdle"], flows(a, w))


def level_price(a, w):
    r, g = a["hurdle"] / 100, a["growth"] / 100
    s = sum((1 + g) ** (t - 1) / (1 + r) ** t for t in range(1, a["life"] + 1))
    return (w["cost"] / w["energy"]) * s / annuity(a["hurdle"], a["life"])


def level_gpu_hour(a, w):
    return present_value(a, w) / (gpu_hours_year(a, w) * annuity(a["hurdle"], a["life"]))


def irr(fl):
    lo, hi = -99.0, 1000.0
    flo, fhi = npv(lo, fl), npv(hi, fl)
    if not (math.isfinite(flo) and math.isfinite(fhi)):
        return None
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


def against(a, wa, b, wb):
    pa, pb = present_value(a, wa), present_value(b, wb)
    more = "b" if b["upfront"] > a["upfront"] else "a" if a["upfront"] > b["upfront"] else None
    same = a["life"] == b["life"]
    rate = None
    if more and same:
        hi, wh, lo, wl = (b, wb, a, wa) if more == "b" else (a, wa, b, wb)
        fl = [-(hi["upfront"] - lo["upfront"]) * 1000] + [cost_in_year(lo, wl, t) - cost_in_year(hi, wh, t) for t in range(1, hi["life"] + 1)]
        rate = irr(fl)
    return dict(bill=bill(b, wb) - bill(a, wa), gpuHours=gpu_hours_year(b, wb) - gpu_hours_year(a, wa), pv=pb - pa,
                evenUpfront=(pa - (pb - b["upfront"] * 1000)) / 1000, more=more, extra=abs(b["upfront"] - a["upfront"]), rate=rate, sameYears=same)


def sensitivity(a, ways):
    """{key: (down, up, size)}; a side is (value, figure) or None. Empty when the scenario's own way is not held."""
    def at(x):
        w = way_of(x, ways)
        return None if w is None else level_gpu_hour(x, w)
    base = at(a)
    if base is None:
        return {}
    out = {}
    for k in KEYS:
        sides = []
        for d in (-1, 1):
            v = math.floor((a[k] + d * SWING[k]) * 1e6 + 0.5) / 1e6          # the page's Math.round
            if v < BOUNDS[k][0] or v > BOUNDS[k][1]:
                sides.append(None)
                continue
            got = at(dict(a, **{k: int(v) if k in ("run", "life") else v}))
            sides.append(None if got is None else (v, got))
        size = max(abs(s[1] - base) if s else 0 for s in sides)
        out[k] = (sides[0], sides[1], 0 if size < 1e-12 * abs(base) else size)
    return out


def cases():
    """Hand cases first, then 300 seeded ones: (a, b, [flat way, flexible way or None])."""
    out = [(DEFAULT, dict(DEFAULT, run=1, upfront=50), [FLAT, FLEX]), (dict(DEFAULT, growth=8), dict(DEFAULT, pue=1.2, upfront=500), [FLAT, FLEX]),
           (dict(DEFAULT, adder=10, upfront=100, growth=10, life=3, hurdle=0), dict(DEFAULT, run=1, life=10), [FLAT, FLEX]), (DEFAULT, dict(DEFAULT, adder=5), [FLAT, None])]
    rng = random.Random(194)
    for _ in range(300):
        per = round(rng.uniform(5, 150), 4)
        flat = dict(per=per, cost=per * 8760, energy=8760, held=8760, flatCost=per * 8760, down=0, bad=None, of=0)
        down = rng.randint(1, 600)
        saved = round(rng.uniform(per, 20 * per), 4) * down                    # the hours off cost more than the average hour
        cost = max(1.0, per * 8760 - saved)
        flex = None if rng.random() < 0.15 else dict(per=cost / (8760 - down), cost=cost, energy=8760 - down, held=8760, flatCost=per * 8760, down=down, bad=None, of=0)
        def one():
            return dict(run=rng.randint(0, 1) if flex else 0, gpu=round(rng.uniform(0.3, 3), 3), pue=round(rng.uniform(1, 2.5), 3), adder=round(rng.uniform(0, 60), 2),
                        growth=round(rng.uniform(-10, 15), 2), upfront=round(rng.uniform(0, 3000), 2) if rng.random() < 0.7 else 0, life=rng.randint(1, 40), hurdle=round(rng.uniform(0, 25), 2))
        a, b = one(), one()
        if rng.random() < 0.6:
            b["life"] = a["life"]
        out.append((a, b, [flat, flex]))
    return out


def node(args, timeout=300):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, os.path.join("scripts", "test-datacenter-finance.mjs"), *args], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=timeout, encoding="utf-8")
    if r.returncode != 0 and ("Unknown file extension" in r.stderr or "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr):
        raise unittest.SkipTest("this node does not read TypeScript files")
    return r


def node_results(cs):
    d = tempfile.mkdtemp(prefix="erw194_")
    try:
        p = os.path.join(d, "cases.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump([dict(a=a, b=b, ways=ways) for a, b, ways in cs], f)
        r = node(["--cases", p])
        if r.returncode != 0:
            raise AssertionError(r.stderr[-2000:])
        return json.loads(r.stdout)
    finally:
        shutil.rmtree(d, ignore_errors=True)


class TheFinanceByHand(unittest.TestCase):
    def test_a_flat_megawatt_at_forty(self):
        self.assertAlmostEqual(price(DEFAULT, FLAT), 40)
        self.assertAlmostEqual(bill(DEFAULT, FLAT), 350400)
        self.assertAlmostEqual(gpu_hour(DEFAULT, FLAT), 0.08112, places=12)            # 40 x 1.3 x 1.56 / 1,000
        self.assertAlmostEqual(gpus_per_mw(DEFAULT), 1000 / 2.028)
        self.assertAlmostEqual(gpu_hours_year(DEFAULT, FLAT), 8760000 / 2.028)
        self.assertIsNone(off_of(DEFAULT, FLAT))
        self.assertAlmostEqual(bill(dict(DEFAULT, adder=10), FLEX), 329080 + 86600)

    def test_the_hours_off_and_the_breakeven_value_of_a_gpu_hour(self):
        o = off_of(DEFAULT, FLEX)
        self.assertEqual(o["hours"], 100)
        self.assertAlmostEqual(o["perMwh"], 213.2)                                      # (350,400 - 329,080) / 100
        self.assertAlmostEqual(o["perGpuHour"], 213.2 * 2.028 / 1000)
        self.assertAlmostEqual(off_of(dict(DEFAULT, adder=10), FLEX)["perMwh"], 223.2)
        # at that value of a GPU-hour, running through the hours off earns exactly the power it costs
        gpu_hours_lost = o["mwh"] * gpus_per_mw(DEFAULT)
        self.assertAlmostEqual(o["perGpuHour"] * gpu_hours_lost, FLAT["cost"] - FLEX["cost"])

    def test_present_value_by_hand(self):
        u = dict(DEFAULT, upfront=100, growth=10, life=3, hurdle=0)
        fl = flows(u, FLAT)
        self.assertEqual(fl[0], 100000)
        for got, want in zip(fl[1:], (350400, 385440, 423984)):
            self.assertAlmostEqual(got, want)
        self.assertAlmostEqual(present_value(u, FLAT), 100000 + 350400 + 385440 + 423984)
        self.assertAlmostEqual(annuity(8, 20), (1 - 1.08 ** -20) / 0.08)
        self.assertAlmostEqual(round(annuity(8, 20), 6), 9.818147)
        self.assertAlmostEqual(present_value(DEFAULT, FLAT), 350400 * annuity(8, 20))

    def test_the_fixed_price_has_the_markets_present_value(self):
        self.assertAlmostEqual(level_price(DEFAULT, FLAT), 40, places=12)
        g = dict(DEFAULT, growth=8)                                                     # growth equal to the hurdle rate
        self.assertAlmostEqual(level_price(g, FLAT), 40 * (20 / 1.08) / annuity(8, 20))
        for a, _, ways in cases()[4:60]:
            w = way_of(a, ways)
            plain = dict(a, adder=0, upfront=0)
            self.assertAlmostEqual(level_price(a, w) * w["energy"] * annuity(a["hurdle"], a["life"]) / present_value(plain, w), 1, places=9)

    def test_the_all_in_figure_is_the_gpu_hour_with_nothing_upfront_and_no_change(self):
        for a, _, ways in cases()[4:60]:
            w = way_of(a, ways)
            plain = dict(a, upfront=0, growth=0)
            self.assertAlmostEqual(level_gpu_hour(plain, w) / gpu_hour(plain, w), 1, places=9)
        self.assertGreater(level_gpu_hour(dict(DEFAULT, upfront=500), FLAT), gpu_hour(DEFAULT, FLAT))

    def test_b_against_a_by_hand(self):
        b = dict(DEFAULT, run=1, upfront=50)
        g = against(DEFAULT, FLAT, b, FLEX)
        self.assertAlmostEqual(g["bill"], -21320)
        self.assertAlmostEqual(g["evenUpfront"], 21.32 * annuity(8, 20))
        self.assertAlmostEqual(present_value(dict(b, upfront=g["evenUpfront"]), FLEX), present_value(DEFAULT, FLAT), places=4)
        self.assertEqual((g["more"], g["extra"], g["sameYears"]), ("b", 50, True))
        self.assertAlmostEqual(npv(g["rate"], [-50000] + [21320] * 20), 0, places=3)
        self.assertTrue(42 < g["rate"] < 43)
        self.assertIsNone(against(DEFAULT, FLAT, dict(b, life=10), FLEX)["rate"])       # different years: no rate
        self.assertIsNone(against(DEFAULT, FLAT, dict(DEFAULT, run=1), FLEX)["rate"])   # neither costs more upfront
        lower = against(DEFAULT, FLAT, dict(DEFAULT, pue=1.2, upfront=500), FLAT)       # the overhead ratio moves GPUs, not the bill
        self.assertAlmostEqual(lower["bill"], 0)
        self.assertGreater(lower["gpuHours"], 0)
        self.assertIsNone(lower["rate"])
        self.assertLess(against(DEFAULT, FLAT, dict(DEFAULT, adder=5), FLAT)["evenUpfront"], 0)

    def test_the_rate_of_return_by_hand(self):
        self.assertAlmostEqual(irr([-100, 110]), 10, places=6)
        self.assertAlmostEqual(irr([-100, 0, 121]), 10, places=6)
        self.assertIsNone(irr([-100, -5, -5]))


class ThePageLibraryIsTheMirror(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = cases()
        cls.node = node_results(cls.cases)

    def same(self, x, y, what):
        if x is None or y is None:
            self.assertEqual(x, y, what)
        else:
            self.assertLessEqual(abs(x - y), 1e-6 * max(1, abs(y)), what)

    def test_every_number_to_one_in_a_million(self):
        self.assertEqual(len(self.node), len(self.cases))
        rates = 0
        for i, ((a, b, ways), n) in enumerate(zip(self.cases, self.node)):
            wa, wb = way_of(a, ways), way_of(b, ways)
            self.assertIsNotNone(wa, i)
            r = n["a"]
            for key, want in (("price", price(a, wa)), ("bill", bill(a, wa)), ("gpuHour", gpu_hour(a, wa)), ("gpus", gpus_per_mw(a)), ("gpuHours", gpu_hours_year(a, wa)),
                              ("pv", present_value(a, wa)), ("level", level_price(a, wa)), ("allIn", level_gpu_hour(a, wa))):
                self.same(r[key], want, f"{i} {key}")
            o = off_of(a, wa)
            self.assertEqual(r["off"] is None, o is None, f"{i} off")
            if o:
                for key in ("hours", "mwh", "perMwh", "perGpuHour"):
                    self.same(r["off"][key], o[key], f"{i} off {key}")
            for got, want in zip(n["flows"], flows(a, wa)):
                self.same(got, want, f"{i} flows")
            self.assertEqual(len(n["flows"]), a["life"] + 1)
            if wb is None:
                self.assertIsNone(n["against"], i)
                continue
            g = against(a, wa, b, wb)
            for key in ("bill", "gpuHours", "pv", "evenUpfront", "extra", "rate"):
                self.same(n["against"][key], g[key], f"{i} against {key}")
            self.assertEqual((n["against"]["more"], n["against"]["sameYears"]), (g["more"], g["sameYears"]), i)
            rates += g["rate"] is not None
        self.assertGreater(rates, 40)                                                   # the rate of return is exercised, not only its absence

    def test_every_bar_of_the_chart(self):
        for i, ((a, _, ways), n) in enumerate(zip(self.cases, self.node)):
            mine = sensitivity(a, ways)
            self.assertEqual(sorted(b["key"] for b in n["bars"]), sorted(mine), i)
            sizes = [b["size"] for b in n["bars"]]
            self.assertEqual(sizes, sorted(sizes, reverse=True), i)                      # largest first
            for b in n["bars"]:
                down, up, size = mine[b["key"]]
                for side, want in ((b["down"], down), (b["up"], up)):
                    self.assertEqual(side is None, want is None, f"{i} {b['key']}")
                    if want:
                        self.same(side["value"], want[0], f"{i} {b['key']} value")
                        self.same(side["v"], want[1], f"{i} {b['key']} figure")
                self.same(b["size"], size, f"{i} {b['key']} size")
                self.same(b["base"], level_gpu_hour(a, way_of(a, ways)), f"{i} base")

    def test_the_node_assertions_pass(self):
        r = node([])
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertIn("all passed", r.stdout)
        self.assertNotIn("FAIL", r.stdout)
        for words in ("at the defaults the price, the year's cost, the GPU-hour, the GPUs and the bad month are the page's", "the flat page and the flexible page hand over the same two ways",
                      "equal the generator page's library exactly"):
            self.assertIn(words, r.stdout)


class TheDefaultPage(unittest.TestCase):
    """The page's own files, through lib/datacenter.ts: what the scenarios are handed, and that at their defaults they
    are the headline. No figure is pinned but under the window the note's worked example names."""

    @classmethod
    def setUpClass(cls):
        r = node(["--page"])
        if r.returncode != 0:
            raise AssertionError(r.stderr[-2000:])
        cls.p = json.loads(r.stdout)

    def test_a_scenario_at_its_defaults_is_the_headline(self):
        p = self.p
        flat = p["ways"][0]
        self.assertIsNotNone(flat)
        a = dict(DEFAULT, gpu=p["x"]["gpu"], pue=p["x"]["pue"])
        self.assertEqual(p["x"]["run"], "flat")
        self.assertEqual(price(a, flat), p["per"])
        self.assertEqual(bill(a, flat), p["cost"])
        self.assertAlmostEqual(gpu_hour(a, flat), p["gpuHour"], places=15)
        self.assertAlmostEqual(gpus_per_mw(a) * p["x"]["mw"], p["gpus"], places=6)
        self.assertEqual((flat["bad"]["m"], flat["bad"]["per"]), (p["bad"]["m"], p["bad"]["per"]))
        self.assertAlmostEqual(level_price(a, flat), p["per"], places=9)
        self.assertAlmostEqual(level_gpu_hour(a, flat), p["gpuHour"], places=12)

    def test_the_two_ways_are_the_flat_pages_and_the_flexible_pages(self):
        p = self.p
        self.assertEqual(p["ways"], p["flexPage"])                                      # whichever page is open hands over the same two
        flat, flex = p["ways"]
        self.assertIsNotNone(flex)
        self.assertEqual(flex["flatCost"], flat["cost"])                                # the same hours, run flat
        self.assertEqual(flex["held"], flat["held"])
        self.assertEqual(flex["held"] - flex["energy"], flex["down"])                   # an hour off is a MWh not bought, per MW
        self.assertLess(flex["cost"], flat["cost"])
        o = off_of(DEFAULT, flex)
        self.assertGreater(o["perMwh"], flat["per"])                                    # the hours off cost more than the average hour

    def test_the_notes_worked_example_while_its_window_stands(self):
        p = self.p
        if (p["from"], p["to"]) != ("2025-10", "2026-09"):
            raise unittest.SkipTest(f"the page's twelve months are now {p['from']} to {p['to']}: section 4.14's worked figures are a dated record")
        flat, flex = p["ways"]
        a, b = DEFAULT, dict(DEFAULT, run=1, upfront=50)
        self.assertEqual(f"{flat['per']:.4f}", "33.7289")
        self.assertEqual(round(bill(a, flat) * 100), 29546505)
        self.assertEqual(f"{flex['per']:.4f}", "31.4583")
        self.assertEqual(flex["down"], 100)
        self.assertEqual(f"{off_of(a, flex)['perMwh']:.2f}", "230.36")
        self.assertEqual(f"{off_of(a, flex)['perGpuHour']:.4f}", "0.4672")
        self.assertEqual(round(present_value(a, flat) * 100 / 1e4), 29009)              # USD 290.09 million
        self.assertEqual(f"{level_price(dict(a, growth=2), flat):.2f}", "39.00")
        g = against(a, flat, b, flex)
        self.assertEqual(f"{g['evenUpfront']:.2f}", "226.17")
        self.assertEqual(f"{g['rate']:.1f}", "46.0")
        self.assertEqual(round(-g["gpuHours"] * 100), 4930966)
        self.assertEqual(round(-g["pv"] * 100 / 1e4), 1762)                             # USD 17.62 million
        note = src("docs", "methods", "datacenter_pays_algorithm.md")
        part = note[note.index("### 4.14 Scenarios A and B"):note.index("## 5. A load that is not flat")]
        for words in ("33.7289", "295,465.05", "31.4583", "272,428.84", "230.36", "0.4672", "290.09 million", "9.818147", "39.00", "226.17", "46.0 percent", "4,930,966", "17.62 million", "431,952,663"):
            self.assertIn(words, part, words)


class ThePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = src("site", "lib", "datacenter", "finance.ts")
        cls.block = src("site", "app", "cost-of-power", "LoadScenarios.tsx")
        cls.shared = src("site", "components", "decisions", "ScenarioBlock.tsx")   # session 195: the block the three pages share
        cls.page = src("site", "app", "cost-of-power", "page.tsx")
        cls.form = src("site", "app", "cost-of-power", "LoadForm.tsx")

    def test_eight_assumptions_and_no_others(self):
        self.assertIn('export const KEYS: Key[] = ["run", "gpu", "pue", "adder", "growth", "upfront", "life", "hurdle"];', self.lib)
        self.assertEqual(re.findall(r'(?m)^  (\w+): \{ key: "\w+", letter: "(\w)"', self.lib), list(zip(KEYS, "wgpdeulh")))
        for k in KEYS:
            lo, hi = BOUNDS[k]
            spec = re.search(rf'(?m)^  {k}: \{{ key: "{k}".*?min: ([\w.-]+), max: ([\w.-]+), whole: (\w+), swing: ([\d.]+),', self.lib)
            self.assertIsNotNone(spec, k)
            lows = {"FLAT": 0, "FLEX": 1}
            self.assertEqual((float(lows.get(spec.group(1), spec.group(1))), float(lows.get(spec.group(2), spec.group(2))), float(spec.group(4))), (lo, hi, SWING[k]), k)
        self.assertIn("return { run: load.run === FLEX ? FLEX : FLAT, gpu: load.gpu, pue: load.pue, adder: 0, growth: 0, upfront: 0, life: LIFE, hurdle: HURDLE };", self.lib)
        self.assertIn("export const LIFE = 20, HURDLE = 9.6;", self.lib)                 # session 196: Lazard's weighted cost

    def test_each_default_states_its_source_and_the_uncited_say_so(self):
        # the two cited defaults are the page's own, with their sources
        dc = src("site", "lib", "datacenter.ts")
        self.assertIn('gpu: { value: 1.3, unit: "kW per GPU", source: "NVIDIA DGX H100 system', dc)
        self.assertIn('pue: { value: 1.56, unit: "facility power over IT power", source: "Uptime Institute, Global Data Center Survey 2024', dc)
        # session 195: the two are scenario A's, and their defaults are the page's cited ones
        self.assertIn("load: { run: flex ? FLEX : FLAT, gpu: DEFAULTS.gpu, pue: DEFAULTS.pue }, gpuSource: ASSUMED.gpu.source, pueSource: ASSUMED.pue.source", self.page)
        # the four no source in the repository gives say so on the page, and are not dressed as cited
        for words in ("No cited forecast is held, so the default is no change", "No cited cost is held, so the default is none", "No cited term is held for a datacenter's power. The default is 20 years",
                      "It is the cost of capital of a power plant's builder, not a datacenter's own, for which no cited rate is held"):
            self.assertIn(words, self.lib, words)
        self.assertIn('"60% debt at an 8% interest rate"', src("docs", "methods", "cost_of_power.md"))
        self.assertIn("Default {plain(d[k])}. {sourceOf(k)}.", self.block)

    def test_a_reset_each_one_for_all_and_copy_a_to_b(self):
        # session 195: the panel is the shared block's, which this page's file hands its fields
        self.assertIn("data-reset={k}", self.shared)
        self.assertIn(">Reset</button>", self.shared)
        self.assertIn("data-reset-all", self.shared)
        self.assertIn(">Copy A to B</button>", self.shared)
        self.assertIn("<ScenarioBlock", self.block)

    def test_the_eight_rows_in_order_then_the_words_and_b_against_a(self):
        keys = re.findall(r'\n    row\("(\w+)", ', self.block)
        self.assertEqual(keys, ["price", "bill", "gpu", "bad", "off", "pv", "level", "allin"])
        self.assertLess(self.shared.index("data-row={r.key}"), self.shared.index('data-row="differs"'))
        self.assertLess(self.shared.index('data-row="differs"'), self.shared.index('data-row="against"'))
        self.assertIn("differenceWords(s.a, s.b)", self.block)
        self.assertIn("against={{ words: versus, rate: versusRate, even: versusEven }}", self.block)
        for label in ("Present value of the cost, at the hurdle rate", "Fixed price with the same present value", "Hours off, and the breakeven value of a GPU-hour", "All-in power per GPU-hour, over the years counted"):
            self.assertIn(f'", "{label}", ', self.block)
        self.assertIn("hurdle rate is ${hurdle} percent.", self.block)                 # the rate of return is stated beside the hurdle rate

    def test_it_computes_in_the_browser_and_asks_for_nothing(self):
        self.assertTrue(self.block.startswith('"use client";'))
        code = re.sub(r"(?m)^\s*//.*$", "", self.block + self.shared)
        for word in ("fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "sessionStorage", "document.cookie", "router.", "useRouter", "track(", "import("):
            self.assertNotIn(word, code, word)
        self.assertIn("window.history.replaceState(", self.shared)
        self.assertNotRegex(self.lib, r"(?m)^import ")
        self.assertNotIn('from "react"', self.lib)
        self.assertNotIn("useContext", self.block)                                      # the typed contract is not read

    def test_no_word_of_recommendation_and_no_colour_that_judges(self):
        # "A bad month" is the page's own headline since session 138: the top tenth of 36 months, a rank
        text = re.sub(r"(?m)^\s*//.*$", "", self.block + self.shared)
        for word in ("better", "worse", "attractive", "should", "recommend", "best", "worst", "good", "poor", "prefer", "favou", "favor"):
            self.assertNotRegex(text.lower(), rf"\b{word}", word)
        for colour in ("color-up", "color-down", "#175E54", "green", "red-", "#8C1515"):
            self.assertNotIn(colour, text, colour)
        self.assertIn('const DOWN = "#2a78d6", UP = "#eb6834";', self.shared)
        tokens = src("site", "app", "tokens.css")
        self.assertIn("--color-fuel-gas: #2a78d6;", tokens)
        self.assertIn("--color-fuel-coal: #eb6834;", tokens)

    def test_the_chart_answers_the_mouse_and_the_keyboard(self):
        for words in ("onMouseEnter={() => setOn(b.key)}", "onFocus={() => setOn(b.key)}", "title={c.says(b)}", 'data-sensitivity-readout="1"', "The chart as a table"):
            self.assertIn(words, self.shared, words)                                      # session 195: the chart is the shared block's
        self.assertIn("tooltip:", src("site", "app", "cost-of-power", "LoadCharts.tsx"))  # the page's other chart, as it was

    def test_one_tool_one_page_one_address(self):
        d = os.path.join(ROOT, "site", "app", "cost-of-power")
        self.assertEqual(sorted(x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x))), ["battery", "seller"])
        self.assertEqual(self.page.count("<LoadScenarios "), 1)
        self.assertLess(self.page.index("<ContractResult "), self.page.index("<LoadScenarios "))
        self.assertLess(self.page.index("<LoadScenarios "), self.page.index('<ToolSection title="Will the power be there"'))
        self.assertIn('<ToolSection title="Scenarios A and B" id="scenarios">', self.page)
        rel = src("site", "lib", "release.ts")
        self.assertIn('"/cost-of-power": "review",', rel)
        self.assertNotIn("scenarios", re.sub(r"(?m)^\s*//.*$", "", rel).lower())           # no new address
        self.assertIn('action="/cost-of-power"', self.form)

    def test_the_two_ways_come_from_the_pages_own_functions(self):
        for words in ("const flatMonths = (ms: Month[]): Month[] => ms.map((r) => ({ ...r, cost: r.flat, energy: r.held, down: 0, tightDown: 0 }));",
                      'const altFlex = { run: "hours" as const, n: DEFAULTS.n, pct: 0, shift: 0 };',
                      'monthsRuled(files, x.region, x.buy, altFlex, "forecast").months',
                      "const s = span(l), w = last36(ms), b = badMonth(w?.months ?? []);"):
            self.assertIn(words, self.page, words)
        self.assertNotIn('"hindsight"', self.page.split("// session 194: the two ways of running", 1)[1].split("const facts: Facts", 1)[0])   # the foreseen load is not used

    def test_the_form_carries_the_scenarios(self):
        self.assertEqual(self.form.count("carry(window.location.search)"), 2)             # Show, and the choice of a grid
        # session 195: the power per GPU and the overhead ratio are scenario A's; the other eight are the page's own
        self.assertIn('const KEYS = ["grid", "region", "mw", "run", "n", "pct", "shift", "buy"] as const;', self.form)
        self.assertNotIn('name="gpu"', self.form)
        self.assertNotIn('name="pue"', self.form)
        self.assertIn('name === "v" || /^[ab][wgpdeulh]$/.test(name)', self.lib)
        for own in ("view", "grid", "region", "mw", "run", "n", "pct", "shift", "buy", "gpu", "pue"):
            self.assertIsNone(re.fullmatch(r"v|[ab][wgpdeulh]", own), own)                # none of the page's own parameters is taken for a scenario's

    def test_session_190s_additions_stand(self):
        self.assertEqual(self.page.count("download data-download="), 3)
        self.assertIn("<Link href={METHOD}>Method note</Link>. <Link href={ALGORITHM}>Every number, step by step</Link>.</>}", self.page)
        lib = src("site", "lib", "datacenter.ts")
        self.assertIn("let left = cap ? shedBudget(x, pay[y].length) : Infinity;", lib)      # finding 1: the rule's budget, as it was
        self.assertIn("const k = Math.min(held.length, Math.round(x.run === \"hours\" ? (x.n * held.length) / p.length : (x.pct / 100) * held.length));", lib)   # and the foreseen load's
        self.assertIn("if (twelve.every((t) => t && t.complete)) return (twelve as Month[]).reverse();", lib)   # finding 2: twelve months in a row, as it was


class TheNotes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.note = src("docs", "methods", "datacenter_pays_algorithm.md")
        cls.cost = src("docs", "methods", "datacenter_cost.md")

    def test_every_formula_is_stated(self):
        n = self.note
        self.assertLess(n.index("### 4.13 The view"), n.index("### 4.14 Scenarios A and B (session 194)"))
        self.assertLess(n.index("### 4.14 Scenarios A and B (session 194)"), n.index("## 5. A load that is not flat"))
        part = n[n.index("### 4.14 Scenarios A and B"):n.index("## 5. A load that is not flat")]
        for words in ("price = cost / energy + d", "bill = cost + d x energy", "price x kW per GPU x overhead ratio / 1,000", "1,000 / (kW per GPU x overhead ratio)",
                      "((flatCost - cost) / (held - energy) + d) x kW per GPU x overhead ratio / 1,000", "C_0 = 1,000 x U; C_t = bill x (1 + g)^(t - 1)",
                      "sum over t = 0 to N of C_t / (1 + r)^t", "[sum of (1 + g)^(t - 1) / (1 + r)^t] / [sum of 1 / (1 + r)^t]",
                      "present value of the cost / (GPU-hours a year x sum of 1 / (1 + r)^t)", "(pv_A - (pv_B - 1,000 x U_B)) / 1,000", "bisection", "-99", "1,000 percent",
                      "replaceState", "to be confirmed by the owner", "one part in 10^12"):
            self.assertIn(words, part, words)
        for k in ("aw", "ag", "ap", "ad", "ae", "au", "al", "ah", "bw", "bh"):
            self.assertIn(f"`{k}`", part, k)
        self.assertEqual(part.count("**none held**"), 4)

    def test_session_190s_two_findings_are_flagged_as_they_stood(self):
        n = self.note
        findings = n[n.index("## 11. Findings of this session"):n.index("## Sign-off")]
        self.assertIn('1. **In a year held in part, "if perfectly foreseen" is given fewer hours than the rule.**', findings)
        self.assertIn("2. **New York's real-time window is held in June 2026**", findings)
        part = n[n.index("### 4.14 Scenarios A and B"):n.index("## 5. A load that is not flat")]
        self.assertIn("Finding 1 of section 11", part)
        self.assertIn("Finding 2 of section 11", part)
        c = self.cost[self.cost.index("### Scenarios A and B (session 194)"):self.cost.index("### Delivery and transmission charges, Texas")]
        self.assertIn("Two findings of session 190 stand as they were, for the owner's ruling", c)
        for words in ("Finding 1:", "Finding 2:", "July 2025 to June 2026", "section 4.14", "It recommends nothing"):
            self.assertIn(words, c, words)
        self.assertLess(self.cost.index("### The contract"), self.cost.index("### Scenarios A and B (session 194)"))

    def test_the_tools_list_names_the_block(self):
        self.assertIn("since session 194 two scenarios A and B on eight assumptions", src("docs", "tools.md"))


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
                names += [os.path.join(d, f) for f in files if f == "test_session194.py"]
        self.assertEqual(len(names), 1, names)


if __name__ == "__main__":
    unittest.main()
