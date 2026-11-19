"""Session 8602 (chain 504, 19 November 2026): the whole country in the Grid tool.

Energy Research Warehouse (ERW). EIA's thirteen regions of the lower 48 can be chosen in the Grid tool beside the seven
grids and the Lower 48, each with the tool's four tabs, drawn from the whole country's page files (site/data/regions/,
the data machine's; the contract docs/state/page_files_regions.md). What is held here:
- the address: a region has its own word, so every address of a grid reads exactly as it did;
- the readers of the contract's files (site/lib/gridregions.ts), run in Node on the tests' own fixture: the index, a
  region's mix (the latest hour held, the hours, the months), its trade (a month one side did not report is blank, and
  the total with it), the `alike` object and the one sentence a hover carries; anything that is not the file is null;
- the page: it hands over to the region's page only when the index holds the region named; the picker's row says "not
  built yet" until the index is on the site; a part a region's file does not hold is drawn blank with its reason; the
  seven grids' own blocks stand as they were; Ask is the Lower 48's, unchanged;
- the files the server must carry for a request, the release gate untouched, the fixture never shipped, no em dash.
The browser's proof is site/scripts/check-grid-regions.mjs on a built site (its run is in the session's report).
Nothing here sets the environment, reads a table or makes a request.
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)
FIX = os.path.join(ROOT, "tests", "fixtures", "session8602", "regions").replace(os.sep, "/")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


LOAD = ("import fs from 'node:fs'; import * as r from './lib/gridregions.ts';"
        "const j = (p) => JSON.parse(fs.readFileSync(" + json.dumps(FIX + "/") + " + p, 'utf-8'));")


@unittest.skipUnless(NODE, "node is not installed")
class TheAddress(unittest.TestCase):
    def test_the_thirteen_in_the_contracts_order(self):
        got = node("import { REGIONS, NEW_REGIONS, ALIKE } from './lib/gridregions.ts'; console.log(JSON.stringify([REGIONS.map((x) => x[0]), REGIONS.map((x) => x[1]), NEW_REGIONS, ALIKE]));")
        self.assertEqual(got[0], ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"])
        self.assertEqual(got[1], ["California", "Carolinas", "Central", "Florida", "Mid-Atlantic", "Midwest", "New England", "Northwest", "New York", "Southeast", "Southwest", "Tennessee", "Texas"])
        self.assertEqual(sorted(got[2]), ["CAR", "FLA", "NW", "SE", "SW", "TEN"])          # the six the site never drew
        self.assertEqual({k: v["ba"] for k, v in got[3].items()}, {"TEX": "ERCO", "NY": "NYIS", "NE": "ISNE", "MIDA": "PJM"})
        contract = src("docs", "state", "page_files_regions.md")
        for code in got[0]:
            self.assertIn("`" + code + "`", contract)

    def test_a_region_has_its_own_word(self):
        got = node("import { regionBy, regionHref } from './lib/gridregions.ts';"
                   "console.log(JSON.stringify([regionBy('se'), regionBy('SE'), regionBy(['ten', 'se']), regionBy('ercot'), regionBy(''), regionBy(undefined), regionHref('SE'), regionHref('TEX', 'network', { node: 'ERCO' }), regionHref('SE', 'gravity', { month: '2026-09', x: undefined })]));")
        self.assertEqual(got, ["SE", "SE", "TEN", None, None, None, "/grid?region=se", "/grid?region=tex&view=network&node=ERCO", "/grid?region=se&view=gravity&month=2026-09"])

    def test_every_address_of_a_grid_reads_as_it_did(self):
        # gridPick does not know the word: an address with a region picks what it picked without it
        got = node("import { gridPick, gridHref } from './lib/gridtool.ts';"
                   "const pick = (q) => { const p = gridPick(q); return [p.grid.slug, p.view, p.node, p.named]; };"
                   "console.log(JSON.stringify([pick({}), pick({ region: 'se' }), pick({ grid: 'ercot', view: 'clean' }), pick({ grid: 'ercot', view: 'clean', region: 'se' }), pick({ region: 'se', view: 'gravity' }), gridHref('ercot', 'mix'), gridHref('pjm', 'network')]));")
        self.assertEqual(got[0], got[1])
        self.assertEqual(got[2], got[3])
        self.assertEqual(got[4][:2], ["us48", "gravity"])
        self.assertEqual(got[5:], ["/grid?grid=ercot", "/grid?grid=pjm&view=network"])
        self.assertNotIn("region", src("site", "lib", "gridtool.ts").split("export function gridPick")[1].split("export function gridHref")[0])


@unittest.skipUnless(NODE, "node is not installed")
class TheFilesOfTheContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = node(LOAD + "const ix = r.readIndex(j('index.json')), m = r.readMix(j('mix/se.json')), t = r.readTrade(j('trade/se.json')), a = r.readAlike(j('demand/tex.json'));"
                     "const now = r.latestHour(m), h = r.lastHours(m, 35), w = r.lastHours(m, 7);"
                     "console.log(JSON.stringify({ regions: ix.regions.length, bas: ix.bas.length, of: r.regionOfBa(ix), now, n: m.hourly.hours.n, x: [h.x.length, h.x[0], h.x[h.x.length - 1], w.x.length, w.from], gaps: h.get('solar').filter((v) => v === null).length,"
                     " none: h.get('no_such_series').length, months: r.monthsOf(m).slice(0, 2), upto: m.upto, newest: r.newestTradeMonth(t), oct: r.tradeMonth(t, '2026-10'), aug: r.tradeMonth(t, '2026-08'), gone: r.tradeMonth(t, '2020-01'),"
                     " names: [r.neighborName('CAN'), r.neighborName('MEX'), r.neighborName('TEN'), r.regionName('SE'), r.regionName('ZZ')], why: r.whySentence(a), grid: a.grid, hour: r.hourAt({ start: '2025-08-01T19:00:00Z', step_hours: 1, n: 3 }, 5),"
                     " bad: [r.readIndex({}), r.readIndex({ built: 'x', regions: [{ code: 'SE' }], bas: [] }), r.readMix({}), r.readMix(null), r.readTrade({ months: [] }), r.readAlike({}), r.readAlike({ alike: { grid: 'ERCO', why: '  ' } }), r.latestHour({ months: {}, years: {}, sources: [] })] }));")

    def test_the_index(self):
        self.assertEqual((self.d["regions"], self.d["bas"]), (13, 49))
        self.assertEqual(self.d["of"]["TVA"], {"code": "TEN", "name": "Tennessee"})
        self.assertEqual(self.d["of"]["ERCO"], {"code": "TEX", "name": "Texas"})

    def test_the_latest_hour_is_the_newest_that_holds_a_net_generation(self):
        now = self.d["now"]
        self.assertEqual(self.d["n"], 840)
        self.assertEqual(now["i"], 838)                                   # the fixture's last hour holds none
        self.assertEqual(now["ts"], "2026-11-18T04:00:00Z")              # the start plus 838 hours
        self.assertEqual([s["key"] for s in now["sources"]], ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"])
        gas = now["sources"][0]
        self.assertAlmostEqual(gas["share_pct"], round(gas["mw"] / now["net_generation"] * 100, 2), places=2)
        self.assertAlmostEqual(now["net_imports"], round(now["demand"] - now["net_generation"], 1), places=1)

    def test_the_hours(self):
        self.assertEqual(self.d["x"], [840, "2026-10-14 06", "2026-11-18 05", 168, 672])
        self.assertEqual(self.d["gaps"], 1)                               # the hour the fixture blanks stays a gap
        self.assertEqual(self.d["none"], 0)
        self.assertEqual(self.d["hour"], "2025-08-02T00:00:00Z")
        self.assertEqual(self.d["months"][0], self.d["upto"])

    def test_a_month_one_side_did_not_report_is_blank_and_so_is_its_total(self):
        oct_ = self.d["oct"]
        self.assertEqual(self.d["newest"], "2026-10")
        self.assertIsNone(oct_["total"])
        self.assertEqual([x["code"] for x in oct_["rows"]], ["TEN", "CAR", "FLA"])        # the largest flow first, the unreported last
        fla = oct_["rows"][2]
        self.assertEqual((fla["own"], fla["theirs"], fla["gap"], fla["hoursOwn"]), (None, -700300, None, 0))
        aug = self.d["aug"]
        self.assertEqual(aug["rows"][0]["code"], "FLA")
        self.assertEqual(aug["total"], round(sum(x["own"] for x in aug["rows"]), 1))
        self.assertIsNone(self.d["gone"])

    def test_the_names_and_the_one_sentence(self):
        self.assertEqual(self.d["names"], ["Canada", "Mexico", "Tennessee", "Southeast", "ZZ"])
        self.assertEqual(self.d["grid"], "ERCO")
        self.assertEqual(self.d["why"], "Fixture sentence: the region sums the authorities EIA places in it and the grid's file reads one authority's own workbook.")

    def test_anything_that_is_not_the_file_is_nothing(self):
        self.assertEqual(self.d["bad"], [None] * 8)

    def test_the_fixture_says_what_it_is_and_is_never_shipped(self):
        for rel in ("index.json", "trade/se.json", "demand/tex.json"):
            self.assertIn("TEST FIXTURE", json.loads(src("tests", "fixtures", "session8602", "regions", *rel.split("/")))["fixture"])
        self.assertIn("TEST FIXTURE", json.loads(src("tests", "fixtures", "session8602", "regions", "mix", "se.json"))["name"])
        for rel in (("site", "lib", "gridregions.ts"), ("site", "lib", "regionsdata.ts"), ("site", "components", "grid", "RegionViews.tsx"), ("site", "app", "grid", "RegionTool.tsx"), ("site", "app", "grid", "page.tsx")):
            self.assertNotIn("session8602", src(*rel))
            self.assertNotIn("fixture", src(*rel).lower())
        # no file of the data machine's folder is written by this branch
        tracked = subprocess.run(["git", "ls-files", "site/data/regions"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        self.assertEqual([f for f in tracked if "session8602" in f], [])


class ThePage(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "grid", "page.tsx")
        self.views = src("site", "components", "grid", "RegionViews.tsx")
        self.tool = src("site", "app", "grid", "RegionTool.tsx")

    def test_it_hands_over_only_for_a_region_the_index_holds(self):
        self.assertIn("const region = index?.regions.find((r) => r.code === code) ?? null;", self.page)
        self.assertIn("return index && region ? { index, region } : null;", self.page)
        self.assertIn("if (inRegion) return <RegionTool ", self.page)
        self.assertLess(self.page.index("if (inRegion) return <RegionTool "), self.page.index("const cfg = grid.slug === \"us48\" ? null : gridOf(grid.slug);"))

    def test_the_seven_grids_own_blocks_stand_as_they_were(self):
        for words in (
            '<ToolPicker label="Grid" items={GRID_CHOICES.map((g) => ({ key: g.slug, label: g.label, href: gridHref(g.slug, view), on: g.slug === grid.slug, title: g.name }))} />',
            '<ToolTabs label="Views" items={GRID_VIEWS.map(([k, label]) => ({ key: k, label, href: gridHref(grid.slug, k), on: k === view }))} />',
            '{view === "network" ? <NetworkView keep={keep} node={p.node} grid={grid} /> : null}',
            '<div data-grid-now="1"><NowView grid={grid} cfg={cfg} data={data} /></div>',
            "<MixView c={mix} />",
            '{cfg && data ? <div className="mt-10"><GridMixParts g={cfg} d={data} /></div> : null}',
            '<div className="mt-10"><MixTable /></div>',
            "<EmissionsParts focus={`eia930:${grid.ba}`} grid={grid.slug} />",
            '<div className="mt-10"><ExchangeView grid={grid} /></div>',
            '<AskView grid={grid} question={one(sp.q) ?? ""} tab={view} compact />',
        ):
            self.assertIn(words, self.page)
        choices = src("site", "lib", "gridtool.ts")
        for slug, label, ba in (("ercot", "ERCOT", "ERCO"), ("caiso", "CAISO", "CISO"), ("pjm", "PJM", "PJM"), ("miso", "MISO", "MISO"), ("nyiso", "NYISO", "NYIS"), ("isone", "ISO-NE", "ISNE"), ("spp", "SPP", "SWPP"), ("us48", "US48", "US48")):
            self.assertIn('{ slug: "%s", label: "%s", ba: "%s",' % (slug, label, ba), choices)
        # the seven grids' files are read as they were: nothing of the regions' reading is in the mix's own libraries
        for rel in (("site", "lib", "mixdata.ts"), ("site", "lib", "mix2.ts"), ("site", "lib", "mixpage.ts"), ("site", "components", "grid", "MixView.tsx"), ("site", "components", "mix", "views.tsx"), ("site", "lib", "grid.ts")):
            self.assertNotIn("regions", src(*rel).replace("@/lib/regions", "").replace("lib/regions.ts", ""), rel)

    def test_the_pickers_row_until_the_index_is_on_the_site(self):
        self.assertIn("<RegionPicker index={index} on={null} view={view} alike={alikeOf(index)} />", self.page)
        self.assertIn('data-region-picker="absent"', self.views)
        self.assertIn('words="not built yet"', self.views)
        self.assertIn("site/data/regions/index.json", self.views)

    def test_a_part_not_held_is_drawn_blank_with_its_reason(self):
        block = self.views.split("const NOT_HELD: [string, string][] = [")[1].split("];")[0]
        self.assertEqual(block.count('  ["'), 7)
        for part in ("Hub price beside the mix", "Wind and solar forecasts against actual", "Records: the highest and lowest hours", "How hard the system works", "Availability by source", "By state, and since 2001"):
            self.assertIn(part, block)
        self.assertIn('words = "not held for this region"', self.views)
        self.assertIn("rows={NOT_HELD.map(([part, why]) => ({ key: part, cells: [part, <NH key=\"w\" why={`${why} (${file(\"mix\", code)})`} />] }))}", self.views)
        # nothing is filled: a figure the file does not hold is the placeholder, never a zero
        self.assertIn('v === null ? <NH words="not held"', self.views)

    def test_a_region_has_the_four_tabs_and_the_same_ask(self):
        for words in ("{view === \"mix\" ? <RegionMixView ", "{view === \"clean\" ? <RegionCleanView ", "{view === \"gravity\" ? <RegionTradeView ", "<RegionAuthorities region={region} index={index} node={node} />",
                      "<AskView grid={us48} question={one(sp.q) ?? \"\"} tab={view} compact />", "<AskExamples grid={us48} />", 'data-decisions="8602"'):
            self.assertIn(words, self.tool)
        # Ask is not changed: its component and its routes are not edited by this session (their words are not in the new files)
        self.assertNotIn("api/ask", self.tool + self.views)

    def test_the_panel_names_the_region_only_when_the_index_is_held(self):
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn("{page?.regions?.[pick.id] ? <div className=\"text-xs\" data-panel-region={page.regions[pick.id].code}>EIA region: ", n)
        v = src("site", "components", "grid", "NetworkView.tsx")
        self.assertIn("const regions = regionIndex ? regionOfBa(regionIndex) : undefined;", v)

    def test_the_server_carries_the_files_a_request_reads(self):
        cfg = src("site", "next.config.ts")
        self.assertIn('"/grid": ["./data/regions/index.json", "./data/regions/mix/*.json", "./data/regions/trade/*.json", "./data/regions/demand/*.json"]', cfg)
        data = src("site", "lib", "regionsdata.ts")
        self.assertIn('const fileOf = (code: string) => (regionBy(code) ? `${regionBy(code)!.toLowerCase()}.json` : null);', data)   # a path is made only from one of the thirteen codes
        self.assertIn('import "server-only";', data)

    def test_the_release_gate_is_not_touched(self):
        rel = src("site", "lib", "release.ts")
        self.assertIn('  "/grid": "review",', rel)
        self.assertNotIn("region", rel.lower().replace("regions.ts", ""))

    def test_the_method_note(self):
        note = src("docs", "methods", "grid_network.md")
        for words in ("## The thirteen regions in the Grid tool (session 8602)", "docs/state/page_files_regions.md", "not held for this region", "region=se"):
            self.assertIn(words, note)

    def test_no_em_dash(self):
        for parts in (("site", "lib", "gridregions.ts"), ("site", "lib", "regionsdata.ts"), ("site", "components", "grid", "RegionViews.tsx"), ("site", "app", "grid", "RegionTool.tsx"), ("site", "app", "grid", "page.tsx"),
                      ("site", "scripts", "check-grid-regions.mjs"), ("site", "next.config.ts"), ("tests", "fixtures", "session8602", "make_regions_8602.py"), ("docs", "methods", "grid_network.md"), ("tests", "test_session8602.py")):
            self.assertNotIn(EM, src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
