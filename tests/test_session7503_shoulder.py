"""Session 7503 (chain 304): "The shoulder hours" (/shoulder) at the done line.

The page is drawn with the site's own code on real rows of its table (tests/fixtures/session7503: each grid's last year
held and ERCOT's May 2024, as built on 4 October 2026), and the replication (replication/shoulder/replicate.py, written from the method
notes) is run on the same rows: every figure the page draws is inside the tolerance. The rest reads the files: the
page's decisions are the note's, each with a default and a source on hover and no grey text; the four faults the
replication found on the page stay fixed; the do-file's expected lines are the ones the Python headline prints; the
committed figures are whole; and none of the session's files holds an em or an en dash.
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
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "session7503")
REPLICATION = os.path.join(ROOT, "replication", "shoulder")

# chain 301 (session 7020, the landing desk): several replication folders hold modules of the same name (replicate,
# from_hourly, ...); in one suite process the first one loaded was reused by the next test file. This takes this folder's.
_SHARED_NAMES = ("replicate", "from_hourly", "fetch_rows", "cross_check", "crosscheck", "extract_hours", "california_charging")


def _fresh(name):
    import importlib
    here = os.path.abspath(REPLICATION)
    for n in set(_SHARED_NAMES) | {name}:
        m = sys.modules.get(n)
        if m is not None and os.path.dirname(os.path.abspath(getattr(m, "__file__", "") or "")) != here:
            del sys.modules[n]
    if REPLICATION in sys.path:
        sys.path.remove(REPLICATION)
    sys.path.insert(0, REPLICATION)
    return importlib.import_module(name)

EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)
MINE = (
    ("site", "app", "shoulder", "page.tsx"), ("site", "app", "shoulder", "Decisions.tsx"), ("site", "scripts", "shoulder-figures.mjs"),
    ("docs", "methods", "shoulder.md"), ("docs", "methods", "shoulder_hours.md"), ("docs", "reviews", "shoulder-faults-2026-11-16.md"),
    ("replication", "shoulder", "replicate.py"), ("replication", "shoulder", "from_hourly.py"), ("replication", "shoulder", "replicate.do"),
    ("replication", "shoulder", "page_figures.json"), ("replication", "shoulder", "page_figures.csv"), ("replication", "shoulder", "hourly_sample.json"),
    ("tests", "test_session7503_shoulder.py"),
)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def text_of(html):
    t = re.sub(r"<[^>]+>", " ", html.replace("<!-- -->", ""))
    for a, b in (("&#x27;", "'"), ("&quot;", '"'), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t)


def replication():
    return _fresh("replicate")


def decision_keys():
    return re.findall(r'\{ key: "([a-z-]+)",', src("site", "app", "shoulder", "Decisions.tsx"))


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageDrawnAndReplicated(unittest.TestCase):
    """The page itself, every view of the fixture's rows, and the replication beside it."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="erw7503_")
        cls.page_file = os.path.join(cls.tmp, "page.json")
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/shoulder-figures.mjs", os.path.join(FIXTURE, "shoulder_hours_monthly.csv"),
                            cls.page_file, f"--html={cls.tmp}"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=900)
        cls.node = r
        cls.page = None
        if r.returncode == 0:
            with open(cls.page_file, encoding="utf-8") as f:
                cls.page = json.load(f)
        env = dict(os.environ, ERW_SPEND_CAP_USD="0")
        cls.rep = subprocess.run([sys.executable, os.path.join(REPLICATION, "replicate.py"), "--in-dir", FIXTURE, "--page", cls.page_file],
                                 capture_output=True, text=True, encoding="utf-8", timeout=600, env=env)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def html(self, grid):
        with open(os.path.join(self.tmp, f"shoulder_{grid}_opening.html"), encoding="utf-8") as f:
            return f.read()

    def test_every_view_draws(self):
        self.assertEqual(self.node.returncode, 0, self.node.stdout[-2000:] + self.node.stderr[-2000:])
        views = self.page["views"]
        self.assertEqual(len(views), 33)                       # 10 + 11 + 9 months, and each grid with no month named
        self.assertEqual(self.page["conflicts"], [])           # no figure is shown two ways in two views
        for v in views:
            self.assertFalse(v["no_data"] or v["undefined_or_nan"] or v["em_dash"], v)
            self.assertGreaterEqual(v["keyed"], 40, v)
        opened = {v["grid"]: v["drawn"] for v in views if v["asked"] is None}
        self.assertEqual(opened, {"ercot": "August 2026", "caiso": "November 2025", "caiso-own": "August 2026"})

    def test_every_figure_is_inside_the_tolerance(self):
        self.assertEqual(self.rep.returncode, 0, self.rep.stdout[-3000:] + self.rep.stderr[-2000:])
        m = re.search(r"(\d+) of (\d+) inside the tolerance; (\d+) named \(a rounding edge\); (\d+) differ; (\d+) recomputed", self.rep.stdout)
        self.assertTrue(m, self.rep.stdout[-500:])
        inside, total, named, differ, recomputed = (int(x) for x in m.groups())
        self.assertEqual((inside + named, differ), (total, 0))
        self.assertGreaterEqual(total, 3500)
        self.assertGreaterEqual(recomputed, 700)
        self.assertLessEqual(named, 2)

    def test_the_decisions_block(self):
        keys = decision_keys()
        self.assertEqual(len(keys), 18)
        for grid in ("ercot", "caiso", "caiso-own"):
            h = self.html(grid)
            block = h[h.index('data-decisions="7503"'):h.index("</details>", h.index('data-decisions="7503"'))]
            self.assertEqual(re.findall(r'data-decision="([a-z-]+)"', block), keys)
            self.assertIn(f'data-decision-count="{len(keys)}"', block)
            for k in keys:                                      # each choice: a default and a source, in a tip that has its target
                self.assertIn(f'data-decision-default="{k}"', block)
                self.assertIn(f'data-decision-source="{k}"', block)
                self.assertIn(f'aria-describedby="tip-decision-7503-{k}"', block)
                self.assertEqual(block.count(f'id="tip-decision-7503-{k}"'), 1)
            # no grey text in the block: the only muted thing is the tip's own mark
            self.assertEqual(len(re.findall(r'class="[^"]*text-muted', block)), len(keys))
            self.assertEqual(len(re.findall(r'<button[^>]*class="[^"]*text-muted', block)), len(keys))
            self.assertNotIn("<details open", block[:40])
            self.assertLess(h.index("What this cannot see"), h.index('data-decisions="7503"'))   # under the folds: nothing the page had is dropped

    def test_the_faults_found_stay_fixed(self):
        own, ercot = self.html("caiso-own"), self.html("ercot")
        # 1. the heading of the months' chart names the grid's first month held (it said 2019 for data held from June 2025)
        heading = {v["grid"]: v["heading_months"] for v in self.page["views"] if v["asked"] is None}
        self.assertEqual(heading, {"ercot": "By month since May 2024", "caiso": "By month since January 2025", "caiso-own": "By month since January 2026"})
        self.assertNotIn('title="By month since 2019"', src("site", "app", "shoulder", "page.tsx"))
        # 2. the days ranked are not "complete days": a day with no shoulder is not ranked
        self.assertIn("days (complete, of 24 hours, with a shoulder)", text_of(ercot))
        self.assertNotRegex(text_of(ercot), r"Ranked among [\d,]+ complete days")
        # 3. a figure not held carries no unit after "not held"
        self.assertIn("not held", text_of(own))
        self.assertNotIn("not held hours needed", text_of(own))
        self.assertRegex(text_of(ercot), r"The ten worst days of 2026 [\d.]+ hours needed")
        # 4. the definitions say what the table computes
        for h in (own, ercot):
            t = text_of(h)
            self.assertIn("counting only the hours in which net load is above the mean", t)
            self.assertIn("a day with no shoulder is not ranked", t)
            self.assertIn("read one hour earlier than EIA stamps them", t)
            self.assertIn("discharge only from 23 October 2024 to 15 December 2025", t)

    def test_a_night_low_is_said_beside_the_midday_surplus(self):
        """In Texas net load's lowest hour is often before dawn: the page says so in a tip, and only then."""
        rep = replication()
        T = rep.Tables(FIXTURE)
        said = 0
        for v in self.page["views"]:
            if v["asked"] is None:
                continue
            entity = next(e for s, e, _ in rep.GRIDS if s == v["grid"])
            low = T.t[(entity, "midday_low_hour", v["asked"] + "-01")]
            with open(os.path.join(self.tmp, f"shoulder_{v['grid']}_{v['asked']}.html"), encoding="utf-8") as f:
                h = f.read()
            self.assertEqual(f'data-night-low="{v["asked"]}"' in h, low < 8, f"{v['grid']} {v['asked']} low {low}")
            if low < 8:
                said += 1
                self.assertIn(f"net load is lowest at {int(low):02d}:00, before the sun is up", text_of(h))
                self.assertEqual(h.count('id="tip-shoulder-night-low"'), 1)
            self.assertNotEqual(v["grid"] != "ercot" and low < 8, True)          # California's low is in the day, every month
        self.assertEqual(said, 1)                                              # the fixture's one such month: ERCOT, May 2024

    def test_nothing_the_page_had_is_dropped(self):
        t = text_of(self.html("ercot"))
        for words in ("The evening shoulder", "Hours the battery fleet covers", "The midday surplus", "The average day", "The shoulder, second measure",
                      "Hours needed, second measure", "The ten worst days of 2026", "The shoulder hours by year", "By year: the second measure and the ten worst days",
                      "The definitions, exactly as computed", "What this cannot see"):
            self.assertIn(words, t)
        self.assertEqual(len(re.findall(r"<svg ", self.html("ercot"))), 2)
        self.assertEqual(len(re.findall(r'\|worst_rank\|', self.html("ercot"))), 10)


