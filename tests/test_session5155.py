"""Session 5155: row 24 of the security list (docs/reviews/security-faults-2026-11-13.md): do the usage counts run only
on the pages the owner's ruling allows ("no usage count on tool pages", 12 October 2026)?

Energy Research Warehouse (ERW). No network, no model, no build: the source is read (the behaviour is tested by
site/scripts/test-usage.mjs, which tests/test_session5102.py runs).

What stands today, pinned: a page that carries the mark (<Brand noUsage>) sends its page view and nothing after it; the
browser's component asks the mark before every count but the page view. What the setting adds: with
USAGE_TOOL_PAGES=off the server records nothing for such a page. The server's list of those pages is held to the page
files here.

    python -m unittest tests.test_session5155 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP = os.path.join(ROOT, "site", "app")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def marked_pages():
    """The address of every page file, outside the internal view, whose whole page carries the mark."""
    out = []
    for base, _dirs, names in os.walk(APP):
        if "page.tsx" not in names:
            continue
        route = "/" + os.path.relpath(base, APP).replace(os.sep, "/")
        route = "/" if route == "/." else route
        if route.startswith("/internal") or "[" in route:
            continue
        if "<Brand noUsage>" in open(os.path.join(base, "page.tsx"), encoding="utf-8").read():
            out.append(route)
    return sorted(out)


def no_count():
    m = re.search(r"export const NO_COUNT = \[([^\]]*)\];", src("site", "lib", "usagepath.ts"))
    return re.findall(r'"([^"]+)"', m.group(1))


class TheServersListIsThePagesMark(unittest.TestCase):
    def test_the_list_equals_the_marked_page_files(self):
        self.assertEqual(no_count(), marked_pages(),
                         "a page gained or lost <Brand noUsage>: bring NO_COUNT in site/lib/usagepath.ts up to date (and the node test's lines)")

    def test_the_list_is_matched_exactly(self):
        self.assertIn("export const noCount = (path: string) => NO_COUNT.includes(path);", src("site", "lib", "usagepath.ts"))

    def test_the_marked_pages_are_the_ones_the_ruling_was_made_for(self):
        marked = marked_pages()
        for page in ("/cost-of-power", "/cost-of-power/battery", "/cost-of-power/seller"):
            self.assertIn(page, marked)


class TheSetting(unittest.TestCase):
    def test_the_route_drops_a_marked_page_only_under_the_setting(self):
        r = src("site", "app", "api", "usage", "route.ts")
        line = "if (usageToolPagesOff() && noCount(path)) return done();"
        self.assertIn(line, r)
        # after the path is known to be a page of this site, before the limit is counted and the database is asked
        self.assertLess(r.index("const path = cleanPath(body.path);"), r.index(line))
        self.assertLess(r.index(line), r.index('limited(req, "usage", 600, 3600)'))
        self.assertLess(r.index('limited(req, "usage", 600, 3600)'), r.index('rpc("site_usage_record"'))

    def test_the_setting_is_one_word_and_off_by_default(self):
        g = src("site", "lib", "guard.ts")
        self.assertIn('return (env.USAGE_TOOL_PAGES ?? "").trim().toLowerCase() === "off";', g)
        t = src("site", "scripts", "test-usage.mjs")
        self.assertIn("guard.usageToolPagesOff({}), false", t)
        self.assertIn('guard.usageToolPagesOff({ USAGE_TOOL_PAGES: "off" }), true', t)


class TheBrowsersSide(unittest.TestCase):
    def test_nothing_after_the_page_view_on_a_marked_page(self):
        u = src("site", "components", "Usage.tsx")
        self.assertIn('if (t.closest("[data-no-usage]")) return true;', u)
        # both handlers ask before they count
        self.assertIn("|| silent(t)) return;", u)
        self.assertIn("if (!a || silent(a)) return;", u)
        # the page view is the one count sent without asking
        self.assertEqual(len(re.findall(r"\btrack\(", u)), 3)
        self.assertIn('track("tool opened");', u)

    def test_the_mark_is_written_by_the_wrapper(self):
        b = src("site", "components", "Brand.tsx")
        self.assertIn('data-no-usage={noUsage ? "1" : undefined}', b)

    def test_no_tool_sends_a_count_of_its_own(self):
        # "scenario compared" is a count a tool would send itself; none does, so the browser's component is the one sender
        hits = []
        for d in ("app", "components"):
            for base, _dirs, names in os.walk(os.path.join(ROOT, "site", d)):
                for n in names:
                    if n.endswith((".ts", ".tsx")) and n != "Usage.tsx":
                        if re.search(r"""\btrack\(\s*["']""", open(os.path.join(base, n), encoding="utf-8").read()):
                            hits.append(os.path.relpath(os.path.join(base, n), ROOT).replace(os.sep, "/"))
        self.assertEqual(hits, [], "a tool now sends a count itself: is it inside a marked page?")


class TheRecords(unittest.TestCase):
    def test_the_list_the_note_and_the_state_file(self):
        row = [line for line in src("docs", "reviews", "security-faults-2026-11-13.md").splitlines() if line.startswith("| 24 |")]
        self.assertEqual(len(row), 1)
        self.assertIn("**ruling**", row[0])
        self.assertIn("USAGE_TOOL_PAGES=off", row[0])
        self.assertIn("USAGE_TOOL_PAGES=off", src("docs", "methods", "usage_counts.md"))
        self.assertIn("## The usage counts and the pages the ruling allows", src("docs", "security.md"))

    def test_no_em_or_en_dash(self):
        for parts in (("tests", "test_session5155.py"), ("site", "lib", "usagepath.ts"), ("site", "lib", "guard.ts"), ("site", "app", "api", "usage", "route.ts")):
            t = src(*parts)
            self.assertNotIn(chr(0x2014), t, parts)
            self.assertNotIn(chr(0x2013), t, parts)


if __name__ == "__main__":
    unittest.main()
