"""Session 1421 (chain 111): the older blocks' anchors and method links.

Energy Research Warehouse (ERW).

The blocks session 1420 named as panels (YourGrid's Right now, Batteries, What it costs and What is being built;
Reliability's three tables; the Now view's mix in that hour) each carry a stable anchor (session 1183's rules) and a
link to the section of the note that defines it (session 1184's rules), named in site/lib/gridAnchors.ts outside the
pinned lists of 17 (OLDER_ANCHOR, OLDER_BLOCKS, one METHOD_ constant a link). Where a block's link to a whole note
stood, it now opens the section, its words unchanged; Right now, the mix in that hour and Reliability's daily tables
gain one line. The fragments are held by site/scripts/test-grid-older-methods.mjs to the ids the site's renderer writes;
test-grid-addresses.mjs holds the anchors and the route check's list; test-grid-render.mjs's cases carry both.

    python -m unittest tests.test_session1421 -v
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


class TheAnchors(unittest.TestCase):
    def test_the_list_outside_the_pinned_seventeen(self):
        a = src("site", "lib", "gridAnchors.ts")
        for w in ('rightNow: "right-now",', 'batteries: "batteries",', 'cost: "what-it-costs",', 'building: "what-is-being-built",',
                  'reliability: "reliability",', 'reliabilityDays: "reliability-days",', 'reliabilityPeaks: "reliability-peaks",',
                  'reliabilityLatest: "reliability-latest",', 'nowMix: "now-mix",', "export const OLDER_BLOCKS: OlderBlock[] = ["):
            self.assertIn(w, a)
        # the pinned lists stand: GRID_ANCHOR and GRID_METHOD still hold their 17 panels and no older block
        g = a[a.index("export const GRID_ANCHOR = {"):a.index("} as const;", a.index("export const GRID_ANCHOR = {"))]
        self.assertEqual(g.count(": \""), 17)
        self.assertNotIn("right-now", g)

    def test_each_block_carries_its_anchor(self):
        y = src("site", "components", "grid", "YourGrid.tsx")
        for k, t in (("rightNow", "Right now: demand"), ("batteries", "Batteries"), ("cost", "What it costs"), ("building", "What is being built")):
            self.assertIn('<Section title="%s" id={OLDER_ANCHOR.%s}' % (t, k), y)   # the title first: session 137 reads the titles in order
        self.assertIn('g.slug === "caiso" ? <Section id="reliability" title="Reliability"', y)   # sessions 58 and 1420, kept
        for k in ("rightnow", "batteries", "cost", "building"):
            self.assertIn("<div data-grid-panel={`grid_%s_${g.slug}`}>" % k, y)   # session 1420's, kept
        r = src("site", "components", "grid", "Reliability.tsx")
        self.assertIn('<div data-grid-panel="grid_reliability_caiso">', r)   # session 1420's, kept
        for k in ("reliabilityDays", "reliabilityPeaks", "reliabilityLatest"):
            self.assertIn('<h3 id={OLDER_ANCHOR.%s} className="mb-1 text-base">' % k, r)
        n = src("site", "components", "grid", "NowView.tsx")
        self.assertIn("<div data-grid-panel={`grid_nowmix_${grid.slug}`}>", n)   # session 1420's, kept
        self.assertIn('<ToolSection title="The mix in that hour" id={OLDER_ANCHOR.nowMix}>', n)

    def test_the_route_check_lists_each(self):
        r = src("site", "scripts", "check-routes.mjs")
        for e in ("/grid?grid=ercot#right-now", "/grid?grid=ercot#batteries", "/grid?grid=ercot#what-it-costs", "/grid?grid=caiso#what-is-being-built",
                  "/grid?grid=caiso#reliability", "/grid?grid=caiso#reliability-days", "/grid?grid=caiso#reliability-peaks",
                  "/grid?grid=caiso#reliability-latest", "/grid?grid=ercot#now-mix"):
            self.assertIn('"%s"' % e, r)
        self.assertIn("const GRID_ANCHORS = [", r)   # session 1183's, kept


class TheMethods(unittest.TestCase):
    def test_the_constants(self):
        a = src("site", "lib", "gridAnchors.ts")
        for w in ('export const METHOD_RIGHT_NOW = "/data/methods/grid_network#right-now-and-the-mix-in-that-hour-what-each-figure-is-session-1421";',
                  'export const METHOD_BATTERIES = "/data/methods/storage#the-figures-on-the-page-and-their-keys";',
                  'export const METHOD_COST = "/data/methods/price_board#the-figures-on-the-page-and-their-keys";',
                  'export const METHOD_BUILDING_QUEUE = "/data/methods/energy_projects#the-figures-on-the-grid-page-and-their-keys";',
                  'export const METHOD_BUILDING_DATACENTERS = "/data/methods/datacenter_facilities#grid-pages-which-grid-a-facility-belongs-to-session-36a";',
                  'export const METHOD_RELIABILITY_NOTICES = "/data/methods/california_reliability#1-every-notice-since-1998-caiso_grid_emergencies";',
                  'export const METHOD_RELIABILITY_DAILY = "/data/methods/california_reliability#2-how-tight-was-it-caiso_reliability_daily-derived";'):
            self.assertIn(w, a)

    def test_each_link_in_its_block(self):
        y = src("site", "components", "grid", "YourGrid.tsx")
        for c in ("METHOD_BATTERIES", "METHOD_COST", "METHOD_BUILDING_QUEUE", "METHOD_BUILDING_DATACENTERS"):
            self.assertEqual(y.count("<Link href={%s}>Method</Link>" % c), 1, c)   # the existing link, its words unchanged
        self.assertIn("<Link href={METHOD_RIGHT_NOW}>Method: &quot;Right now&quot; and the mix in that hour</Link>", y)
        for gone in ('href="/data/methods/storage"', 'href="/data/methods/price_board"', 'href="/data/methods/energy_projects"', 'href="/data/methods/datacenter_facilities"'):
            self.assertNotIn(gone, y)
        r = src("site", "components", "grid", "Reliability.tsx")
        self.assertIn("<Link href={METHOD_RELIABILITY_NOTICES}>the method</Link>", r)
        self.assertIn("<Link href={METHOD_RELIABILITY_DAILY}>Method: how tight was it, the daily figures</Link>", r)
        n = src("site", "components", "grid", "NowView.tsx")
        self.assertIn("<Link href={METHOD_NOW_MIX}>Method: &quot;Right now&quot; and the mix in that hour</Link>", n)

    def test_the_note(self):
        m = src("docs", "methods", "grid_network.md")
        sec = m[m.index("## The older blocks' files, anchors"):m.index("## Not here")]
        self.assertIn("Decisions (chain 111, session 1421):", sec)
        self.assertIn('### "Right now" and the mix in that hour, what each figure is (session 1421)', sec)
        for w in ("`#right-now`", "`#batteries`", "`#what-it-costs`", "`#what-is-being-built`", "`#reliability-days`", "`#reliability-peaks`",
                  "`#reliability-latest`", "`#now-mix`", "`OLDER_BLOCKS`", "series_max|eia930_all_demand|demand_mw|", "`latestHour`"):
            self.assertIn(w, sec)
        self.assertIn("Decisions (chain 111, session 1420):", sec)   # session 1420's, kept

    def test_the_tests_hold_them(self):
        t = src("site", "scripts", "test-grid-older-methods.mjs")   # its own file: session 1184's counts test-grid-methods.mjs's five
        self.assertIn("const OLDER_HEADING = {", t)
        self.assertIn("const ids = n.heads.map((x) => slugs.next(x.html));", t)
        self.assertIn("each older block's method is a constant of lib/gridAnchors.ts, its fragment the renderer's id for its heading", t)
        self.assertIn("each older block's anchor is one plain id", src("site", "scripts", "test-grid-addresses.mjs"))
        r = src("site", "scripts", "test-grid-render.mjs")
        self.assertIn('"anchors": ["reliability-days", "reliability-peaks", "reliability-latest"], "methods": ["METHOD_RELIABILITY_NOTICES", "METHOD_RELIABILITY_DAILY"]', r)
        self.assertIn('"anchors": ["right-now"], "methods": ["METHOD_RIGHT_NOW"]', r)

    @unittest.skipUnless(NODE, "node is not on this machine")
    def test_they_parse(self):
        for f in ("check-routes.mjs", "check-links.mjs", "test-grid-older-methods.mjs", "test-grid-addresses.mjs", "test-grid-render.mjs"):
            r = subprocess.run([NODE, "--check", os.path.join("scripts", f)], cwd=SITE, capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, f + r.stderr[-1000:])

    def test_no_em_dash(self):
        for parts in (("site", "components", "grid", "YourGrid.tsx"), ("site", "components", "grid", "Reliability.tsx"), ("site", "components", "grid", "NowView.tsx"),
                      ("site", "lib", "gridAnchors.ts"), ("site", "scripts", "check-routes.mjs"), ("site", "scripts", "test-grid-older-methods.mjs"),
                      ("site", "scripts", "test-grid-addresses.mjs"), ("site", "scripts", "test-grid-render.mjs"), ("docs", "methods", "grid_network.md"),
                      ("tests", "test_session1421.py")):
            self.assertNotIn(EM, src(*parts), parts)
        if os.path.exists(os.path.join(ROOT, "archive", "sessions", "SESSION_1421_REPORT.md")):
            self.assertNotIn(EM, src("archive", "sessions", "SESSION_1421_REPORT.md"))


if __name__ == "__main__":
    unittest.main()
