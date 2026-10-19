"""Session 264: What a generator earns, deep (the chain of 14 October 2026; the owner's list for this tool).

Energy Research Warehouse (ERW). What is held here:
  1. the capture rate stands beside every capture price the page states, from the same rows, with a check key: the
     summary sentence and the headline carry cap|<grid>|...|l12|rate, the income table and the headline's spans carry
     ms|iso=<grid>&...|<span>|<stat>, and scripts/check-values.mjs recomputes ms| from the snapshot;
  2. the PPA term is the eleventh assumption (site/lib/seller/finance.ts): letter y, 1 to 40 years, whole, its default
     the asset's life, used where the contract and the breakeven PPA price are; the library's own node test passes;
  3. check-seller.mjs and check-seller-face.mjs are retired to site/scripts/_retired/ with a README, not deleted;
  4. the two CSV downloads follow the license verdicts (lib/license.ts): off, with the catalogue's words, for a grid
     whose prices are "license needed" on the day; ERCOT and CAISO are not among those grids;
  5. every generator check key names its grid, and check-values refuses one that does not;
  6. a typed value outside its bounds is held at the bound with one line under "Your plant";
  7. the replication's mirror prints the capture rate, NPV and the breakeven PPA price, and its closed form equals the
     library's year-by-year sum;
  8. the review pack replaces the how-it-works note, and the links point at it.
Nothing here sets the environment at import, reads a table or makes a request. node runs inside a test only.
"""

import importlib.util
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SELLER = ("site", "app", "cost-of-power", "seller")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheCaptureRateBesideThePrice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = src(*SELLER, "page.tsx")
        cls.check = src("site", "scripts", "check-values.mjs")

    def test_the_sentence_and_the_headline_carry_the_rate_with_its_key(self):
        self.assertIn('const capKey = (what: "price" | "flat" | "rate") => `cap|${iso}|${hub.id}|${mk}|${fuel}|l12|${what}`;', self.page)
        self.assertIn('const mineRate = mine && mine.flat > 0 ? Math.round((100 * mine.price) / mine.flat) : null;', self.page)
        self.assertEqual(self.page.count('a capture rate of <Num check={capKey("rate")} raw={mineRate}>'), 1)          # the summary sentence
        self.assertEqual(self.page.count('<span data-stat="cap_rate"><Num check={capKey("rate")} raw={mineRate}>'), 1)  # the headline
        self.assertIn('<span data-stat="cap_price"><Num check={capKey("price")} raw={mine.price}>', self.page)
        self.assertIn('a capture rate of {spanNum("twelve", "rate", s.twelve.rate, whole(s.twelve.rate))} percent', self.page)   # a battery's and a peaker's

    def test_the_spans_carry_ms_keys_at_the_main_hub_only(self):
        self.assertIn("atHub ? <>{text}</> : <Num check={`ms|${key}|${span}|${stat}`}", self.page)
        self.assertIn('raw={stat === "energy" || stat === "rate" ? Math.round(v) : v}', self.page)
        self.assertIn('if (p[0] === "ms") {', self.check)
        self.assertIn('rate: capture !== null && flat ? Math.round((100 * capture) / flat) : null }[p[3]];', self.check)

    def test_the_results_row_names_the_capture_rate(self):
        block = src(*SELLER, "SellerScenarios.tsx")
        self.assertIn("note: `a capture rate of ${num(f.capture.ratio, 1)} percent of USD ${num(f.capture.flat)}; ${f.capture.words}` }", block)
        self.assertIn('captureLabel: fuel ? "Capture price and rate"', src(*SELLER, "model.ts"))

    def test_no_section_was_added_moved_or_removed(self):
        self.assertEqual(self.page.count("<ToolSection "), 3)
        self.assertEqual(self.page.count("<Sub>"), 3)
        self.assertEqual(self.page.count("<ChartFrame "), 2)
        self.assertEqual(self.page.count("<ToolTable "), 2)


class TheKeysNameTheGrid(unittest.TestCase):
    def test_check_values_refuses_a_key_without_its_grid(self):
        c = src("site", "scripts", "check-values.mjs")
        self.assertIn("const namesGrid = (inputs) => /(^|&)iso=(ercot|caiso|nyiso|isone|spp|miso)(&|$)/.test(inputs) && !/(^|&)hub=/.test(inputs);", c)
        self.assertEqual(c.count("if (!namesGrid(p[1])) return null;"), 3)        # mr|, ms| and (session 288, problem set E) mrs|
        self.assertIn("if (!file.grids[p[1]]) return null;", c)                     # cap|
        self.assertIn("export const inputsKey = (x: Inputs) => `iso=${x.iso}&", src("site", "lib", "merchant.ts"))
        page = src(*SELLER, "page.tsx")
        for key in re.findall(r"check=\{`([^`]+)`\}", page):
            self.assertTrue(key.startswith(("cap|${iso}|", "ms|${key}|")), key)       # ${key} is inputsKey: iso= first


