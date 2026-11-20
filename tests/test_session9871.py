"""Session 9871 (chain 610, part E): the five pages with the fewest tests, drawn to HTML with the site's own code and
read as a reader, a screen reader and a checker would: /ai-energy, /industry, /queues/places, /storage/places and
/curtailment/where-when (site/scripts/test-reader-pages-render.mjs). Each draws without an error, has one h1 and no
skipped heading level, names every button, gives every tip its one target and every table a caption; /ai-energy's
three headline figures are the file's own counts.

Energy Research Warehouse (ERW). No network, no build: runs under node where site/node_modules is (the drawing needs
react-dom), and is skipped elsewhere.

    python -m unittest tests.test_session9871 -v
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
PAGES = ["/ai-energy", "/industry", "/queues/places", "/storage/places", "/curtailment/where-when", "/states", "/conditions", "/congestion", "/attention", "/deals/capital"]


class TheFivePages(unittest.TestCase):
    def test_the_script_names_the_five_pages(self):
        with open(os.path.join(SITE, "scripts", "test-reader-pages-render.mjs"), encoding="utf-8") as f:
            t = f.read()
        for p in PAGES:
            self.assertIn(f'["{p}", "../app{p}/page.tsx"]', t)

    @unittest.skipUnless(shutil.which("node") and os.path.isdir(os.path.join(SITE, "node_modules", "react-dom")), "node or site/node_modules is not here")
    def test_drawn_and_read(self):
        r = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/test-reader-pages-render.mjs"], cwd=SITE,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=600)
        self.assertEqual(r.returncode, 0, (r.stdout or "")[-2500:] + (r.stderr or "")[-1500:])
        last = [line for line in r.stdout.splitlines() if line.endswith("passed")][-1]
        got, of = last.split(" passed")[0].split(" of ")
        self.assertEqual(got, of)
        self.assertGreaterEqual(int(of), 74)


if __name__ == "__main__":
    unittest.main()
