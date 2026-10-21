"""Session 408: every page that shows a warehouse figure is read by check-values (chain 015, 21 October 2026).

Energy Research Warehouse (ERW). site/scripts/check-values.mjs reads a list of addresses and compares each number a
page draws through components/Num.tsx with Supabase. This test holds that list against the routes under site/app/:
a route whose page shows a warehouse figure must be in it, or in EXEMPT below with the reason it is not.

The rule, decided by code (the chain's words: "a page whose code renders a Num with a check key or reads Supabase
through lib/supabase.ts"):

- a route is a folder of site/app/ (outside _retired) that holds a page.tsx; its address is the folder's path, a
  [segment] matching any one segment of an address;
- the page's code is its page.tsx and every file of the site it imports, followed through imports ("@/..." and
  relative ones; a layout is not the page's code);
- it shows a warehouse figure when that code holds a "<Num ... check=" (followed through every file), or when it
  reaches lib/supabase.ts through app/ and lib/ files (a shared component's own read, such as the citation's dates
  or the download buttons, is the component's, not the page's figure);
- it is read when some address of the list (its path, the query set aside) matches the route.

The list is the script's own (`node scripts/check-values.mjs --list`, which stops before any request), so a page a
later session adds, in the literal list or with PAGES.push, is seen as the script reads it. Nothing here sets the
environment, reads a table or makes a request.
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
APP = os.path.join(SITE, "app")
COMPONENTS = os.path.join(SITE, "components") + os.sep
SUPABASE = os.path.normpath(os.path.join(SITE, "lib", "supabase.ts"))
CODE = (".ts", ".tsx", ".js", ".mjs")
RESOLVE = ["", ".ts", ".tsx", ".js", ".mjs", "/index.ts", "/index.tsx"]
IMPORT = re.compile(r"""(?:import|export)\s[^;]*?from\s+["']([^"']+)["']|import\s*\(\s*["']([^"']+)["']\s*\)|import\s+["']([^"']+)["']""", re.S)
NUM = re.compile(r"<Num\b[^>]*\bcheck=")

# The routes that show a figure by the rule and are not read, each with its reason (session 408). A route here must
# still exist, must still show a figure by the rule, and must not be in the list: an exemption that no longer holds fails.
EXEMPT = {
    "/internal/ask": "the internal view's ledger of Ask questions (the site's own table), not a warehouse figure",
    "/internal/costs": "the internal view's model spend (the site's own ledger), not a warehouse figure",
    "/internal/health": "the internal view's run health (the runs' own records), not a figure a reader reads",
    "/internal/usage": "the internal view's usage counts (the site's own ledger), not a warehouse figure",
    "/internal/waits": "the internal view's list of what waits for the owner, not a warehouse figure",
    "/internal/findings": "draft finding cards waiting for review; a card's figures are read once it is published, on /research and /research/card/<id>",
    "/thesis": "internal (the Thesis Builder): the runs of its own tables, checked by scripts/check-thesis.mjs",
    "/severance/lease/real": "internal: the RRC lease table lives on a warehouse machine, not on the site's server; its prices go to the client lease tool, which draws no Num",
    "/learn/problems": "the index of the problem sets: it imports lib/problems.ts for the sets' titles and draws no figure",
    "/learn/problems/[slug]/[edition]": "a dated edition: its numbers are the day's, from a file (lib/problemEditions.ts), not the live table's",
    "/learn/problems/[slug]/[edition]/teacher": "a dated edition's teacher copy: the day's numbers from a file (lib/problemEditions.ts), not the live table's",
}


def resolve(frm, spec):
    if spec.startswith("@/"):
        base = os.path.join(SITE, spec[2:])
    elif spec.startswith("."):
        base = os.path.normpath(os.path.join(os.path.dirname(frm), spec))
    else:
        return None
    for ext in RESOLVE:
        f = base + ext
        if os.path.isfile(f) and f.endswith(CODE):
            return os.path.normpath(f)
    return None


_DEPS = {}
_TEXT = {}


def text(f):
    if f not in _TEXT:
        with open(f, encoding="utf-8") as h:
            _TEXT[f] = h.read()
    return _TEXT[f]


def deps(f):
    if f not in _DEPS:
        out = set()
        for m in IMPORT.finditer(text(f)):
            r = resolve(f, m.group(1) or m.group(2) or m.group(3))
            if r:
                out.add(r)
        _DEPS[f] = out
    return _DEPS[f]


def closure(start, through_components):
    seen, todo = set(), [start]
    while todo:
        f = todo.pop()
        if f in seen:
            continue
        seen.add(f)
        for g in deps(f):
            if through_components or not g.startswith(COMPONENTS):
                todo.append(g)
    return seen


def routes():
    """{route: (renders a Num with a check key, reads Supabase)} for every page under site/app/."""
    out = {}
    for d, _, files in os.walk(APP):
        if "page.tsx" not in files:
            continue
        rel = os.path.relpath(d, APP).replace("\\", "/")
        if rel.split("/")[0] == "_retired":
            continue
        page = os.path.normpath(os.path.join(d, "page.tsx"))
        num = any(NUM.search(text(f)) for f in closure(page, True))
        supa = SUPABASE in closure(page, False)
        out["/" if rel == "." else "/" + rel] = (num, supa)
    return out


def shows_a_figure():
    return sorted(r for r, (num, supa) in routes().items() if num or supa)


def matches(route, address):
    want = [s for s in route.split("/") if s]
    got = [s for s in address.split("?")[0].split("/") if s]
    return len(want) == len(got) and all((w.startswith("[") and w.endswith("]")) or w == g for w, g in zip(want, got))


def listed():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "scripts/check-values.mjs", "--list"], cwd=SITE, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    got = json.loads(r.stdout.strip().splitlines()[-1])
    return got["pages"] + got["internal"]


class TheRule(unittest.TestCase):
    def test_the_rule_sees_what_it_should(self):
        rs = routes()
        # a page that draws Num with its keys; a page whose lib reads Supabase; a page of words only
        self.assertTrue(rs["/cost-of-power/battery"][0])
        self.assertTrue(rs["/contracts"][1])
        self.assertEqual(rs["/terms"], (False, False))
        # a shared component's own read is not the page's: the faults page reaches lib/supabase.ts only through the citation
        self.assertFalse(rs["/data/faults"][1])
        # a dynamic route keeps its brackets
        self.assertIn("/prices/[entity]", rs)

    def test_the_address_match(self):
        self.assertTrue(matches("/prices/[entity]", "/prices/ercot%3AHB_HUBAVG"))
        self.assertTrue(matches("/grid", "/grid?grid=ercot&view=clean"))
        self.assertTrue(matches("/", "/"))
        self.assertFalse(matches("/", "/board"))
        self.assertFalse(matches("/cost-of-power/battery", "/cost-of-power/battery/awards"))


class EveryRouteIsRead(unittest.TestCase):
    def test_a_route_that_shows_a_figure_is_read_or_exempt(self):
        addresses = listed()
        missing = [r for r in shows_a_figure() if r not in EXEMPT and not any(matches(r, a) for a in addresses)]
        self.assertEqual(missing, [], "routes that show a warehouse figure and are not in site/scripts/check-values.mjs "
                                      "(add an address of each to PAGES, or to EXEMPT here with its reason)")

    def test_each_exemption_still_holds(self):
        addresses = listed()
        figure = set(shows_a_figure())
        for r, why in EXEMPT.items():
            self.assertIn(r, figure, f"{r} no longer shows a figure by the rule (or no longer exists): take it out of EXEMPT")
            self.assertFalse(any(matches(r, a) for a in addresses), f"{r} is read by check-values now: take it out of EXEMPT")
            self.assertGreater(len(why), 20)

    def test_the_two_pages_added_here_are_read_with_a_floor(self):
        addresses = listed()
        with open(os.path.join(SITE, "scripts", "check-values-floor.json"), encoding="utf-8") as f:
            floor = json.load(f)["floor"]
        for page in ("/contracts", "/cost-of-power/battery/awards"):
            self.assertIn(page, addresses)
            self.assertIn(page, floor)

    def test_no_address_is_read_twice(self):
        addresses = listed()
        self.assertEqual(sorted(a for a in set(addresses) if addresses.count(a) > 1), [])


class TheScript(unittest.TestCase):
    def test_the_list_mode_stops_before_any_variable_or_request(self):
        with open(os.path.join(SITE, "scripts", "check-values.mjs"), encoding="utf-8") as f:
            cv = f.read()
        stop = cv.index('if (process.argv[2] === "--list")')
        self.assertLess(stop, cv.index('const origin = new URL(env("SUPABASE_URL")).origin;'))
        self.assertGreater(stop, cv.index("const INTERNAL = ["))
        self.assertIn('PAGES.push("/contracts", "/cost-of-power/battery/awards");', cv)
        self.assertIn("has no floor in scripts/check-values-floor.json", cv)


if __name__ == "__main__":
    unittest.main()
