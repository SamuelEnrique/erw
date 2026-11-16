"""Session 7517 (chain 304, part B): the demand growth explorer (/explore/demand-growth) read as its reader.

The page is drawn with the site's own code on the rows of its table (replication/demand_growth/table_rows.csv) for
PJM, CAISO and the Lower 48, and each fix of docs/reviews/demand-growth-read-2026-11-16.md is held on the drawn HTML:
the newest year's highest hour in the peak window (row 4), the months under the year so far's second headline (row 5),
the line that says where a forecast is held and how the All grids tab's growth differs (rows 9 and 10), and the
decisions' words on California's charging (row 6), which are held to their own recomputation from public rows
(replication/demand_growth/california_charging.py). The replication is run beside the page: every slot the same.
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
    ("docs", "reviews", "demand-growth-read-2026-11-16.md"), ("replication", "demand_growth", "california_charging.py"),
    ("replication", "demand_growth", "california_rows.csv"), ("tests", "test_session7517_demand_growth_read.py"),
    ("site", "lib", "explore", "demandgrowth.ts"), ("archive", "sessions", "SESSION_7517_REPORT.md"),
)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def california():
    sys.path.insert(0, REPLICATION)
    import california_charging as c
    rows = c.read()
    return c, rows


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageAsItsReaderMeetsIt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="erw7517_")
        cls.drawn = os.path.join(cls.tmp, "drawn.json")
        env = {k: v for k, v in os.environ.items() if not k.startswith("SUPABASE")}
        cls.proc = subprocess.run([NODE, "--no-warnings", "--import", "./scripts/tsx-register.mjs", "scripts/demand-growth-figures.mjs", ROWS, cls.drawn, "--grids=pjm,caiso,us48"],
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

    def test_the_page_draws(self):
        self.assertEqual(self.proc.returncode, 0, self.proc.stderr[-2000:])
        self.assertEqual(len(self.page["views"]), 3 * 39 + 3)
        for v in self.page["views"]:
            self.assertFalse(v["undefined_or_nan"] or v["em_dash"] or v["no_data"], v["q"])

    def test_the_peak_window_gives_the_newest_years_highest_hour(self):
        # row 4: PJM's record of 2 July 2026 was in the table and not on the page
        s = self.view("pjm", "peak")["slots"]
        self.assertEqual(s["peak.sofar"], "The highest hour of 2026 so far (January to October): 162,648 MW, +6.78 percent on the highest hour of the same months of 2019 (152,315 MW).")
        self.assertEqual(self.view("caiso", "peak")["slots"]["peak.sofar"],
                         "The highest hour of 2026 so far (January to October): 49,959 MW, +13.93 percent on the highest hour of the same months of 2019 (43,849 MW).")
        # each figure of the line is a checked row of the table
        k = self.page["keyed"]
        self.assertEqual(k["series|eia930_demand_growth|eia930:PJM|ytd_peak_demand_mw|2026-01-01T00:00:00Z"], {"raw": 162648, "text": "162,648"})
        self.assertEqual(k["series|eia930_demand_growth|eia930:PJM|ytd_peak_demand_growth_since_2019_pct|2026-01-01T00:00:00Z"], {"raw": 6.78, "text": "6.78"})
        self.assertEqual(k["series|eia930_demand_growth|eia930:PJM|ytd_peak_demand_mw|2019-01-01T00:00:00Z"], {"raw": 152315, "text": "152,315"})
        # the Lower 48 has no peak: no line, and no unit beside nothing
        self.assertNotIn("peak.sofar", self.view("us48", "peak")["slots"])
        # no other window draws it or reads its rows
        for v in self.page["views"]:
            if v["q"].get("window") != "peak":
                self.assertNotIn("peak.sofar", v["slots"], v["q"])
                self.assertFalse([x for x in v["keys"] if "ytd_peak" in x], v["q"])

    def test_the_year_so_fars_second_headline_names_its_months(self):
        # row 5: "2019: 91,744 MW" under the year so far is January to October of 2019, not the year (91,354 MW)
        s = self.view("pjm", "ytd")["slots"]
        self.assertEqual(s["h2.note"], "2019, January to October: 91,744 MW")
        self.assertEqual(self.view("pjm", "avg")["slots"]["h2.note"], "2019: 91,354 MW")
        self.assertEqual(self.view("pjm", "m07")["slots"]["h2.note"], "2019: 109,329 MW")

    def test_every_view_says_where_a_forecast_is_held(self):
        # rows 9 and 10: the page linked /demand only, which holds no forecast; the All grids tab's growth is another period
        for v in self.page["views"]:
            self.assertEqual(v["forecast_link"], "/cost-of-power?view=allgrids", v["q"])
            self.assertIn("the mean of the last twelve months over the twelve before", v["forecast_tip"])
            self.assertIn("FERC Form 714", v["forecast_tip"])

    def test_the_decisions_state_californias_charging_as_recomputed(self):
        # row 6: "Why California's two figures have opposite signs is not established here" is replaced by the figures
        c, rows = california()
        words = self.view("caiso", "avg")["against_sales"]
        self.assertNotIn("not established", words)
        a, b = c.window(rows, 2025, range(6, 13)), c.window(rows, 2026, range(1, 9))
        self.assertIn(f"June to December 2025, demand here {c.signed(a['growth_pct'])} percent on the same months of 2019, the charging {a['charging']:,.0f} MW on average, "
                      f"demand less the charging {c.signed(a['less_charging_pct'])} percent, retail sales {c.signed(a['sales_pct'])} percent", words)
        self.assertIn(f"January to August 2026, demand {c.signed(b['growth_pct'])} percent, the charging {b['charging']:,.0f} MW, "
                      f"demand less the charging {c.signed(b['less_charging_pct'])} percent, retail sales {c.signed(b['sales_pct'])} percent", words)
        self.assertGreater(a["share_pct"], 100)
        self.assertIn(f"{b['share_pct']:.0f} percent of that of January to August 2026", words)

    def test_the_replication_gives_every_slot_the_page_draws(self):
        out = subprocess.run([sys.executable, os.path.join(REPLICATION, "replicate.py"), f"--table={ROWS}", f"--page={self.drawn}"],
                             capture_output=True, text=True, encoding="utf-8", timeout=600, env={**os.environ, "ERW_SPEND_CAP_USD": "0"})
        self.assertEqual(out.returncode, 0, out.stdout[-3000:] + out.stderr[-2000:])
        m = re.search(r"/explore/demand-growth: (\d+) of (\d+) slots of text on (\d+) views", out.stdout)
        self.assertEqual(m.group(1), m.group(2))
        a = re.search(r"arithmetic: (\d+) of (\d+) growth figures", out.stdout)
        self.assertEqual(a.group(1), a.group(2))


class TheCaliforniaFindingAndTheFiles(unittest.TestCase):
    def test_californias_charging_on_the_rows_as_held(self):
        c, rows = california()
        a, b = c.window(rows, 2025, range(6, 13)), c.window(rows, 2026, range(1, 9))
        # the growth with the charging has the sign of the page's figure; without it, in 2025, the sign of the sales
        self.assertEqual([round(a[k], 2) for k in ("growth_pct", "less_charging_pct", "own_pct", "sales_pct")], [2.81, -3.60, -3.25, -2.28])
        self.assertEqual([round(b[k], 2) for k in ("growth_pct", "less_charging_pct", "own_pct", "sales_pct")], [10.75, 2.05, 2.13, -2.90])
        self.assertEqual((round(a["charging"]), round(b["charging"])), (1690, 2114))
        lines, held = c.lines(rows)
        self.assertEqual(len(held), 16)
        self.assertIn("within 300 MW in 14 of the 16 months held", lines[-1])
        # a month of the average day: August 2025, the charging of session 7512's row 7 (42,433 MWh a day)
        aug = c.month(rows, 2025, 8)
        self.assertEqual(round(aug["charging"] * 24), 42433)
        # the low base the note names: EIA's March 2019
        self.assertEqual(rows[("eia930_demand_growth", "avg_demand_mw_m03", "2019-01")], 19536.4)

    def test_the_committed_figures_and_the_note_carry_the_new_line(self):
        f = json.loads(src("replication", "demand_growth", "page_figures.json"))
        self.assertEqual((f["views"], f["differences"]), (315, []))
        self.assertEqual(f["slots_all_views"], f["equal_all_views"])
        self.assertIn(f["line"], src("docs", "methods", "demand_growth.md"))
        note = src("docs", "methods", "demand_growth.md")
        section = note[note.index("## Read as its reader (session 7517"):]
        for words in ("Figure 3a", "ytd_peak_demand_mw", "ytd_peak_demand_growth_since_2019_pct", "California: the batteries' charging inside EIA's demand", "| June to December 2025 | +2.81 percent"):
            self.assertIn(words, section)
        lib = src("site", "lib", "explore", "demandgrowth.ts")
        self.assertIn('export const PEAK_SO_FAR = ["ytd_peak_demand_mw", "ytd_peak_demand_growth_since_2019_pct"];', lib)

    def test_the_shared_explore_files_are_not_edited_here(self):
        for f in ("site/components/explore/Explore.tsx", "site/components/explore/HeldFreshness.tsx", "site/lib/explore/index.ts", "site/lib/explore/source.ts"):
            self.assertNotIn("7517", src(*f.split("/")), f)

    def test_the_read_is_in_the_form(self):
        read = src("docs", "reviews", "demand-growth-read-2026-11-16.md")
        self.assertTrue(read.startswith("# The demand growth explorer"))
        for words in ("**The reader:**", "**The five cases:**", "**How it was read.**", "## The rows", "## What this reader still cannot get from the tool, and why"):
            self.assertIn(words, read)
        numbered = re.findall(r"^\| (\d+) \|", read, flags=re.M)
        self.assertEqual(numbered, [str(i) for i in range(1, len(numbered) + 1)])
        self.assertGreaterEqual(len(numbered), 10)
        self.assertEqual(len(re.findall(r"^- \*\*", read[read.index("## What this reader still cannot get"):], flags=re.M)), 5)

    def test_no_dash_in_the_sessions_files(self):
        for parts in MINE:
            text = src(*parts)
            self.assertNotIn(EM_DASH, text, parts)
            self.assertNotIn(EN_DASH, text, parts)


if __name__ == "__main__":
    unittest.main()
