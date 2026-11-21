"""Session 9818 (chain 610, part D): headings that skipped a level or stood twice, found in the pages' HTML read on
20 November 2026 without a browser (docs/reviews/browser-without-2026-11-20.md):

- /data/licenses and /map?tab=resources drew a method note's own h1 under the page's h1: two h1 on one page. The
  renderer now sets such a note's headings one level down (site/lib/markdown.ts, render's `under`).
- /map?tab=queues went from the page's h1 to an h3 ("Every entry year"): it is an h2, drawn as before.

Energy Research Warehouse (ERW). No network, no build: the source is read, and the renderer is run under node when
site/node_modules is there.

    python -m unittest tests.test_session9818 -v
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheHeadings(unittest.TestCase):
    def test_the_renderer_can_set_a_note_one_level_down(self):
        m = src("site", "lib", "markdown.ts")
        self.assertIn("export function render(md: string, repoPath: string, opts: { under?: boolean } = {}): string {", m)
        self.assertIn("return opts.under ? headingsUnder(html) : html;", m)

    def test_the_two_pages_with_their_own_title_use_it(self):
        self.assertIn('render(DOCS.licenses, "docs/licenses.md", { under: true })', src("site", "app", "data", "licenses", "page.tsx"))
        self.assertIn('render(doc, "docs/methods/resources.md", { under: true })', src("site", "app", "resources", "view.tsx"))
        # the method pages themselves draw the note as the page: its h1 is the page's one h1
        self.assertIn("render(md, `docs/methods/${slug}.md`)", src("site", "app", "data", "methods", "[slug]", "page.tsx"))

    def test_the_queues_table_heading_is_an_h2(self):
        t = src("site", "app", "map", "QueuesView.tsx")
        self.assertIn('<h2 className="mb-2 mt-2 font-serif text-lg text-accent">Every entry year', t)
        self.assertNotIn("<h3", t)

    @unittest.skipUnless(shutil.which("node") and os.path.isdir(os.path.join(SITE, "node_modules", "marked")), "node or site/node_modules is not here")
    def test_the_renderer_under_node(self):
        r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "scripts/test-headings-under.mjs"], cwd=SITE,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=300)
        self.assertEqual(r.returncode, 0, (r.stdout or "")[-1500:] + (r.stderr or "")[-1500:])
        self.assertIn("3 passed", r.stdout)


if __name__ == "__main__":
    unittest.main()
