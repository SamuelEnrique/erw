"""Session 9812 (chain 610, part B): every try of the internal token from one address is counted, right or wrong, at
each door that takes the token from an address or a form (site/lib/guard.ts, TOKEN_TRIES; docs/security.md, T1).

Energy Research Warehouse (ERW). No network, no model, no build: the source is read, and the guard is run under node.

    python -m unittest tests.test_session9812 -v
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
APP = os.path.join(SITE, "app")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


PAGES = ["internal/ask", "internal/costs", "internal/usage", "reports/draft/ai-gigawatts", "reports/draft/shape-premium", "severance/finder"]
PAGE_LINE = "  if (token && !(await pageTokenTriesLeft(await headers()))) notFound();"


class EveryDoorCountsItsTries(unittest.TestCase):
    def test_the_guard(self):
        g = src("site", "lib", "guard.ts")
        self.assertIn("export const TOKEN_TRIES = 30;", g)
        self.assertIn('return (await limited(req, "token_tries", TOKEN_TRIES, 3600)).ok;', g)

    def test_each_page_counts_before_it_compares(self):
        for p in PAGES:
            t = src("site", "app", *p.split("/"), "page.tsx")
            self.assertIn(PAGE_LINE, t, p)
            compare = t.index("internalOpen(token" if p == "severance/finder" else "token !== want")
            self.assertLess(t.index(PAGE_LINE), compare, p)

    def test_the_unlock_doors_count_before_they_compare(self):
        r = src("site", "app", "internal", "unlock", "route.ts")
        get, post = r.split("export async function POST")
        self.assertLess(get.index(".tokenTriesLeft(req)"), get.index("given !== token"))
        self.assertLess(post.index('if (given !== "" && !(await tokenTriesLeft(req))) return back("wait");'), post.index("sameSecret(given, token)"))

    def test_the_finder_download_counts(self):
        t = src("site", "app", "severance", "finder", "download", "route.ts")
        self.assertLess(t.index("!(await tokenTriesLeft(req))"), t.index("internalOpen("))

    def test_every_door_that_reads_a_token_from_the_address_is_listed(self):
        doors = []
        for base, dirs, names in os.walk(APP):
            dirs[:] = [d for d in dirs if d != "_retired"]
            for n in names:
                if n in ("page.tsx", "route.ts"):
                    t = open(os.path.join(base, n), encoding="utf-8").read()
                    if re.search(r'sp\.token\b|searchParams\.get\("token"\)', t):
                        doors.append(os.path.relpath(os.path.join(base, n), APP).replace(os.sep, "/"))
        want = sorted([f"{p}/page.tsx" for p in PAGES] + ["internal/unlock/route.ts", "severance/finder/download/route.ts"])
        self.assertEqual(sorted(doors), want)

    @unittest.skipUnless(shutil.which("node"), "node is not on this machine")
    def test_the_guard_under_node(self):
        r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "scripts/test-token-tries.mjs"], cwd=SITE,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=300)
        self.assertEqual(r.returncode, 0, (r.stdout or "")[-1500:] + (r.stderr or "")[-1500:])
        self.assertIn("3 passed", r.stdout)


if __name__ == "__main__":
    unittest.main()
