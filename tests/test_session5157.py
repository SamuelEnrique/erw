"""Session 5157: the old link's retirement (docs/security.md, H1 and L5; rows 3 and 4 of
docs/reviews/security-faults-2026-11-13.md), prepared on a branch of its own.

Energy Research Warehouse (ERW). No network, no model, no build: the source is read.

THIS BRANCH LANDS ONLY ON THE OWNER'S WORD (the ruling's default: after he has used /internal/open once on production).
Once it is on main these tests hold the retirement in place:

    no file of the site reads a token from an address, and none compares the token with === or !==
    GET /internal/unlock opens nothing: 404, no cookie, whatever the address carries
    the form (POST /internal/unlock, the token in the request's body, compared in constant time) is the one door
    the pages that took ?token= open with the internal view's cookie alone

    python -m unittest tests.test_session5157 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def code(text):
    """The text without its comments (a comment may tell the history), line by line (session 5169: a comment of several
    lines is one whose first line begins with its opening mark; a slash and a star inside a string no longer take code
    out with them)."""
    out, inside = [], False
    for line in text.splitlines():
        s = line.strip()
        if inside:
            inside = "*/" not in s
            continue
        if s.startswith(("/*", "{/*")):
            if "*/" not in s:
                inside = True
                continue
            line = line.split("*/", 1)[1]
        line = re.sub(r"\{/\*.*?\*/\}", "", line)
        out.append(re.sub(r"(^|\s)//.*$", "", line))
    return "\n".join(out)


def site_files():
    out = []
    for d in ("app", "lib", "components"):
        for base, _dirs, names in os.walk(os.path.join(SITE, d)):
            out += [os.path.join(base, n) for n in names if n.endswith((".ts", ".tsx"))]
    return sorted(out + [os.path.join(SITE, "proxy.ts")])


def rel(path):
    return os.path.relpath(path, SITE).replace(os.sep, "/")


# A token read from an address, in the forms the site used.
FROM_ADDRESS = (r"""searchParams\.get\(\s*["']token["']\s*\)""", r"\bsp\.token\b", r"""\bone\(\s*["']token["']\s*\)""", r"""\bsp\[\s*["']token["']\s*\]""")
# The token compared in a way that is not constant time.
PLAIN_COMPARE = (r"\btoken\s*[!=]==\s*want\b", r"\bgiven\s*[!=]==\s*token\b", r"\bwant\s*[!=]==\s*token\b")


class NoTokenInAnAddress(unittest.TestCase):
    def test_no_file_reads_a_token_from_an_address(self):
        for f in site_files():
            t = code(open(f, encoding="utf-8").read())
            for pat in FROM_ADDRESS:
                self.assertNotRegex(t, pat, f"{rel(f)} reads a token from an address")

    def test_no_file_compares_the_token_plainly(self):
        for f in site_files():
            t = code(open(f, encoding="utf-8").read())
            for pat in PLAIN_COMPARE:
                self.assertNotRegex(t, pat, f"{rel(f)} compares the token with === or !==")

    def test_no_file_writes_a_token_into_a_link_or_a_form(self):
        for f in site_files():
            t = code(open(f, encoding="utf-8").read())
            self.assertNotRegex(t, r"[?&]token=\$\{", f"{rel(f)} writes a token into an address")
            if rel(f) != "app/internal/open/page.tsx":       # the form's own field, posted in the body
                self.assertNotRegex(t, r"""<input[^>]*name=["']token["']""", f"{rel(f)} carries the token in a form")


class TheOldLink(unittest.TestCase):
    def test_a_get_opens_nothing(self):
        r = src("site", "app", "internal", "unlock", "route.ts")
        get = r[r.index("export async function GET"):r.index("export async function POST")]
        self.assertIn("export async function GET() {", get)          # it is handed no request: nothing of the address can be read
        self.assertIn("status: 404", get)
        self.assertIn('"X-Robots-Tag": "noindex"', get)
        for word in ("cookies.set", "redirect", "process.env", "digest(", "searchParams"):
            self.assertNotIn(word, code(get), word)

    def test_the_form_is_the_door(self):
        r = src("site", "app", "internal", "unlock", "route.ts")
        post = r[r.index("export async function POST"):]
        self.assertIn("sameOrigin(req)", post)
        self.assertIn('form.get("token")', post)
        self.assertIn("sameSecret(given, token)", post)
        self.assertIn("if (raw.length > 2000)", post)
        self.assertIn("res.cookies.set(COOKIE, await digest(token), { httpOnly: true, secure, sameSite: \"lax\", path: \"/\", maxAge: MAX_AGE });", post)
        form = src("site", "app", "internal", "open", "page.tsx")
        self.assertIn('method="post" action="/internal/unlock"', form)


class ThePagesOpenWithTheCookieAlone(unittest.TestCase):
    def test_the_five_pages(self):
        gate = "if (want.length < 24 || !(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();"
        for parts in (("internal", "costs"), ("internal", "ask"), ("internal", "usage"), ("reports", "draft", "ai-gigawatts"), ("reports", "draft", "shape-premium")):
            t = src("site", "app", *parts, "page.tsx")
            self.assertIn(gate, t, parts)
            self.assertNotIn("searchParams", code(t), parts)
            self.assertIn("robots: { index: false, follow: false }", t, parts)

    def test_the_severance_pages_and_the_download(self):
        lib = src("site", "lib", "finder.ts")
        self.assertIn("export async function internalOpen(cookie: string | undefined): Promise<boolean> {", lib)
        self.assertNotIn("tokenOk", lib)
        for parts in (("severance", "finder", "page.tsx"), ("severance", "lease", "real", "page.tsx"), ("severance", "finder", "download", "route.ts")):
            self.assertIn("internalOpen((await cookies()).get(COOKIE)?.value)", src("site", "app", *parts), parts)

    def test_the_check_on_a_build_says_the_link_is_retired(self):
        c = src("site", "scripts", "check-security.mjs")
        self.assertIn('"the old link is retired: the right token in the address gets 404 and no cookie"', c)
        self.assertNotIn("the old link works as it did", c)


class TheRecords(unittest.TestCase):
    def test_the_documents_name_the_form(self):
        g = src("docs", "release-gate.md")
        self.assertIn("The form at `/internal/open`", g)
        self.assertIn("it is retired", g)
        self.assertNotIn("unlock?token=", src("docs", "battery_game_demo.md"))
        s = src("docs", "security.md")
        self.assertIn("session 5157", s)

    def test_no_em_or_en_dash(self):
        for parts in (("tests", "test_session5157.py"), ("site", "app", "internal", "unlock", "route.ts"), ("site", "lib", "finder.ts"), ("docs", "release-gate.md")):
            t = src(*parts)
            self.assertNotIn(chr(0x2014), t, parts)
            self.assertNotIn(chr(0x2013), t, parts)


if __name__ == "__main__":
    unittest.main()
