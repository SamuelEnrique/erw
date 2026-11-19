"""Session 8430 (chain 503, part D): /supply for the whole country.

The page gains a section "The whole country" (site/components/supply/Country.tsx) that draws EIA's thirteen regions of
the lower 48, with Canada and Mexico as neighbours, from the data machine's files (site/data/regions/trade/<region>.json,
trade_matrix.json and mix/<region>.json, the contract docs/state/page_files_regions.md): a region's net imports by
month and by neighbour with each side's report, who trades with whom in a year, and the generation mix by month, two
regions side by side. Held here:

- add, never change: outside what the session added, the page is byte for byte what its code drew before it, at each
  of the 103 addresses it answered (site/scripts/test-supply-pin.mjs, on a copy of the page's input files);
- the section drawn to HTML from fixtures in the contract's form, and the whole page with and without the files
  (site/scripts/test-supply-regions.mjs);
- the rules of the chain in the source: no fixture in the site's folder, no dash, the page still in review, no ledger
  and no share covered by imports, the method note says what the section shows.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
DASHES = (chr(0x2014), chr(0x2013))
NEW = ["site/lib/countrytrade.ts", "site/components/supply/Country.tsx", "site/scripts/regions-fixture-trade.mjs", "site/scripts/supply-added.mjs",
       "site/scripts/supply-pin-loader.mjs", "site/scripts/supply-pin-register.mjs", "site/scripts/test-supply-regions.mjs", "site/scripts/test-supply-pin.mjs"]
FIGURES = ("last", "prev", "year", "avg5", "change", "spark", "season")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(script):
    env = {k: v for k, v in os.environ.items() if k not in ("ERW_REGIONS_DIR", "SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_KEY")}
    return subprocess.run([NODE, "--import", "./scripts/supply-pin-register.mjs", script], cwd=SITE, capture_output=True, text=True,
                          encoding="utf-8", timeout=900, env=env)


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageDrawn(unittest.TestCase):
    def check(self, r, least):
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1500:])
        self.assertNotIn("FAIL", r.stdout)
        m = re.search(r"(\d+) of (\d+) passed", r.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= least, r.stdout[-500:])

    def test_nothing_the_page_showed_moves(self):
        self.check(node("scripts/test-supply-pin.mjs"), 208)

    def test_the_whole_country_section(self):
        r = node("scripts/test-supply-regions.mjs")
        self.check(r, 109)
        for held in ("a large gap is marked and said plainly on hover, with the rule, its default and its source",
                     "two regions side by side, A and B, in the trade view and in the mix view",
                     "pair by pair: which sent and which received, Canada and Mexico among them",
                     "the six regions new to the site are named, and each can be chosen",
                     "with no file the section says not built yet",
                     "a fixture in the site's own folder is refused",
                     "files that are not public: every cell blank with license needed on hover",
                     "a choice of region and year in the address moves nothing outside the section",
                     "the page with the files: outside the section it is, byte for byte, the page with none"):
            self.assertIn(held, r.stdout)


class TheSource(unittest.TestCase):
    def test_the_pin_holds_every_address_the_page_answered(self):
        pin = json.loads(src("site", "scripts", "pins", "supply-page-8430.json"))
        self.assertRegex(pin["clock"], r"^2026-11-19T")
        self.assertGreaterEqual(len(pin["addresses"]), 100)
        for must in ("", "g=burn", "s=eia-wcestus1", "s=cleared-miso&g=nowhere", "~catalogue-unread"):
            self.assertIn(must, pin["addresses"])
        for page in pin["addresses"].values():
            self.assertRegex(page["sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(page["bytes"], 20000)
        self.assertEqual(pin["addresses"][""]["figures"], 184)

    def test_the_pins_copy_of_the_input_is_the_public_file_and_no_more(self):
        copy = json.loads(src("site", "scripts", "pins", "supply-page-8430-input.json"))
        self.assertEqual(sorted(k for k in copy if k not in ("what", "from_commit")), ["license_status", "supply"])
        self.assertIn("Never read by the site", copy["what"])
        rows = {r["id"]: r for r in copy["supply"]["rows"]}
        # session 7051's rule holds for the copy too: a held grid's cleared row carries its status and note only
        for held in ("cleared-nyiso", "cleared-iso-ne"):
            self.assertEqual(rows[held]["status"], "licensed", held)
            self.assertEqual([k for k in FIGURES if k in rows[held]], [], held)
        # only the pin's own loader names the copy; no file of the site's app, components or lib reads it
        for base in ("app", "components", "lib"):
            for folder, _dirs, files in os.walk(os.path.join(SITE, base)):
                for name in files:
                    if name.endswith((".ts", ".tsx")):
                        with open(os.path.join(folder, name), encoding="utf-8") as f:
                            self.assertNotIn("supply-page-8430", f.read(), name)

    def test_the_page_mounts_the_section_once_above_the_decisions_block(self):
        page = src("site", "app", "supply", "page.tsx")
        self.assertEqual(page.count("<SupplyCountry "), 1)
        self.assertIn('<SupplyCountry searchParams={searchParams} keep={{ g: c.groups.join(","), s: c.s ?? "" }} />', page)
        self.assertIn('import { SupplyCountry } from "@/components/supply/Country";', page)
        self.assertLess(page.index("{shown.map((g) => <Table "), page.index("<SupplyCountry "))
        self.assertLess(page.index("<SupplyCountry "), page.index("<DecisionsBlock "))
        self.assertIn("const c = choiceOf(await searchParams, file);", page)

    def test_the_section_stands_between_its_marks_and_writes_none_of_the_pages_own(self):
        code = src("site", "components", "supply", "Country.tsx")
        self.assertIn('<section data-whole-country="supply" id="whole-country"', code)
        self.assertIn('<span data-whole-country-end="1"></span>', code)
        self.assertNotIn("data-n=", code)
        self.assertNotIn("data-row=", code)
        self.assertNotIn("data-group=", code)
        self.assertIn('data-whole-country="supply"', src("site", "scripts", "supply-added.mjs"))

    def test_no_dash_in_what_was_written(self):
        for f in NEW + ["tests/test_session8430_supply_regions.py", "site/app/supply/page.tsx", "docs/methods/supply_and_trade.md"]:
            text = src(*f.split("/"))
            for d in DASHES:
                self.assertNotIn(d, text, f)

    def test_no_fixture_in_the_sites_folder(self):
        folder = os.path.join(SITE, "data", "regions")
        if not os.path.isdir(folder):
            return
        for base, _dirs, files in os.walk(folder):
            for name in files:
                if name.endswith(".json"):
                    with open(os.path.join(base, name), encoding="utf-8") as f:
                        head = f.read(4000)
                    self.assertNotIn('"fixture"', head, name)

    def test_the_server_trace_names_the_folder_once_the_files_are_there(self):
        # /supply is drawn at each request and reads site/data/regions by names built from the address, so Vercel's
        # server trace does not find the files on its own: next.config.ts names such a folder for its page
        # (outputFileTracingIncludes, as data/datacenter and data/seller/hubs are named). Until the files land there is
        # nothing to name; from the day they are on a branch, a build without the line would draw "not built yet" for good.
        folder = os.path.join(SITE, "data", "regions")
        if not any(os.path.exists(os.path.join(folder, name)) for name in ("trade", "mix", "trade_matrix.json")):
            self.skipTest("the trade, matrix and mix files are not on this branch yet")
        m = re.search(r'"/supply": \[([^\]]*)\]', src("site", "next.config.ts"))
        self.assertTrue(m and "./data/regions/" in m.group(1), 'next.config.ts: outputFileTracingIncludes needs "/supply": ["./data/regions/**/*.json"]')

    def test_the_fixture_says_it_is_not_data(self):
        fx = src("site", "scripts", "regions-fixture-trade.mjs")
        self.assertIn("not data", fx)
        self.assertIn("fixture: FIXTURE", fx)
        lib = src("site", "lib", "countrytrade.ts")
        self.assertIn('import { REGION_CODES, REGION_NAME, SOURCES, readRegionFile, type Arr } from "./countryfiles";', lib)
        self.assertNotIn("node:fs", lib)  # every file is read through session 8410's reader, which refuses a fixture
        self.assertIn('"fixture" in v && v.fixture && !process.env.ERW_REGIONS_DIR', src("site", "lib", "countryfiles.ts"))

    def test_the_page_stays_in_review(self):
        self.assertIn('"/supply": "review"', src("site", "lib", "release.ts"))

    def test_no_ledger_no_ranking_and_no_share_covered_by_imports(self):
        code = src("site", "components", "supply", "Country.tsx") + src("site", "lib", "countrytrade.ts")
        shown = re.sub(r"//.*|/\*\*?[\s\S]*?\*/", "", code).lower()
        for word in ("donor", "taker", "giver", "covered by imports", "ledger"):
            self.assertNotIn(word, shown)
        # the share of demand the matrix file holds is not drawn until the owner rules
        self.assertIn("export const SHOWN = { importShare: false };", src("site", "components", "supply", "Country.tsx"))
        self.assertIn("export const REGIONS_HELD: string[] = [];", src("site", "components", "supply", "Country.tsx"))

    def test_the_large_gap_is_a_default_said_with_its_source(self):
        self.assertIn("export const LARGE_GAP_PCT = 10;", src("site", "lib", "countrytrade.ts"))
        code = src("site", "components", "supply", "Country.tsx")
        self.assertIn("this page's own choice (session 8430); no publisher's threshold stands behind it", code)
        self.assertIn("That is large by this page's rule", code)

    def test_the_method_note_says_what_the_section_shows(self):
        note = src("docs", "methods", "supply_and_trade.md")
        self.assertIn("\n## The whole country (session 8430, 19 November 2026)\n", note)
        part = note[note.index("## The whole country (session 8430"):note.index("## The cross-checks (session 7018")]
        for said in ("site/data/regions/", "trade/<region>.json", "trade_matrix.json", "mix/<region>.json", "docs/state/page_files_regions.md", "not built yet",
                     "10 percent", "no publisher's threshold", "no ledger", "Region A California", "never filled", "the Grid page"):
            self.assertIn(said, part, said)


if __name__ == "__main__":
    unittest.main()
