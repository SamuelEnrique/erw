"""Session 7507 (chain 304): the ERCOT peak premium explorer (/explore/ercot-peak-premium) at the done line.

The page is drawn with the site's own code on real rows of its two tables (tests/fixtures/session7507: two hubs, as
built on 29 September 2026), and the replication (replication/ercot_peak_premium/replicate.py, written from the method
note) is run on the same rows: every view opens as the note says and every figure is inside the tolerance. A month of
each kind of clock change is recomputed from real 15-minute prices (from_hourly.py). The rest reads the files: the three
faults fixed on the page stay fixed; the page's decisions are the note's, each with a default and a source on hover and
no grey text; the do-file's expected lines are the ones the Python headline prints; the committed figures are whole; and
none of the session's files holds an em or an en dash.
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "session7507")
REPLICATION = os.path.join(ROOT, "replication", "ercot_peak_premium")
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)
COVERAGE = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")   # the catalogue the freshness line is read from
MINE = (
    ("site", "app", "explore", "ercot-peak-premium", "page.tsx"), ("site", "app", "explore", "ercot-peak-premium", "Decisions.tsx"),
    ("site", "lib", "explore", "peakpremium.ts"), ("site", "scripts", "peak-premium-figures.mjs"),
    ("docs", "methods", "ercot_peak_premium.md"), ("docs", "reviews", "ercot-peak-premium-faults-2026-11-16.md"),
    ("replication", "ercot_peak_premium", "replicate.py"), ("replication", "ercot_peak_premium", "from_hourly.py"),
    ("replication", "ercot_peak_premium", "replicate.do"), ("replication", "ercot_peak_premium", "page_figures.json"),
    ("replication", "ercot_peak_premium", "page_figures.csv"), ("tests", "test_session7507_peak_premium.py"),
)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def module(name):
    if REPLICATION not in sys.path:
        sys.path.insert(0, REPLICATION)
    return __import__(name)


def decision_keys():
    return re.findall(r'\{ key: "([a-z-]+)",', src("site", "app", "explore", "ercot-peak-premium", "Decisions.tsx"))


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageDrawnAndReplicated(unittest.TestCase):
    """The page itself on the fixture's rows (the views a reader opens, and three more), and the replication beside it."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="erw7507_")
        cls.page_file = os.path.join(cls.tmp, "page.json")
        cls.node = subprocess.run(
            [NODE, "--import", "./scripts/tsx-register.mjs", "scripts/peak-premium-figures.mjs", os.path.join(FIXTURE, "ercot_peak_premium_annual.csv"),
             os.path.join(FIXTURE, "ercot_peak_premium_monthly.csv"), cls.page_file, "--opening", f"--html={cls.tmp}", f"--coverage={COVERAGE}"],
            cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=900)
        cls.page = None
        if cls.node.returncode == 0:
            with open(cls.page_file, encoding="utf-8") as f:
                cls.page = json.load(f)
        env = dict(os.environ, ERW_SPEND_CAP_USD="0")
        cls.rep = subprocess.run([sys.executable, os.path.join(REPLICATION, "replicate.py"), "--in-dir", FIXTURE, "--page", cls.page_file, "--coverage", COVERAGE],
                                 capture_output=True, text=True, encoding="utf-8", timeout=600, env=env)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def view(self, why):
        return next(v for v in self.page["views"] if v["why"] == why)

    def test_every_view_draws(self):
        self.assertEqual(self.node.returncode, 0, self.node.stdout[-2000:] + self.node.stderr[-2000:])
        # the opening, two hubs by thirteen periods, three more; since session 7516 the views with a second hub: the two
        # ordered pairs, one pair by the twelve months, four more
        self.assertEqual(len(self.page["views"]), 1 + 2 * 13 + 3 + 2 + 12 + 4)
        self.assertEqual(self.page["conflicts"], [])                   # no figure is shown two ways in two views
        for v in self.page["views"]:
            self.assertTrue(v["thesis_chart"], v["q"])
            section = v["two_hubs"] is not None and v["two_hubs"]["table"]
            self.assertEqual(section, bool(v["q"].get("vs")) and v["why"] not in ("the same hub twice", "a second hub the tables do not hold"), v["q"])
            # two years, or one year alone; with a second hub, 13 figures more for each hub and year
            self.assertIn(v["keyed"] + v["not_held"], (64 + 52, 32 + 26) if section else (64, 32), v["q"])

    def test_the_page_opens_on_the_thesis(self):
        v = self.view("the page as it opens")
        self.assertEqual((v["filters"]["hub"]["chosen"], v["filters"]["month"]["chosen"], v["filters"]["from"]["chosen"], v["filters"]["to"]["chosen"]),
                         ("ercot:HB_HUBAVG", "", "2015", "2025"))
        self.assertEqual(v["filters"]["to"]["marked"], ["2026 (partial)"])
        k = self.page["keyed"]
        self.assertEqual(k["series|ercot_peak_premium_annual|ercot:HB_HUBAVG|peak_iqr|2025-01-01T00:00:00Z"]["text"], "34.12")
        self.assertEqual(k["series|ercot_peak_premium_annual|ercot:HB_HUBAVG|peak_minus_midday_median|2015-01-01T00:00:00Z"]["text"], "-0.16")
        self.assertEqual(k["series|ercot_peak_premium_annual|ercot:HB_HUBAVG|n_intervals|2025-01-01T00:00:00Z"]["text"], "35,040")

    def test_the_replication_meets_every_figure(self):
        self.assertEqual(self.rep.returncode, 0, self.rep.stdout[-3000:] + self.rep.stderr[-2000:])
        m = re.search(r"(\d+) of (\d+) figures inside the tolerance", self.rep.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) == "1431", self.rep.stdout[-600:])   # the distinct figures of the 30 views
        v = re.search(r"(\d+) of (\d+) views open as the note says", self.rep.stdout)
        self.assertTrue(v and v.group(1) == v.group(2) == "48", self.rep.stdout[-600:])
        # session 7516: the section of two hubs and the marks of a partial period, by the note's section 10
        s = re.search(r"(\d+) of (\d+) figures of the section of two hubs, in (\d+) views with a second hub", self.rep.stdout)
        self.assertTrue(s and s.group(1) == s.group(2) == "780" and s.group(3) == "16", self.rep.stdout[-900:])
        p = re.search(r"(\d+) of (\d+) periods that head a figure are written as the note says", self.rep.stdout)
        self.assertTrue(p and p.group(1) == p.group(2) == "894", self.rep.stdout[-900:])

    def test_fault_1_a_price_always_has_two_decimals(self):
        prices = {k: x for k, x in self.page["keyed"].items() if "|n_" not in k}
        whole = [k for k, x in prices.items() if x["raw"] == int(x["raw"])]
        self.assertGreater(len(whole), 0)        # the fixture holds prices that are a whole number of dollars
        for k, x in prices.items():
            self.assertRegex(x["text"], r"^-?[\d,]+\.\d\d$", k)
        for k, x in self.page["keyed"].items():
            if "|n_" in k:
                self.assertRegex(x["text"], r"^[\d,]+$", k)

    def test_fault_2_not_held_carries_no_unit(self):
        v = self.view("a month of the newest year")       # December 2026, which the monthly table does not hold
        self.assertEqual(v["not_held"], 32)
        self.assertFalse(v["unit_beside_not_held"])
        with open(os.path.join(self.tmp, "peak_hub-ercot_HB_HUBAVG_month-12_from-2015_to-2026.html"), encoding="utf-8") as f:
            html = f.read()
        self.assertEqual(html.count('<span class="text-muted">not held</span>'), 32)
        self.assertNotRegex(html, r"not held</span>(<!-- -->)?\s*(<span[^>]*>)?\s*USD/MWh")

    def test_fault_3_a_month_is_partial_below_its_exact_count(self):
        code = ("const P = await import('./lib/explore/peakpremium.ts');"
                "console.log(JSON.stringify([P.partialMonth(2026, 9, 2876), P.partialMonth(2026, 9, 2880), P.partialMonth(2025, 11, 2880),"
                " P.partialMonth(2025, 11, 2884), P.partialMonth(2025, 3, 2972), P.partialMonth(2025, 3, 2971), P.fullMonth(2024, 2)]))")
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        self.assertEqual(json.loads(r.stdout.strip().splitlines()[-1]), [True, False, True, False, False, True, 29 * 96])
        rep = module("replicate")
        self.assertEqual([rep.full_period(2026, 9), rep.full_period(2025, 11), rep.full_period(2025, 3), rep.full_period(2024, None)], [2880, 2884, 2972, 35136])

    def test_an_address_the_tables_do_not_hold(self):
        v = self.view("an address the tables do not hold")
        self.assertTrue(v["asked_unknown"])
        self.assertEqual((v["filters"]["hub"]["chosen"], v["filters"]["from"]["chosen"], v["filters"]["to"]["chosen"]), ("ercot:HB_HUBAVG", "2015", "2025"))

    def test_the_decisions_are_drawn_with_default_and_source_on_hover(self):
        with open(os.path.join(self.tmp, "peak_opening.html"), encoding="utf-8") as f:
            html = f.read()
        block = html[html.index('data-decisions="7507"'):]
        block = block[:block.index("</details>")]
        keys = decision_keys()
        self.assertEqual(re.findall(r'data-decision="([a-z-]+)"', block), keys)
        for k in keys:
            self.assertIn(f'id="tip-decision-7507-{k}"', block)
            self.assertIn(f'data-decision-default="{k}"', block)
            self.assertIn(f'data-decision-source="{k}"', block)
        self.assertNotIn("text-xs text-muted", block.replace("border border-muted text-[10px] leading-none text-muted", ""))


