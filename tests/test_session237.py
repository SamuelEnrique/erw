"""Session 237: the Grid tool, one page at /grid (the roadmap's item 2; the owner's task of 12 October 2026).

What is held to:

  /grid is one page with a picker of eight (ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, SPP, the Lower 48) and six views
    (Now, Network, Mix, Clean, Exchange, Ask); the grid and the view are in the address;
  /network, /mix, /emissions, /mix/clean, /mix/stress and the seven /grid/<iso> redirect into its views, and an old
    address's own words are still read (the network's view and grid, the mix's view, ba and grids);
  the old pages' files are not deleted: they are the parts the views draw, under site/components/grid;
  the menu's Grid group shows the one tool; the page is in review;
  the page takes the brand through <Brand>, and the files written for it hold no color literal;
  the Exchange view's two new check keys are computed by the function the value checker calls.
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)

NEW = [("site", "lib", "gridtool.ts"), ("site", "app", "grid", "page.tsx"), ("site", "components", "grid", "NowView.tsx"),
       ("site", "components", "grid", "ExchangeView.tsx"), ("site", "components", "grid", "AskView.tsx"), ("site", "components", "tool", "Choose.tsx")]
MOVED = {  # where an old page's file is now
    ("site", "app", "network", "page.tsx"): ("site", "components", "grid", "NetworkView.tsx"),
    ("site", "app", "mix", "page.tsx"): ("site", "components", "grid", "MixView.tsx"),
    ("site", "app", "emissions", "page.tsx"): ("site", "components", "grid", "Emissions.tsx"),
    ("site", "app", "grid", "[iso]", "page.tsx"): ("site", "components", "grid", "YourGrid.tsx"),
    ("site", "app", "grid", "[iso]", "Reliability.tsx"): ("site", "components", "grid", "Reliability.tsx"),
}


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


@unittest.skipUnless(NODE, "node is not installed")
class TheAddress(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        asks = {
            "bare": {}, "ercot_mix": {"grid": "ercot", "view": "mix"}, "label": {"grid": "ISO-NE"}, "code": {"grid": "ERCO", "view": "network"},
            "other_node": {"grid": "BPAT", "view": "network"}, "ba": {"view": "mix", "ba": "ciso"}, "grids": {"view": "mix", "mix": "day", "grids": "pjm,miso"},
            "network_bare": {"view": "network"}, "mix_bare": {"view": "mix"}, "clean_bare": {"view": "clean"}, "mix_clean": {"view": "mix", "mix": "clean", "grid": "nyiso"},
            "odd": {"grid": "nowhere", "view": "nothing"}, "node": {"grid": "ercot", "view": "network", "node": "SWPP"}, "us48": {"grid": "us48", "view": "exchange"},
        }
        code = ("import * as g from './lib/gridtool.ts'; import { choiceOf, hrefOf } from './lib/mixpage.ts'; "
                f"const asks = {json.dumps(asks)}; const out = {{ picks: {{}} }}; "
                "for (const [k, q] of Object.entries(asks)) { const p = g.gridPick(q); out.picks[k] = [p.grid.slug, p.view, p.node, p.named]; } "
                "out.choices = g.GRID_CHOICES.map((c) => [c.slug, c.label, c.ba]); out.views = g.GRID_VIEWS.map((v) => v[0]); "
                "out.hrefs = [g.gridHref('ercot'), g.gridHref('ercot', 'mix'), g.gridHref('us48', 'network', { net: 'day', t: '2021-02-15' })]; "
                "out.own = [g.netFromPage('?grid=ercot&view=network&net=day&t=2021-02-15&node=ERCO&prices=1&shape=map'), g.netFromPage('?grid=ercot&view=network', 'ERCO'), g.netFromPage('?grid=us48&view=network', null)]; "
                "out.page = [g.netToPage('?grid=ercot&view=network', '?view=day&t=2021-02-15&grid=ERCO&prices=1&shape=map'), g.netToPage('?grid=us48&view=network', '')]; "
                "const base = { href: '/grid?grid=pjm&view=mix', viewKey: 'mix', grid: 'pjm' }; const c = { ...choiceOf({ view: 'day', grids: 'pjm' }), base }; "
                "out.mix = [hrefOf(c), hrefOf(c, { view: 'stress' }), hrefOf(c, { view: 'now' }), hrefOf({ ...choiceOf({ view: 'clean', grids: 'pjm' }), base: { href: '/grid?grid=pjm&view=clean', viewKey: null, grid: 'pjm' } }, { year: '2024' }), "
                "hrefOf(choiceOf({ view: 'day', grids: 'pjm' }))]; console.log(JSON.stringify(out));")
        cls.d = node(code)

    def test_the_picker_is_the_eight_in_the_owners_order_and_the_views_are_six(self):
        self.assertEqual([c[1] for c in self.d["choices"]], ["ERCOT", "CAISO", "PJM", "MISO", "NYISO", "ISO-NE", "SPP", "US48"])
        self.assertEqual([c[2] for c in self.d["choices"]], ["ERCO", "CISO", "PJM", "MISO", "NYIS", "ISNE", "SWPP", "US48"])
        self.assertEqual(self.d["views"], ["now", "network", "mix", "clean", "exchange", "ask"])

    def test_the_grid_and_the_view_are_in_the_address(self):
        self.assertEqual(self.d["hrefs"], ["/grid?grid=ercot", "/grid?grid=ercot&view=mix", "/grid?grid=us48&view=network&net=day&t=2021-02-15"])
        p = self.d["picks"]
        self.assertEqual(p["ercot_mix"], ["ercot", "mix", "ERCO", True])
        self.assertEqual(p["us48"], ["us48", "exchange", None, True])
        self.assertEqual(p["label"][0], "isone")

    def test_an_address_that_names_no_grid(self):
        p = self.d["picks"]
        self.assertEqual(p["bare"], ["ercot", "now", "ERCO", False])                # the first of the picker
        self.assertEqual(p["odd"], ["ercot", "now", "ERCO", False])                 # an address it does not understand
        # the views the old all-grid pages redirect into open on the Lower 48, as those pages opened: no panel on the network
        self.assertEqual(p["network_bare"], ["us48", "network", None, False])
        self.assertEqual(p["mix_bare"][0], "us48")
        self.assertEqual(p["clean_bare"][0], "us48")

    def test_an_old_address_is_still_read(self):
        p = self.d["picks"]
        self.assertEqual(p["code"], ["ercot", "network", "ERCO", True])             # /network?grid=ERCO
        self.assertEqual(p["other_node"], ["us48", "network", "BPAT", True])        # /network?grid=BPAT: no grid of the eight, that panel open
        self.assertEqual(p["ba"][0], "caiso")                                       # /mix?ba=ciso
        self.assertEqual(p["grids"][0], "pjm")                                      # /mix?view=day&grids=pjm,miso
        self.assertEqual(p["mix_clean"][:2], ["nyiso", "clean"])                    # the mix's "How clean, and when" is the Clean view
        self.assertEqual(p["node"], ["ercot", "network", "SWPP", True])             # a panel opened from another grid's view

    def test_the_network_reads_and_writes_its_own_words_under_the_tools(self):
        self.assertEqual(self.d["own"], ["?view=day&t=2021-02-15&grid=ERCO&prices=1&shape=map", "?grid=ERCO", ""])
        self.assertEqual(self.d["page"], ["?grid=ercot&view=network&net=day&t=2021-02-15&node=ERCO&prices=1&shape=map", "?grid=us48&view=network"])

    def test_the_mix_writes_its_addresses_under_the_tools(self):
        day, stress, now, clean, plain = self.d["mix"]
        self.assertEqual(day, "/grid?grid=pjm&view=mix&mix=day&grids=pjm")
        self.assertEqual(stress, "/grid?grid=pjm&view=mix&mix=stress&grids=pjm")
        self.assertTrue(now.startswith("/grid?grid=pjm&view=mix") and "mix=" not in now.split("view=mix", 1)[1], now)
        self.assertEqual(clean, "/grid?grid=pjm&view=clean&grids=pjm&year=2024")      # the Clean view's own view is fixed: no word for it
        self.assertEqual(plain, "/mix?view=day&grids=pjm")                            # without a base the mix's addresses are as they were


class TheRedirects(unittest.TestCase):
    def test_each_folded_address_redirects_into_a_view(self):
        cfg = src("site", "next.config.ts")
        for line in ('{ source: "/network", has: [{ type: "query", key: "view", value: "(?<net>[a-z0-9_]+)" }], destination: "/grid?view=network&net=:net", permanent: true }',
                     '{ source: "/network", destination: "/grid?view=network", permanent: true }',
                     '{ source: "/mix", has: [{ type: "query", key: "view", value: "clean" }], destination: "/grid?view=clean", permanent: true }',
                     '{ source: "/mix", has: [{ type: "query", key: "view", value: "(?<mix>[a-z]+)" }], destination: "/grid?view=mix&mix=:mix", permanent: true }',
                     '{ source: "/mix", destination: "/grid?view=mix", permanent: true }',
                     '{ source: "/emissions", destination: "/grid?view=clean", permanent: true }',
                     '{ source: "/mix/clean", destination: "/mix?view=clean", permanent: true }',      # session 133's, kept: it arrives in two steps
                     '{ source: "/mix/stress", destination: "/mix?view=stress", permanent: true }'):
            self.assertIn(line, cfg)
        for g in ("ercot", "caiso", "pjm", "nyiso", "isone", "miso", "spp"):
            self.assertIn(f'{{ source: "/grid/{g}", destination: "/grid?grid={g}", permanent: true }}', cfg)
        # a rule with a condition stands before the rule without one, or it would never be reached
        self.assertLess(cfg.index('source: "/network", has:'), cfg.index('{ source: "/network", destination: "/grid?view=network"'))
        self.assertLess(cfg.index('key: "view", value: "clean" }], destination: "/grid?view=clean"'), cfg.index('value: "(?<mix>[a-z]+)"'))
        self.assertLess(cfg.index('value: "(?<mix>[a-z]+)"'), cfg.index('{ source: "/mix", destination: "/grid?view=mix"'))

    def test_the_old_pages_files_moved_and_none_is_a_route(self):
        for old, new in MOVED.items():
            self.assertFalse(os.path.exists(os.path.join(ROOT, *old)), "/".join(old))
            self.assertTrue(os.path.exists(os.path.join(ROOT, *new)), "/".join(new))
        # what stood at /grid ("Grid conditions") is drawn from its own file; the Flex Alert scorecard keeps its page
        cond = src("site", "components", "grid", "Conditions.tsx")
        for words in ("export async function GridYesterday(", "export async function MixTable(", "Peak demand, {r.day} (UTC day)", "Generation mix, as a table"):
            self.assertIn(words, cond)
        self.assertTrue(os.path.exists(os.path.join(SITE, "app", "grid", "caiso", "alerts", "page.tsx")))
        # the network's component and its reads stay where they were
        for f in ("Network.tsx", "NetworkMap.tsx", "data.ts"):
            self.assertTrue(os.path.exists(os.path.join(SITE, "app", "network", f)), f)

    def test_the_page_stays_in_review_and_the_old_addresses_keep_their_lines(self):
        rel = src("site", "lib", "release.ts")
        for h in ("/grid", "/network", "/mix", "/emissions", "/mix/clean", "/mix/stress", "/grid/ercot", "/grid/spp"):
            self.assertIn(f'  "{h}": "review",', rel, h)
        self.assertNotIn('"live",', rel.split("export const RELEASE")[1].split("};")[0])


class ThePage(unittest.TestCase):
    def test_the_page_draws_the_six_views_under_the_brand(self):
        page = src("site", "app", "grid", "page.tsx")
        self.assertIn("<Brand>", page)
        for words in ("<ToolPicker label=\"Grid\"", "<ToolTabs label=\"Views\"", '{view === "now" ? <NowView', '{view === "network" ? <NetworkView', "<MixView c={mix} />",
                      "<EmissionsParts focus={`eia930:${grid.ba}`} />", "<MixClean c={mix} />", '{view === "exchange" ? <ExchangeView', '{view === "ask" ? <AskView', "<GridMixParts", "<GridCleanParts", "<MixTable />"):
            self.assertIn(words, page)

    def test_the_four_numbers_of_now_read_the_public_eia930_tables(self):
        now = src("site", "components", "grid", "NowView.tsx")
        self.assertIn('const DEMAND = "eia930_all_demand", GEN = "eia930_all_generation", CARBON = "carbon_intensity_hourly";', now)
        for key in ("`series|${t}|${r.entity}|${r.variable}|${r.ts_utc}`", "`net|export|${grid.ba}|${xHour}`", "`net|ties|${grid.ba}|${xHour}`"):
            self.assertIn(key, now)
        self.assertIn("data-now-sentence={grid.slug}", now)
        self.assertIn('const withheld = grid.slug === "caiso";', now)               # session 118's rule holds here too
        self.assertIn("<GridNowParts g={cfg} d={data} />", now)
        self.assertIn("<GridYesterday code={CONDITIONS_CODE[grid.slug]} />", now)

    def test_ask_is_ercots_profile_for_ercot_and_the_general_chat_for_the_others(self):
        ask = src("site", "components", "grid", "AskView.tsx")
        self.assertIn('<AskPanel grid="ercot" initial={q} inputId="ask-grid" showContext={false} context={context} />', ask)
        self.assertIn("<AskForm grid={grid.slug} initial={q}", ask)
        self.assertIn("<AskForm initial={q} />", ask)
        self.assertNotIn("fetch(", ask)                                             # the view sends nothing itself
        self.assertNotIn("AutoSubmit", ask)

    def test_what_a_grid_page_showed_is_drawn_by_the_views(self):
        g = src("site", "components", "grid", "YourGrid.tsx")
        for title in ('title="Right now: demand"', 'title="Who runs this grid"', 'title="Batteries"', 'title="What it costs"', 'title="Reliability"', 'title="What is being built"',
                      'title="In the news"', "title={`About ${g.iso}`}", 'title="Where the power comes from"', 'title="How clean"', "Reads that failed:", "<AskErcotLink "):
            self.assertIn(title, g)
        for part in ("export function GridNowParts(", "export function GridMixParts(", "export function GridCleanParts("):
            self.assertIn(part, g)

    def test_the_new_files_hold_no_color_literal_and_no_em_dash(self):
        for parts in NEW:
            s = src(*parts)
            self.assertNotIn(EM, s, "/".join(parts))
            self.assertIsNone(re.search(r"#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?\b", s), "/".join(parts))
            self.assertNotIn("rgb(", s, "/".join(parts))
        for parts in list(MOVED.values()) + [("site", "components", "grid", "Conditions.tsx"), ("tests", "test_session237.py"), ("site", "next.config.ts"), ("site", "lib", "pages.ts")]:
            self.assertNotIn(EM, src(*parts), "/".join(parts))

    def test_the_brand_holds_one_rule_for_tabs_and_segments(self):
        css = src("site", "app", "tokens.css")
        self.assertIn(".brand-a nav[data-tabs] a[aria-current=\"page\"]", css)
        self.assertIn(".brand-a nav[data-segments] a[aria-current=\"page\"]", css)
        choose = src("site", "components", "tool", "Choose.tsx")
        self.assertIn("data-tabs={label}", choose)
        self.assertIn("data-segments={label}", choose)

    def test_the_networks_canvas_reads_its_colors_from_the_tokens(self):
        net = src("site", "app", "network", "Network.tsx")
        self.assertIn('ink: "--color-ink", ground: "--color-panel", muted: "--color-muted", accent: "--color-accent", rule: "--color-rule"', net)
        self.assertIn("readPalette(box.current);", net)
        drawn = net.split("function readPalette(")[1]
        self.assertEqual(re.findall(r'"#[0-9a-fA-F]{6}"', drawn), [])
        self.assertEqual(re.findall(r'"#[0-9a-fA-F]{6}"', src("site", "app", "network", "NetworkMap.tsx")), [])


@unittest.skipUnless(NODE, "node is not installed")
class TheMenuAndTheKeys(unittest.TestCase):
    def test_the_grid_group_shows_the_one_tool(self):
        d = node("import { GROUPS, PAGES } from './lib/pages.ts'; const g = GROUPS.find((x) => x.label === 'Grid'); "
                 "console.log(JSON.stringify({ pages: g.pages.map((p) => [p.href, p.label]), sub: g.sub ?? null, groups: GROUPS.map((x) => [x.label, x.pages.length]), "
                 "related: PAGES.flatMap((p) => p.related ?? []), hrefs: PAGES.map((p) => p.href) }));")
        self.assertEqual(d["pages"], [["/grid", "The grid"], ["/demand", "Demand growth"], ["/curtailment", "Curtailment"], ["/consumption", "Consumption"]])
        self.assertIsNone(d["sub"])
        # nothing else of the menu changed: the other groups hold what they held
        self.assertEqual(d["groups"], [["Economics", 8], ["Grid", 4], ["Infrastructure", 8], ["Analysis", 5], ["Games", 6], ["About", 3], ["News", 3]])
        # no Related line points at a page that left the list
        self.assertEqual([h for h in d["related"] if h not in d["hrefs"] and not h.startswith("/learn/problems") and not h.startswith("/explorer")], [])

    def test_the_exchange_keys_are_the_checkers_own_function(self):
        d = node("import { netValue } from './lib/network.ts'; "
                 "const snap = { built: 'x', window: ['a', 'b'], hours: ['2026-10-10T00:00:00Z', '2026-10-10T01:00:00Z'], rule: '', nodes: [], "
                 "links: [{ a: 'ERCO', b: 'SWPP', mw: [120, null] }, { a: 'CEN', b: 'ERCO', mw: [30, 5] }] }; "
                 "const h = '2026-10-10T00:00:00Z'; console.log(JSON.stringify([netValue(snap, `net|export|ERCO|${h}`), netValue(snap, `net|tie|ERCO|SWPP|${h}`), netValue(snap, `net|tie|ERCO|CEN|${h}`), "
                 "netValue(snap, `net|ties|ERCO|${h}`), netValue(snap, `net|maxflow|ERCO|${h}`), netValue(snap, 'net|export|ERCO|2026-10-10T01:00:00Z'), netValue(snap, 'net|export|PJM|' + h) ?? null, "
                 "netValue(snap, 'net|export|ERCO|2026-10-11T00:00:00Z') ?? null]));")
        self.assertEqual(d, [90, 120, -30, 2, 120, -5, None, None])
        self.assertIn('if (p[0] === "net") {', src("site", "scripts", "check-values.mjs"))


if __name__ == "__main__":
    unittest.main()
