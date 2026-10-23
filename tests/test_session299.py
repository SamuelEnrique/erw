"""Session 299: the Grid tool as one page of four tabs (the owner's merge of 18 October 2026, the Grid pack's rulings;
the chain prompt of 19 October). What is held to:

  the tabs are Network, Mix, Clean and Gravity, in that order; the grid is picked once above them; the page opens on
    the Lower 48 (ruling 4b) and on the Mix tab, which holds the Now view's blocks (so /grid draws what it drew);
  Ask is a panel beside every tab, drawn by the Ask view with the tab in its context (a site path, which the route's
    cleaner admits), and /ask redirects to it with the grid and the question carried;
  every old address resolves: view=now opens Mix, view=exchange opens Gravity, view=ask opens the panel, and the
    Gravity tab's address carries the network component's own shape word;
  the gravity shape's pull is a square-root scale (2c) in the page's rule and in the replication script alike, and
    the shape's note names EIA-930 as the one source, CAISO's break (1a) and the 63 undrawn authorities (6a);
  the line under the network gives the hour's age twice (3c): against the refresh (the check key) and the clock;
  the decisions block is on the page; the value checker and the route checker know the new addresses;
  the methods note and the review folder carry the session; no em dash in any file the session wrote.

No request, no model call; the environment is read, never set."""
import json
import math
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)
FILES = [
    "site/lib/gridtool.ts", "site/app/grid/page.tsx", "site/app/ask/page.tsx", "site/app/_retired/ask-original/page.tsx",
    "site/components/grid/AskView.tsx", "site/components/grid/NetworkView.tsx", "site/app/network/Network.tsx",
    "site/app/network/NetworkGravity.tsx", "site/lib/networkGravity.ts", "site/public/grid/erw_2026_grid_replication.py",
    "site/scripts/check-values.mjs", "site/scripts/check-routes.mjs", "site/scripts/check-ask-panel.mjs",
    "docs/methods/grid_network.md", "docs/brand/review-299/README.md", "tests/test_session299.py",
]


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
            "bare": {}, "now": {"grid": "ercot", "view": "now"}, "exchange": {"grid": "pjm", "view": "exchange"}, "ask": {"view": "ask"},
            "ask_flag": {"grid": "caiso", "ask": "1"}, "shape": {"grid": "ercot", "view": "network", "shape": "gravity"}, "gravity": {"grid": "spp", "view": "gravity"},
            "network": {"grid": "nyiso", "view": "network"}, "mix": {"view": "mix"}, "clean": {"grid": "isone", "view": "clean"},
        }
        code = ("import * as g from './lib/gridtool.ts'; "
                f"const asks = {json.dumps(asks)}; const out = {{ picks: {{}} }}; "
                "for (const [k, q] of Object.entries(asks)) { const p = g.gridPick(q); out.picks[k] = [p.grid.slug, p.view, p.ask]; } "
                "out.views = g.GRID_VIEWS.map((v) => v); out.old = g.OLD_VIEWS; out.defaults = [g.DEFAULT_VIEW, g.DEFAULT_GRID]; "
                "out.hrefs = [g.gridHref('us48'), g.gridHref('ercot', 'network'), g.gridHref('ercot', 'gravity'), g.gridHref('pjm', 'clean')]; "
                "console.log(JSON.stringify(out));")
        cls.d = node(code)

    def test_four_tabs_in_the_owners_order_and_the_old_words(self):
        self.assertEqual(self.d["views"], [["network", "Network"], ["mix", "Mix"], ["clean", "Clean"], ["gravity", "Gravity"]])
        self.assertEqual(self.d["old"], {"now": "mix", "exchange": "gravity", "ask": "mix"})

    def test_the_page_opens_on_the_lower_48_and_the_mix_tab(self):
        self.assertEqual(self.d["defaults"], ["mix", "us48"])        # ruling 4b: the Lower 48; Mix holds the Now view's blocks, the opening view until then
        self.assertEqual(self.d["picks"]["bare"], ["us48", "mix", False])
        self.assertEqual(self.d["picks"]["mix"], ["us48", "mix", False])

    def test_every_old_address_resolves_to_the_tab_that_holds_its_blocks(self):
        p = self.d["picks"]
        self.assertEqual(p["now"], ["ercot", "mix", False])
        self.assertEqual(p["exchange"], ["pjm", "gravity", False])
        self.assertEqual(p["ask"], ["us48", "mix", True])
        self.assertEqual(p["ask_flag"], ["caiso", "mix", True])
        self.assertEqual(p["shape"], ["ercot", "gravity", False])    # the network's own shape word opens the Gravity tab
        self.assertEqual(p["gravity"], ["spp", "gravity", False])
        self.assertEqual(p["network"], ["nyiso", "network", False])
        self.assertEqual(p["clean"], ["isone", "clean", False])

    def test_the_addresses_written(self):
        self.assertEqual(self.d["hrefs"], ["/grid?grid=us48", "/grid?grid=ercot&view=network", "/grid?grid=ercot&view=gravity&shape=gravity", "/grid?grid=pjm&view=clean"])


