"""Session 5153: row 22 of the security list (docs/reviews/security-faults-2026-11-13.md): the enforced policy allows
inline scripts (script-src 'self' 'unsafe-inline').

Energy Research Warehouse (ERW). No network, no model, no build: the source is read.

Why the word stays (the ruling's default): the only inline scripts on a page are the framework's own (the data it
writes for the page it has rendered), and a nonce for them makes every page render on each request (Next 16.4.5's own
guide, node_modules/next/dist/docs/01-app/02-guides/content-security-policy.md, "Dynamic Rendering Requirement").

What keeps the word from mattering, pinned here: the site's own source writes no script into a page, and no text
reaches a page as markup except through the renderer that escapes it.

    python -m unittest tests.test_session5153 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def site_files():
    out = []
    for d in ("app", "components", "lib"):
        for base, _dirs, names in os.walk(os.path.join(SITE, d)):
            out += [os.path.join(base, n) for n in names if n.endswith((".ts", ".tsx"))]
    return sorted(out)


def rel(path):
    return os.path.relpath(path, SITE).replace(os.sep, "/")


def code(text):
    """The text without its comments (a comment may name what the code must not do)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(re.sub(r"(^|\s)//.*$", "", line) for line in text.splitlines())


# The renderers of site/lib/markdown.ts and what is built on them: each escapes raw HTML and refuses an unsafe link.
RENDERERS = {"render", "renderDigest", "renderRoundup"}


class TheSitesOwnSourceWritesNoScript(unittest.TestCase):
    def test_no_script_element_no_eval(self):
        for f in site_files():
            t = code(open(f, encoding="utf-8").read())
            for pat, what in ((r"<script\b", "a script element"), (r"""from\s+["']next/script["']""", "next/script"), (r"\beval\(", "eval"),
                              (r"new Function\(", "new Function"), (r"document\.write", "document.write"), (r"\bsetTimeout\(\s*[\"'`]", "a timer given text")):
                self.assertNotRegex(t, pat, f"{rel(f)}: {what}")

    def test_the_one_script_the_site_adds_is_the_chart_library_with_its_hash(self):
        makers = [rel(f) for f in site_files() if re.search(r"""createElement\(\s*["']script["']""", code(open(f, encoding="utf-8").read()))]
        self.assertEqual(makers, ["components/echarts.ts"])
        e = src("site", "components", "echarts.ts")
        self.assertRegex(e, r'export const ECHARTS_SRI = "sha384-[A-Za-z0-9+/=]{64}";')
        self.assertIn("s.integrity = ECHARTS_SRI;", e)
        self.assertIn('s.crossOrigin = "anonymous";', e)

    def test_markup_reaches_a_page_only_through_the_renderer(self):
        uses = 0
        for f in site_files():
            t = code(open(f, encoding="utf-8").read())
            for m in re.finditer(r"dangerouslySetInnerHTML", t):
                uses += 1
                got = re.match(r"dangerouslySetInnerHTML=\{\{\s*__html:\s*([A-Za-z_]+)\(", t[m.start():])
                self.assertIsNotNone(got, f"{rel(f)}: markup set from something that is not a call of the renderer")
                self.assertIn(got.group(1), RENDERERS, f"{rel(f)}: markup set by {got.group(1)}(), not one of the renderers")
        self.assertGreaterEqual(uses, 10, "the scan found too few uses to mean anything")

    def test_the_renderer_escapes_and_refuses(self):
        m = src("site", "lib", "markdown.ts")
        self.assertIn('.replace(/</g, "&lt;").replace(/>/g, "&gt;")', m)
        self.assertIn("return SAFE_HTML.some((re) => re.test(raw)) ? raw : escapeHtml(raw);", m)
        self.assertIn('if (!safeHref(t.href)) { t.href = "#"; return; }', m)
        self.assertIn("if (!safeHref(href)) return escapeHtml(text);", m)

    def test_the_one_copy_of_markup_in_a_browser_copies_what_the_server_rendered(self):
        setters = [rel(f) for f in site_files() if re.search(r"\.innerHTML\s*=|\.outerHTML\s*=|insertAdjacentHTML", code(open(f, encoding="utf-8").read()))]
        self.assertEqual(setters, ["components/GateRestore.tsx"])
        self.assertIn("a.innerHTML = s.innerHTML;", src("site", "components", "GateRestore.tsx"))


class ThePolicy(unittest.TestCase):
    def test_the_script_rule_as_it_stands(self):
        c = src("site", "next.config.ts")
        self.assertIn("\"script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com\"", c)
        self.assertNotIn("unsafe-eval", code(c))
        self.assertIn("const CSP_ENFORCED = CSP_FULL;", c)

    def test_the_list_says_the_ruling(self):
        row = [line for line in src("docs", "reviews", "security-faults-2026-11-13.md").splitlines() if line.startswith("| 22 |")]
        self.assertEqual(len(row), 1)
        self.assertIn("**ruling**", row[0])
        self.assertIn("tests/test_session5153.py", row[0])

    def test_no_em_or_en_dash(self):
        t = src("tests", "test_session5153.py")
        self.assertNotIn(chr(0x2014), t)
        self.assertNotIn(chr(0x2013), t)


if __name__ == "__main__":
    unittest.main()
