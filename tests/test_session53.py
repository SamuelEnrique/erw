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
    parts = [p for p in href.split("#")[0].split("?")[0].strip("/").split("/") if p]
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
        code = "import { GROUPS } from './lib/pages.ts'; console.log(JSON.stringify(GROUPS.map((g) => ({ label: g.label, n: g.pages.length + (g.sub ? g.sub.links.length : 0), hrefs: [...g.pages.map((p) => p.href), ...(g.sub ? g.sub.links.map((l) => l.href) : [])] }))));"
        r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr
        cls.groups = json.loads(r.stdout.strip().splitlines()[-1])

    def test_no_menu_over_eight(self):
        for g in self.groups:
            self.assertLessEqual(g["n"], 8, g["label"])

    def test_nothing_removed(self):
        now = {h for g in self.groups for h in g["hrefs"]}
        self.assertEqual([h for h in BEFORE if h not in now], [])
        for h in ("/tour", "/cost-of-power/seller", "/severance/lease"):
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
        cards = re.findall(r'\{ href: "([^"]+)", name:', home)
        stops = re.findall(r'href: "([^"]+)", title:', tour)
        self.assertGreaterEqual(len(cards), 15)
        self.assertEqual(len(stops), 5)
        for h in cards + stops + ["/tour"]:
            self.assertTrue(route_exists(h), h)
            self.assertIn(f'"{h}"', routes, f"{h} is not in check-routes")

    def test_home_layout(self):
        home = src("site", "app", "page.tsx")
        self.assertIn('href="/tour"', home)
        self.assertLess(home.index("<PriceBoard />"), home.index('<Audience title="Students and teachers"'))
        for a in ("Students and teachers", "Investors and lenders", "Researchers"):
            self.assertIn(f'<Audience title="{a}"', home)
        self.assertIn("AI&apos;s demand for power", home)

    def test_tour_minutes(self):
        tour = src("site", "lib", "tour.ts")
        secs = [int(m) for m in re.findall(r'minutes: "about (\d+) seconds"', tour)]
        self.assertEqual(len(secs), 5)
        self.assertTrue(150 <= sum(secs) <= 210, sum(secs))
        self.assertNotIn(chr(0x2014), tour + src("docs", "tools.md"))


if __name__ == "__main__":
    unittest.main()