class ThePage(unittest.TestCase):
    def test_the_picker_once_the_tabs_the_panel_and_the_decisions(self):
        page = src("site", "app", "grid", "page.tsx")
        self.assertEqual(page.count("<ToolPicker "), 1)
        self.assertEqual(page.count("<ToolTabs "), 1)
        self.assertIn('items={GRID_VIEWS.map(([k, label]) => ({ key: k, label, href: gridHref(grid.slug, k), on: k === view }))}', page)
        for tab in ("network", "mix", "clean", "gravity"):
            self.assertIn(f'view === "{tab}" ?', page)
        self.assertIn('<div data-grid-now="1"><NowView grid={grid} cfg={cfg} data={data} /></div>', page)             # the Now view's blocks, on the Mix tab
        self.assertIn('<NetworkView keep={keep} node={p.node} shape="gravity" grid={grid} />', page)                   # the gravity shape, on the Gravity tab (session 1151: with the grid, for its keyed figures)
        self.assertIn('<div className="mt-10"><ExchangeView grid={grid} /></div>', page)                                # the Exchange view's blocks under it
        self.assertIn('<aside className="min-w-0 lg:border-l lg:border-rule lg:pl-6" aria-label="Ask" data-ask-side={grid.slug} data-ask-tab={view}>', page)
        self.assertIn('<AskView grid={grid} question={one(sp.q) ?? ""} tab={view} compact />', page)
        self.assertIn('data-decisions="299"', page)
        for word in ("4b", "1a", "2c", "3c", "6a"):
            self.assertIn(f"({word})" if word != "4b" else "ruling 4b", page)
        self.assertNotIn('data-ask-panel=', page)     # the Ask panel's own attribute stays unique to it (scripts/check-ask-panel.mjs)

    def test_the_ask_panel_names_the_tab_in_a_context_the_route_admits(self):
        ask = src("site", "components", "grid", "AskView.tsx")
        self.assertIn('const context = { view: "/grid/ercot", title: `The grid: ERCOT, ${tab}`, settings: { grid: "ERCOT", tab } };', ask)
        self.assertRegex("/grid/ercot", r"^/[A-Za-z0-9/_-]{0,80}$")     # lib/chat/ercot.ts cleanContext: a site path, no query
        self.assertIn('data-ask-compact={compact ? "1" : undefined}', ask)
        self.assertIn("[data-ask-compact]", src("site", "app", "tokens.css"))

    def test_ask_redirects_to_the_panel_and_the_old_page_is_kept(self):
        page = src("site", "app", "ask", "page.tsx")
        self.assertIn('import { redirect } from "next/navigation";', page)
        self.assertIn('const base = gridHref(gridBy(grid)?.slug ?? "us48");', page)
        self.assertIn('redirect(`${base}${base.includes("?") ? "&" : "?"}ask=1${q ? `&q=${encodeURIComponent(q.slice(0, 500))}` : ""}`);', page)
        old = src("site", "app", "_retired", "ask-original", "page.tsx")
        self.assertIn('import { AskForm } from "@/app/ask/AskForm";', old)
        self.assertIn("<AskForm grid={g?.slug ?? null} initial={sp.q ?? \"\"}", old)
        self.assertTrue(os.path.exists(os.path.join(SITE, "app", "ask", "AskForm.tsx")))
        self.assertTrue(os.path.exists(os.path.join(SITE, "app", "ask", "ercot", "page.tsx")))    # the reference version stays

    def test_the_hours_age_is_said_twice(self):
        view = src("site", "components", "grid", "NetworkView.tsx")
        self.assertIn("data-network-lag={lag} data-network-clock-lag={clockLag}", view)
        self.assertIn("<Num check={`net|lag|${shownHour}|${snap.built}`} raw={lag}>", view)
        self.assertIn("hours before this page was drawn", view)
        self.assertIn('shape?: Shape', view)
        self.assertIn("page={{ keep, node, shape }}", view)

    def test_the_gravity_note_names_the_source_the_break_and_the_undrawn(self):
        note = src("site", "app", "network", "NetworkGravity.tsx")
        block = note[note.index('data-gravity-note="1"'):]
        for words in ("EIA-930", "CAISO", "December 2025", "square root", "63 other balancing authorities"):
            self.assertIn(words, block)


