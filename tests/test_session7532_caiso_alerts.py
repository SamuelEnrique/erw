"""Session 7532 (chain 304, part A): /grid/caiso/alerts, the Flex Alert scorecard, taken to the done line.

Held here: the page drawn to HTML with its own function on made-up rows (site/scripts/test-caiso-alerts-render.mjs:
faults 1, 2 and 4, the decisions block, the method note's list); the replication run again on the public rows copied
beside it (every rebuilt figure inside half the page's last shown digit or named, none failing); the do-file's expected
values against the replication's own figures; CAISO's yearly counts as transcribed; the method note, the faults file
and the cross-check. No table of the warehouse is needed.
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
REP = os.path.join(ROOT, "replication", "caiso_alerts")
NODE = shutil.which("node")
DASHES = (chr(0x2014), chr(0x2013))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def rows(name):
    with open(os.path.join(REP, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageDrawn(unittest.TestCase):
    """The whole page drawn without a build, on made-up rows."""

    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, "--import", "./scripts/battery-awards-page-register.mjs", "scripts/test-caiso-alerts-render.mjs"], cwd=SITE,
                           capture_output=True, text=True, encoding="utf-8", timeout=600)
        cls.code, cls.out, cls.err = r.returncode, r.stdout, r.stderr

    def test_every_check_passes(self):
        self.assertEqual(self.code, 0, self.out[-3000:] + self.err[-1500:])
        self.assertNotIn("FAIL", self.out)
        m = re.search(r"(\d+) of (\d+) passed", self.out)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 28, self.out[-500:])

    def test_the_faults_are_held(self):
        for f, at_least in (("fault 1: ", 2), ("fault 2: ", 5), ("fault 4: ", 1)):
            self.assertGreaterEqual(len(re.findall(r"(?m)^ok   " + re.escape(f), self.out)), at_least, f)


class ThePageSource(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "grid", "caiso", "alerts", "page.tsx")

    def test_the_fixes_are_in_the_source(self):
        self.assertIn("return Math.round(v).toLocaleString(\"en-US\");", self.page)                 # fault 1
        self.assertNotIn("CAISO, 2018 to 2024</h1>", self.page)                                     # fault 2: the title from the rows
        self.assertNotIn("runs to 2025-04-30, so the 2025 season has none here", self.page)        # fault 2: the caution from the rows
        self.assertNotIn('gridNotices("2018-07-01", "2025-10-31")', self.page)
        self.assertIn('id="alerts-left-out"', self.page)                                            # fault 4
        self.assertIn("<AlertsDecisions />", self.page)

    def test_nothing_the_page_had_is_dropped(self):
        for kept in ("The answer, pooled", "Every alert day, ranked", "Year by year", "Each alert day through the evening",
                     "What it was worth, at the day-ahead price", "The model's check: the hottest days it did not see",
                     "What the estimate can and cannot say", "<YearChart", "<DayChart", "<CheckChart", "<Cite tables="):
            self.assertIn(kept, self.page)

    def test_no_dashes_in_what_this_session_wrote(self):
        for p in (("site", "app", "grid", "caiso", "alerts", "page.tsx"), ("site", "app", "grid", "caiso", "alerts", "Decisions.tsx"),
                  ("site", "scripts", "caiso-alerts-figures.mjs"), ("site", "scripts", "test-caiso-alerts-render.mjs"),
                  ("docs", "methods", "caiso_alerts.md"), ("docs", "reviews", "caiso-alerts-faults-2026-11-16.md"),
                  ("docs", "reviews", "caiso-alerts-crosscheck-2026-11-16.md"), ("replication", "caiso_alerts", "replicate.py"),
                  ("replication", "caiso_alerts", "replicate.do")):
            text = src(*p)
            for d in DASHES:
                self.assertNotIn(d, text, "/".join(p))


class TheReplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([sys.executable, os.path.join(REP, "replicate.py")], capture_output=True, text=True, encoding="utf-8", timeout=600)
        cls.code, cls.out = r.returncode, r.stdout + r.stderr

    def test_it_runs_on_the_rows_beside_it(self):
        self.assertEqual(self.code, 0, self.out[-2000:])
        m = re.search(r"figures of the page: (\d+)\. Rebuilt from the public tables: (\d+), of which (\d+) agree inside half the page's last shown digit, "
                      r"(\d+) differ and are named, (\d+) fail\. Not rebuildable from the public tables, named: (\d+)\.", self.out)
        self.assertTrue(m, self.out[-1500:])
        total, rebuilt, agree, named_diff, fail, named = map(int, m.groups())
        self.assertEqual(fail, 0)
        self.assertEqual(rebuilt, agree + named_diff)
        self.assertEqual(total, rebuilt + named)
        self.assertGreaterEqual(agree, 460)
        self.assertLessEqual(named_diff, 4)

    def test_the_alert_days_by_the_rule(self):
        self.assertIn("by the rule from the notices, 2018-07-01 to 2025-10-31: 39; held by the table: 38; by the rule and not held: 2021-07-12; held and not by the rule: none", self.out)
        self.assertIn("alert days in the notices after the sample (2025-10-31): 0", self.out)

    def test_every_named_figure_has_its_reason(self):
        for r in rows("page_figures.csv"):
            self.assertTrue(r["status"] == "agrees" or r["status"].startswith("named: ") or r["status"].startswith("named difference: "), r)
            if r["status"].startswith("named"):
                self.assertGreater(len(r["status"]), 30, r)

    def test_the_figures_file_is_the_pages(self):
        with open(os.path.join(REP, "page_figures.json"), encoding="utf-8") as f:
            fig = json.load(f)
        self.assertEqual(fig["drawn_by"], "site/scripts/caiso-alerts-figures.mjs (session 7532)")
        self.assertEqual(len(fig["ranked"]), 38)
        self.assertGreaterEqual(len(fig["nums"]), 430)
        self.assertEqual(fig["words"]["report_ends"], "2026-10-08")

    def test_the_do_files_expected_values(self):
        do = src("replication", "caiso_alerts", "replicate.do")
        ours = {r["key"]: r["ours"] for r in rows("page_figures.csv")}
        k = lambda v: f"series|flex_alert_model|erw:flex_alert_model|{v}|2018-07-01T00:00:00Z"
        for v, shown in (("pooled_reduction_mw", "-503.1849"), ("pooled_reduction_mwh", "-102649.7289"), ("pooled_reduction_pct", "-1.2012"),
                         ("oos_bias_mw", "-239.3376"), ("heldout_threshold_temp_f", "87.008")):
            self.assertIn(shown, do, v)
            self.assertAlmostEqual(float(ours[k(v)]), float(shown), places=3)
        self.assertAlmostEqual(float(ours[k("pooled_value_usd")]), -5469360.66, places=1)
        self.assertIn("-5,469,360.66", do)
        for y, d in (("2018", 2), ("2019", 2), ("2020", 11), ("2021", 8), ("2022", 11), ("2023", 3), ("2024", 1)):
            self.assertEqual(float(ours[f"series|flex_alert_effects|eia930:CISO|year_days|{y}-01-01T00:00:00Z"]), d)

    def test_caisos_yearly_counts(self):
        cc = rows("crosscheck_rows.csv")
        self.assertEqual(len(cc), 71)
        self.assertEqual(sum(1 for r in cc if r["agrees"] == "yes"), 66)
        differ = {(r["year"], r["event_type"]) for r in cc if r["agrees"] != "yes"}
        self.assertEqual(differ, {("2018", "transmission_emergency"), ("2019", "transmission_emergency"), ("2020", "rmo"),
                                  ("2022", "transmission_emergency"), ("2022", "eea2")})
        flex = {r["year"]: int(r["caiso_days"]) for r in rows("gehr_summary_2026-10-09.csv") if r["event_type"] == "flex_alert"}
        self.assertEqual(flex, {"2018": 2, "2019": 1, "2020": 10, "2021": 8, "2022": 11, "2023": 0, "2024": 0, "2025": 0, "2026": 0})


class TheNotes(unittest.TestCase):
    def test_the_method_note(self):
        note = src("docs", "methods", "caiso_alerts.md")
        for s in ("## 6. The decisions on the page", "## 7. What the tool does not hold", "flex_alert_scorecard.md", "caiso_grid_emergencies.md",
                  "caiso_dam_alert_day_hub_prices.md", "467 agree", "4 differ and are named"):
            self.assertIn(s, note)

    def test_the_scorecard_note_is_extended_not_rewritten(self):
        note = src("docs", "methods", "flex_alert_scorecard.md")
        self.assertIn("The report ends 2025-04-30, so the 2025 season has no alert days.", note)   # kept as written
        self.assertIn("revised on 9 October 2026", note)

    def test_the_faults_file(self):
        f = src("docs", "reviews", "caiso-alerts-faults-2026-11-16.md")
        self.assertIn("| # | Kind | The cell or click | What is wrong | What was done |", f)
        self.assertEqual(len(re.findall(r"(?m)^\| \d+ \| ", f)), 11)
        self.assertIn("data machine", f)

    def test_the_crosscheck(self):
        c = src("docs", "reviews", "caiso-alerts-crosscheck-2026-11-16.md")
        for s in ("Grid Emergencies History Report", "10/09/2026", "U.S. Energy Information Administration", "robots"):
            self.assertIn(s, c)


if __name__ == "__main__":
    unittest.main()
