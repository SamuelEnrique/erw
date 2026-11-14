"""Session 5162: the fresh pass of the security review, the usage counts' method note read against the code
(docs/methods/usage_counts.md; docs/reviews/security-faults-2026-11-13.md, "The fresh pass", row 32).

Energy Research Warehouse (ERW). No network, no model, no build: the note, the site's source and the migration are read.

The note is the promise a reader is pointed to from /privacy. Each number and each list in it is held to the code
here, so the note and the code cannot drift apart unseen:

    the four events, in the browser's sender, the server's filter and the database's function
    the path: its form and its 120 characters, in the server and in the database
    the limits: 600 counts an hour from one address, 400 lines a code a day, 200,000 lines a day, 600 characters a body
    the quiet pages, and what silences a count in the browser
    what is never read: the referrer, the query, a cookie of the count's own, the browser's storage

    python -m unittest tests.test_session5162 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def code(text):
    """The text without its comments, line by line (session 5169: a comment of several lines is one whose first line
    begins with its opening mark; a slash and a star inside a string no longer take code out with them)."""
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


NOTE = ("docs", "methods", "usage_counts.md")
MIGRATION = ("warehouse", "supabase", "migrations", "028_security_usage.sql")
EVENTS = ["tool opened", "input changed", "scenario compared", "download"]


class TheNoteAndTheCodeSayTheSame(unittest.TestCase):
    def test_the_four_events(self):
        note = src(*NOTE)
        for e in EVENTS:
            self.assertIn(f"**{e}**", note)
        self.assertIn('export const EVENTS = ["tool opened", "input changed", "scenario compared", "download"] as const;', src("site", "lib", "usagepath.ts"))
        self.assertIn('export type UsageEvent = "tool opened" | "input changed" | "scenario compared" | "download";', src("site", "lib", "usage.ts"))
        self.assertIn("p_event not in ('tool opened', 'input changed', 'scenario compared', 'download')", src(*MIGRATION))

    def test_the_path(self):
        note = src(*NOTE)
        self.assertIn("without a query or a hash, at most 120 characters", note)
        # one leading slash and up to 119 more characters, the same form in the server and in the database
        self.assertIn(r"const SAFE = /^\/[A-Za-z0-9/_.~:%-]{0,119}$/;", src("site", "lib", "usagepath.ts"))
        self.assertIn("p_path !~ '^/[A-Za-z0-9/_.~:%-]{0,119}$'", src(*MIGRATION))
        u = src("site", "lib", "usagepath.ts")
        self.assertIn('const p = raw.split(/[?#]/)[0]', u)                       # the query and the hash are cut before anything else
        self.assertIn('if (p.startsWith("/api/") || p.startsWith("/internal/") || p.startsWith("/_next/")) return null;', u)
        self.assertIn("An address under `/api/`, `/internal/` or `/_next/` is never a page for the count.", note)
        self.assertIn("return entryOf(p) === null ? null : p;", u)                # a page of the release list, or a page under one
        self.assertIn("location.pathname", src("site", "lib", "usage.ts"))

    def test_the_limits(self):
        note = src(*NOTE)
        r = src("site", "app", "api", "usage", "route.ts")
        m = src(*MIGRATION)
        self.assertIn("More than 600 counts in an hour from one address", note)
        self.assertIn('limited(req, "usage", 600, 3600)', r)
        self.assertIn("its body is over 600 characters", note)
        self.assertIn("if (raw.length > 600) return done();", r)
        self.assertIn("More than 400 different lines from one code in a day, or 200,000 lines in a day", note)
        self.assertIn("if mine >= 400 then", m)
        self.assertIn(">= 200000 then", m)

    def test_the_daily_code(self):
        note = src(*NOTE)
        self.assertIn('`v1 = HMAC-SHA256(key = ASK_VISITOR_SALT, "erw-usage\\n" + address + "\\n" + user agent)`', note)
        self.assertIn('return createHmac("sha256", secret).update(`erw-usage\\n${ip}\\n${ua}`).digest("hex");', src("site", "lib", "guard.ts"))
        m = src(*MIGRATION)
        self.assertIn("extensions.gen_random_bytes(32)", m)                       # the day's salt: random, derived from nothing
        self.assertIn("v := substr(encode(extensions.hmac(decode(p_visitor, 'hex'), s, 'sha256'), 'hex'), 1, 32);", m)
        self.assertIn("first 32 hexadecimal characters of HMAC-SHA256(key = today's salt, v1)", note)
        # the day is closed by each of the three functions the note names
        self.assertEqual(m.count("perform erw_private.usage_rollover();"), 3)
        for fn in ("site_rate_admit", "site_usage_record", "internal_usage"):
            body = m[m.index(f"create or replace function public.{fn}("):]
            self.assertIn("perform erw_private.usage_rollover();", body[:body.index("$$;")], fn)

    def test_when_nothing_is_counted(self):
        note = src(*NOTE)
        r = src("site", "app", "api", "usage", "route.ts")
        u = src("site", "lib", "usage.ts")
        self.assertIn('if (req.headers.get("dnt") === "1" || req.headers.get("sec-gpc") === "1") return done();', r)
        self.assertIn('return dnt === "1" || dnt === "yes" || nav.globalPrivacyControl === true;', u)
        self.assertIn('if (!sameOrigin(req) || scripted(req) || !typed(req, "json")) return done();', r)
        self.assertIn('if (!path || !secret || token.length < 24 || ip === "unknown") return done();', r)
        self.assertIn("The server holds no secret to make the code with, or cannot tell the visitor's address", note)
        # the quiet pages the note names are the ones the code holds
        self.assertIn('export const QUIET = ["/battery/customer", "/severance", "/learn/bill"];', u)
        for words in ("`/battery/customer`", "the severance tools", "the bill page", "the contract boxes of the cost-of-power pages"):
            self.assertIn(words, note)
        self.assertIn("export const PROMISE = /sent or stored|never sent|nothing is uploaded/i;", u)

    def test_what_is_never_read(self):
        note = src(*NOTE)
        self.assertIn("Never recorded, in a table or in a log: the IP address, the user agent string, the referrer, a query string, the name or the value of any input, a cookie, an identifier from `localStorage`.", note)
        r = code(src("site", "app", "api", "usage", "route.ts"))
        for word in ("console.", "referer", "referrer", "Set-Cookie"):
            self.assertNotIn(word, r, f"the route names {word}")
        b = code(src("site", "components", "Usage.tsx")) + code(src("site", "lib", "usage.ts"))
        for word in (".value", ".name", "document.cookie", "localStorage", "sessionStorage", "document.referrer", "location.search", "location.hash"):
            self.assertNotIn(word, b, f"the browser's side names {word}")
        self.assertIn('referrerPolicy: "no-referrer"', src("site", "lib", "usage.ts"))

    def test_the_note_says_what_no_tool_sends_and_what_a_check_adds(self):
        note = src(*NOTE)
        self.assertIn("no tool does (read on 13 November 2026, session 5155)", note)
        self.assertIn("**The site's own checks.**", note)
        links = src("site", "scripts", "check-links.mjs")
        self.assertIn('DNT: "1", "Sec-GPC": "1"', links)
        self.assertIn('"*/api/usage*"', links)


class TheRecords(unittest.TestCase):
    def test_the_list(self):
        t = src("docs", "reviews", "security-faults-2026-11-13.md")
        row = [line for line in t.splitlines() if line.startswith("| 32 |")]
        self.assertEqual(len(row), 1)
        self.assertIn("noted", row[0])
        self.assertIn("**Session 5162, the usage counts' method against the code.**", t)

    def test_no_em_or_en_dash(self):
        for parts in (("tests", "test_session5162.py"), NOTE):
            t = src(*parts)
            self.assertNotIn(chr(0x2014), t, parts)
            self.assertNotIn(chr(0x2013), t, parts)


if __name__ == "__main__":
    unittest.main()