class TheGravityRule(unittest.TestCase):
    def test_the_pull_is_a_square_root_in_both_rules(self):
        ts = src("site", "lib", "networkGravity.ts")
        self.assertIn("pull = clamp(Math.sign(share) * Math.sqrt(Math.abs(share) / S_FULL), -1, 1)", ts)
        py = src("site", "public", "grid", "erw_2026_grid_replication.py")
        self.assertIn("pull = clamp(math.copysign(math.sqrt(abs(share) / S_FULL), share), -1, 1)", py)

    @unittest.skipUnless(NODE, "node is not installed")
    def test_the_page_rule_against_the_replication_rule(self):
        gen = {"US48": 400000, "ERCO": 50000, "CISO": 20000, "PJM": 90000, "MISO": 80000, "NYIS": 15000, "ISNE": 12000, "SWPP": 40000}
        net = {"ERCO": 3125, "CISO": 5000, "PJM": -9000, "MISO": 0, "NYIS": 1500, "ISNE": None, "SWPP": -40000}
        out = node("import { gravityLayout } from './lib/networkGravity.ts'; "
                   f"const l = gravityLayout({json.dumps(gen)}, {json.dumps(net)}); console.log(JSON.stringify(l.places.map((p) => [p.id, p.r, p.d, p.share])));")
        SIZE, R_CENTER, D_MID, D_SPAN, S_FULL, R_MIN, GAP = 640, 80, 205, 90, 0.25, 6, 4
        clamp = lambda v, lo, hi: max(lo, min(hi, v))
        for pid, r, d, share in out:
            g, n = gen[pid], net[pid]
            er = max(R_MIN, R_CENTER * math.sqrt(g / gen["US48"]))
            pull = 0.0 if n is None else clamp(math.copysign(math.sqrt(abs(n / g) / S_FULL), n / g), -1, 1)
            ed = clamp(D_MID - D_SPAN * pull, R_CENTER + er + GAP, SIZE / 2 - er - GAP)
            self.assertAlmostEqual(r, er, places=9, msg=pid)
            self.assertAlmostEqual(d, ed, places=9, msg=pid)
        # a sixteenth of generation imported (ERCOT) is half the full pull: nearer the center than the linear rule put it
        ercot = next(p for p in out if p[0] == "ERCO")
        self.assertAlmostEqual(ercot[3], 0.0625)
        self.assertAlmostEqual(ercot[2], D_MID - D_SPAN * 0.5)
        # a full export (SPP) is the full push, held inside the frame; no tie (ISO-NE) is the middle ring
        spp = next(p for p in out if p[0] == "SWPP")
        self.assertAlmostEqual(spp[2], SIZE / 2 - spp[1] - GAP)      # the full push, held inside the frame (D_MID + D_SPAN would leave it)
        self.assertAlmostEqual(next(p for p in out if p[0] == "ISNE")[2], D_MID)


class TheChecks(unittest.TestCase):
    def test_the_value_checker_and_the_route_checker_know_the_new_addresses(self):
        values = src("site", "scripts", "check-values.mjs")
        for a in ("/grid?grid=ercot&view=gravity&shape=gravity", "/grid?grid=us48&view=gravity&shape=gravity"):
            self.assertIn(f'"{a}"', values)
        routes = src("site", "scripts", "check-routes.mjs")
        for a in ("/grid?grid=ercot&view=gravity&shape=gravity", "/grid?grid=us48&view=gravity&shape=gravity", "/grid?grid=ercot&view=now", "/grid?grid=caiso&ask=1",
                  "/grid?grid=ercot&view=exchange", "/grid?grid=ercot&view=ask", "/ask"):
            self.assertIn(f'"{a}"', routes)
        panel = src("site", "scripts", "check-ask-panel.mjs")
        self.assertIn("""document.querySelector('[data-ask-side="ercot"]')""", panel)

    def test_the_methods_note_and_the_review_folder(self):
        note = src("docs", "methods", "grid_network.md")
        self.assertIn("## One page, four tabs, and the Ask panel (session 299)", note)
        for words in ("4b, the opening grid", "1a, one source", "2c, a square-root pull", "3c, the age of", "6a, the 63 other"):
            self.assertIn(words, note)
        self.assertIn("Since session 299 the pull is a square-root scale", note)
        folder = os.path.join(ROOT, "docs", "brand", "review-299")
        shots = sorted(f for f in os.listdir(folder) if f.endswith(".png"))
        self.assertEqual(len(shots), 24)
        for state in ("before", "after"):
            for name in ("network", "mix", "clean", "gravity", "ercot_network", "ercot_ask"):
                for w in ("1280", "390"):
                    self.assertIn(f"{state}_{name}_{w}.png", shots)

    def test_no_em_dash_in_any_file_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
