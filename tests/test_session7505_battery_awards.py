"""Session 7505 (chain 304, part A): /cost-of-power/battery/awards taken to the done line.

Held here: the page's sections drawn to HTML with the site's own code on made-up rows
(site/scripts/test-battery-awards-render.mjs: fault 1, the decisions block, the method note's list); the replication's
files (every figure of the page inside half its last shown digit, the monthly tables' rows equal to ERCOT's disclosure
rows, the replication run again on the public rows copied beside it); the do-file's expected values; the method note
and the faults file. No table of the warehouse is needed: every table the tool reads is public, and the rows the page
reads are beside the replication.
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
REP = os.path.join(ROOT, "replication", "battery_awards")
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
    """The real-time section and the decisions block drawn without a build."""

    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-battery-awards-render.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600)
        cls.code, cls.out, cls.err = r.returncode, r.stdout, r.stderr

    def test_every_check_passes(self):
        self.assertEqual(self.code, 0, self.out[-3000:] + self.err[-1500:])
        self.assertNotIn("FAIL", self.out)
        m = re.search(r"(\d+) of (\d+) passed", self.out)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 25, self.out[-500:])

    def test_fault_1_is_held(self):
        self.assertGreaterEqual(len(re.findall(r"(?m)^ok   fault 1: ", self.out)), 5)


class ThePage(unittest.TestCase):
    def test_the_fix_and_the_block_are_in_the_source(self):
        rt, page = src("site", "app", "cost-of-power", "battery", "awards", "RealTime.tsx"), src("site", "app", "cost-of-power", "battery", "awards", "page.tsx")
        self.assertIn("basis.wholeDays <= 7", rt)
        self.assertIn("One week is one week.", rt)                               # a table of one week reads as it did (tests/test_session120_page.py)
        self.assertIn("days of one autumn", rt)
        self.assertIn("<AwardsDecisions />", page)
        self.assertRegex(src("site", "lib", "release.ts"), r'"/cost-of-power/battery/awards":\s*"review"')

    def test_the_decisions_each_have_a_default_and_a_source(self):
        d = src("site", "app", "cost-of-power", "battery", "awards", "Decisions.tsx")
        n = len(re.findall(r'\{ key: "', d))
        self.assertEqual(n, 15)
        self.assertEqual(len(re.findall(r'\n    def: "', d.replace("\r\n", "\n"))), n)
        self.assertEqual(len(re.findall(r'\n    source: "', d.replace("\r\n", "\n"))), n)
        self.assertNotIn("text-muted", d)                                        # the page standard: no grey text, tips only


class TheReplication(unittest.TestCase):
    def test_every_figure_of_the_page_is_inside_half_its_last_digit(self):
        fig = json.loads(src("replication", "battery_awards", "page_figures.json"))
        table = rows("page_figures.csv")
        page = [r for r in table if not r["key"].startswith("beside|")]
        self.assertEqual({r["key"] for r in page}, set(fig["figures"]))
        self.assertGreaterEqual(len(page), 300)
        for r in table:
            self.assertEqual(r["verdict"], "within half the last digit", r)
            if not r["key"].startswith("beside|"):
                self.assertEqual(r["page"], fig["figures"][r["key"]], r["key"])
        self.assertEqual(len(table) - len(page), 24)                             # the six cases of site/data/battery_awards_beside.json
        self.assertEqual(fig["drawn"]["missing"], [])

    def test_the_monthly_tables_equal_the_disclosure_rows(self):
        table = rows("source_rows.csv")
        self.assertEqual({r["verdict"] for r in table}, {"agrees"})
        months = {(r["table"], r["month"]) for r in table}
        self.assertGreaterEqual(len({m for t, m in months if t == "ercot_storage_dam_awards_monthly"}), 3)   # the brief asks for at least three months
        self.assertGreaterEqual(len({m for t, m in months if t == "ercot_storage_rt_monthly"}), 3)
        held = {(r["table"], r["variable"]) for r in table}
        for need in (("ercot_storage_dam_awards_monthly", "revenue_total_usd_per_mw"), ("ercot_storage_dam_awards_monthly", "mw"),
                     ("ercot_storage_dam_awards_monthly", "resource_hours_energy_award"), ("ercot_storage_rt_monthly", "revenue_rt_deviation_hub_usd_per_mw"),
                     ("ercot_storage_rt_monthly", "rt_discharge_mwh")):
            self.assertIn(need, held)

    def test_it_runs_again_on_the_public_rows_beside_it(self):
        env = dict(os.environ, ERW_SPEND_CAP_USD="0")
        r = subprocess.run([sys.executable, os.path.join(REP, "replicate.py")], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=300, env=env)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        m = re.search(r"The page: (\d+) of (\d+) figures within half the page's last shown digit, 0 named, 0 failed", r.stdout)
        self.assertTrue(m and m.group(1) == m.group(2), r.stdout)
        self.assertIn("The file battery_awards_beside.json: 24 of 24 figures", r.stdout)

    def test_the_rows_beside_it_are_the_five_public_tables(self):
        table = rows("monthly_rows.csv")
        self.assertEqual({r["table"] for r in table}, {"ercot_storage_dam_awards_monthly", "ercot_storage_dam_offers_monthly", "ercot_storage_rt_monthly", "ercot_storage_node_basis", "battery_stack_monthly"})
        self.assertEqual({r["entity"] for r in table}, {"ercot:esr_fleet", "ercot:esr_nodes", "ercot:HB_HUBAVG"})   # the fleet, never a named resource
        script = src("replication", "battery_awards", "replicate.py")
        self.assertNotIn("site/lib", script)                                     # written from the notes, not from the page's code
        self.assertNotIn("import requests", script)

    def test_the_do_file_states_the_figures_the_replication_gives(self):
        do = src("replication", "battery_awards", "replicate.do")
        ours = {r["key"]: float(r["ours"]) for r in rows("page_figures.csv")}
        for key, places in (("month|2026-07|total_kw", 4), ("year|2026|awarded_whole_kw", 4), ("year|2026|model_whole_kw", 4), ("offers|gap_kw", 4), ("offers|part|never_kw", 4),
                            ("offers|part|unawarded_kw", 4), ("offers|part|price_kw", 4), ("rt|whole|dayahead_kw", 4), ("rt|whole|deviation_kw", 4), ("rt|whole|market_kw", 4), ("rt|whole|model_kw", 4)):
            self.assertIn(f"({ours[key]:.{places}f})", do, key)
        self.assertIn("has not been run", do)
        self.assertIn('import delimited using "monthly_rows.csv"', do)


class TheNoteAndTheFaults(unittest.TestCase):
    def test_no_dash_in_any_file_of_the_session(self):
        for parts in (("docs", "methods", "battery_awards.md"), ("docs", "reviews", "battery-awards-faults-2026-11-16.md"), ("replication", "battery_awards", "replicate.py"),
                      ("replication", "battery_awards", "replicate.do"), ("site", "app", "cost-of-power", "battery", "awards", "Decisions.tsx"),
                      ("site", "scripts", "battery-awards-figures.mjs"), ("site", "scripts", "test-battery-awards-render.mjs"), ("archive", "sessions", "SESSION_7505_REPORT.md")):
            text = src(*parts)
            for d in DASHES:
                self.assertNotIn(d, text, parts[-1])

    def test_the_note_says_what_the_replication_found(self):
        note = src("docs", "methods", "battery_awards.md")
        # session 7514: 307 of 307 until the read of 16 November 2026 added 66 figures to the page (the note's section 8)
        self.assertIn("373 of 373 figures within half the page's last shown digit, 0 named, 0 failed", note)
        self.assertRegex(note, r"Session 7505\s+counted 307 of 307")
        self.assertIn("297 of 297 rows agree", note)
        self.assertIn("Nothing published stands against them", note)
        for publisher in ("Potomac Economics", "U.S. Energy Information Administration", "Modo Energy"):
            self.assertIn(publisher, note)
        self.assertNotRegex(note, r"(?m)^Tables: ")                              # the tables' own notes stay the ones the coverage page links

    def test_the_faults_file_numbers_its_rows(self):
        faults = src("docs", "reviews", "battery-awards-faults-2026-11-16.md")
        kinds = re.findall(r"(?m)^\| (\d+) \| (site, fixed|note, completed|data machine|ruling) \|", faults)
        # session 7602 (chain 305, browser read row 55): row 10, the battery page's snapshot a month behind, for the data machine
        self.assertEqual([int(n) for n, _ in kinds], list(range(1, 11)))
        self.assertEqual(sum(k == "site, fixed" for _, k in kinds), 1)
        self.assertEqual(sum(k == "data machine" for _, k in kinds), 2)
        self.assertEqual(sum(k == "ruling" for _, k in kinds), 5)


if __name__ == "__main__":
    unittest.main()
