"""Session 1116 (chain 075): the price board's held rows and stale closes.

Held here: site/scripts/test-board-1116.mjs passes (holdRows makes every row of a grid held for a license on the day
"license needed" in place with no figure and leaves its week rows and spikes out; closeAge's thresholds); the board's
page applies the hold on the server, before the file reaches the browser; the method note states both rules.
No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheBoard(unittest.TestCase):
    def test_the_hold_is_applied_on_the_server(self):
        page = src("site", "app", "board", "page.tsx")
        self.assertNotIn('"use client"', page)
        self.assertIn("const file = holdRows(raw, licenseHeldGrids().map(gridName));", page)
        self.assertIn("<BoardView file={file}", page)

    def test_the_method_note_states_the_rules(self):
        note = src("docs", "methods", "price_board.md")
        self.assertIn("## The held rows and the stale closes (session 1116, 23 October 2026)", note)
        for words in ("past 10 days for a daily series", "17 for a weekly one", "132 for a monthly one", "license needed"):
            self.assertIn(words, note)
        board = src("site", "lib", "board.ts")
        self.assertIn('export const STALE_DAYS: Record<"D" | "W" | "M" | "Q", number> = { D: 10, W: 17, M: 132, Q: 135 };', board)   # Q: session 1135

    def test_the_node_tests(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        for script, want in (("scripts/test-board-1116.mjs", "5 of 5 passed"),):
            r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", script], cwd=SITE,
                               capture_output=True, text=True, timeout=300, encoding="utf-8")
            if r.returncode != 0 and "Unknown file extension" in r.stderr:
                raise unittest.SkipTest("this node does not read TypeScript files")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn(want, r.stdout)


if __name__ == "__main__":
    unittest.main()
