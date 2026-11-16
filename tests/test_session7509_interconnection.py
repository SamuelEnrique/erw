"""Session 7509 (chain 304, 16 November 2026): the interconnection queue explorer, /explore/interconnection, at the done
line. What is held here:

- a figure is written by its variable (lib/explore/interconnection.ts, figureText): positions whole; MW, the withdrawn
  share and the wait always with two decimals, a whole value included, and the text still begins with what
  site/scripts/check-values.mjs expects of the raw value;
- the two year filters show the years as the page reads them when the address names them the other way round;
- the page says what "Entered" does not hold for CAISO and for ERCOT, and its source line no longer says the queues
  are "as the ERW last pulled them" (the table is as old as its last build);
- the decisions block is the page's own file, mounted under the figures and under a held queue's line, and its keys
  are the method note's;
- the replication's committed figures are N of N, hold no figure of a held queue, and, where the tables are on the
  machine (replication/interconnection/rows/, not in git), the replication runs to N of N on the page as its own code
  draws it.
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "interconnection")
ROWS = os.path.join(REP, "rows", "iso_queue_statistics.csv")
DASHES = (chr(0x2014), chr(0x2013))
FILES = [
    ("site", "app", "explore", "interconnection", "page.tsx"), ("site", "app", "explore", "interconnection", "Decisions.tsx"),
    ("site", "lib", "explore", "interconnection.ts"), ("site", "scripts", "interconnection-figures.mjs"),
    ("replication", "interconnection", "replicate.py"), ("replication", "interconnection", "fetch_rows.py"),
    ("replication", "interconnection", "cross_check.py"), ("replication", "interconnection", "replicate.do"),
    ("docs", "methods", "interconnection_explorer.md"), ("docs", "reviews", "interconnection-faults-2026-11-16.md"),
    ("tests", "test_session7509_interconnection.py"),
]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_eval(code):
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node is not on the path")
    out = subprocess.run([node, "--no-warnings", "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise AssertionError(out.stderr[-800:])
    return json.loads(out.stdout)


class TheFigureText(unittest.TestCase):
    def test_a_figure_is_written_by_its_variable(self):
        r = node_eval(
            'const m = await import("./lib/explore/interconnection.ts");'
            'const f = m.figureText;'
            'console.log(JSON.stringify([f("positions_entered", 1234), f("wait_positions", 7), f("mw_entered", 550), f("mw_entered", 64734.01),'
            ' f("withdrawal_rate", 1), f("withdrawal_rate", 0), f("withdrawal_rate", 0.625), f("wait_years_median", 5.059548), f("mw_withdrawn", 4006)]));')
        self.assertEqual(r, ["1,234", "7", "550.00", "64,734.01", "1.00", "0.00", "0.63", "5.06", "4,006.00"])

    def test_the_text_still_begins_with_what_check_values_expects(self):
        # scripts/check-values.mjs: text.startsWith(shown(raw)), shown being a whole number with commas, else two decimals
        r = node_eval(
            'const m = await import("./lib/explore/interconnection.ts");'
            'const shown = (x) => Number.isInteger(x) ? x.toLocaleString("en-US") : x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });'
            'const cases = [["positions_entered", 4], ["mw_entered", 550], ["mw_entered", 11456.085], ["withdrawal_rate", 1], ["withdrawal_rate", 0.719424], ["wait_years_median", 3], ["wait_positions", 0]];'
            'console.log(JSON.stringify(cases.map(([v, x]) => m.figureText(v, x).startsWith(shown(x)))));')
        self.assertEqual(r, [True] * 7)
        self.assertIn("text.startsWith(usdFormat ? usd(Number(raw)) : whole ? Math.round(Number(raw)).toLocaleString(\"en-US\") : shown(raw))", src("site", "scripts", "check-values.mjs"))


class ThePage(unittest.TestCase):
    def setUp(self):
        self.p = src("site", "app", "explore", "interconnection", "page.tsx")
        self.lib = src("site", "lib", "explore", "interconnection.ts")

    def test_every_row_figure_is_written_by_figureText(self):
        self.assertIn("<Num check={key(q, y, v)} raw={x} source={sourceWords(q, y, v)}>{figureText(v, x)}</Num>", self.p)
        self.assertEqual(self.p.count("shown("), 1, "only the header's count, a whole number, is written by shown()")

    def test_the_year_filters_show_the_years_as_read(self):
        self.assertIn('{ name: "from", label: "First entry year", value: String(lo), options: years.map(yearOpt) },', self.p)
        self.assertIn('{ name: "to", label: "Last entry year", value: String(hi), options: years.map(yearOpt) },', self.p)

    def test_what_entered_does_not_hold_is_said(self):
        r = node_eval('const m = await import("./lib/explore/interconnection.ts"); console.log(JSON.stringify(m.NOT_HELD));')
        self.assertIn("far fewer than the requests made that year", r["caiso"])
        self.assertIn("not every request made that year", r["ercot"])
        self.assertIn("{notHeld}", self.p)

    def test_the_source_line_names_the_build_not_the_last_pull(self):
        self.assertNotIn("as the ERW last pulled them", self.p)
        self.assertIn("as the ERW held them when this table was built", self.p)

    def test_a_weekly_table_is_stale_after_eight_days_not_three(self):
        self.assertIn("staleAfterDays={8}", self.p)
        self.assertIn('echo "iso_queues: weekly (Mondays UTC)', src("warehouse", "run_daily.sh"))

    def test_the_decisions_block_is_mounted_under_the_figures_and_under_a_hold(self):
        self.assertIn('import { InterconnectionDecisions } from "@/app/explore/interconnection/Decisions";', self.p)
        self.assertEqual(self.p.count("<InterconnectionDecisions />"), 2)
        self.assertIn("), true);", self.p)
        for i in re.findall(r'from "([^"]+)"', self.p):
            self.assertFalse(i.startswith("./"), i)   # tests/test_session405.py: no private import


class TheDecisions(unittest.TestCase):
    def test_each_choice_has_a_default_and_a_source_and_the_note_lists_the_same_keys(self):
        d = src("site", "app", "explore", "interconnection", "Decisions.tsx")
        keys = re.findall(r'\{ key: "([a-z-]+)",', d)
        self.assertEqual(len(keys), 12)
        self.assertEqual(len(set(keys)), 12)
        self.assertEqual(d.count("\n    def: \""), 12)
        self.assertEqual(d.count("\n    source: \""), 12)
        note = src("docs", "methods", "interconnection_explorer.md")
        section = note[note.index("## The decisions on the page"):]
        section = section[:section.index("\n## ", 5)]
        self.assertEqual(re.findall(r"^\d+\. `([a-z-]+)`", section, re.M), keys)
        self.assertIn("data-decision-default={d.key}", d)
        self.assertIn("data-decision-source={d.key}", d)
        self.assertNotIn("lib/decisions\"", d, "the list is the page's own file, not the shared one")

    def test_no_dash_in_what_this_session_wrote(self):
        for parts in FILES:
            s = src(*parts)
            for dash in DASHES:
                self.assertNotIn(dash, s, "/".join(parts))


class TheReplication(unittest.TestCase):
    def test_the_committed_figures_are_n_of_n_and_hold_no_held_queue(self):
        with open(os.path.join(REP, "page_figures.json"), encoding="utf-8") as f:
            j = json.load(f)
        self.assertEqual(j["figures"], j["figures_inside_the_tolerance"])
        self.assertEqual(j["views"], j["views_as_the_note_says"])
        self.assertGreaterEqual(j["figures"], 700)
        self.assertEqual(j["held"], ["isone", "miso", "nyiso"])
        with open(os.path.join(REP, "page_figures.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), j["figures"])
        self.assertEqual({r["queue"] for r in rows}, {"caiso", "ercot", "spp"})
        with open(os.path.join(SITE, "data", "license_status.json"), encoding="utf-8") as f:
            lic = json.load(f)["tables"]
        for q in ("caiso", "ercot", "spp"):
            self.assertEqual(lic[f"{q}_interconnection_queue"]["status"], "public")
        for r in rows:
            shown = float(r["page"].replace(",", ""))
            self.assertLessEqual(abs(shown - float(r["replication"])), float(r["tolerance"]) + 1e-9, r)
        self.assertEqual(src("replication", "interconnection", "rows", ".gitignore").split("\n")[-3:-1], ["*", "!.gitignore"])

    @unittest.skipUnless(os.path.exists(ROWS) and shutil.which("node"), "the tables are not in replication/interconnection/rows (fetch_rows.py), or node is not on the path")
    def test_the_replication_runs_to_n_of_n_on_the_page_as_drawn(self):
        import tempfile
        out = os.path.join(tempfile.mkdtemp(prefix="erw7509_"), "page.json")
        r = subprocess.run([shutil.which("node"), "--no-warnings", "--import", "./scripts/tsx-register.mjs", "scripts/interconnection-figures.mjs", ROWS, out],
                           cwd=SITE, capture_output=True, text=True, timeout=1500)
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        with open(out, encoding="utf-8") as f:
            page = json.load(f)
        by = {"&".join(f"{k}={v}" for k, v in x["q"].items()): x for x in page["views"]}
        opening = by[""]
        self.assertEqual(opening["decisions"], 12)
        self.assertEqual(by["queue=nyiso&measure=positions"]["decisions"], 12)
        self.assertEqual(by["queue=nyiso&measure=positions"]["keyed"], 0)
        self.assertEqual(opening["not_held_line"], "caiso")
        # the years the other way round: the filters read as the page does
        back = by["queue=caiso&from=2020&to=2010"]
        self.assertEqual((back["filters"]["from"]["chosen"], back["filters"]["to"]["chosen"]), ("2010", "2020"))
        # a whole value keeps its decimals where its column has them, and a count has none
        for key, f in page["keyed"].items():
            variable = key.split("|")[3]
            if key.startswith("series|") and not (variable.startswith("positions_") or variable == "wait_positions"):
                self.assertRegex(f["text"], r"^-?[\d,]+\.\d\d$", key)
            else:
                self.assertRegex(f["text"], r"^[\d,]+$", key)
        r = subprocess.run([sys.executable, os.path.join(REP, "replicate.py"), "--page", out], capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-1500:])
        m = re.search(r"part A: ([\d,]+) of ([\d,]+) figures inside the tolerance; (\d+) of (\d+) views", r.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) and m.group(3) == m.group(4), r.stdout[-600:])


if __name__ == "__main__":
    unittest.main()
