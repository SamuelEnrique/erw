"""Session 505: site/scripts/check-holds.mjs, a check for held figures that show.

The check reads the pages check-values reads and lists each figure drawn from a table held for a license without the
words "license needed": a checked number judged by components/Num.tsx's own rule, a research card's small-multiple
panel of a held grid, and (to read by hand) a chart series named for a held grid on a page that reads a table held by
grid. It changes no page. Its list goes to docs/licenses_holds.csv, which scripts/licenses.py write turns into a section
of docs/licenses.md (a generated file, never edited by hand). These tests hold the check's maps to the site's, run its
node test, and write docs/licenses.md into a scratch file with and without the list."""

import csv
import importlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
CHECK = os.path.join(SITE, "scripts", "check-holds.mjs")
NODE_TEST = os.path.join(SITE, "scripts", "test-check-holds.mjs")
NUM = os.path.join(SITE, "components", "Num.tsx")
LICENSE_TS = os.path.join(SITE, "lib", "license.ts")
ANALYSIS = os.path.join(SITE, "scripts", "check-analysis.mjs")
SCRIPT = os.path.join(ROOT, "scripts", "licenses.py")
DOC = os.path.join(ROOT, "docs", "licenses.md")
HOLDS = os.path.join(ROOT, "docs", "licenses_holds.csv")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_505_REPORT.md")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def pairs(js):
    """The key: value pairs of a JS object literal's text, comments dropped."""
    js = re.sub(r"//[^\n]*", "", js)
    return dict(re.findall(r"""["']?([A-Za-z0-9_-]+)["']?\s*:\s*"([^"]*)\"""", js))


def block(text, start):
    i = text.index(start)
    j = text.index("{", i)
    depth = 0
    for k in range(j, len(text)):
        depth += {"{": 1, "}": -1}.get(text[k], 0)
        if depth == 0:
            return text[j:k + 1]
    raise AssertionError(f"no end to {start}")


class Maps(unittest.TestCase):
    def test_the_key_table_is_nums(self):
        self.assertEqual(pairs(block(read(CHECK), "export const KEY_TABLE")), pairs(block(read(NUM), "const KEY_TABLE")))

    def test_the_grid_prefixes_are_lib_licenses(self):
        self.assertEqual(pairs(block(read(CHECK), "export const GRID_PREFIX")), pairs(block(read(LICENSE_TS), "const GRID_PREFIX")))

    def test_the_grid_words_are_the_cards(self):
        mine = re.search(r"export const GRID_WORD = (\[.*\]);", read(CHECK)).group(1)
        theirs = re.search(r"const GRID_WORD = (\[.*\]);", read(ANALYSIS)).group(1)
        self.assertEqual(mine, theirs)
        self.assertEqual(len(re.findall(r'"([a-z]+)"\]', mine)), 7)

    def test_the_page_list_is_check_values(self):
        s = read(CHECK)
        self.assertIn('"check-values.mjs"), "--list"]', s)
        self.assertNotIn("const PAGES", s)

    def test_the_check_changes_no_page(self):
        s = read(CHECK)
        # it writes only the files it is asked for (--json, --csv), never under site/app, components or lib
        self.assertEqual(len(re.findall(r"fs\.writeFileSync\(", s)), 2)
        for w in ("site/app", "components/", "lib/license"):
            self.assertNotIn(f'writeFileSync(path.join(SITE, "{w}', s)


@unittest.skipUnless(shutil.which("node"), "node is not on this machine")
class NodeTest(unittest.TestCase):
    def test_the_node_test_passes(self):
        r = subprocess.run(["node", NODE_TEST], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertRegex(r.stdout, r"\d+ tests passed")


class LicensesDoc(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        self.lic = importlib.import_module("licenses")
        self.tmp = tempfile.mkdtemp()
        self.was = self.lic.HOLDS_SHOWN

    def tearDown(self):
        self.lic.HOLDS_SHOWN = self.was
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, holds):
        self.lic.HOLDS_SHOWN = holds
        out = os.path.join(self.tmp, "licenses.md")
        self.lic.write(out)
        return read(out)

    def test_no_list_no_section(self):
        text = self.write(os.path.join(self.tmp, "absent.csv"))
        self.assertNotIn("Held figures that still show", text)

    def test_the_list_is_one_line_a_page(self):
        f = os.path.join(self.tmp, "holds.csv")
        with open(f, "w", encoding="utf-8", newline="") as h:
            w = csv.writer(h)
            w.writerow(["page", "figures", "kinds", "tables", "grids", "day"])
            w.writerow(["/research/card/peak_hour_grids", "2", "panel", "iso_hub_prices_history", "ISO-NE; NYISO", "2026-10-21"])
            w.writerow(["/x", "1", "number", "energy_deals", "", "2026-10-21"])
        text = self.write(f)
        sec = text.split("## Held figures that still show (session 505)", 1)[1]
        self.assertIn("Read on 2026-10-21: 2 pages.", sec)
        self.assertIn("- `/research/card/peak_hour_grids`: 2 held figures shown (panel), from `iso_hub_prices_history`, grids ISO-NE; NYISO.", sec)
        self.assertIn("- `/x`: 1 held figures shown (number), from `energy_deals`.", sec)
        self.assertNotIn(chr(0x2014), text)

    def test_the_committed_document_is_the_scripts(self):
        # docs/licenses.md is what the script writes from the files in git (with the list when it is there)
        text = self.write(self.was)
        self.assertEqual(text, read(DOC).replace("\r\n", "\n"))


class Words(unittest.TestCase):
    def test_no_dashes(self):
        for p in (CHECK, NODE_TEST, __file__, REPORT, HOLDS):
            if os.path.exists(p):
                s = read(p)
                self.assertNotIn(chr(0x2014), s, p)
                self.assertNotIn(chr(0x2013), s, p)


if __name__ == "__main__":
    unittest.main()
