"""Session 7502 (chain 304): the severance tool at the done line.

Energy Research Warehouse (ERW). No network, no model, no warehouse table needed.

- ThePageDrawn       site/scripts/test-severance-page.mjs: the decisions block drawn to HTML, the calculator as it opens,
                     and the default price read from a month's first day (the fault this session fixed).
- TheReplication     replication/severance/: the files are there, the figures file says every figure is inside its
                     tolerance, no row, lease id or operator of the internal RRC table is in a committed file, the
                     sample lease is the page's own, and the calculator's part runs from the rules file alone.
- TheNote            docs/methods/severance.md is completed, not rewritten, and lists the page's choices.
"""
import csv
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "severance")
NODE = shutil.which("node")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageDrawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-severance-page.mjs"], cwd=SITE, capture_output=True, text=True,
                           encoding="utf-8", timeout=600)
        cls.code, cls.out, cls.err = r.returncode, r.stdout, r.stderr

    def test_every_check_passes(self):
        self.assertEqual(self.code, 0, self.out[-3000:] + self.err[-1500:])
        self.assertNotIn("FAIL", self.out)
        m = re.search(r"(\d+) of (\d+) passed", self.out)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 20, self.out[-500:])

    def test_the_default_price_is_a_whole_month_when_the_table_is_behind(self):
        self.assertRegex(self.out, r"(?m)^ok   a table three weeks behind: July whole, 23 days")
        self.assertRegex(self.out, r"(?m)^ok   the request asks from 1 June, a month's first day")


class ThePage(unittest.TestCase):
    def test_the_page_mounts_the_block_and_reads_its_price_from_the_library(self):
        page = src("site", "app", "severance", "page.tsx")
        self.assertIn("<SeveranceDecisions />", page)
        self.assertIn('import { latestMonthMean } from "@/lib/leaseprices";', page)
        self.assertNotIn("75 * 86_400_000", page)          # the read that could begin mid-month
        lib = src("site", "lib", "leaseprices.ts")
        self.assertIn("export async function latestMonthMean", lib)
        self.assertIn("Date.UTC(d.getUTCFullYear(), d.getUTCMonth() - 3, 1)", lib)

    def test_the_district_list_is_keyed_by_the_district_not_its_rate(self):
        c = src("site", "app", "severance", "Calculator.tsx")
        self.assertIn('<option key={d.label} value={d.label}>', c)
        self.assertNotIn("value={Math.round(d.rate * 1e6) / 1e4}", c)
        self.assertIn('setDistrict("");', c)                 # Reset puts the district back too
        rules = json.loads(src("site", "data", "severance_rules.json"))
        rates = [d["rate"] for d in next(b for b in rules["states"]["NM"]["products"]["oil"]["base"] if b["rate"] == "district")["districts"]["list"]]
        self.assertEqual((len(rates), len(set(rates))), (35, 32))     # three pairs share a rate: the reason a rate cannot be the key

    def test_the_block_is_the_tools_own_file_and_no_grey_note(self):
        d = src("site", "app", "severance", "Decisions.tsx")
        self.assertEqual(len(re.findall(r"\{ key: \"", d)), 14)
        self.assertNotIn("text-muted", d)                   # defaults and sources are in the tip (the page standard)
        self.assertNotIn("@/lib/decisions", d)              # not appended to the file other tools share


