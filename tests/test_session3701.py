"""Session 3701 (chain 208): Research's replication a reader can run (replication/analysis/). It reads only the page's
public downloads (the finding cards' CSVs and the week's chart file) and its own assumptions, recomputes every figure
/research prints, and meets each to half of the last shown digit; a figure the page prints as "license needed" is printed
so and not computed. replicate.py uses the standard library and pandas only; replicate.do keeps the owner's Stata rules.

The figures are built afresh from the cards' own files for the checks, so a card the data machine recomputes is held to
its new figures and never turns main red by itself; the committed page_figures.json is compared with the cards only for
the cards whose computed_at it recorded. No network, no warehouse table, no model.
"""
import ast
import copy
import csv
import importlib.util
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "replication", "analysis")
FINDINGS = os.path.join(ROOT, "site", "public", "findings")
CARDS = os.path.join(ROOT, "site", "data", "findings")


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REP, file))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheReplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (os.path.isdir(FINDINGS) and os.path.isdir(CARDS)):
            raise unittest.SkipTest("the findings' downloads are not in this copy")
        try:
            import pandas  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("pandas is not installed")
        cls.r = module("replicate_analysis", "replicate.py")
        cls.b = module("figures_of_the_page", "figures_of_the_page.py")
        cls.a = cls.r.load_json(os.path.join(REP, "assumptions.json"))
        cls.committed = cls.r.load_json(os.path.join(REP, "page_figures.json"))
        cls.page = json.loads(cls.b.build(cls.committed["written_for_day"])[0])
        cls.csv_base, cls.week_base = cls.r.default_bases()
        cls.n = cls.r.compute(cls.csv_base, cls.week_base, cls.page, cls.a)
        cls.rows = cls.r.compare(cls.n, cls.page)

    def test_every_computed_figure_inside_its_tolerance(self):
        bad = [(f["card"], f["field"], got, f["page"]) for f, status, got, _ in self.rows if status.startswith("NO")]
        self.assertEqual(bad, [])
        computed = [r for r in self.rows if r[1] == "yes"]
        self.assertGreaterEqual(len(computed), 60)
        # the one known difference is the weekly score's, and only when its file holds fewer changes than the rule ranked
        for f, status, _, _ in self.rows:
            if status.startswith("no: a known"):
                self.assertEqual(f["field"], "score")

    def test_a_held_figure_is_license_needed_and_not_computed(self):
        held = [r for r in self.rows if r[0]["held"]]
        self.assertTrue(held)
        for f, status, got, diff in held:
            self.assertEqual(status, "license needed")
            self.assertIsNone(got)
            self.assertIsNone(f["page"])
            self.assertEqual(f["page_text"], "license needed")
            self.assertIn(f["key"].rsplit("|", 1)[1], self.page["held_grids"])

    def test_the_committed_figures_are_the_cards_unless_a_card_was_recomputed(self):
        fresh = {(f["card"], f["callout"], f["side"], f["part"]): f for f in self.page["figures"]}
        stale = []
        for f in self.committed["figures"]:
            when = self.committed["cards_computed_at"].get(f["card"])
            if f["card"] != "chart_of_the_week" and when != self.page["cards_computed_at"].get(f["card"]):
                continue   # the data machine recomputed the card: figures_of_the_page.py writes the file again
            g = fresh.get((f["card"], f["callout"], f["side"], f["part"]))
            if g is None or any(f[k] != g[k] for k in ("page_text", "page", "field", "held", "tolerance")):
                if f["card"] == "chart_of_the_week" and self.committed["week"] != self.page["week"]:
                    continue   # a newer Roundup's chart
                stale.append((f["card"], f["field"]))
        self.assertEqual(stale, [])

    def test_the_assumptions_drive_the_figures(self):
        a = copy.deepcopy(self.a)
        a["batteries_curtailment_hourly_ceiling_pct"]["value"] = 95
        rows = self.r.read_csv(self.csv_base, "erw_2026_caiso_curtailment_hourly.csv")
        n95 = self.r.batteries_curtailment_hourly(rows, a)
        n90 = self.n["batteries_curtailment_hourly"]
        self.assertLess(n95["y2025_sat_curt_hours"], n90["y2025_sat_curt_hours"])
        self.assertEqual(n95["y2025_obs_charging_mw"], n90["y2025_obs_charging_mw"])   # the observed mean does not move with the ceiling

    def test_the_script_exits_0_and_says_license_needed(self):
        p = subprocess.run([sys.executable, os.path.join(REP, "replicate.py")], capture_output=True, text=True, encoding="utf-8", timeout=600)
        self.assertEqual(p.returncode, 0, p.stdout[-3000:] + p.stderr[-2000:])
        self.assertIn("license needed", p.stdout)
        self.assertRegex(p.stdout, r"\d+ of \d+ computed figures inside the tolerance")
        for line in p.stdout.splitlines():
            if "|nyiso" in line or "|isone" in line or "|miso" in line:
                self.assertTrue(line.endswith("| license needed"), line)


