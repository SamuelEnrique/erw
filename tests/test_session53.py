"""Session 53: home page v2, tools by audience, the tour and the nav.

Energy Research Warehouse (ERW). No network, no model.
1. The nav: no menu holds more than eight entries, and no page left it (every page of session 52's nav is still there).
2. Every home page card and every tour stop links to a route under site/app, and check-routes fetches it.
3. docs/tools.md lists every page of the nav.
4. The tour has five stops, about three minutes; the home page links to it and keeps the live-price strip at the top.

    python -m unittest tests.test_session53 -v
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
# session 52's nav, every page of it (lib/pages.ts at ad79ec2)
BEFORE = ["/board", "/markets", "/cost-of-power", "/prices", "/explorer/ercot-peak-premium", "/network", "/grid", "/mix", "/curtailment",
          "/emissions", "/storage", "/consumption", "/map", "/datacenters", "/companies", "/policy", "/deals", "/events",
          "/learn/problems/know-your-grid", "/learn/problems/prices-and-your-bill", "/learn/problems/when-the-grid-broke", "/learn/bill",
          "/severance", "/play/battery", "/digest", "/roundup", "/subscribe", "/data", "/analysis", "/ask", "/about", "/terms",
          "/grid/ercot", "/grid/caiso", "/grid/pjm", "/grid/nyiso", "/grid/isone", "/grid/miso", "/grid/spp"]


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def route_exists(href):
    """A page.tsx under site/app for the path, static segments first, then a dynamic [segment]."""
    # session 239: an address folded into a tab of another page answers through its redirect (next.config.ts)
    with open(os.path.join(SITE, "next.config.ts"), encoding="utf-8") as f:
        if 'source: "%s"' % href.split("#")[0].split("?")[0] in f.read():
            return True
    parts = [p for p in href.split("#")[0].split("?")[0].strip("/").split("/") if p]
    # session 237: an address folded into the Grid tool (/network, /mix, /grid/<iso>) redirects into it
    # (site/next.config.ts): it resolves, through its redirect
    if f'source: "/{"/".join(parts)}", ' in src("site", "next.config.ts"):
        return True
    d = os.path.join(SITE, "app")
    for p in parts:
        if os.path.isdir(os.path.join(d, p)):
            d = os.path.join(d, p)
            continue
        dyn = [x for x in os.listdir(d) if x.startswith("[") and os.path.isdir(os.path.join(d, x))]
        if not dyn:
            return False
        d = os.path.join(d, dyn[0])
    return os.path.exists(os.path.join(d, "page.tsx"))


@unittest.skipUnless(NODE, "node is not installed")
class Nav(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        code = "import { GROUPS } from './lib/pages.ts'; console.log(JSON.stringify(GROUPS.map((g) => ({ label: g.label, n: g.pages.length, sub: g.sub ? g.sub.pages.length : 0, hrefs: [...g.pages.map((p) => p.href), ...(g.sub ? g.sub.pages.map((l) => l.href) : [])] }))));"
        r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr
        cls.groups = json.loads(r.stdout.strip().splitlines()[-1])

    def test_no_menu_over_eight(self):
        # session 203 (the roadmap's ruling of 12 October 2026): a menu may end with a sub-group under its own name
        # (Economics: Infrastructure Economics, five; Grid: the seven grid pages). Neither list holds more than eight.
        for g in self.groups:
            self.assertLessEqual(g["n"], 8, g["label"])
            self.assertLessEqual(g["sub"], 8, g["label"])

    def test_nothing_removed(self):
        now = {h for g in self.groups for h in g["hrefs"]}
        # session 132: a page folded into its tool's one page leaves the menu and its address redirects (next.config.ts)
        with open(os.path.join(SITE, "next.config.ts"), encoding="utf-8") as f:
            cfg = f.read()
        # session 288 (Samuel's ruling 14): a problem set left the menu for the index of the five, which is in it
        indexed = lambda h: h.startswith("/learn/problems/") and "/learn/problems" in now
        self.assertEqual([h for h in BEFORE if h not in now and f'source: "{h}"' not in cfg and not indexed(h)], [])
        for h in ("/tour", "/cost-of-power/seller", "/severance"):   # session 239: the lease tool is a tab of /severance
            self.assertIn(h, now)

    def test_every_nav_page_in_the_inventory(self):
        tools = src("docs", "tools.md")
        for g in self.groups:
            for h in g["hrefs"]:
                self.assertIn(f"`{h}`", tools, h)


class Links(unittest.TestCase):
    def test_cards_and_stops_resolve(self):
        home = src("site", "app", "page.tsx")
        tour = src("site", "lib", "tour.ts")
        routes = src("site", "scripts", "check-routes.mjs")
        # session 300: the home page links the five groups' first pages (lib/pages.ts) and the board, research, the digest and the roundup
        cards = sorted(set(re.findall(r'href="(/[a-z][^"]*)"', home)))
        stops = re.findall(r'href: "([^"]+)", title:', tour)
        self.assertGreaterEqual(len(cards), 4)
        self.assertEqual(len(stops), 7)   # session 292 (ruling 11a): seven stops
        for h in cards + stops + ["/tour"]:
            self.assertTrue(route_exists(h), h)
            self.assertIn(f'"{h}"', routes, f"{h} is not in check-routes")

    def test_home_layout(self):
        home = src("site", "app", "page.tsx")
        # session 300 (the owner's ruling of 18 October 2026, mockup A): the one line, the "right now" strip, today's chart,
        # the five groups, the latest Digest, in that order; the three audiences and the tour's button are gone from the page
        self.assertIn('title="The live, citable record of the US energy system."', home)
        self.assertLess(home.index("<RightNow />"), home.index("<TodayChart />"))
        self.assertLess(home.index("<TodayChart />"), home.index("<Groups N={N} />"))
        self.assertLess(home.index("<Groups N={N} />"), home.index("<Digest />"))
        self.assertEqual(home.count('<Audience title='), 0)

    def test_tour_minutes(self):
        tour = src("site", "lib", "tour.ts")
        # session 292: seven stops, their seconds a number each, about five minutes in all
        secs = [int(m) for m in re.findall(r'seconds: (\d+),', tour)]
        self.assertEqual(len(secs), 7)
        self.assertTrue(240 <= sum(secs) <= 330, sum(secs))
        self.assertNotIn(chr(0x2014), tour + src("docs", "tools.md"))


if __name__ == "__main__":
    unittest.main()
