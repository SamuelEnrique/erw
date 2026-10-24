"""Session 168, part A: version 3 is the network page (/network); /network/v3 redirects to it; the old page is retired.

The owner's instruction of 8 October 2026: serve version 3 at /network, redirect /network/v3, move the old page to
site/app/_retired/network-original; carry over the "Newest hour ... Demand of the seven ISOs" line and MISO's panel
reading "paused while terms are reviewed"; move the folded sections of both pages to docs/methods/grid_network.md; keep
the one source line. Asserts on file contents only (no branch comparison); the browser checks are
site/scripts/check-network-v3.mjs and check-network-v3-hard.mjs against a served build.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


MOVED = ["Who supplies each ISO grid: three measures", "What this is, and what it is not", "How fresh each layer is",
         "The replay: what a day is", "Prices, and what the ring does not say", "Trace the power: what it is, and what it is not"]


class OneAddress(unittest.TestCase):
    def test_version_3_stands_at_network_and_the_old_page_is_retired(self):
        page = src("site", "components", "grid", "NetworkView.tsx")  # session 237: the page is a view of the Grid tool (/grid); its file moved to site/components/grid
        self.assertIn("v3={{ index, complete }}", page)
        # session 237: the title "The grid network" was the page's own; the page is the Network view of the Grid tool now,
        # whose title names the grid in view (site/app/grid/page.tsx generateMetadata)
        self.assertIn("export async function NetworkView(", page)
        # session 1151: the view also takes the grid in view, whose keyed figures it draws under the component
        # session 1170: and the replayed day the address names, whose figures it draws from the replay's daily file
        self.assertIn('{view === "network" ? <NetworkView keep={keep} node={p.node} grid={grid}', src("site", "app", "grid", "page.tsx"))
        self.assertIn('{view === "network" ? <NetworkView keep={keep} node={p.node} grid={grid} day={p.day} /> : null}', src("site", "app", "grid", "page.tsx"))
        self.assertFalse(os.path.exists(os.path.join(ROOT, "site", "app", "network", "v3", "page.tsx")))
        old = src("site", "app", "_retired", "network-original", "page.tsx")
        self.assertIn("<Network snap={snap} supply={supply} live={extras} />", old)
        self.assertIn('from "@/app/network/Network"', old)

    def test_the_old_address_redirects_and_keeps_its_status_line(self):
        self.assertIn('{ source: "/network/v3", destination: "/grid?view=network", permanent: true }', src("site", "next.config.ts"))   # session 237, the finishing pass: in one step to the Network view of /grid (it went to /network, which redirects there)
        self.assertRegex(src("site", "lib", "release.ts"), r'"/network/v3":\s*"review"')
        self.assertNotIn('"/network/v3"', src("site", "lib", "audience.ts"))
        self.assertNotIn('page="/network/v3"', src("warehouse", "scheduled.py"))

    def test_the_line_carried_over_and_the_one_source_line(self):
        page = src("site", "components", "grid", "NetworkView.tsx")  # session 237: the page is a view of the Grid tool (/grid); its file moved to site/components/grid
        self.assertIn("Newest hour: {both(newest)}, refreshed {utc(snap.built)}", page)
        # also covered by site/scripts/test-grid-render.mjs: view_gravity on /grid?grid=ercot&view=gravity
        self.assertIn("Demand of the seven ISOs: newest hour {both(demandTs)}.", page)
        self.assertEqual(page.count("<SourceLine "), 1)
        self.assertNotIn("<Fold", page)
        self.assertNotIn("CaisoBreakNote", page)
        face = "\n".join(line for line in page.splitlines() if not line.lstrip().startswith("//"))   # the header comment names them; the page does not
        for title in MOVED:
            self.assertNotIn(title, face)

    def test_miso_reads_the_fixed_words_with_the_reason_on_hover(self):
        comp = src("site", "app", "network", "Network.tsx")
        self.assertIn("data-price-paused={pick.id} title={PAUSED_PRICE[pick.id]}", comp)
        self.assertIn(">{PAUSED_WORDS}</span>", comp)
        self.assertIn('export const PAUSED_WORDS = "paused while terms are reviewed";', src("site", "lib", "networkV3.ts"))

    def test_the_moved_text_is_in_the_method_note_under_headings_that_say_where_it_stood(self):
        note = src("docs", "methods", "grid_network.md")
        self.assertIn("## What stood on the page face until session 168", note)
        heads = re.findall(r"^### (.+)$", note, flags=re.M)
        for title in MOVED:
            self.assertTrue(any(title in h and ("old page" in h or "version 3" in h) for h in heads), title)
        self.assertTrue(any("California data-break note" in h for h in heads))
        self.assertTrue(any("the line under its folds" in h for h in heads))
        for words in ("MISO has no ring: it is paused.", "A day the record confirms is kept.", "Nothing is traced through Mexico.", "| CAISO | 16.84 percent"):
            self.assertIn(words, note)

    def test_no_em_dash(self):
        for parts in (("site", "components", "grid", "NetworkView.tsx"), ("site", "app", "_retired", "network-original", "page.tsx"), ("site", "app", "network", "Network.tsx"),  # session 237: the page is a view of the Grid tool (/grid); its file moved to site/components/grid
                      ("docs", "methods", "grid_network.md"), ("docs", "methods", "grid_network_v3.md"), ("site", "scripts", "check-network-v3.mjs"),
                      ("site", "scripts", "check-network-v3-hard.mjs"), ("tests", "test_session168_network.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts[-1])


if __name__ == "__main__":
    unittest.main()
