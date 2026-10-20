"""Session 203: the navigation of the roadmap's ruling of 12 October 2026, and docs/brand.md version 0.

What is held to:

  the menus are Economics, Grid, Infrastructure, Analysis, Games and About, in that order, and Energy Digest, Roundup and
    Email are not a menu: they stand at the right of the header, in grey;
  Economics ends with the sub-group "Infrastructure Economics": Batteries, Generators, Datacenters, What a battery saves
    a customer, The shoulder hours, in the ruling's order; About is Data and methods, About, Terms;
  every page kept its address, its line and its tables: only the groups and the menu's names changed;
  the datacenter page is "Datacenter tracker";
  on a phone a menu spans the menus' width, so that none runs past the screen;
  docs/brand.md states direction A, and the mark in use is untouched: the redrawn one is a proposal beside it.
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

# the 52 addresses of the menu as it stood before the session (site/lib/pages.ts at 5f944708)
# session 239 (the owner's instruction of 12 October 2026): seven pages became tabs of another page and left the menu, each
# address redirecting to its tab (tests/test_session239.py): /companies, /consumption, /explorer/ercot-peak-premium,
# /resources, /severance/lease, /storage/buildout and /storage/owners. The list below is the menu without them.
BEFORE = """/about /analysis /ask /battery/customer /board /contracts /cost-of-power /cost-of-power/battery
/cost-of-power/seller /curtailment /data /datacenters /deals /demand /digest /emissions /events /grid
/grid/caiso /grid/ercot /grid/isone /grid/miso /grid/nyiso /grid/pjm /grid/spp /learn/bill /learn/problems/know-your-grid
/learn/problems/networks-and-money /learn/problems/prices-and-your-bill /learn/problems/when-the-grid-broke /map /mix /network
/play/battery /policy /prices /roundup /severance /shoulder /storage
/subscribe /supply /terms /thesis /tour""".split()


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
class TheMenu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        code = ("import { GROUPS, PAGES } from './lib/pages.ts'; const n = (p) => p.menu ?? p.label; "
                "console.log(JSON.stringify({ groups: GROUPS.map((g) => ({ label: g.label, aside: !!g.aside, pages: g.pages.map((p) => [p.href, n(p), p.label]), "
                "sub: g.sub ? { label: g.sub.label, inline: !!g.sub.inline, pages: g.sub.pages.map((p) => [p.href, n(p), p.label]) } : null })), "
                "all: PAGES.map((p) => ({ href: p.href, line: p.line, tables: p.tables })) }));")
        r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr
        d = json.loads(r.stdout.strip().splitlines()[-1])
        cls.groups, cls.all = d["groups"], d["all"]
        cls.by = {g["label"]: g for g in cls.groups}

    def test_the_menus_are_the_six_of_the_ruling_and_the_news_is_aside(self):
        self.assertEqual([g["label"] for g in self.groups if not g["aside"]], ["Economics", "Grid", "Infrastructure", "Analysis", "Games", "About"])
        self.assertEqual([g["label"] for g in self.groups if g["aside"]], ["News"])
        self.assertEqual([p[1] for p in self.by["News"]["pages"]], ["Energy Digest", "Roundup", "Email"])
        self.assertEqual([p[0] for p in self.by["News"]["pages"]], ["/digest", "/roundup", "/subscribe"])

    def test_economics_ends_with_infrastructure_economics_in_the_rulings_order(self):
        sub = self.by["Economics"]["sub"]
        self.assertEqual((sub["label"], sub["inline"]), ("Infrastructure Economics", False))
        self.assertEqual([p[1] for p in sub["pages"]], ["Batteries", "Generators", "Datacenters", "What a battery saves a customer", "The shoulder hours"])
        self.assertEqual([p[0] for p in sub["pages"]], ["/cost-of-power/battery", "/cost-of-power/seller", "/cost-of-power", "/battery/customer", "/shoulder"])
        # the short names are the menu's alone: each page keeps its own
        self.assertEqual([p[2] for p in sub["pages"]][:3], ["What a battery earns", "What a generator earns", "Cost of power"])

    def test_about_is_the_rulings_three(self):
        self.assertEqual([p[1] for p in self.by["About"]["pages"]], ["Data and methods", "About", "Terms"])
        self.assertIsNone(self.by["About"]["sub"])

    def test_the_grid_menu_shows_the_one_grid_tool(self):
        # session 237 (the roadmap's item 2): the Grid tool is one page. Until then this test held the seven grid pages
        # as the Grid menu's line of short links ("Your grid": ERCOT, CAISO, PJM, NYISO, ISO-NE, MISO, SPP); they are
        # the tool's picker now, and the menu shows the tool in place of the pages that redirect into it
        self.assertIsNone(self.by["Grid"]["sub"])
        self.assertEqual([p[0] for p in self.by["Grid"]["pages"]], ["/grid", "/demand", "/curtailment"])   # session 239: Consumption is a view of /demand
        self.assertEqual(self.by["Grid"]["pages"][0][1], "The grid")

    def test_the_datacenter_page_is_renamed_and_the_two_names_do_not_meet(self):
        infra = {p[0]: p[1] for p in self.by["Infrastructure"]["pages"]}
        self.assertEqual(infra["/datacenters"], "Datacenter tracker")
        names = [p[1] for g in self.groups for p in g["pages"] + (g["sub"]["pages"] if g["sub"] else [])]
        self.assertEqual(names.count("Datacenters"), 1)                                     # the cost-of-power page, in Economics
        self.assertIn('title: "Datacenter tracker"', src("site", "app", "datacenters", "page.tsx"))

    def test_every_page_kept_its_address_and_none_was_added(self):
        now = sorted(p["href"] for p in self.all)
        # session 237: the ten pages folded into the Grid tool (/grid) left the menu; each address redirects into the
        # tool (site/next.config.ts). Every other page is where session 203 left it, and none was added
        folded = ["/network", "/mix", "/emissions", "/grid/ercot", "/grid/caiso", "/grid/pjm", "/grid/nyiso", "/grid/isone", "/grid/miso", "/grid/spp"]
        cfg = src("site", "next.config.ts")
        for h in folded:
            self.assertIn(f'source: "{h}", ', cfg, h)
        # session 238 (the owner's task of 12 October 2026): Automated Analysis is Research, at /research; the old
        # address is not dropped, it redirects (next.config.ts). Every other page keeps its address.
        moved = {"/analysis": "/research"}
        for old, new in moved.items():
            self.assertIn('{ source: "%s", destination: "%s", permanent: true }' % (old, new), src("site", "next.config.ts"))
        # session 288 (Samuel's ruling 14 of 14 October 2026): the four problem sets listed one by one left the menu for
        # their index, /learn/problems, which lists all five; each set keeps its address and is reached from the index
        sets = [h for h in BEFORE if h.startswith("/learn/problems/")]
        self.assertEqual(len(sets), 4)
        self.assertEqual(now, sorted([moved.get(h, h) for h in BEFORE if h not in folded and h not in sets] + ["/learn/problems", "/play/ev", "/impact"]))   # sessions 237, 238, 288, 294 (the EV game) and 347 (/impact)
        self.assertEqual(len(now), len(set(now)))                                           # each page once
        for p in self.all:
            self.assertTrue(p["line"], p["href"])

    def test_no_list_of_a_menu_is_longer_than_eight(self):
        for g in self.groups:
            self.assertLessEqual(len(g["pages"]), 8, g["label"])
            self.assertLessEqual(len(g["sub"]["pages"]) if g["sub"] else 0, 8, g["label"])


class TheHeader(unittest.TestCase):
    def test_the_aside_links_are_grey_by_a_rule_of_the_stylesheet(self):
        nav = src("site", "components", "Nav.tsx")
        self.assertIn('className="nav-aside ml-auto flex flex-wrap gap-x-4"', nav)
        self.assertIn("const ASIDE = GROUPS.filter((g) => g.aside).flatMap((g) => g.pages);", nav)
        css = src("site", "app", "globals.css").replace("\r\n", "\n")
        self.assertIn(".nav-aside a {\n  color: var(--color-muted);\n}", css)
        self.assertNotIn("style={{ color", nav)                                             # no color written in the component

    def test_a_menu_on_a_phone_spans_the_menus_width(self):
        nav = src("site", "components", "Nav.tsx")
        self.assertIn('className="relative flex min-w-0 flex-1 flex-wrap gap-x-5 gap-y-1 text-sm"', nav)
        self.assertIn('className="sm:relative"', nav)
        self.assertIn('absolute left-0 right-0 ${gi >= 3 ? "sm:left-auto sm:right-0" : "sm:right-auto"}', nav)

    def test_the_internal_view_keeps_its_lock(self):
        self.assertIn('internal view <a href="/internal/lock" className="text-muted">lock</a>', src("site", "components", "Nav.tsx"))

    def test_the_about_page_lists_a_sub_groups_pages_too(self):
        self.assertIn("[...g.pages, ...(g.sub?.pages ?? [])].map((p) => (", src("site", "app", "about", "page.tsx"))

    def test_the_release_gate_is_as_it_was(self):
        r = src("site", "lib", "release.ts")
        self.assertNotIn('"live",', r.split("export const RELEASE")[1])                      # every page stays in review
        self.assertNotIn("session 203", r)


class TheBrand(unittest.TestCase):
    def test_version_0_states_direction_a(self):
        b = src("docs", "brand.md")
        for words in ("# The ERW brand, version 0", "Source Serif 4", "IBM Plex Sans", "IBM Plex Mono", "`#FFFFFF`", "`#F7F3EA`", "`#E3DED1`", "`#6B675F`",
                      "`#2E2D29`", "`#8C1515`", "`#3C6E9E`", "One dark rule (ink, 1 px) under a table's header", "No legend box",
                      "default in grey with its source", "editable in place",
                      "**Status: approved 12 October 2026; the battery page is the reference.**"):   # session 234: approved
            self.assertIn(words, b, words)
        self.assertNotIn(EM, b)

    def test_the_mark_in_use_is_untouched_and_the_redrawn_one_is_beside_it(self):
        old = '<rect width="32" height="32" rx="3" fill="#8C1515"/><rect x="8" y="7" width="3" height="18" fill="#FFFFFF"/>'
        self.assertIn(old, src("docs", "brand", "erw-mark.svg"))
        self.assertIn('<rect width="32" height="32" rx="3" fill="#8C1515" />', src("site", "components", "Wordmark.tsx"))
        for f in ("erw-mark-proposed.svg", "erw-wordmark-proposed.svg"):
            s = src("site", "public", "brand", f)
            self.assertIn('<rect width="40" height="40" rx="2" fill="#8C1515"/>', s)
            self.assertIn("proposed", s)
            self.assertNotIn("<script", s)
        self.assertNotIn("proposed", src("site", "components", "Wordmark.tsx"))

    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in ("site/lib/pages.ts", "site/components/Nav.tsx", "site/app/globals.css", "docs/brand.md", "tests/test_session203.py",
                  "site/public/brand/erw-mark-proposed.svg", "site/public/brand/erw-wordmark-proposed.svg"):
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
