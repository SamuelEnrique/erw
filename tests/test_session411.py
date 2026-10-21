"""Session 411: Lighthouse on every visitor page at 1280 and 390 px (docs/reviews/performance-2026-10-20.md).

The runner, site/scripts/lighthouse-pages.mjs, reads the 25 addresses of scripts/snapshot-live.mjs and the tool pages
that are not among them, refuses any host but the local one (never production), opens the internal view by the posted
token (never in an address) and sets its cookies for the local host only. The review records the four scores of every
page at both widths, before and after the fixes, and lists what needs a ruling.
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
SCRIPT = os.path.join(SITE, "scripts", "lighthouse-pages.mjs")
DOC = os.path.join(ROOT, "docs", "reviews", "performance-2026-10-20.md")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def node_pages():
    probe = "import('./scripts/lighthouse-pages.mjs').then(m => console.log(JSON.stringify({pages: m.PAGES, cats: m.CATEGORIES, forms: Object.keys(m.FORMS)})))"
    out = subprocess.run(["node", "-e", probe], cwd=SITE, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return json.loads(out.stdout.strip().splitlines()[-1])


@unittest.skipUnless(shutil.which("node"), "node is not on this machine")
class TheRunner(unittest.TestCase):
    def test_every_visitor_page_and_each_tool_page(self):
        got = node_pages()
        pages = got["pages"]
        self.assertEqual(len(pages), len(set(pages)))
        for p in ["/", "/about", "/storage", "/cost-of-power/seller", "/network", "/cost-of-power/battery", "/terms",
                  "/data/methods/storage", "/cost-of-power/battery?grid=caiso&dur=8&strat=dayahead",
                  "/cost-of-power", "/research", "/grid"]:
            self.assertIn(p, pages)
        self.assertEqual(len(pages), 28)
        self.assertEqual(got["cats"], ["performance", "accessibility", "best-practices", "seo"])
        self.assertEqual(sorted(got["forms"]), ["1280", "390"])

    def test_local_build_only(self):
        out = subprocess.run(["node", "scripts/lighthouse-pages.mjs", "https://erw-flame.vercel.app", os.devnull],
                             cwd=SITE, capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 2)
        self.assertIn("local build only", out.stderr)


class TheRunnerSource(unittest.TestCase):
    def test_token_posted_and_cookie_kept_to_the_local_host(self):
        s = read(SCRIPT)
        self.assertIn("unlockPost(base, token)", s)
        self.assertNotIn("extraHeaders", s)
        self.assertNotRegex(s, r"unlock\?token=")
        self.assertIn("domain", s)
        self.assertIn("browser.close()", s)
        self.assertNotIn(chr(0x2014), s)


class TheReview(unittest.TestCase):
    def test_scores_before_and_after_for_every_page(self):
        d = read(DOC)
        self.assertNotIn(chr(0x2014), d)
        for head in ["## Scores before", "## Scores after", "## For Samuel's ruling", "## Fixed"]:
            self.assertIn(head, d)
        pages = node_pages()["pages"] if shutil.which("node") else []
        before = d.split("## Scores before", 1)[1].split("## ", 1)[0]
        for p in pages:
            self.assertIn(f"`{p}`", before, p)
        rows = [r for r in before.splitlines() if r.startswith("| `")]
        self.assertGreaterEqual(len(rows), len(pages))
        for r in rows:
            cells = [c.strip() for c in r.strip("|").split("|")]
            scored = [c for c in cells[1:] if re.fullmatch(r"\d{1,3}", c)]
            self.assertEqual(len(scored), 8, r)  # four scores at each of the two widths


class TheFixes(unittest.TestCase):
    def test_home_link_not_prefetched(self):
        # a prefetch of / carried React's preload of the home page's chart (156 KB) into every page showing the mark
        s = read(os.path.join(SITE, "app", "layout.tsx"))
        self.assertRegex(s, r'<Link href="/" prefetch=\{false\}[^>]*aria-label="ERW, home">')

    def test_chart_of_the_day_takes_its_own_size(self):
        b = read(os.path.join(SITE, "scripts", "build-content.mjs"))
        self.assertIn("function pngSize(file)", b)
        self.assertIn('"IHDR"', b)
        self.assertIn("Object.assign(digestChartRecords[m[1]], pngSize(", b)
        self.assertIn("width?: number; height?: number", read(os.path.join(SITE, "lib", "markdown.ts")))
        p = read(os.path.join(SITE, "app", "page.tsx"))
        self.assertIn("width={today.width ?? 1600} height={today.height ?? 900}", p)
        self.assertNotIn("width={1600} height={900} />", p)

    @unittest.skipUnless(shutil.which("node"), "node is not on this machine")
    def test_png_size_reads_the_header(self):
        charts = os.path.join(ROOT, "docs", "digest", "charts")
        pngs = sorted(f for f in os.listdir(charts) if f.endswith(".png")) if os.path.isdir(charts) else []
        if not pngs:
            self.skipTest("no chart of the day held")
        f = os.path.join(charts, pngs[-1])
        src = read(os.path.join(SITE, "scripts", "build-content.mjs"))
        fn = re.search(r"function pngSize\(file\) \{.*?\n\}", src, re.S).group(0)
        probe = "const fs = require('fs');\n" + fn + "\nconsole.log(JSON.stringify(pngSize(process.argv[1])));"
        out = subprocess.run(["node", "-e", probe, f], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        got = json.loads(out.stdout)
        with open(f, "rb") as h:
            head = h.read(24)
        self.assertEqual(got, {"width": int.from_bytes(head[16:20], "big"), "height": int.from_bytes(head[20:24], "big")})
        self.assertGreater(got["width"], 0)

    def test_unused_imports_gone(self):
        self.assertNotIn("ReactNode", read(os.path.join(SITE, "app", "deals", "v2", "view.tsx")))
        self.assertNotIn("NoData", read(os.path.join(SITE, "components", "grid", "YourGrid.tsx")))
        self.assertNotIn("hrefOf", read(os.path.join(SITE, "components", "mix", "views.tsx")))
        self.assertNotIn("type Fuel", read(os.path.join(SITE, "app", "cost-of-power", "seller", "tables.csv", "route.ts")))


if __name__ == "__main__":
    unittest.main()
