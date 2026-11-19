"""Chain 507 (session 8900): the findings audit made into site/data/findings_audit.json for /internal/findings.

The file is what warehouse/analysis/findings/audit_page.py writes from the audit (docs/reviews/findings-audit-2026-11-19/
and its document) and the sheet of forty; every draft of docs/findings/ has a row; a draft the audit did not reproduce,
withdrew, or found on a table that is not public is stopped from approval; the sheet's forty are in order and passed.
No network."""
import glob
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(ROOT, "site", "data", "findings_audit.json")
SCRIPT = os.path.join(ROOT, "warehouse", "analysis", "findings", "audit_page.py")


def load():
    with open(FILE, encoding="utf-8") as f:
        return json.load(f)


class AuditFile(unittest.TestCase):
    def test_the_file_is_what_the_audit_says(self):
        # --check-structure: the "already known?" answers grow through the day on main (part A); the rest must agree
        r = subprocess.run([sys.executable, SCRIPT, "--check-structure"], capture_output=True, text=True, cwd=ROOT, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_every_draft_of_docs_findings_has_a_row(self):
        d = load()["drafts"]
        ids = {}
        for md in glob.glob(os.path.join(ROOT, "docs", "findings", "*", "*.md")):
            m = re.search(r"Draft `(scan-[a-z]+-[0-9a-f]{12})`", open(md, encoding="utf-8").read())
            if m:
                ids[m.group(1)] = os.path.basename(md)[:-3]
        self.assertGreaterEqual(len(ids), 549)
        self.assertEqual(set(ids), set(d))
        for i, slug in ids.items():
            self.assertEqual(d[i]["slug"], slug)

    def test_approval_is_stopped_where_the_audit_says(self):
        d = load()["drafts"]
        for i, r in d.items():
            if r["verdict"] in ("passed", "passed after a fix"):
                self.assertEqual(r["blocked"], "", r["slug"])
            else:
                self.assertTrue(len(r["blocked"]) > 10, r["slug"])
            self.assertEqual(len(r["checks"]), 4 if r["verdict"] != "not audited" else 0, r["slug"])
            if r["verdict"] == "withdrawn":
                self.assertEqual(r["checks"][1]["state"], "withdrawn")

    def test_counts_are_the_audits(self):
        # the counts table of the audit document, verdict by verdict, is the file's
        a = load()
        doc = open(os.path.join(ROOT, "docs", "reviews", "findings-audit-2026-11-19.md"), encoding="utf-8").read()
        words = {"passed": "passed", "passed after a fix": "passed after a fix", "not checked": "not checked",
                 "held: internal table, not for the sheet": "held", "withdrawn: the figure does not reproduce": "withdrawn"}
        table = {}
        for m in re.finditer(r"^\| ([a-z][^|]*?) \| (\d+) \|$", doc, re.M):
            if m.group(1) in words:
                table[words[m.group(1)]] = int(m.group(2))
        self.assertEqual({k: v for k, v in a["counts"].items() if k != "not audited"}, table)
        self.assertEqual(sum(a["counts"].values()), len(a["drafts"]))
        for r in a["drafts"].values():
            self.assertFalse(r["title"].startswith("Withdrawn by the audit"), r["slug"])

    def test_the_sheet_of_forty(self):
        a = load()
        self.assertEqual(len(a["sheet"]), 40)
        self.assertEqual(len(a["readers"]), 3)
        fam = {}
        for n, i in enumerate(a["sheet"], 1):
            r = a["drafts"][i]
            self.assertEqual(r["sheet"]["rank"], n)
            self.assertIn(r["verdict"], ("passed", "passed after a fix"))
            self.assertIn(r["sheet"]["reader"], a["readers"])
            self.assertTrue(r["sheet"]["risk"])
            self.assertTrue(all(t["license"] == "public" for t in r["tables"]), r["slug"])
            disk = open(os.path.join(ROOT, *r["files"]["do"].split("/")), encoding="utf-8").read().replace("\r\n", "\n")
            self.assertEqual(r["sheet"]["do_text"], disk)
            fam[r["family"]] = fam.get(r["family"], 0) + 1
        self.assertLessEqual(max(fam.values()), 6)
        # a finding that repeats a publisher's own headline says so on the sheet, and the page carries it
        doc = open(os.path.join(ROOT, "docs", "reviews", "findings-shortlist-2026-11-19.md"), encoding="utf-8").read()
        self.assertEqual(doc.count("**A publisher's own headline:** yes"), sum(1 for i in a["sheet"] if a["drafts"][i]["sheet"].get("headline")))

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), open(FILE, encoding="utf-8").read())


if __name__ == "__main__":
    unittest.main()
