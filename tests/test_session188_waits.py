"""Session 188: the page of what waits for the owner (/internal/waits; site/scripts/build-waits.mjs).

Energy Research Warehouse (ERW). What is held to:

  the reader of the reports (site/scripts/test-waits.mjs, run here): what counts as waiting, in the report's own words
    with its line, reports after the last one answered only, newest first, a report with nothing waiting not listed,
    and a marker that cannot be read hiding nothing;
  the marker archive/sessions/LAST_ANSWERED is two lines a person edits, and names a report that exists;
  the page checks the internal cookie as /internal/findings does, takes no token in its address, is not indexed, has
    no line in the release list, and is linked from nothing a visitor is sent;
  the file the page reads is written before every build and is not in git, as the documents' file is.

No request, no model call; the environment is read, never set. The test that needs node skips when it is absent.

    python -m unittest tests.test_session188_waits -v
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
PAGE = ("site", "app", "internal", "waits", "page.tsx")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheReader(unittest.TestCase):
    def test_the_node_cases_hold(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("no node on this machine")
        r = subprocess.run([node, os.path.join("site", "scripts", "test-waits.mjs")], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=180)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])
        self.assertRegex(r.stdout, r"test-waits: (\d+) of \1 held")

    def test_the_reader_needs_no_package_and_cannot_fail_a_build(self):
        s = src("site", "scripts", "build-waits.mjs")
        imports = re.findall(r'^import .* from "([^"]+)";$', s, re.M)
        self.assertEqual(sorted(imports), ["node:fs", "node:path", "node:url"])
        self.assertNotIn("process.exit", s, "an internal page's file never fails the site's build")
        self.assertIn("unread", s)
        self.assertNotIn("fetch(", s)
        self.assertNotIn(EM, s)

    def test_it_runs_before_every_build_and_its_file_is_not_in_git(self):
        scripts = json.loads(src("site", "package.json"))["scripts"]
        for name in ("prebuild", "predev", "content"):
            self.assertEqual(scripts[name], "node scripts/build-content.mjs && node scripts/build-waits.mjs", name)
        self.assertIn("/content/waits.json", src("site", ".gitignore").splitlines())
        self.assertIn('import waits from "@/content/waits.json";', src("site", "lib", "waits.ts"))
        self.assertIn('import "server-only";', src("site", "lib", "waits.ts"))


class TheMarker(unittest.TestCase):
    def test_it_is_two_lines_a_person_edits_and_names_a_report_that_exists(self):
        lines = [ln.strip() for ln in src("archive", "sessions", "LAST_ANSWERED").splitlines()]
        notes = [ln for ln in lines if ln.startswith("#")]
        held = [ln for ln in lines if ln and not ln.startswith("#")]
        self.assertGreaterEqual(len(notes), 3, "the file says what it is and how to edit it")
        self.assertEqual(len(held), 2)
        m = re.fullmatch(r"last_answered: (\d+[a-z]?)", held[0])
        self.assertIsNotNone(m, held[0])
        self.assertRegex(held[1], r"^on: \d{4}-\d{2}-\d{2}$")
        self.assertTrue(os.path.exists(os.path.join(ROOT, "archive", "sessions", f"SESSION_{m.group(1).upper()}_REPORT.md")))
        self.assertNotIn(EM, "\n".join(lines))

    def test_the_marker_is_not_taken_for_a_report(self):
        self.assertIsNone(re.fullmatch(r"SESSION_\d+[A-Za-z]?_REPORT\.md", "LAST_ANSWERED"))
        self.assertIn("LAST_ANSWERED", os.listdir(os.path.join(ROOT, "archive", "sessions")))


class ThePage(unittest.TestCase):
    def test_it_checks_the_internal_cookie_as_the_findings_page_does(self):
        page, findings = src(*PAGE), src("site", "app", "internal", "findings", "page.tsx")
        gate = 'if (want.length < 24 || !(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();'
        self.assertIn(gate, findings, "the page this one follows")
        self.assertIn(gate, page)
        self.assertIn('const want = process.env.INTERNAL_COSTS_TOKEN ?? "";', page)
        body = page.split("export default async function WaitsPage()", 1)[1]
        self.assertLess(body.index(gate), body.index("WAITS"), "nothing of the reports is touched before the cookie is checked")
        self.assertNotIn("searchParams", page, "no token in the address")
        self.assertNotIn("token=", page)

    def test_a_visitors_404_does_not_carry_the_pages_name(self):
        page = src(*PAGE)
        self.assertNotIn("export const metadata", page, "a fixed title is sent with the 404 too")
        meta = page.split("export async function generateMetadata()", 1)[1].split("\n}\n", 1)[0]
        self.assertIn("internalOk((await cookies()).get(COOKIE)?.value)", meta)
        self.assertIn('inside ? { title: "Waits for Samuel (internal)" } : {}', meta)
        check = src("site", "scripts", "check-internal-waits.mjs")
        for word in ("without the cookie /internal/waits is 404", "a visitor is sent none of the page's words", "a token in the address opens nothing",
                     "at 390 px does not scroll sideways", "every waiting item links to its line of the report"):
            self.assertIn(word, check, word)
        self.assertNotIn(EM, check)

    def test_it_is_not_indexed_never_cached_and_reads_no_database(self):
        page = src(*PAGE)
        self.assertIn("robots: { index: false, follow: false }", page)
        self.assertIn('export const dynamic = "force-dynamic";', page)
        for never in ("rpc(", "supabase", "fetch(", '"use client"', "useState", "localStorage"):
            self.assertNotIn(never, page, never)
        config = src("site", "next.config.ts")
        self.assertIn('source: "/internal/:path*"', config, "every internal address is sent no-store and noindex")

    def test_it_says_what_is_listed_where_the_marker_is_and_links_each_report(self):
        page = src(*PAGE)
        for word in ("the last one marked as answered", "last_answered:", "{m.path}", "commit", "the report on GitHub", "lineUrl(r, line)",
                     "A report with nothing waiting is not", "Session {r.id}: {r.title}", "r.date_words", "the report&apos;s own words",
                     "Decided without you in this session"):
            self.assertIn(word, page, word)
        self.assertIn('export const MARKER = "archive/sessions/LAST_ANSWERED";', src("site", "scripts", "build-waits.mjs"))
        self.assertIn("?plain=1#L", src("site", "lib", "waits.ts"))
        self.assertNotIn(EM, page)

    def test_it_reads_at_a_phones_width(self):
        page = src(*PAGE)
        self.assertIn('overflowWrap: "anywhere"', page, "a long path or command wraps instead of widening the page")
        self.assertNotIn("<table", page, "a table row of a report is said in lines, not drawn as a table")
        self.assertNotIn("min-w-", page)
        self.assertNotIn("whitespace-nowrap", page)

    def test_nothing_a_visitor_is_sent_links_to_it_and_the_release_list_has_no_line_for_it(self):
        hits = []
        for base in ("site/app", "site/components", "site/lib", "site/data"):
            for folder, _, files in os.walk(os.path.join(ROOT, *base.split("/"))):
                for f in files:
                    if not f.endswith((".ts", ".tsx", ".json", ".mjs")):
                        continue
                    rel = os.path.relpath(os.path.join(folder, f), ROOT).replace(os.sep, "/")
                    if rel in ("site/app/internal/waits/page.tsx", "site/lib/waits.ts"):
                        continue
                    with open(os.path.join(folder, f), encoding="utf-8", errors="replace") as fh:
                        if "/internal/waits" in fh.read():
                            hits.append(rel)
        self.assertEqual(hits, [], "the page is linked for nobody")
        release = src("site", "lib", "release.ts")
        self.assertNotIn('"/internal/waits"', release)
        self.assertIn('path.startsWith("/internal/")', release, "every /internal address is outside the curtain and checks the cookie itself")
        self.assertNotIn("waits", src("site", "proxy.ts"))

    def test_the_documents_say_where_the_page_is_and_how_to_mark_a_report_answered(self):
        for rel in (("docs", "release-gate.md"), ("docs", "machines.md"), ("docs", "tools.md")):
            text = src(*rel)
            self.assertIn("/internal/waits", text, rel)
            self.assertNotIn(EM, text, rel)
        doc = src("docs", "machines.md")
        for word in ("archive/sessions/LAST_ANSWERED", "last_answered:", "site/scripts/build-waits.mjs"):
            self.assertIn(word, doc, word)


if __name__ == "__main__":
    unittest.main()
