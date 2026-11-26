"""Audit of the Digest and the Roundup, finding 1 (session 10235, docs/reviews/digest-model-audit-2026-11-26.md): the
Roundup's index page, /roundup, drew the newest Roundup with lib/markdown.ts render, not renderRoundup, so the hold of a
licence-held grid that /roundup/<week> applies (rows 94 and 108 of docs/reviews/periodicals-faults-2026-11-05.md) did
not reach it: W45's NYISO 40.90 and ISO-NE 40.28 stood on /roundup while /roundup/2026-W45 held them. The source trail
and the fold were missing there too.

1. The index draws the newest Roundup with renderRoundup. Fails on main.
2. Through the site's own library (Node with the site's loaders): renderRoundup's hold takes both figures out of the
   stored W45. Passes on main and on the branch."""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheRoundupIndexHoldsAsTheWeekPageDoes(unittest.TestCase):
    def test_the_index_draws_with_render_roundup(self):
        page = src("site", "app", "roundup", "page.tsx")
        self.assertIn("renderRoundup(DOCS.weeklies[newest], DOCS.weekly_source[newest])", page)
        self.assertIsNone(re.search(r"[^p]render\(DOCS\.weeklies", page))

    def test_render_roundup_holds_the_held_grids(self):
        self.assertIn("render(holdRoundupGrids(md), repoPath)", src("site", "lib", "markdown.ts"))

    @unittest.skipUnless(NODE, "node is not installed")
    @unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
    def test_the_hold_takes_w45s_held_cells_out(self):
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-audit-digest-1.mjs"], cwd=SITE,
                           capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(out["stored"], [True, True])
        self.assertEqual(out["drawn"], [False, False])


if __name__ == "__main__":
    unittest.main()