class TheRules(unittest.TestCase):
    """The note's rules as the replication writes them, on the fixture's real rows."""

    def test_the_energy_counts_only_the_hours_above_the_mean(self):
        rep = replication()
        T = rep.Tables(FIXTURE)
        differ = 0
        for _, entity, _ in rep.GRIDS:
            for month in T.months(entity):
                net, solar = T.day(entity, "net_load", month), T.day(entity, "solar", month)
                m = rep.measures(net, solar)
                held = T.t[(entity, "shoulder_mwh_above_mean", month + "-01")]
                self.assertAlmostEqual(m["shoulder_mwh_above_mean"], held, delta=0.002, msg=f"{entity} {month}")
                every_hour = sum(net[h] - m["net_load_mean_mw"] for h in range(m["shoulder_start_hour"], m["shoulder_end_hour"]))
                differ += abs(every_hour - held) > 1
                self.assertEqual(m["shoulder_hours"], T.t[(entity, "shoulder_hours", month + "-01")])
                self.assertEqual(m["shoulder2_hours"], T.t[(entity, "shoulder2_hours", month + "-01")])
                self.assertEqual(m["midday_low_hour"], T.t[(entity, "midday_low_hour", month + "-01")])
        self.assertGreaterEqual(differ, 2)      # California, February: the sentence the note had gave another figure

    def test_the_month_a_grid_opens_on(self):
        rep = replication()
        T = rep.Tables(FIXTURE)
        self.assertEqual([rep.opening(T, e) for _, e, _ in rep.GRIDS], ["2026-08", "2025-11", "2026-08"])
        self.assertEqual(T.months("iso:ercot")[-1], "2026-09")          # the newest month is held, and lacks the fleet
        self.assertNotIn(("iso:ercot", "fleet_mw", "2026-09-01"), T.t)

    def test_the_headline_is_the_do_files(self):
        r = subprocess.run([sys.executable, os.path.join(REPLICATION, "replicate.py"), "--in-dir", FIXTURE, "--headline"], capture_output=True, text=True,
                           encoding="utf-8", timeout=120, env=dict(os.environ, ERW_SPEND_CAP_USD="0"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        lines = [line for line in r.stdout.splitlines() if re.match(r"\d\. ", line)]
        self.assertEqual(len(lines), 5)
        do = src("replication", "shoulder", "replicate.do")
        for line in lines:
            self.assertIn("*   " + line + "\n", do)
        self.assertIn("This do-file has not been run", do)
        self.assertIn('display "1. the evening shoulder, hours: "', do)


class TheFiles(unittest.TestCase):
    def test_the_committed_figures(self):
        p = json.loads(src("replication", "shoulder", "page_figures.json"))
        figures = p["figures"]
        self.assertEqual((p["views"], p["figures_all_views"], p["inside_all_views"]), (193, 20634, 20633))
        self.assertEqual(len(figures), 1196)
        self.assertTrue(all(f["inside"] for f in figures))
        self.assertEqual(p["opening"], {"iso:ercot": "2026-08", "iso:caiso": "2025-11", "iso:caiso_own": "2026-08"})
        by_key = {f["key"]: f for f in figures}
        self.assertEqual(by_key["series|shoulder_hours_monthly|iso:ercot|shoulder_hours|2026-08-01T00:00:00Z"]["page"], "5")
        self.assertEqual(by_key["series|shoulder_hours_monthly|iso:ercot|shoulder_hours_needed|2026-08-01T00:00:00Z"]["page"], "3.66")
        self.assertEqual(by_key["series|shoulder_hours_monthly|iso:ercot|year_worst10_mean_shoulder_hours_needed|2026-01-01T00:00:00Z"]["page"], "6.58")
        rows = list(csv.reader(line for line in src("replication", "shoulder", "page_figures.csv").split("\n") if line and not line.startswith("#")))
        self.assertEqual(rows[0], ["key", "where", "page", "replication", "tolerance", "inside", "basis"])
        self.assertEqual(len(rows) - 1, len(figures))
        self.assertTrue(all(r[5] == "yes" for r in rows[1:]))

    def test_the_hours_behind_the_table(self):
        h = json.loads(src("replication", "shoulder", "hourly_sample.json"))
        self.assertEqual((h["values"], h["equal"], h["differences"]), (22092, 22092, []))
        months = [s for s in h["sample"] if "month" in s]
        self.assertEqual(len([s for s in months if s["entity"] == "iso:ercot"]), 93)
        self.assertEqual(len([s for s in months if s["entity"] == "iso:caiso"]), 81)
        self.assertTrue(all(s["values"] == s["inside"] for s in h["sample"]))

    def test_the_note_holds_the_pages_decisions(self):
        keys, note = decision_keys(), src("docs", "methods", "shoulder.md")
        listed = re.search(r"Its keys, in order: (.*?)\. `tests/", note).group(1)
        self.assertEqual(re.findall(r"`([a-z-]+)`", listed), keys)
        table = note.split("## 5. The assumptions")[1].split("## 6.")[0]
        self.assertEqual(re.findall(r"(?m)^\| `([a-z-]+)` \|", table), keys)
        for head in ("## 1. The views", "## 3. Every figure, block by block", "## 7. What the tool does not hold", "## 8. The replication", "## 9. The cross-check",
                     "## 10. What waits for the owner", "## Sign-off"):
            self.assertIn("\n" + head, note)
        self.assertIn("**20,633 of 20,634 inside the tolerance**", note)
        self.assertIn("**22,092 of 22,092 values equal the table's rows**", note)
        completed = src("docs", "methods", "shoulder_hours.md")
        for words in ("counting only the hours in which net load is above the mean", "California's late hours", "An impossible hour of demand is a blank",
                      "## Rules stated in full (session 7503)", "Nor is a day with no shoulder"):
            self.assertIn(words, completed)
        self.assertIn("**The question.** Solar floods the middle of the day", completed)      # completed, not rewritten

    def test_the_cross_check_names_its_documents(self):
        check = src("docs", "methods", "shoulder.md").split("## 9. The cross-check")[1].split("## 10.")[0]
        rows = [line for line in check.split("\n") if line.startswith("| ") and not line.startswith("| Figure") and not line.startswith("|---")]
        self.assertEqual(len(rows), 12)
        for r in rows:
            self.assertEqual(r.count(" | "), 5, r[:80])
        for words in ("2025 State of the Market Report for the ERCOT Electricity Markets", "2025 Annual Report on Market Issues and Performance", "Today in Energy",
                      "nothing published", "The page holds no price"):
            self.assertIn(words, check)

    def test_no_dash_in_the_sessions_files(self):
        for parts in MINE:
            if not os.path.exists(os.path.join(ROOT, *parts)):
                continue
            t = src(*parts)
            self.assertNotIn(EM_DASH, t, "/".join(parts))
            self.assertNotIn(EN_DASH, t, "/".join(parts))


if __name__ == "__main__":
    unittest.main()
