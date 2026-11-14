"""Session 5423 (chain 261, portable laptop window P1): Grid faults row 5. site/scripts/a11y-axe.mjs ran axe straight after
a page's load, before components/ScrollRegions.tsx had made each scrolling box a stop of the keyboard (it marks them 150
ms after it mounts), so at 390 px it reported scrollable-region-focusable on the Grid's monthly mix table, a box the page
does mark: axe run after a wait found nothing. The script now waits after each load (A11Y_WAIT_MS, default 2000). The
source is read; the run on production is in the session's report.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheReadWaits(unittest.TestCase):
    def test_axe_runs_after_the_wait(self):
        s = src("site", "scripts", "a11y-axe.mjs")
        self.assertIn('const WAIT = Number(process.env.A11Y_WAIT_MS ?? 2000);', s)
        go, wait, axe = s.index("await go(base + p);"), s.index("await sleep(WAIT);"), s.index("await evaluate(AXE")
        self.assertLess(go, wait)
        self.assertLess(wait, axe)
        self.assertRegex(s, r"withBrowser\(async \(\{[^}]*\bsleep\b[^}]*\}\)")
        self.assertIn("A11Y_WAIT_MS=4000 node scripts/a11y-axe.mjs", s)

    def test_the_wait_is_longer_than_the_marking(self):
        regions = src("site", "components", "ScrollRegions.tsx")
        delay = int(re.search(r"setTimeout\(\(\) => markScrollers\(\), (\d+)\)", regions).group(1))
        self.assertLess(delay * 5, 2000)

    def test_the_faults_file_has_the_row(self):
        self.assertRegex(src("docs", "reviews", "grid-faults-2026-11-13.md"), r"\| 5 \|.*scrollable-region-focusable.*\| fixed \(session 5423\) \|")


if __name__ == "__main__":
    unittest.main()
