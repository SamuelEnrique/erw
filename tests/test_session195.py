"""Session 195: the decisions layer becomes one system on the three decision pages (/cost-of-power/battery,
/cost-of-power/seller, /cost-of-power). What is held to:

  one shared component (site/components/decisions/ScenarioBlock.tsx) holds the assumptions panel, the two columns, the
    rows in words and the sensitivity chart; each page's own file hands it its fields, rows and figures and keeps no
    copy of the panel or of the chart;
  scenario A sets the headline: the two scenarios are held above each page's sections, the duplicate fields of "Your
    battery", "Your plant" and "Your load" are gone, and the sentence under the table states scenario A;
  the old parameter names (fom, ds, gpu, pue) are read as the scenarios' own, so an older link opens the same headline
    (site/scripts/test-decisions-195.mjs: the debt payment to the dollar, the old names, the whole-month rule);
  the battery's last twelve months end with the last complete month in the table;
  nothing is sent from the block: no request, no storage, no usage count;
  no sentence of the block or of the headline tells the reader what to do;
  the three pages stay in review, and the three Method notes describe the shared block once and point to it.

No request, no model call; the environment is read, never set. The test that needs node skips when it is absent."""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
SHARED = "site/components/decisions/ScenarioBlock.tsx"
WRAPPERS = {
    "battery": "site/app/cost-of-power/battery/Scenarios.tsx",
    "seller": "site/app/cost-of-power/seller/SellerScenarios.tsx",
    "datacenter": "site/app/cost-of-power/LoadScenarios.tsx",
}
PAGES = {
    "battery": "site/app/cost-of-power/battery/page.tsx",
    "seller": "site/app/cost-of-power/seller/page.tsx",
    "datacenter": "site/app/cost-of-power/page.tsx",
}
FORMS = {
    "battery": ("site/app/cost-of-power/battery/BatteryForm.tsx", ("fom", "ds")),
    "seller": ("site/app/cost-of-power/seller/SellerForm.tsx", ("fom", "ds")),
    "datacenter": ("site/app/cost-of-power/LoadForm.tsx", ("gpu", "pue")),
}
NOTES = ["docs/methods/battery_earns_algorithm.md", "docs/methods/generator_earns_algorithm.md", "docs/methods/datacenter_pays_algorithm.md"]
FILES = [SHARED, *WRAPPERS.values(), *PAGES.values(), *(f for f, _ in FORMS.values()), *NOTES,
         "site/app/cost-of-power/LoadHeadline.tsx", "site/app/cost-of-power/battery/nums.tsx", "site/app/cost-of-power/seller/nums.tsx",
         "site/lib/batterystack.ts", "site/lib/battery/finance.ts", "site/lib/seller/finance.ts", "site/lib/datacenter/finance.ts",
         "site/scripts/check-decisions-face.mjs", "site/scripts/test-decisions-195.mjs", "site/scripts/check-battery-scenarios.mjs",
         "site/scripts/check-seller-scenarios.mjs", "site/scripts/check-datacenter-scenarios.mjs", "site/scripts/check-seller.mjs",
         "docs/methods/datacenter_cost.md", "tests/test_session195.py", "archive/sessions/SESSION_195_REPORT.md"]


def src(rel):
    with open(os.path.join(ROOT, *rel.split("/")), encoding="utf-8") as f:
        return f.read()


def code(text):
    """The text without its comment lines."""
    return re.sub(r"(?m)^\s*//.*$", "", text)


