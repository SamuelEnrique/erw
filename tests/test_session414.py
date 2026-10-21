"""Session 414: /internal/waits, each ruling once (site/scripts/build-waits.mjs, "the ledger").

Energy Research Warehouse (ERW). What is held to:

  the ledger's rules (site/scripts/test-waits-ledger.mjs, run here): the words compared, the sessions an item names,
    the one subject, what an item blocks, two items merged only by a written rule and an item that restates two kept
    beside each, the rank taken only from a note that says its list is by value, nothing put first where no note
    ranks, and on the repository's own reports every line of the run in one item, linked to its line;
  the run is sessions 351 to 413, and the ledger never fails the site's build;
  the page draws the ledger after the cookie is checked, with its count at the top, the first three, the five blocks,
    what was not listed, and the rules it applied; a visitor's 404 carries none of it;
  the documents say where the rules are.

No request, no model call; the environment is read, never set. The test that needs node skips when it is absent.

    python -m unittest tests.test_session414 -v
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EM = chr(0x2014)
PAGE = ("site", "app", "internal", "waits", "page.tsx")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheRules(unittest.TestCase):
    def test_the_node_cases_hold(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("no node on this machine")
        r = subprocess.run([node, os.path.join("site", "scripts", "test-waits-ledger.mjs")], cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", timeout=180)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])
        self.assertRegex(r.stdout, r"test-waits-ledger: (\d+) of \1 held")

    def test_the_run_is_351_to_413_and_the_ledger_cannot_fail_a_build(self):
        s = src("site", "scripts", "build-waits.mjs")
        self.assertIn("export const LEDGER = { from: 351, to: 413 };", s)
        build = s.split("export function build(repo", 1)[1]
        self.assertIn("led = ledger(all, readNotes(repo), marker);", build)
        self.assertIn("} catch (e) {", build.split("led = ledger(", 1)[1].split("return {", 1)[0], "a fault in the ledger is said, not thrown")
        imports = re.findall(r'^import .* from "([^"]+)";$', s, re.M)
        self.assertEqual(sorted(imports), ["node:fs", "node:path", "node:url"])
        for never in ("fetch(", "anthropic", "process.exit", EM):
            self.assertNotIn(never, s, never)

    def test_the_four_blocks_and_none_of_them_are_named_with_what_they_mean(self):
        s = src("site", "scripts", "build-waits.mjs")
        for key, label in (("money", "Money"), ("pull", "A data pull"), ("figure", "A ruling on a figure"), ("page", "A public page"), ("other", "None of the four")):
            self.assertIn(f'{{ key: "{key}", label: "{label}", says: "', s)
        self.assertIn('{ block: "other", re: /[\\s\\S]/ }', s, "the last rule takes what no other matched")
        self.assertIn("BY_VALUE = /\\bhighest value first\\b|\\bin the order of (?:their )?value\\b|\\bby value\\b/i", s)


class ThePage(unittest.TestCase):
    def test_the_ledger_is_drawn_after_the_cookie_is_checked(self):
        page = src(*PAGE)
        body = page.split("export default async function WaitsPage()", 1)[1]
        gate = 'if (want.length < 24 || !(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();'
        self.assertLess(body.index(gate), body.index("<LedgerSection L={w.ledger} />"))
        self.assertLess(body.index("<LedgerSection L={w.ledger} />"), body.index("Report by report"), "the ledger, then the reports one by one")

    def test_it_says_its_count_its_first_three_its_blocks_and_its_rules(self):
        page = src(*PAGE)
        for word in ('data-ln="items"', 'data-ln="lines"', 'data-ln="reports"', "data-ln-block={b.key}", "each ruling once",
                     "First: the three the notes rank highest", "this page does not make a rank up", "No note ranks it.",
                     "Not yet in", "a report that lands joins this list at the next build", "Why these are one item",
                     "The rules, as the build applied them", "restated with another item in", "of the first three: item",
                     "no rule of the four matched its words", "Not listed:", "with no section for your ruling"):
            self.assertIn(word, page, word)
        for never in ("<table", "min-w-", "whitespace-nowrap", EM):
            self.assertNotIn(never, page, never)
        self.assertIn("ledger?: Ledger;", src("site", "lib", "waits.ts"))

    def test_the_browser_check_reads_the_ledger_and_the_visitor_sees_none_of_it(self):
        check = src("site", "scripts", "check-internal-waits.mjs")
        for word in ("the ledger's counts are the file's", "every item of the ledger links to each line that asks it",
                     "the first three are drawn first, in their order", "a visitor is sent none of the ledger"):
            self.assertIn(word, check, word)

    def test_the_documents_say_where_the_rules_are(self):
        doc = src("docs", "machines.md")
        for word in ("Each ruling once (session 414)", "`LEDGER`", "`BLOCK_RULES`", "`SUBJECTS`", "test-waits-ledger.mjs"):
            self.assertIn(word, doc, word)


if __name__ == "__main__":
    unittest.main()
