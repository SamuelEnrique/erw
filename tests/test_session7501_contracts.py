"""Session 7501 (chain 304, part A): /contracts taken to the done line.

Held here: the page drawn to HTML with its own code on made-up rows (site/scripts/test-contracts-render.mjs: the five
faults fixed and the decisions block); the replication's files (counts only, no party's name and no party's own
figure, every figure inside its tolerance or named); the method note and the faults file; and that no row of the
internal tables is in git with the replication. The real tables are internal: no name of them is in this file.
"""
import csv
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "contracts")
NODE = shutil.which("node")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageDrawn(unittest.TestCase):
    """The page's default export drawn for each view without a build (scripts/test-contracts-render.mjs)."""

    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-contracts-render.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600)
        cls.code, cls.out, cls.err = r.returncode, r.stdout, r.stderr

    def test_every_view_draws_and_every_check_passes(self):
        self.assertEqual(self.code, 0, self.out[-3000:] + self.err[-1500:])
        self.assertNotIn("FAIL", self.out)
        m = re.search(r"(\d+) of (\d+) passed", self.out)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 40, self.out[-500:])

    def test_the_five_faults_are_each_held(self):
        for n in range(1, 6):
            self.assertRegex(self.out, rf"(?m)^ok   fault {n}: ", f"fault {n}")
        self.assertRegex(self.out, r"(?m)^ok   without the token nothing is asked of the database")


class ThePageAndTheLibrary(unittest.TestCase):
    def test_the_fixes_are_in_the_source(self):
        lib, page = src("site", "lib", "contracts.ts"), src("site", "app", "contracts", "page.tsx")
        self.assertIn("baOf(r.pod_ba) === baOf(ba)", lib)                       # "not stated" and a code's capitals
        self.assertIn("export function heldFrom(", lib)
        self.assertIn("export function inForce(", lib)
        self.assertNotIn("</span> do.</>", page)                                # the limits box no longer says the rows with no number "do" give words
        self.assertIn('file\n        no number.', page.replace("\r\n", "\n"))
        self.assertIn(' as filed" : ""}.`}>', page)
        self.assertIn("<ContractsDecisions />", page)
        self.assertIn('<Link href="/data/methods/contracts">', page)

    def test_the_page_stays_in_review_and_keeps_what_it_had(self):
        self.assertRegex(src("site", "lib", "release.ts"), r'"/contracts":\s*"review"')
        page = src("site", "app", "contracts", "page.tsx")
        for words in ("Three limits of this record", "What a row is", "What this cannot see", "How a buyer's names are brought together", "What the ranking is, and is not",
                      "What a megawatt stated is, and what this leaves out", "FERC's terms for this data", "Contracts new and gone, by quarter"):
            self.assertTrue(words in page or words.replace("'", "&apos;") in page, words)
        self.assertNotIn("TableDownloads", page)                                # internal: no download
        decisions = src("site", "app", "contracts", "Decisions.tsx")
        self.assertEqual(len(re.findall(r'\{ key: "', decisions)), 19)
        self.assertEqual(len(re.findall(r"\n    def: \"", decisions)), 19)
        self.assertEqual(len(re.findall(r"\n    source: \"", decisions)), 19)


class TheReplication(unittest.TestCase):
    def test_its_files_hold_counts_only_and_every_figure_is_inside_or_named(self):
        with open(os.path.join(REP, "page_figures.json"), encoding="utf-8") as f:
            d = json.load(f)
        figs = d["figures"]
        self.assertGreaterEqual(len(figs), 2600)
        inside = named = 0
        for x in figs:
            if "internal" in x:                                                   # one party's own figure: compared, not written
                self.assertNotIn("page", x)
                self.assertNotIn("replication", x)
                self.assertTrue(x["agrees"] or "named" in x, x["key"])
            else:
                self.assertTrue(abs(float(x["page"]) - float(x["replication"])) <= x["tolerance"] + 1e-9 or "named" in x, x["key"])
            named += "named" in x
            inside += "named" not in x
        self.assertEqual(d["result"], f"{inside} of {len(figs)} inside the tolerance; {named} named; 0 not explained")
        self.assertTrue(all(re.search(r"\|place$", x["key"]) for x in figs if "named" in x))          # the one named difference: fault 5
        text = json.dumps(d)
        self.assertNotRegex(text, r'"(seller|buyer|name|parties)":')                 # no party is named in the file
        self.assertIsNone(re.search(r"\|party\|", text))
        with open(os.path.join(REP, "page_figures.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.reader(line for line in f if not line.startswith("#")))
        self.assertEqual(rows[0], ["key", "page", "replication", "tolerance", "agrees"])
        self.assertEqual(len(rows) - 1, len(figs))
        self.assertGreater(sum(1 for r in rows[1:] if r[1] == "internal"), 1000)

    def test_no_row_of_an_internal_table_is_in_git(self):
        self.assertEqual(src("replication", "contracts", "rows", ".gitignore").split("\n")[-3:-1], ["*", "!.gitignore"])
        tracked = subprocess.run(["git", "ls-files", "replication/contracts"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        self.assertTrue(tracked)
        self.assertEqual([p for p in tracked if p.startswith("replication/contracts/rows/") and not p.endswith(".gitignore")], [])
        code = src("replication", "contracts", "replicate.py")
        self.assertNotIn("import pandas", code)                                   # standard library only
        self.assertNotRegex(code, r"from (load|eqr_buyers|eqr_terms)|import (load|eqr_buyers|eqr_terms)\b")   # not the builders' code, not the loader's

    def test_the_do_file_states_its_expected_values(self):
        do = src("replication", "contracts", "replicate.do")
        for line in ("1. contract rows filed for the quarter: 186,873", "2. rows that file their rate as a number: 81,718", "3. rows that file words and no number: 104,952",
                     "4. energy contracts in force: 22,808", "5. energy contracts in force that state megawatts, and the megawatts: 356, 31,402.3"):
            self.assertIn("*   " + line, do)
        self.assertIn("This do-file has not been run", do)


class TheNotes(unittest.TestCase):
    def test_the_note_of_the_page_and_the_faults_file(self):
        note = src("docs", "methods", "contracts.md")
        for words in ("## 3. View 1: the contracts by the quarter signed", "## 4. What a visitor sees, and what the internal view sees", "## 5. View 2: the largest buyers and sellers",
                      "## 6. View 3: ranked by megawatts stated", "## 7. View 4: what the filings state", "## 8. The cross-check against published figures",
                      "## 9. The decisions on the page", "## 10. What the tool does not hold", "91 FR 14306", "3,672", "HTTP 403", "nothing published"):
            self.assertIn(words, note, words)
        faults = src("docs", "reviews", "contracts-faults-2026-11-16.md")
        rows = re.findall(r"(?m)^\| (\d+) \|", faults)
        self.assertEqual(rows, [str(i) for i in range(1, len(rows) + 1)])
        self.assertGreaterEqual(len(rows), 9)
        for kind in ("site, fixed", "data machine", "ruling"):
            self.assertIn(kind, faults)
        for p in ("docs/methods/contracts.md", "docs/reviews/contracts-faults-2026-11-16.md", "replication/contracts/replicate.py", "replication/contracts/replicate.do",
                  "site/app/contracts/Decisions.tsx", "site/scripts/test-contracts-render.mjs", "site/scripts/contracts-figures.mjs"):
            text = src(*p.split("/"))
            self.assertNotIn(chr(0x2014), text, p)
            self.assertNotIn(chr(0x2013), text, p)


if __name__ == "__main__":
    unittest.main()
