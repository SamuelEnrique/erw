"""Session 7506 (chain 304): the forecast tool, Local impact (/impact), at the done line: its replication.

Energy Research Warehouse (ERW). What is held to:

  the replication's files are whole and say what they are: seventeen addresses (the page as it opens, ten planned
    projects of EIA-860M, six addresses the value check reads), each figure with its case, scenario, name and
    tolerance; the ten projects of projects.csv each a case; no dash the repository forbids;
  the Stata do-file states its five expected values at its top, and they are the five the page's own view drew for the
    page as it opens (page_figures.json, written from the drawn HTML), each inside half of the page's last shown digit;
    the do-file follows the house rules for a do-file (no continuation operator, an empty line between commands
    outside loops and none inside);
  the method note names the replication, its result line, the cross-check's two documents and the sign-off block, and
    the faults file counts its rows by kind;
  where the table nlr_jedi_multipliers is on the machine (ERW_TABLES_DIR or ERW_TABLES names another copy's
    warehouse/output, read only; else this copy's) and node is there: the page's view is drawn again from the day's
    table into a temporary folder and the replication is run against that, so the two implementations are compared on
    the same day's rows and no committed figure is compared with the day's data (the owner's ruling of 11 October
    2026); a changed parameter must be caught. Skipped on a machine without the table, as GitHub's runner.

No request, no model call, no site build. The environment is read, never set."""
import csv
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HERE = os.path.join(ROOT, "replication", "impact")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.environ.get("ERW_TABLES") or os.path.join(ROOT, "warehouse", "output")
JEDI = os.path.join(TABLES, "nlr_jedi_multipliers.csv")
EM, EN = chr(0x2014), chr(0x2013)


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def replicate_module():
    spec = importlib.util.spec_from_file_location("erw_impact_replicate_7506", os.path.join(HERE, "replicate.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pf = json.loads(read("replication", "impact", "page_figures.json"))
        with open(os.path.join(HERE, "projects.csv"), encoding="utf-8", newline="") as f:
            cls.projects = list(csv.DictReader(line for line in f if not line.startswith("#")))

    def test_seventeen_addresses_and_every_project_a_case(self):
        cases = self.pf["cases"]
        self.assertEqual(len(cases), 17)
        self.assertEqual(cases[0]["id"], "default")
        self.assertEqual(cases[0]["address"], "/impact")
        self.assertEqual(len(self.projects), 10)
        ids = {c["project"] for c in cases if c["project"]}
        self.assertEqual(ids, {p["id"] for p in self.projects})
        # four technologies and at least six states among the named projects
        self.assertEqual({p["tech"] for p in self.projects}, {"land_based_wind", "utility_pv", "natural_gas", "geothermal"})
        self.assertGreaterEqual(len({p["state"] for p in self.projects}), 6)

    def test_each_figure_is_whole(self):
        known = {c["id"] for c in self.pf["cases"]}
        seen = set()
        for f in self.pf["figures"]:
            self.assertIn(f["case"], known)
            self.assertIn(f["scenario"], ("a", "b"))
            key = (f["case"], f["scenario"], f["figure"])
            self.assertNotIn(key, seen)
            seen.add(key)
            if f["figure"].startswith("cell:"):
                self.assertIsNone(f["page"])                      # a cell drawn with no number
                self.assertRegex(f["shown"], r"^(not held|none|no figure) \(")
            elif f["page"] is not None and f["tolerance"] is not None:
                self.assertGreaterEqual(f["tolerance"], 0)
        self.assertGreater(len(seen), 5000)

    def test_the_csv_holds_the_same_figures(self):
        with open(os.path.join(HERE, "page_figures.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), len(self.pf["figures"]))
        self.assertEqual([(r["case"], r["scenario"], r["figure"]) for r in rows], [(f["case"], f["scenario"], f["figure"]) for f in self.pf["figures"]])

    def test_no_forbidden_dash(self):
        for parts in (("replication", "impact", "replicate.py"), ("replication", "impact", "replicate.do"), ("replication", "impact", "projects.csv"),
                      ("replication", "impact", "page_figures.csv"), ("site", "scripts", "impact-figures.mjs"), ("site", "scripts", "impact-crosscheck.mjs"),
                      ("docs", "reviews", "impact-faults-2026-11-16.md"), ("docs", "reviews", "impact-crosscheck-2026-11-16.json")):
            text = read(*parts)
            self.assertNotIn(EM, text, parts[-1])
            self.assertNotIn(EN, text, parts[-1])


class TheDoFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.do = read("replication", "impact", "replicate.do")
        pf = json.loads(read("replication", "impact", "page_figures.json"))
        cls.page = {f["figure"]: f for f in pf["figures"] if f["case"] == "default" and f["scenario"] == "a"}

    def test_its_expected_values_are_the_pages(self):
        names = ["c:jobs:total", "o:jobs:total", "c:earnings:total", "pv:taxes", "pv:earnings"]
        got = re.findall(r"^\*\s+(\d)\. [^:]+: ([\d,.]+)\s", self.do, flags=re.M)
        self.assertEqual([g[0] for g in got], ["1", "2", "3", "4", "5"])
        for (_, value), name in zip(got, names):
            f = self.page[name]
            self.assertLessEqual(abs(float(value.replace(",", "")) - f["page"]), f["tolerance"], name)

    def test_house_rules(self):
        self.assertNotIn("///", self.do)
        self.assertIn('import delimited using "rows/jedi_tx_wind.csv"', self.do)
        lines = self.do.split("\n")
        depth = 0
        for i, line in enumerate(lines[:-1]):
            if line.strip() == "}":
                depth -= 1
            if depth > 0:
                self.assertTrue(line.strip(), f"an empty line inside a loop, line {i + 1}")
            elif line.strip() and not line.strip() == "}":
                self.assertEqual(lines[i + 1].strip() if not line.rstrip().endswith("{") else "", "", f"no empty line after line {i + 1}")
            if line.rstrip().endswith("{"):
                depth += 1
        self.assertEqual(self.do.count("display "), 6)


class TheNoteAndTheFaults(unittest.TestCase):
    def test_the_note_names_the_replication_and_the_sign_off(self):
        note = read("docs", "methods", "forecast.md")
        for words in ("## 12. The replication", "### 12.1", "replication/impact/replicate.py", "7593 of 7593 inside the tolerance",
                      "NREL/CP-500-40085", "Lone Mountain Geothermal", "### 12.5 Sign-off", "- Signed off by:"):
            self.assertIn(words, note)
        tail = note[note.index("## 12. The replication"):]
        self.assertNotIn(EM, tail)
        self.assertNotIn(EN, tail)

    def test_the_faults_file_counts_its_rows(self):
        faults = read("docs", "reviews", "impact-faults-2026-11-16.md")
        rows = re.findall(r"^\| (\d+) \|.*\| (note|data machine|ruling|site) \| ", faults, flags=re.M)
        self.assertEqual([int(n) for n, _ in rows], list(range(1, len(rows) + 1)))
        kinds = [k for _, k in rows]
        self.assertIn(f"Note: {kinds.count('note')} rows", faults)
        self.assertIn(f"Data machine: {kinds.count('data machine')} rows", faults)
        self.assertIn(f"Ruling: {kinds.count('ruling')} rows", faults)
        self.assertIn("Site faults fixed: 0", faults)

    def test_the_cross_check_holds_ours_and_theirs(self):
        x = json.loads(read("docs", "reviews", "impact-crosscheck-2026-11-16.json"))
        self.assertEqual(len(x["documents"]), 2)
        for r in x["rows"]:
            for k in ("document", "figure", "ours", "theirs", "quote", "why"):
                self.assertIn(k, r)
            self.assertIn(r["document"], x["documents"])
        self.assertGreaterEqual(len(x["rows"]), 15)


class TheTwoImplementations(unittest.TestCase):
    """The page's own view, drawn again from the day's table, against the replication: no committed figure is read."""

    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(JEDI):
            raise unittest.SkipTest("nlr_jedi_multipliers is not on this machine; ERW_TABLES_DIR names another copy's warehouse/output")
        node = shutil.which("node")
        if not node or not os.path.isdir(os.path.join(ROOT, "site", "node_modules")):
            raise unittest.SkipTest("node or the site's modules are not here")
        cls.tmp = tempfile.TemporaryDirectory()
        r = subprocess.run([node, "--import", "./scripts/tsx-register.mjs", "scripts/impact-figures.mjs", JEDI, "--out", cls.tmp.name],
                           cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            raise AssertionError(f"the page's view was not drawn: {r.stdout[-800:]} {r.stderr[-800:]}")
        cls.R = replicate_module()
        cls.P = cls.R.Params()
        cls.jedi = cls.R.read_jedi(JEDI)
        with open(os.path.join(cls.tmp.name, "page_figures.json"), encoding="utf-8") as f:
            cls.pf = json.load(f)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def differences(self, P):
        with redirect_stdout(io.StringIO()):
            return self.R.compare(P, self.jedi, self.pf)

    def test_every_figure_the_page_draws_is_recomputed(self):
        self.assertGreater(len(self.pf["figures"]), 5000)
        self.assertEqual(self.differences(self.P), 0)

    def test_a_changed_parameter_is_caught(self):
        P = self.R.Params()
        P.sales["tx"]["state_rate"] += 0.001
        self.assertGreater(self.differences(P), 0)
        P = self.R.Params()
        P.index["2017"] *= 1.01
        self.assertGreater(self.differences(P), 100)


if __name__ == "__main__":
    unittest.main()