class TheLibraries(unittest.TestCase):
    def test_the_node_assertions_pass(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        r = subprocess.run([exe, os.path.join("scripts", "test-decisions-195.mjs")], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertNotIn("FAIL", r.stdout)
        self.assertIn("all 30 passed", r.stdout)

    def test_the_last_twelve_months_end_with_a_whole_month(self):
        stack = src("site/lib/batterystack.ts")
        self.assertIn("whole: daysInMonth > 0 && daysHeld + (v.days_left_out ?? 0) >= daysInMonth,", stack)
        self.assertIn("if (!r.held || !r.whole) continue;", stack)
        # one definition: the page, its check keys, the contract and the 36-month window all call it
        self.assertEqual(len(re.findall(r"(?m)^export function lastTwelve\(", stack)), 1)
        self.assertIn("const to = (lastTwelve(ms)?.[11] ?? held.at(-1)!).m;", stack)

    def test_the_old_names_are_read_in_each_library(self):
        for lib in ("site/lib/battery/finance.ts", "site/lib/seller/finance.ts"):
            text = src(lib)
            self.assertIn('export const isOldParam = (name: string) => name === "fom" || name === "ds";', text, lib)
            self.assertIn('if (!given("af") && given("fom")) a.fom = bound("fom", Number(q.fom), d', text, lib)
            self.assertIn('if (!given("ac") && given("ds") && mw > 0) {', text, lib)
            self.assertIn("export const debtUsd = (a: Assumptions, mw: number) => Math.round(a.capex * 1000 * (a.share / 100) * crf(a.rate / 100, debtYears(a)) * mw);", text, lib)
            self.assertNotRegex(text, r"(?m)^import ", lib)                              # still pure: node runs it as it is
        dc = src("site/lib/datacenter/finance.ts")
        self.assertIn('export const OLD: Record<string, Key> = { gpu: "gpu", pue: "pue" };', dc)
        self.assertNotRegex(dc, r"(?m)^import ")


class OneBlock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared = src(SHARED)
        cls.wrappers = {k: src(v) for k, v in WRAPPERS.items()}

    def test_the_shared_component_holds_the_panel_the_table_and_the_chart(self):
        for words in ("export function ScenarioState(", "export function useScenarios<", "export function ScenarioBlock(", "function Sensitivity(", "function NumberField(",
                      ">Copy A to B</button>", "data-reset-all", "data-reset={k}", 'data-scenario-table="1"', 'data-row="differs"', 'data-row="against"',
                      "How far each assumption moves {c.moves}, scenario {view.toUpperCase()}", "The chart as a table", "Point at a row, or tab to it, for the two values."):
            self.assertIn(words, self.shared, words)
        self.assertEqual(self.shared.count("window.history.replaceState("), 1)

    def test_each_page_uses_it_and_keeps_no_copy(self):
        for name, text in self.wrappers.items():
            self.assertTrue(text.startswith('"use client";'), name)
            self.assertEqual(text.count("<ScenarioBlock"), 1, name)
            self.assertIn('from "@/components/decisions/ScenarioBlock";', text, name)
            self.assertEqual(text.count("<ScenarioState "), 1, name)                      # the scenarios are held above the page's sections
            for copy in ("function Sensitivity(", "function NumberField(", "Copy A to B", "The chart as a table", "window.history.replaceState(", "data-scenario-table"):
                self.assertNotIn(copy, code(text), f"{name}: {copy}")

    def test_the_arithmetic_stays_in_each_pages_library(self):
        for word in ("npv(", "irr(", "crf(", "resultOf(", "sensitivity(", "presentValue("):
            self.assertNotIn(word, code(self.shared), word)
        for name, lib in (("battery", "@/lib/battery/finance"), ("seller", "@/lib/seller/finance"), ("datacenter", "@/lib/datacenter/finance")):
            self.assertIn(f'from "{lib}";', self.wrappers[name], name)

    def test_the_sentence_under_the_table_states_scenario_a(self):
        self.assertIn('data-npv-sentence="a"', self.wrappers["battery"])
        self.assertIn('data-npv-sentence="a"', self.wrappers["seller"])
        self.assertIn('data-pv-sentence="a"', self.wrappers["datacenter"])
        for name, text in self.wrappers.items():
            self.assertIn("          Scenario A, ", text, name)
            self.assertNotIn("Scenario {s.view.toUpperCase()}, ", text, name)             # no longer the scenario in view

    def test_nothing_is_sent_and_nothing_is_stored(self):
        more = [src("site/app/cost-of-power/LoadHeadline.tsx")]
        for text in (self.shared, *self.wrappers.values(), *more):
            c = code(text)
            for word in ("fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "sessionStorage", "document.cookie", "router.", "useRouter", "track(", "lib/usage", "import("):
                self.assertNotIn(word, c, word)

    def test_no_sentence_tells_the_reader_what_to_do(self):
        # "The worst month" (the generator's row, the lowest month) and "the worst tenth" (the datacenter's headline
        # since session 138) are ranks, not verdicts
        texts = [self.shared, *self.wrappers.values(), src("site/app/cost-of-power/LoadHeadline.tsx")]
        for text in texts:
            c = code(text).replace("The worst month", "").replace("the worst tenth", "").lower()
            for word in ("should", "better", "worth", "attractive", "recommend", "advis", "ought", "prefer", "best", "worse", "worst", "good", "poor", "favou", "favor", "ideal"):
                self.assertNotRegex(c, rf"\b{word}", word)


class ScenarioASetsTheHeadline(unittest.TestCase):
    def test_the_duplicate_fields_are_gone(self):
        for name, (form, gone) in FORMS.items():
            text = src(form)
            for field in gone:
                self.assertNotIn(f'name="{field}"', text, f"{name}: {field}")
            self.assertIn('data-costs-in-a="1"', text, name)
            self.assertIn('<a href="#scenarios">Scenarios A and B</a>: scenario A gives the headline.', text, name)

    def test_each_page_takes_its_costs_from_scenario_a(self):
        battery, seller, dc = (src(PAGES[k]) for k in ("battery", "seller", "datacenter"))
        self.assertIn("const x: Inputs = { ...asked, fom: A.fom, ds: debtUsd(A, asked.mw) };", battery)
        self.assertIn("const x: Inputs = { ...asked, fom: A.fom, ds: debtUsd(A, asked.mw) };", seller)
        self.assertIn("gpu: DEFAULTS.gpu, pue: DEFAULTS.pue };", dc)                       # the page's inputs carry the cited defaults; A holds the reader's
        for words in ("<BatteryDecisions ", "<BatteryHeadline ", "<Scenarios ", "<BatterySensitivity "):   # session 208: no contract section; the chart in its own section
            self.assertEqual(battery.count(words), 1, words)
        for words in ("<SellerDecisions ", "<CoverHeadline ", "<MonthsOfA ", "<CoverageOfA ", "<DscrOfA "):
            self.assertEqual(seller.count(words), 1, words)
        for words in ("<LoadDecisions ", "<LoadHeadline "):
            self.assertEqual(dc.count(words), 1, words)
        self.assertEqual(dc.count("<GpuHourOfA "), 2)                                      # the summary sentence and "What will it cost"

    def test_the_headline_keeps_its_check_keys(self):
        battery = src(WRAPPERS["battery"])
        for key in ('s="l12_kw:total"', 's="l12_share:ancillary"', 's="cover"', 's="l12:total"', 's="p10_36"', 's="n36"', 's="ds"'):
            self.assertIn(key, battery, key)
        self.assertIn("const y: Inputs = { ...x, fom: a.fom, ds: debtUsd(a, x.mw) };", battery)
        seller = src(WRAPPERS["seller"])
        for key in ('stat="ttm_last"', 'stat="ds"', 'stat="under1"', 'stat="under125"', 'stat="ttm_min"', "stat={`dscr:${m}`}"):
            self.assertIn(key, seller, key)

    def test_the_three_pages_stay_in_review(self):
        rel = src("site/lib/release.ts")
        for page in ("/cost-of-power/battery", "/cost-of-power/seller", "/cost-of-power"):
            self.assertIn(f'"{page}": "review",', rel, page)


class TheNotes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.battery, cls.generator, cls.datacenter = (src(n) for n in NOTES)

    def test_the_shared_block_is_described_once_and_the_others_point_to_it(self):
        head = "#### The block the three pages share (session 195)"
        self.assertEqual(self.battery.count(head), 1)
        self.assertLess(self.battery.index("### 11.1 Scenarios A and B"), self.battery.index(head))
        part = self.battery[self.battery.index(head):self.battery.index("#### The ten assumptions and their defaults")]
        for words in ("site/components/decisions/ScenarioBlock.tsx", "**Scenario A sets the headline.**", "**The sentence under the table states scenario A**", "**The old names.**",
                      "`capex = ds / (1000 x MW x share x crf(rate, n))`", "`af` over `fom`, `ac` over `ds`", "**Nothing is sent.**", "no usage count is sent from the block",
                      "generator_earns_algorithm.md", "datacenter_pays_algorithm.md", "check-decisions-face.mjs"):
            self.assertIn(words, part, words)
        for note in (self.generator, self.datacenter):
            self.assertNotIn(head, note)
            self.assertIn('`battery_earns_algorithm.md`, section 11.1, "The block the three pages share"', note)
            self.assertIn("**Session 195: the block is the one the three decision pages share**", note)

    def test_the_whole_month_rule_is_stated_with_the_headline_before_and_after(self):
        self.assertIn("**Since session 195 (the owner's ruling of 11 October 2026 on session 178's finding) the last twelve months end with the last complete month in the table**", self.battery)
        self.assertIn("the headline before and after is 81.40, 475,477 and 0.88", self.battery)
        self.assertIn("`days_held + days_left_out = days_in_month`", self.battery)

    def test_each_note_says_whose_the_removed_fields_are(self):
        self.assertIn("**Session 195: `fom` and `ds` are scenario A's.**", self.battery)
        self.assertIn("**Session 195: `ds` and `fom` are scenario A's.**", self.generator)
        self.assertIn("**Session 195: `gpu` and `pue` are the scenarios'.**", self.datacenter)
        self.assertIn("**Session 195: the three headline numbers are scenario A's rows**", self.datacenter)
        for note, numbers in ((self.battery, "(81.40, 475,477, 0.88)"), (self.generator, "coverage 0.67 times on debt payments of USD 7,078,769"), (self.datacenter, "(33.73, 37.88, 0.0684)")):
            self.assertIn(numbers, note, numbers)


class House(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            p = os.path.join(ROOT, *f.split("/"))
            if os.path.exists(p):
                self.assertNotIn(EM, src(f), f)

    def test_the_new_test_modules_name_is_its_own(self):
        found = []
        for top in ("warehouse", "scripts", "tests"):
            for d, dirs, files in os.walk(os.path.join(ROOT, top)):
                dirs[:] = [x for x in dirs if x not in ("output", "__pycache__", "node_modules", "raw")]
                found += [os.path.join(d, f) for f in files if f == "test_session195.py"]
        self.assertEqual(len(found), 1, found)


if __name__ == "__main__":
    unittest.main()