class TheReplication(unittest.TestCase):
    def test_the_files_are_there(self):
        for f in ("replicate.py", "replicate.do", "cases.json", "sample_lease.csv", "page_figures.json", "page_figures.csv", "crosscheck.py", "crosscheck.json",
                  os.path.join("rows", ".gitignore")):
            self.assertTrue(os.path.exists(os.path.join(REP, f)), f)
        self.assertTrue(os.path.exists(os.path.join(SITE, "scripts", "severance-figures.mjs")))

    def test_every_figure_is_inside_its_tolerance(self):
        j = json.loads(src("replication", "severance", "page_figures.json"))
        self.assertEqual((j["differ"], j["named"]), (0, 0))
        self.assertGreaterEqual(j["inside"], 600)
        self.assertEqual(j["inside"], len(j["figures"]))
        self.assertTrue(all(r["state"] == "inside" for r in j["figures"]))
        self.assertTrue(all(w["replication"] == w["page"] for w in j["words"].values()))
        with open(os.path.join(REP, "page_figures.csv"), encoding="utf-8", newline="") as f:
            self.assertEqual(len(list(csv.DictReader(f))), len(j["figures"]))
        keys = {r["key"] for r in j["figures"]}
        for k in ("price|oil|value", "calc|default|base", "calc|LA-oil-base|base", "calc|NM-oil-district-high|with", "lease|sample|potential", "real|A|base"):
            self.assertIn(k, keys)

    def test_no_internal_row_is_in_a_committed_file(self):
        # the RRC table is internal: a real lease is named by the rule that picks it, never by its id, name or operator
        for f in ("page_figures.json", "page_figures.csv", "crosscheck.json", "cases.json"):
            text = src("replication", "severance", f)
            self.assertIsNone(re.search(r"rrc:|\b[OG]-\d{2}-\d{3,6}\b|x_lease_name|x_operator_name", text), f)
        real = [r for r in json.loads(src("replication", "severance", "page_figures.json"))["figures"] if r["key"].startswith("real|")]
        self.assertTrue(real and all(re.fullmatch(r"real\|(leases|operators|[A-D]\|[a-z_|]+)", r["key"]) for r in real))
        self.assertIn("*", src("replication", "severance", "rows", ".gitignore"))

    def test_the_sample_is_the_pages_own(self):
        lease = src("site", "lib", "lease.ts")
        body = re.search(r"export const SAMPLE_CSV = `(.*?)`;", lease, re.S).group(1)
        with open(os.path.join(REP, "sample_lease.csv"), encoding="utf-8", newline="") as f:
            mine = f.read()
        self.assertEqual(mine.replace("\r\n", "\n").splitlines()[2:], body.splitlines()[2:])     # the rows under the header
        words = json.loads(src("replication", "severance", "page_figures.json"))["words"]["lease|sample|sha256"]
        self.assertEqual(words["replication"], words["page"])
        self.assertEqual(hashlib.sha256(mine.replace("\r\n", "\n").encode("utf-8")).hexdigest(), words["page"])

    def test_the_calculator_part_runs_from_the_rules_file_alone(self):
        spec = importlib.util.spec_from_file_location("severance_replicate_7502", os.path.join(REP, "replicate.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        rules = m.Rules(os.path.join(SITE, "data", "severance_rules.json"))
        # the hand-computed cases of site/scripts/test-severance.mjs, worked again by the replication's own function
        r = m.tax(rules, "TX", "gas", 10000, 3, option="tx_lp_gas", period="2026-08")
        self.assertAlmostEqual(r["base"], 2250.0, places=6)
        self.assertAlmostEqual(r["with"], 0.0, places=6)
        r = m.tax(rules, "TX", "oil", 1000, 70, option="tx_eor", credit="tx_lp_oil", credit_period="2026-08")
        self.assertAlmostEqual(r["base"], 3220.0, places=6)
        self.assertAlmostEqual(r["with"], 1610.0, places=6)
        self.assertAlmostEqual(m.tax(rules, "TX", "oil", 1000, 0.5)["base"], 46.0, places=6)            # the floor of 4.6 cents a barrel
        self.assertAlmostEqual(m.tax(rules, "LA", "gas", 10000, 3)["base"], 1514.0, places=6)           # 15.14 cents per Mcf
        # a table that ends in August, drawn on 20 September: July is the latest complete month, read whole
        self.assertEqual(m.default_price({"2026-07": [1.0], "2026-08": [2.0, 4.0]}, datetime.datetime(2026, 9, 20)), {"month": "2026-07", "value": 1.0, "days": 1})
        self.assertIsNone(m.default_price({"2026-05": [1.0]}, datetime.datetime(2026, 9, 20)))
        self.assertEqual(m.round2(2.675), 2.68)

    def test_the_do_file_states_what_it_should_print(self):
        do = src("replication", "severance", "replicate.do")
        j = {r["key"]: r["replication"] for r in json.loads(src("replication", "severance", "page_figures.json"))["figures"]}
        for key in ("price|oil|value", "price|gas|value", "calc|default|base", "calc|TX-gas-base|base", "calc|LA-oil-base|base", "calc|NM-oil-base|base"):
            self.assertIn("%.2f" % j[key], do, key)


class TheNote(unittest.TestCase):
    def test_the_note_is_completed_not_rewritten(self):
        note = src("docs", "methods", "severance.md")
        self.assertTrue(note.startswith("# Severance tax: method"))
        for head in ("## Texas", "## The lease tool (session 45, v0.2)", "## The refund finder (session 57, internal)", "## The pages as they stand (session 334, 20 October 2026)",
                     "## The tool as a reader meets it (session 7502, 16 November 2026)", "### How a figure is computed", "### The choices that move a figure",
                     "### The cross-check (16 November 2026)"):
            self.assertIn(head, note)
        self.assertLess(note.index("## The pages as they stand"), note.index("## The tool as a reader meets it"))

    def test_the_notes_choices_are_the_pages(self):
        note = src("docs", "methods", "severance.md")
        table = note.split("### The choices that move a figure")[1].split("###")[0]
        rows = [l for l in table.splitlines() if l.startswith("| ") and not l.startswith("| Choice") and not l.startswith("|---")]
        self.assertEqual(len(rows), 14)
        self.assertIn("lists these 14", table)

    def test_no_long_dash_in_what_the_session_wrote(self):
        for parts in (("docs", "methods", "severance.md"), ("docs", "reviews", "severance-faults-2026-11-16.md"), ("site", "app", "severance", "Decisions.tsx"),
                      ("site", "scripts", "severance-figures.mjs"), ("site", "scripts", "test-severance-page.mjs"), ("replication", "severance", "replicate.py"),
                      ("replication", "severance", "replicate.do"), ("replication", "severance", "crosscheck.py"), ("replication", "severance", "crosscheck.json"),
                      ("tests", "test_session7502_severance.py")):
            text = src(*parts)
            self.assertNotIn(chr(0x2014), text, parts[-1])
            self.assertNotIn(chr(0x2013), text, parts[-1])


if __name__ == "__main__":
    unittest.main()