class ThePpaTerm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = src("site", "lib", "seller", "finance.ts")

    def test_the_eleventh_assumption(self):
        hit = re.search(r"export const KEYS: Key\[\] = \[(.*?)\];", self.lib)
        self.assertEqual(re.findall(r'"(\w+)"', hit.group(1)), ["capex", "share", "rate", "term", "fom", "deg", "life", "hurdle", "cshare", "cprice", "ppa"])
        self.assertIn('ppa: { key: "ppa", letter: "y", label: "PPA term", unit: "years", min: 1, max: 40, whole: true, swing: 5, swingWords: "5 years",', self.lib)
        self.assertIn("hurdle: HURDLE, cshare: 0, cprice: 0, ppa: costs.life };", self.lib)
        self.assertIn("export const contractYears = (a: Assumptions) => Math.min(a.ppa ?? debtYears(a), a.life);", self.lib)
        self.assertIn("t <= contractYears(a) ?", self.lib)
        self.assertIn("dy = contractYears(a);  // session 264: the PPA term's years", self.lib)
        self.assertIn('/^[ab][csrtfdlhnpy]$/', self.lib)
        self.assertIn('/^[ab][cftly]$/', self.lib)
        self.assertNotIn("out.ppa = out.term", self.lib)                            # never inferred from the debt's term

    def test_the_panel_cites_the_life_and_the_row_names_the_term(self):
        block = src(*SELLER, "SellerScenarios.tsx")
        self.assertIn('k === "life" || k === "term" || k === "ppa" ? `${SPECS[k].source}, ${f.costs.lifeNote}`', block)
        self.assertIn("for a PPA term of ${plain(contractYears(c.y))} years", block)
        self.assertIn("No published PPA term is held, so the default is this asset's life", self.lib)

    def test_the_librarys_own_test_passes(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        r = subprocess.run([exe, "scripts/test-seller-finance.mjs"], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertIn("the contract runs for the PPA term (15 years), the debt for its own (10)", r.stdout)
        self.assertIn("all passed", r.stdout)


class TheRetiredScripts(unittest.TestCase):
    def test_moved_with_a_record_not_deleted(self):
        scripts = os.path.join(ROOT, "site", "scripts")
        for f in ("check-seller.mjs", "check-seller-face.mjs"):
            self.assertFalse(os.path.exists(os.path.join(scripts, f)), f)
            self.assertTrue(os.path.exists(os.path.join(scripts, "_retired", f)), f)
        readme = src("site", "scripts", "_retired", "README.md")
        for words in ("`check-seller.mjs`", "`check-seller-face.mjs`", "session 264", "session 212", "check-values.mjs"):
            self.assertIn(words, readme)
        self.assertNotIn("check-seller.mjs", src("site", "package.json"))


class TheDownloadsFollowTheLicense(unittest.TestCase):
    def test_off_for_a_held_grid_with_the_catalogues_words(self):
        page = src(*SELLER, "page.tsx")
        self.assertIn("const pricesHeld = licenseHeldGrid(iso);", page)
        self.assertEqual(page.count("{pricesHeld ? "), 3)
        for route in ("months.csv", "tables.csv"):
            r = src(*SELLER, route, "route.ts")
            self.assertIn("return text(`${LICENSE_NEEDED}: ${licenseGridTitle(", r)
        self.assertIn('if (licenseHeldGrid(r.grid)) { put("capture_hub_year", row,', src(*SELLER, "tables.csv", "route.ts"))

    def test_the_verdicts_hold_ercot_and_caiso_public_and_were_not_changed(self):
        status = json.loads(src("site", "data", "license_status.json"))
        row = status["tables"]["merchant_revenue_monthly"]
        self.assertEqual((row["status"], row["from"]), ("license needed", "2026-10-21"))
        self.assertEqual(sorted(row["publishers"]), ["ISO-NE", "MISO", "NYISO"])
        lic = src("docs", "licenses.md")
        self.assertIn("| ERCOT | #2: read |", lic)
        self.assertIn("| CAISO | #3: read |", lic)
        for line in lic.splitlines():
            if line.startswith(("| ERCOT | #2", "| CAISO | #3", "| EIA | #1")):
                self.assertIn("| may be public | may be public |", line)


class TheClampLine(unittest.TestCase):
    def test_a_value_outside_its_bounds_is_said(self):
        model = src(*SELLER, "model.ts")
        self.assertIn('typed("mw", "Size, MW", x.mw, 1, 5000);', model)
        self.assertIn("is below the bound of ${fmt(lo)}, so ${whose} ${fmt(used)}.", model)
        self.assertIn("is above the bound of ${fmt(hi)}, so ${whose} ${fmt(used)}.", model)
        self.assertIn('is not a number, so ${whose} ${fmt(used)}.', model)
        self.assertIn('for (const p of ["a", "b"] as const) for (const kk of SCENARIO_KEYS) {', model)
        self.assertIn('role="status" data-clamped={clamped.length}', src(*SELLER, "page.tsx"))


def mirror():
    path = os.path.join(ROOT, "site", "public", "seller", "erw_2026_generator_replication.py")
    spec = importlib.util.spec_from_file_location("erw_generator_mirror_264", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheReplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = mirror()
        cls.n = cls.m.numbers(cls.m.read(os.path.join(ROOT, "site", "public", "seller", cls.m.CSV_NAME)))

    def test_the_defaults_are_the_pages(self):
        self.assertEqual((self.m.HURDLE, self.m.LIFE_YEARS, self.m.PPA_YEARS), (0.12, 35, 35))
        lib = src("site", "lib", "seller", "finance.ts")
        self.assertIn("export const HURDLE = 12;", lib)
        do = src("site", "public", "seller", "erw_2026_generator_replication.do")
        for line in ("scalar s_hurdle = 0.12\n", "scalar s_life_years = 35\n", "scalar s_ppa_years = 35\n"):
            self.assertIn(line, do)

    def test_the_closed_form_equals_the_year_by_year_sum(self):
        n, m = self.n, self.m
        ds = m.CAPEX_USD_KW * m.DEBT_SHARE * m.DEBT_RATE / (1 - (1 + m.DEBT_RATE) ** (-m.DEBT_YEARS))
        e = n["l12_energy"] / 1000
        flows = lambda price: [-m.CAPEX_USD_KW * (1 - m.DEBT_SHARE)] + [price * e - m.FOM_USD_KW_YEAR - ds for _ in range(m.LIFE_YEARS)]
        npv = lambda fl: sum(v / (1 + m.HURDLE) ** t for t, v in enumerate(fl))
        # session 304: the market revenue falls by the degradation each year after the first (the page's default since session 298)
        merchant = [-m.CAPEX_USD_KW * (1 - m.DEBT_SHARE)] + [n["l12_kw"] * (1 - m.DEG) ** k - m.FOM_USD_KW_YEAR - ds for k in range(m.LIFE_YEARS)]
        self.assertAlmostEqual(npv(merchant) * 1000 * m.MW / 1e6, n["npv_million"], places=9)
        self.assertAlmostEqual(npv(flows(n["breakeven_ppa"])), 0, places=6)
        self.assertAlmostEqual((n["contract_price"] * e - m.FOM_USD_KW_YEAR) / ds, 1.25, places=9)
        self.assertEqual(round(n["capture_rate"]), round(100 * n["price_received"] / n["flat_average"]))

    def test_the_mirror_prints_the_new_lines(self):
        out = "\n".join(self.m.report(self.n))
        for words in ("capture rate, percent of the flat average: ", "energy sold, last twelve months, MWh per MW: ", "contract price at which coverage reaches 1.25 times, USD per MWh: ",
                      "NPV at the hurdle rate, USD million for 100 MW: ", "breakeven PPA price, the whole of the energy for the PPA term, USD per MWh: "):
            self.assertIn(words, out)


class ThePack(unittest.TestCase):
    def test_the_pack_replaces_the_note(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "reviews", "packs", "generator.md")))
        self.assertFalse(os.path.exists(os.path.join(ROOT, "docs", "howitworks", "generator.md")))
        readme = src("docs", "howitworks", "README.md")
        self.assertIn("| What a generator earns | `/cost-of-power/seller` | [the review pack](../reviews/packs/generator.md) |", readme)
        pack = src("docs", "reviews", "packs", "generator.md")
        self.assertIn("PPA term", pack)
        self.assertIn("python erw_2026_generator_replication.py", pack)
        self.assertIn("do erw_2026_generator_replication.do", pack)
        self.assertNotIn("{E_", pack)                                                # every edge case filled from tonight's run

    def test_no_em_dash_in_what_this_session_wrote(self):
        for parts in (SELLER + ("page.tsx",), SELLER + ("model.ts",), SELLER + ("SellerScenarios.tsx",), SELLER + ("months.csv", "route.ts"), SELLER + ("tables.csv", "route.ts"),
                      ("site", "lib", "seller", "finance.ts"), ("site", "scripts", "check-values.mjs"), ("site", "scripts", "test-seller-finance.mjs"),
                      ("site", "scripts", "check-seller-scenarios.mjs"), ("site", "scripts", "_retired", "README.md"),
                      ("site", "public", "seller", "erw_2026_generator_replication.do"), ("site", "public", "seller", "erw_2026_generator_replication.py"),
                      ("docs", "reviews", "packs", "generator.md"), ("docs", "methods", "generator_earns_algorithm.md"), ("docs", "howitworks", "README.md"),
                      ("tests", "test_session264.py")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
