"""Session 381: the five sellable tools against roadmap item 2 (the chain of 20 to 21 October 2026).

Energy Research Warehouse (ERW). Roadmap item 2's "done" asks of each of the five tools a method note signed by Samuel,
a replication a reader can run, a cross-check table against published figures and a decisions block. Session 381
wrote, near the top of each pack under docs/reviews/packs/, a table of what the tool has and lacks against it, and
built what needed no ruling: Research's replication from its cards' downloads
(site/public/findings/erw_2026_research_replication.py, standard library and numpy), and a "Cross-checks" section in
the form of the three decision tools' notes for the Grid tool (docs/methods/grid_network.md) and for Research
(docs/methods/automated_analysis_findings.md).

What is held here: the replication runs from its folder and equals every figure of the nine library cards it names;
a planted change in a CSV is caught; it imports nothing of the warehouse; each pack has the table, with a row for each
of the four parts of "done" and an exit code for its replication; the two new sections have the five columns, a source
in every row and no empty cell; no em dash in any file this session wrote. Nothing here sets the environment, reads a
warehouse table or makes a request.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FINDINGS = os.path.join(ROOT, "site", "public", "findings")
MIRROR = os.path.join(FINDINGS, "erw_2026_research_replication.py")
CARDS_JSON = os.path.join(ROOT, "site", "data", "findings")
PACKS = os.path.join(ROOT, "docs", "reviews", "packs")
HEADING = "## Against roadmap item 2 (session 381)"
FIVE = ("battery", "generator", "datacenter", "research", "grid")
WRITTEN = ["site/public/findings/erw_2026_research_replication.py", "tests/test_session381.py", "docs/methods/grid_network.md",
           "docs/methods/automated_analysis_findings.md", "archive/sessions/SESSION_381_REPORT.md"] + [f"docs/reviews/packs/{t}.md" for t in FIVE]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def run(args, cwd):
    return subprocess.run([sys.executable, MIRROR] + args, cwd=cwd, capture_output=True, text=True, timeout=600)


def section(text, heading):
    lines = text.split("\n")
    start = lines.index(heading)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start + 1:end]


def rows(lines):
    """The data rows of the first markdown table in a stretch."""
    table = [ln for ln in lines if ln.startswith("|")]
    return [r for r in table[2:]]


class TheResearchReplication(unittest.TestCase):
    def test_it_equals_every_figure_of_the_cards(self):
        p = run(["--json", CARDS_JSON], FINDINGS)
        self.assertEqual(p.returncode, 0, p.stdout[-2000:] + p.stderr[-2000:])
        m = re.search(r"^(\d+) figures compared with the cards' JSON, (\d+) different$", p.stdout, re.M)
        self.assertIsNotNone(m, p.stdout[-500:])
        self.assertGreaterEqual(int(m.group(1)), 300)
        self.assertEqual(int(m.group(2)), 0)
        self.assertNotIn("DIFFERENT", p.stdout)

    def test_it_runs_from_its_folder_without_the_cards(self):
        p = run([], FINDINGS)
        self.assertEqual(p.returncode, 0, p.stderr[-2000:])
        for card in ("batteries_lunch_grids", "batteries_curtailment", "batteries_curtailment_hourly", "impact_study", "gas_sets_price",
                     "negative_prices_west", "peak_hour_grids", "queue_divorce", "who_rescues_whom"):
            self.assertIn(f"== {card} (", p.stdout)
        self.assertIn("batteries_lunch_grids.ercot_reg_multiple_coef = -10.757", p.stdout)
        self.assertIn("batteries_curtailment.charging_solar_month_coef = 1081.24", p.stdout)
        self.assertIn("impact_study.reg_did = 3016.40", p.stdout)

    def test_a_planted_change_is_caught(self):
        with tempfile.TemporaryDirectory() as d:
            for name in os.listdir(FINDINGS):
                if name.endswith(".csv"):
                    shutil.copy(os.path.join(FINDINGS, name), d)
            path = os.path.join(d, "erw_2026_queue_outcomes_technology.csv")
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertIn(",75.1796387567233,", text)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text.replace(",75.1796387567233,", ",75.2796387567233,"))
            p = run([d, "--json", CARDS_JSON], d)
            self.assertEqual(p.returncode, 1, p.stdout[-1000:])
            self.assertIn("DIFFERENT  queue_divorce.withdrawn_pct", p.stdout)
            os.remove(os.path.join(d, "erw_2026_gas_share_hours.csv"))
            self.assertEqual(run([d], d).returncode, 2)

    def test_it_reads_nothing_of_the_warehouse(self):
        text = src("site", "public", "findings", "erw_2026_research_replication.py")
        imports = set(re.findall(r"^(?:import|from) (\w+)", text, re.M))
        self.assertEqual(imports, {"csv", "json", "math", "os", "sys", "numpy"})
        for word in ("findings_common", "read_table", "warehouse/output", "urllib", "http.client", "import scipy", "import pandas"):
            self.assertNotIn(word, text)


class ThePacks(unittest.TestCase):
    def test_each_pack_has_the_table_before_part_one(self):
        for tool in FIVE:
            text = src("docs", "reviews", "packs", tool + ".md")
            lines = text.split("\n")
            self.assertIn(HEADING, lines, tool)
            self.assertLess(lines.index(HEADING), lines.index("## 1. What it is for, and for whom"), tool)
            body = section(text, HEADING)
            self.assertEqual([ln for ln in body if ln.startswith("|")][0], "| Roadmap item 2 asks | What the tool has | Where | Today | What it lacks |", tool)
            r = rows(body)
            first = [c.strip().strip("*") for c in (x.strip().strip("|").split(" | ")[0] for x in r)]
            for ask in ("A method note signed by Samuel", "A replication a reader can run", "A cross-check table against published figures", "A decisions block"):
                self.assertIn(ask, first, tool)
            for x in r:
                cells = [c.strip() for c in x.strip().strip("|").split(" | ")]
                self.assertEqual(len(cells), 5, f"{tool}: {x[:80]}")
                self.assertTrue(all(cells), f"{tool}: an empty cell: {x[:80]}")
            replication = next(x for x in r if "A replication a reader can run" in x)
            self.assertRegex(replication, r"exit (code )?\d", tool)
            signed = next(x for x in r if "A method note signed by Samuel" in x)
            self.assertIn("not signed", signed, tool)

    def test_the_two_tools_named_apart(self):
        self.assertIn("Automated Analysis in its final form", "\n".join(section(src("docs", "reviews", "packs", "research.md"), HEADING)))
        self.assertIn("The Grid tool one page", "\n".join(section(src("docs", "reviews", "packs", "grid.md"), HEADING)))


class TheNewCrossChecks(unittest.TestCase):
    def test_the_form_of_the_decision_tools(self):
        for note, least in (("grid_network.md", 10), ("automated_analysis_findings.md", 4)):
            text = src("docs", "methods", note)
            self.assertIn('<a id="cross-checks"></a>', text, note)
            body = section(text, "## Cross-checks")
            table = [ln for ln in body if ln.startswith("|")]
            self.assertEqual(table[0], "| Our figure | Published figure | Source and date | Gap | Reason |", note)
            r = table[2:]
            self.assertGreaterEqual(len(r), least, note)
            for x in r:
                cells = [c.strip() for c in x.strip().strip("|").split(" | ")]
                self.assertEqual(len(cells), 5, f"{note}: {x[:80]}")
                self.assertTrue(all(cells), f"{note}: {x[:80]}")
                self.assertTrue(len(cells[4]) > 30, f"{note}: a reason too short: {x[:80]}")
                self.assertTrue("https://" in cells[2] or cells[2] == "the same" or "docs/methods/" in cells[2], f"{note}: no source: {x[:80]}")


class NoEmDash(unittest.TestCase):
    def test_no_em_dash(self):
        for rel in WRITTEN:
            path = os.path.join(ROOT, *rel.split("/"))
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    self.assertEqual(f.read().count(chr(0x2014)), 0, rel)


if __name__ == "__main__":
    unittest.main()
