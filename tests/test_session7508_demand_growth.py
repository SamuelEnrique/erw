"""Session 7508 (chain 304): the demand growth explorer (/explore/demand-growth) at the done line.

The page is drawn with the site's own code on the rows of its table (replication/demand_growth/table_rows.csv: the
rows the page reads, as held on 16 November 2026), for ERCOT and the Lower 48 in all 39 windows, and the replication
(replication/demand_growth/replicate.py, written from the method note) is run beside it: every slot of text is the
same. The rest holds the faults found to their fixes (a whole percent keeps two decimals; no unit beside "not held"; a
month's name in the second chart's hover; the Lower 48's missing bar marked; stale after 35 days), the decisions to the
note's list, the hourly rule on hours made for the test, the do-file's expected lines, and the session's files free of
em and en dashes.
"""
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
REPLICATION = os.path.join(ROOT, "replication", "demand_growth")
ROWS = os.path.join(REPLICATION, "table_rows.csv")
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)
MINE = (
    ("site", "app", "explore", "demand-growth", "page.tsx"), ("site", "app", "explore", "demand-growth", "Decisions.tsx"),
    ("site", "scripts", "demand-growth-figures.mjs"), ("docs", "methods", "demand_growth.md"),
    ("docs", "reviews", "demand-growth-faults-2026-11-16.md"), ("replication", "demand_growth", "replicate.py"),
    ("replication", "demand_growth", "from_hourly.py"), ("replication", "demand_growth", "extract_hours.py"),
    ("replication", "demand_growth", "replicate.do"), ("replication", "demand_growth", "page_figures.json"),
    ("replication", "demand_growth", "page_figures.csv"), ("replication", "demand_growth", "from_hourly.json"),
    ("tests", "test_session7508_demand_growth.py"),
)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def decision_keys():
    return re.findall(r'\{ key: "([a-z0-9-]+)",', src("site", "app", "explore", "demand-growth", "Decisions.tsx"))


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageDrawnAndReplicated(unittest.TestCase):
    """The page itself, on the table's rows, and the replication beside it."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="erw7508_")
        cls.drawn = os.path.join(cls.tmp, "drawn.json")
        env = {k: v for k, v in os.environ.items() if not k.startswith("SUPABASE")}
        cls.proc = subprocess.run([NODE, "--no-warnings", "--import", "./scripts/tsx-register.mjs", "scripts/demand-growth-figures.mjs", ROWS, cls.drawn, "--grids=ercot,us48"],
                                 cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=900, env=env)
        cls.page = None
        if os.path.exists(cls.drawn):
            with open(cls.drawn, encoding="utf-8") as f:
                cls.page = json.load(f)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def view(self, grid, window):
        return next(v for v in self.page["views"] if v["q"].get("grid") == grid and v["q"].get("window") == window and "extra" not in v["q"])

    def test_the_page_draws_every_view(self):
        self.assertEqual(self.proc.returncode, 0, self.proc.stderr[-2000:])
        self.assertEqual(len(self.page["views"]), 2 * 39 + 3)
        self.assertEqual(self.page["conflicts"], [])
        for v in self.page["views"]:
            self.assertFalse(v["undefined_or_nan"] or v["em_dash"] or v["no_data"], v["q"])
            self.assertGreaterEqual(v["keyed"], 20, v["q"])

    def test_the_replication_gives_every_slot_the_page_draws(self):
        out = subprocess.run([sys.executable, os.path.join(REPLICATION, "replicate.py"), f"--table={ROWS}", f"--page={self.drawn}"],
                             capture_output=True, text=True, encoding="utf-8", timeout=600, env={**os.environ, "ERW_SPEND_CAP_USD": "0"})
        self.assertEqual(out.returncode, 0, out.stdout[-3000:] + out.stderr[-2000:])
        m = re.search(r"/explore/demand-growth: (\d+) of (\d+) slots of text on (\d+) views", out.stdout)
        self.assertTrue(m, out.stdout)
        self.assertEqual(m.group(1), m.group(2))
        self.assertGreater(int(m.group(2)), 8000)
        a = re.search(r"arithmetic: (\d+) of (\d+) growth figures", out.stdout)
        self.assertEqual(a.group(1), a.group(2))

    def test_a_whole_percent_keeps_its_two_decimals(self):
        # faults row 1: the Lower 48's July growth is 8.00 percent; the page wrote "+8" beside the bar's "+8.00"
        pct = {k: x for k, x in self.page["keyed"].items() if "pct" in k}
        self.assertGreater(len(pct), 300)
        for k, x in pct.items():
            self.assertRegex(x["text"], r"^-?[\d,]+\.\d\d$", k)
        v = self.view("us48", "m07")
        self.assertEqual(v["slots"]["h1.value"], "+8.00")
        self.assertEqual(v["slots"]["bar1.Lower 48"], "Lower 48: +8.00 percent from 2019 to 2025")

    def test_no_unit_beside_a_figure_not_held(self):
        # faults row 2: the Lower 48 has no peak; the page wrote "not held percent" and "2019: not held MW"
        s = self.view("us48", "peak")["slots"]
        self.assertEqual((s["h1.value"], s["h1.unit"], s["h2.value"], s["h2.unit"]), ("not held", "", "not held", ""))
        self.assertNotIn("not held MW", s["h1.note"] + s["h2.note"])
        self.assertEqual(s["bar1.Lower 48.drawn"], "Lower 48 | not held")     # row 3: it read "shown below", with nothing below
        self.assertEqual(self.view("ercot", "peak")["slots"]["h1.unit"], "percent")

    def test_the_second_charts_hover_keeps_the_months_name(self):
        # faults row 4: "the year so far (january to october)"
        for v in self.page["views"]:
            hovers = [x for k, x in v["slots"].items() if re.match(r"bar2\.\d{4}$", k)]
            self.assertTrue(hovers, v["q"])
            for x in hovers:
                self.assertIn("the year so far (January to October)", x)
                self.assertNotIn("january", x)

    def test_the_decisions_are_drawn_on_every_view(self):
        keys = decision_keys()
        self.assertGreaterEqual(len(keys), 12)
        for v in self.page["views"]:
            self.assertEqual(v["decisions"], len(keys), v["q"])


class TheFilesOfTheDoneLine(unittest.TestCase):
    def test_the_decisions_are_the_notes_and_none_is_grey(self):
        keys = decision_keys()
        self.assertEqual(len(keys), len(set(keys)))
        note = src("docs", "methods", "demand_growth.md")
        section = note[note.index("### The decisions on the page"):]
        listed = re.findall(r"^\| `([a-z0-9-]+)` \|", section, flags=re.M)
        self.assertEqual(listed, keys)
        block = src("site", "app", "explore", "demand-growth", "Decisions.tsx")
        self.assertEqual(len(re.findall(r'^    def: "', block, flags=re.M)), len(keys))
        self.assertEqual(len(re.findall(r'^    source: "', block, flags=re.M)), len(keys))
        self.assertNotIn("text-muted", block)
        self.assertIn("<DemandGrowthDecisions />", src("site", "app", "explore", "demand-growth", "page.tsx"))

    def test_the_page_says_stale_after_a_missed_monthly_build(self):
        # faults row 5: "Stale since 6 November 2026" ten days after the monthly build
        page = src("site", "app", "explore", "demand-growth", "page.tsx")
        self.assertIn("const STALE_AFTER_DAYS = 35;", page)
        self.assertIn("staleAfterDays={STALE_AFTER_DAYS}", page)

    def test_the_shared_explore_files_are_not_edited_here(self):
        # two sibling sessions edit the other explorers: a fault in a shared file is a row, never an edit
        for f in ("site/components/explore/Explore.tsx", "site/components/explore/HeldFreshness.tsx", "site/lib/explore/index.ts", "site/lib/explore/source.ts"):
            self.assertNotIn("7508", src(*f.split("/")), f)

    def test_the_hourly_rule_on_hours_made_for_the_test(self):
        import pandas as pd
        sys.path.insert(0, REPLICATION)
        import from_hourly
        idx = pd.date_range("2024-06-01", periods=12, freq="h", tz="UTC")
        s = pd.Series([100, 102, 104, 300, 108, 110, 0, 114, None, 118, 126, 122], index=idx, dtype=float)
        used, left = from_hourly.screen(s)
        self.assertTrue(pd.isna(used.iloc[3]))                 # 300 between hours near 105: apart from its neighbours
        self.assertTrue(left["apart"].iloc[3])
        self.assertTrue(left["not_positive"].iloc[6] and left["blank"].iloc[8])
        self.assertEqual(used.iloc[4], 108)                    # the hour after the spike: the median of 104, 300, 110 is 110
        self.assertEqual(used.iloc[7], 114)                    # its neighbours that are zero or blank drop out of the median
        self.assertEqual(int(used.notna().sum()), 9)

    def test_the_hourly_recomputation_as_run(self):
        r = json.loads(src("replication", "demand_growth", "from_hourly.json"))
        self.assertEqual((r["summary"]["compared"], r["summary"]["equal"]), (24062, 24060))
        named = [(d["area"], d["variable"], d["year"]) for d in r["differences"] if d.get("recomputed") is not None and d.get("table") is not None]
        self.assertEqual(named, [("US48", "avg_demand_mw_m08", 2026), ("US48", "avg_demand_mw_m09", 2026)])
        self.assertEqual({a: c["left_out_since_2019"]["apart"] for a, c in r["areas"].items() if c["left_out_since_2019"]["apart"]},
                         {"SWPP": 2, "CISO": 38, "PJM": 7, "US48": 1})

    def test_the_committed_figures_are_whole_and_the_do_file_says_them(self):
        f = json.loads(src("replication", "demand_growth", "page_figures.json"))
        self.assertEqual(f["slots_all_views"], f["equal_all_views"])
        self.assertEqual((f["views"], f["differences"]), (315, []))
        out = subprocess.run([sys.executable, os.path.join(REPLICATION, "replicate.py"), "--headline"], capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        lines = [l for l in out.stdout.splitlines() if l.strip()]
        self.assertEqual(lines, f["headline"])
        do = src("replication", "demand_growth", "replicate.do")
        for l in lines:
            self.assertIn(f"*   {l}", do)

    def test_no_dash_in_the_sessions_files(self):
        for parts in MINE:
            text = src(*parts)
            self.assertNotIn(EM_DASH, text, parts)
            self.assertNotIn(EN_DASH, text, parts)


if __name__ == "__main__":
    unittest.main()