class TheTablesFromThePrices(unittest.TestCase):
    """Two months of one hub, each with a clock change, from real 15-minute prices by the note's rule."""

    def test_march_and_november_2025(self):
        fh, rep = module("from_hourly"), module("replicate")
        by, used, after, twice = fh.read_prices(FIXTURE, None)
        self.assertEqual((used, after, twice), (5856, 0, 0))
        table, _ = rep.read_table(os.path.join(FIXTURE, "ercot_peak_premium_monthly.csv"))
        checked = 0
        for month, n in ((3, 2972), (11, 2884)):
            m = fh.metrics(by[("ercot:HB_HUBAVG", 2025, month)])
            self.assertEqual(m["n_intervals"], n)
            self.assertEqual(n, rep.full_period(2025, month))
            for variable, value in m.items():
                row = table[("ercot:HB_HUBAVG", variable, f"2025-{month:02d}")]
                self.assertLessEqual(abs(round(value, 6) - row), 0.0000006, (month, variable))
                checked += 1
        self.assertEqual(checked, 56)


class TheFiles(unittest.TestCase):
    def test_the_decisions_are_the_notes(self):
        keys = decision_keys()
        self.assertEqual(len(keys), 11)
        note = src("docs", "methods", "ercot_peak_premium.md")
        section = note[note.index("### 5. The decisions on the page"):note.index("### 6. Beside published figures")]
        self.assertEqual(re.findall(r"^\| `([a-z-]+)` \|", section, re.M), keys)
        decisions = src("site", "app", "explore", "ercot-peak-premium", "Decisions.tsx")
        self.assertEqual(decisions.count("def: \""), len(keys))
        self.assertEqual(decisions.count("source: \""), len(keys))
        self.assertNotIn("text-muted", decisions)
        self.assertIn("<PeakPremiumDecisions />", src("site", "app", "explore", "ercot-peak-premium", "page.tsx"))

    def test_the_note_is_completed_not_rewritten(self):
        note = src("docs", "methods", "ercot_peak_premium.md")
        for kept in ("# ERCOT peak premium: method", "## Thesis reproduction (HB_HUBAVG)", "## Decisions of the explorer (each dated, and reversible unless said)",
                     "8. 2026-10-23, session 2204"):
            self.assertIn(kept, note)
        self.assertLess(note.index("## Decisions of the explorer"), note.index("## The tool as a reader meets it"))
        for part in ("### 1. What the page shows", "### 2. Every figure's table and rule", "### 4. What the tool does not hold", "### 6. Beside published figures", "### 8. Rulings asked"):
            self.assertIn(part, note)

    def test_the_do_file_expects_what_the_headline_prints(self):
        rep = module("replicate")
        lines = rep.headline(rep.Tables(FIXTURE))
        do = src("replication", "ercot_peak_premium", "replicate.do")
        self.assertEqual(len(lines), 6)
        for line in lines[1:]:
            self.assertIn(f"*   {line}", do)

    def test_the_committed_figures_are_whole(self):
        doc = json.loads(src("replication", "ercot_peak_premium", "page_figures.json"))
        self.assertEqual(doc["figures"], doc["figures_inside_the_tolerance"])
        self.assertEqual(doc["views"], doc["views_as_the_note_says"])
        self.assertEqual(doc["named_differences"], [])
        self.assertEqual(len(doc["opening"]["figures"]), 64)
        with open(os.path.join(REPLICATION, "page_figures.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), doc["figures"])
        for r in rows[:2000]:
            self.assertLessEqual(abs(float(r["page"].replace(",", "")) - float(r["replication"])), float(r["tolerance"]) + 1e-9, r)

    def test_no_em_or_en_dash(self):
        for parts in MINE:
            text = src(*parts)
            self.assertNotIn(EM_DASH, text, parts)
            self.assertNotIn(EN_DASH, text, parts)


if __name__ == "__main__":
    unittest.main()
