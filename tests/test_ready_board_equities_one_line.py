"""Ready branch for the price board (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.5, "the board's
30 blank rows: drawn, or one line with the count and the reason": the other choice). Not the default: it waits for
Samuel's ruling.

site/lib/equities.ts oneLineEquities, applied on the board's page (site/app/board/page.tsx): while no row of the
equities group holds a figure, the group is one line, "30 segment lines, none held", with each reason and its count;
the rows' download (site/app/board/rows/route.ts) keeps every row. Measured on the files now on main: the group's rows
on the page 30 to 1.

1. scripts/test-ready-board-equities-one-line.mjs on the real files, run by Node.
2. The page, the download and the note."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
REACT = os.path.isdir(os.path.join(SITE, "node_modules", "react"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheBlankRowsAreOneLine(unittest.TestCase):
    @unittest.skipUnless(NODE and REACT, "node or the site's packages are not installed")
    def test_on_the_files(self):
        r = subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", "scripts/test-ready-board-equities-one-line.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = json.loads([ln for ln in r.stdout.splitlines() if ln.startswith("{")][-1])
        self.assertEqual(out["rows_after"], 1)
        self.assertGreater(out["rows_before"], 1)

    def test_the_page_and_the_download(self):
        self.assertIn("const raw = oneLineEquities(withEquities(fileJson as unknown as BoardFile, equitiesBoard()));",
                      src("site", "app", "board", "page.tsx"))
        self.assertNotIn("oneLineEquities", src("site", "app", "board", "rows", "route.ts"))
        self.assertIn("**On the board, while no row holds a figure (session 11408", src("docs", "methods", "equities.md"))


if __name__ == "__main__":
    unittest.main()