class TheFiles(unittest.TestCase):
    def test_python_imports_the_standard_library_and_pandas_only(self):
        for name in ("replicate.py", "figures_of_the_page.py"):
            with open(os.path.join(REP, name), encoding="utf-8") as f:
                tree = ast.parse(f.read())
            mods = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    mods.update(a.name.split(".")[0] for a in node.names)
                elif isinstance(node, ast.ImportFrom):
                    mods.add((node.module or "").split(".")[0])
            other = {m for m in mods if m not in sys.stdlib_module_names and m != "pandas"}
            self.assertEqual(other, set(), name)

    def test_the_assumptions_csv_is_the_json(self):
        with open(os.path.join(REP, "assumptions.json"), encoding="utf-8") as f:
            a = json.load(f)
        with open(os.path.join(REP, "assumptions.csv"), encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertTrue(rows)
        for r in rows:
            self.assertEqual(float(r["value"]), float(a[r["name"]]["value"]), r["name"])
            self.assertLessEqual(len("a_" + r["stata"]), 32)
        for k, v in a.items():
            if k != "_about":
                self.assertTrue({"value", "unit", "source", "change"} <= set(v), k)

    def test_the_do_file_keeps_the_owners_rules(self):
        with open(os.path.join(REP, "replicate.do"), encoding="utf-8") as f:
            lines = f.read().splitlines()
        text = "\n".join(lines)
        self.assertNotIn("///", text)
        self.assertNotIn("\n\n\n", text)
        depth = 0
        for i, line in enumerate(lines):
            s = line.strip()
            if s.startswith("destring"):
                self.assertIn("force", s, f"line {i + 1}")
            if s.endswith("{"):
                depth += 1
                self.assertNotEqual(lines[i + 1].strip(), "", f"an empty line inside a loop at line {i + 2}")
                continue
            if s == "}":
                depth -= 1
                continue
            if depth:
                self.assertNotEqual(s, "", f"an empty line inside a loop at line {i + 1}")
            elif s and i + 1 < len(lines):
                self.assertEqual(lines[i + 1].strip(), "", f"two commands without an empty line between them at line {i + 1}")
        # every scalar the comparison reads is set above it
        set_ = set(re.findall(r"^scalar (\w+) =", text, re.M))
        used = set(re.findall(r"scalar\((\w+)\)", text))
        self.assertEqual(used - set_ - {n for n in used if n.startswith("a_")}, set())
        # every computed figure of page_figures.csv has its line in the comparison
        with open(os.path.join(REP, "page_figures.json"), encoding="utf-8") as f:
            page = json.load(f)
        for f in page["figures"]:
            if f["held"] or f["not_in_download"] or f["card"] == "chart_of_the_week":
                continue
            self.assertIn(f'card == "{f["card"]}" & field == "{f["field"]}"', text)


if __name__ == "__main__":
    unittest.main()
