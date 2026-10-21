"""Session 428 (chain 021's "session 420", renumbered: 420 was taken): the performance items session 411 left for
session 401's files (docs/reviews/performance-2026-10-20.md, "For session 401").

- the unused values of /cost-of-power's files are gone (METHOD in GridsView.tsx; one, usd and flat in LoadAnswers.tsx);
- the research page writes the chart of the day at its own size, as the home page does;
- the 3D network's chunk (3d-force-graph with three.js) is fetched only once its frame is on screen or near it;
- the shared ScrollRegions reads every box's size before it writes any attribute (one layout, not one a box);
- docs/tooling.md says that chrome-devtools-mcp's lighthouse_audit cannot score performance.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")


def read(*p):
    with open(os.path.join(*p), encoding="utf-8") as f:
        return f.read()


class TheUnusedValues(unittest.TestCase):
    def test_gone_from_the_cost_of_power_files(self):
        grids = read(SITE, "app", "cost-of-power", "GridsView.tsx")
        self.assertNotIn("const METHOD =", grids)
        answers = read(SITE, "app", "cost-of-power", "LoadAnswers.tsx")
        for gone in ("const one = (v: number)", "const usd = (v: number)", "const flat = s.flatUsd * a.mw;"):
            self.assertNotIn(gone, answers)
        # what the page draws still uses the shared formatter
        self.assertIn("usdShort(v)", answers)


class TheResearchChart(unittest.TestCase):
    def test_written_at_its_own_size(self):
        p = read(SITE, "app", "research", "page.tsx")
        self.assertIn("width={today.width ?? 1600} height={today.height ?? 900}", p)
        self.assertNotIn("width={1600} height={900}", p)


class TheNetworkScene(unittest.TestCase):
    def test_its_chunk_waits_for_the_frame(self):
        n = read(SITE, "app", "network", "Network.tsx")
        self.assertIn('const load = () => Promise.all([import("3d-force-graph"), import("three")])', n)
        self.assertIn("new IntersectionObserver(", n)
        self.assertIn('rootMargin: "200px 0px"', n)
        self.assertIn("seen.observe(el);", n)
        # a browser without the observer loads at once, and the clean-up stops the observer
        self.assertIn('if (typeof IntersectionObserver === "undefined") load();', n)
        self.assertIn("seen?.disconnect(); window.removeEventListener", n)
        # loaded in one place only: the scene's import is not reached any other way
        self.assertEqual(len(re.findall(r'import\("3d-force-graph"\)', n)), 1)
        # the map's shape still loads nothing for the scene (session 180)
        self.assertIn('if (shape !== "network"', n)


class TheScrollRegions(unittest.TestCase):
    def test_reads_before_it_writes(self):
        c = read(SITE, "components", "ScrollRegions.tsx")
        body = c[c.index("export function markScrollers"):c.index("export function ScrollRegions")]
        read_at = body.index("el.scrollWidth > el.clientWidth + 1")
        first_write = body.index("el.tabIndex = 0;")
        self.assertLess(read_at, first_write)
        # the reads are one pass over every box, before the pass that writes
        self.assertIn("const boxes = [...root.querySelectorAll<HTMLElement>(SCROLLERS)].map(", body)
        self.assertIn("boxes.forEach(({ el, scrolls }) => {", body)
        self.assertEqual(body.count("el.scrollWidth"), 1)

    def test_no_pass_inside_the_effect_itself(self):
        c = read(SITE, "components", "ScrollRegions.tsx")
        effect = c[c.index("export function ScrollRegions"):]
        # the first pass is the settled one (soon, 150 ms), not a synchronous read while the page is laid out
        self.assertNotIn("    markScrollers();", effect)
        self.assertIn("t = setTimeout(() => markScrollers(), 150);", effect)
        self.assertIn("    soon();", effect)


class TheToolingLine(unittest.TestCase):
    def test_lighthouse_audit_named(self):
        t = read(ROOT, "docs", "tooling.md")
        self.assertIn("chrome-devtools-mcp's `lighthouse_audit` leaves out performance and cannot score it", t)
        self.assertIn("site/scripts/lighthouse-pages.mjs", t)


class NoDashes(unittest.TestCase):
    def test_no_em_or_en_dash_in_what_this_session_wrote(self):
        for p in [os.path.abspath(__file__), os.path.join(ROOT, "archive", "sessions", "SESSION_428_REPORT.md")]:
            if not os.path.exists(p):
                continue
            s = read(p)
            self.assertNotIn(chr(0x2014), s, p)
            self.assertNotIn(chr(0x2013), s, p)
        t = read(ROOT, "docs", "tooling.md")
        line = [l for l in t.splitlines() if "session 428" in l]
        self.assertTrue(line)
        for l in line:
            self.assertNotIn(chr(0x2014), l)
            self.assertNotIn(chr(0x2013), l)


if __name__ == "__main__":
    unittest.main()
