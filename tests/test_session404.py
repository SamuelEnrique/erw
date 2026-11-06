"""Session 404 (the chain of 20 October 2026, afternoon): the demand growth explorer, /explore/demand-growth, platform
tool 5's second signature explorer, in review. Growth since 2019 by grid and by window of the year from
eia930_demand_growth as it stands in the live set, on session 403's shared frame; its freshness read from the
catalogue's row although the table is held for review; every figure a checked row. Energy Research Warehouse (ERW)."""
import csv
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
DASH = chr(0x2014)
PAGE = ("site", "app", "explore", "demand-growth", "page.tsx")
LIB = ("site", "lib", "explore", "demandgrowth.ts")
HELD = ("site", "lib", "explore", "heldfresh.ts")
COMP = ("site", "components", "explore", "HeldFreshness.tsx")
NEW = [PAGE, LIB, HELD, COMP]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_eval(code):
    """Run a module snippet with node from site/, with the site's "@/" paths resolved (scripts/alias-register.mjs)."""
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node is not on the path")
    out = subprocess.run([node, "--no-warnings", "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", code],
                         cwd=SITE, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr[-2000:])
    return json.loads(out.stdout)


class ThePage(unittest.TestCase):
    def setUp(self):
        self.p = src(*PAGE)

    def test_it_is_in_review_and_not_in_the_menu(self):
        self.assertIn('"/explore/demand-growth": "review",', src("site", "lib", "release.ts"))
        self.assertNotIn("/explore/", src("site", "lib", "pages.ts"))
        # /demand stays as it was: in review, its own reader of the site's copy
        self.assertIn('"/demand": "review",', src("site", "lib", "release.ts"))
        self.assertIn('import fileJson from "@/data/demand_growth.json";', src("site", "app", "demand", "page.tsx"))

    def test_it_reads_one_table_and_every_figure_carries_its_row_key(self):
        p = self.p
        self.assertEqual(set(re.findall(r'table_name: `eq\.\$\{(\w+)\}`', p)), {"TABLE"})
        self.assertIn('export const TABLE = "eia930_demand_growth";', src(*LIB))
        self.assertIn("const key = (entity: string, variable: string, y: number) => `series|${TABLE}|${entity}|${variable}|${isoKey(yearTs(y))}`;", p)
        self.assertEqual(p.count("<Num "), 1)                     # one figure writer, N, keyed by the row it shows
        self.assertIn("<Num check={key(entity, v, y)} raw={x} source={sourceOf(key(entity, v, y), gridName(entity))}>{text}</Num>", p)  # session 2201: the source words in the hover
        # a sign is written outside the number, so the text check-values reads is the number as stored
        self.assertIn('{(pct || v.startsWith("growth_")) && x > 0 ? "+" : ""}<Num', p)

    def test_it_draws_through_the_shared_charts_and_frame_only(self):
        p = self.p
        for i in re.findall(r'from "([^"]+)"', p):
            self.assertFalse(i.startswith("./") or "echarts" in i, i)
        self.assertIn('import { GroupedBars } from "@/components/tool/GroupedBars";', p)
        self.assertIn('<GroupedBars id="growth-by-window"', p)
        self.assertIn('<GroupedBars id="demand-by-year"', p)
        self.assertNotIn("LineChart", p)   # the shared line chart's year axis repeats a year (2024 twice): bars label each year
        self.assertIn('import { ExploreFrame, FilterForm } from "@/components/explore/Explore";', p)
        self.assertNotIn("<svg", p)
        self.assertIn('<GroupedBars id="growth-by-grid"', p)   # its svg a direct child of the figure, so the brand lets it scroll on a phone

    def test_the_definition_method_and_newest_date(self):
        p = self.p
        self.assertIn("Demand growth is how much more power a grid used than in {BASE}", p)
        self.assertIn('method={{ href: "/data/methods/demand_growth", label: "Demand growth since 2019" }}', p)
        self.assertIn("<HeldFreshness", p)
        self.assertIn("ytdThrough(header.data)", p)
        # no date of the table is written by hand: the newest is read from the catalogue and the header
        for s in (p, src(*COMP), src(*LIB)):
            self.assertIsNone(re.search(r"October 2026|September 2026|2026-10|2026-09|\b2025\b|\b2026\b", s))

    def test_a_value_the_table_does_not_hold_falls_back_and_is_said(self):
        p = self.p
        self.assertIn('choose(sp, "grid", GRIDS.map((g) => g.slug), DEFAULT_GRID)', p)
        self.assertIn('choose(sp, "window", WINDOWS.map((w) => w.slug), DEFAULT_WINDOW)', p)
        self.assertIn("data-asked-unknown", p)

    def test_the_shared_parts_are_not_changed(self):
        # session 405 builds on the same frame in parallel: this session adds files and changes none of 403's
        out = subprocess.run(["git", "diff", "--name-only", "f6998a31", "HEAD", "--", "site/components/explore/Explore.tsx",
                              "site/lib/explore/index.ts", "site/lib/explore/fresh.ts"], cwd=ROOT, capture_output=True, text=True)
        if out.returncode != 0:
            self.skipTest("session 403's commit is not in this history")
        self.assertEqual(out.stdout.strip(), "")
        h = src(*HELD)
        self.assertIn('import "server-only";', h)
        self.assertIn('select: "table_name,last_run,ts_max,interval,license,in_live_set"', h)
        self.assertIn('held: tables.filter((t) => by.get(t)?.in_live_set === "review")', h)

    def test_no_em_dash_in_what_this_session_wrote(self):
        for parts in NEW + [("docs", "methods", "demand_growth.md"), ("tests", "test_session404.py")]:
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


class TheHelpers(unittest.TestCase):
    def test_grids_windows_and_the_header(self):
        r = node_eval(
            'const m = await import("./lib/explore/demandgrowth.ts");'
            'const w = (s) => { const x = m.windowOf(s); return [x.mw, x.growth, x.growthMw ?? null, x.perYear, x.latest]; };'
            'console.log(JSON.stringify([m.GRIDS.map((g) => g.slug + ":" + g.ba), m.WINDOWS.length, w("avg"), w("peak"), w("ytd"), w("m08"), w("h17"),'
            ' m.windowOf("x") ?? null, m.ytdThrough(["# Window: whole years 2019 to 2025; year to date: 1 January to the end of 09/2026 of each year."]),'
            ' m.ytdThrough(["none"]), m.variablesOf(m.windowOf("avg")).length, m.variablesOf(m.windowOf("m01")).slice(-3), m.viewHref("pjm", "ytd")]))')
        self.assertEqual(r, [
            ["ercot:ERCO", "caiso:CISO", "pjm:PJM", "miso:MISO", "spp:SWPP", "nyiso:NYIS", "isone:ISNE", "us48:US48"], 39,
            ["avg_demand_mw", "avg_demand_growth_since_2019_pct", None, True, "whole"],
            ["peak_demand_mw", "peak_demand_growth_since_2019_pct", None, True, "whole"],
            ["ytd_avg_demand_mw", "ytd_avg_demand_growth_since_2019_pct", None, True, "newest"],
            ["avg_demand_mw_m08", "growth_pct_m08", "growth_mw_m08", False, "whole"],
            ["avg_demand_mw_h17", "growth_pct_h17", "growth_mw_h17", False, "whole"],
            None, {"month": 9, "year": 2026}, None, 11, ["avg_demand_mw_m01", "growth_pct_m01", "growth_mw_m01"],
            "/explore/demand-growth?grid=pjm&window=ytd"])

    def test_the_years_a_view_reads_its_figures_at(self):
        rows = [{"entity": "eia930:ERCO", "variable": v, "ts_utc": f"{y}-01-01T00:00:00+00:00", "value": val}
                for v, y, val in [("avg_demand_mw", 2019, 1.0), ("avg_demand_mw", 2025, 2.0), ("ytd_avg_demand_mw", 2019, 3.0),
                                  ("ytd_avg_demand_mw", 2026, 4.0), ("growth_pct_m08", 2025, 18.02)]]
        r = node_eval(
            'const m = await import("./lib/explore/demandgrowth.ts");'
            f'const rows = {json.dumps(rows)}; const e = "eia930:ERCO";'
            'console.log(JSON.stringify([m.lastWhole(rows, e), m.newest(rows, e), m.latestOf(rows, e, m.windowOf("ytd")), m.latestOf(rows, e, m.windowOf("m08")),'
            ' m.valueOf(rows, e, "growth_pct_m08", 2025) ?? null, m.valueOf(rows, e, "growth_pct_m08", 2024) ?? null, m.yearsOf(rows, e, "ytd_avg_demand_mw"),'
            ' m.lastWhole(rows, "eia930:PJM") ?? null]))')
        self.assertEqual(r, [2025, 2026, 2026, 2025, 18.02, None, [2019, 2026], None])

    def test_every_window_is_a_row_of_the_table_for_every_grid(self):
        """Against the table on this machine: each window's demand row for every grid in 2019, and its growth row at the
        year the page reads it (the Lower 48 has no peak, the method note's rule). Skipped where the table is absent."""
        path = os.path.join(ROOT, "warehouse", "output", "eia930_demand_growth.csv")
        if not os.path.exists(path):
            self.skipTest("the table is not on this machine")
        with open(path, encoding="utf-8") as f:
            have = {(r["entity"], r["variable"], r["ts_utc"][:4]) for r in csv.DictReader(line for line in f if not line.startswith("#"))}
        wins = node_eval('const m = await import("./lib/explore/demandgrowth.ts"); console.log(JSON.stringify([m.GRIDS.map((g) => g.ba), m.WINDOWS]))')
        missing = []
        for ba in wins[0]:
            e = f"eia930:{ba}"
            whole = max(y for (en, v, y) in have if en == e and v == "avg_demand_mw")
            new = max(y for (en, v, y) in have if en == e and v == "ytd_avg_demand_mw")
            for w in wins[1]:
                if ba == "US48" and w["slug"] == "peak":
                    self.assertNotIn((e, w["mw"], "2019"), have)
                    continue
                at = new if w["latest"] == "newest" else whole
                for need in [(e, w["mw"], "2019"), (e, w["mw"], at), (e, w["growth"], at)] + ([(e, w["growthMw"], at)] if w.get("growthMw") else []):
                    if need not in have:
                        missing.append(need)
        self.assertEqual(missing, [])


class TheChecks(unittest.TestCase):
    def test_check_values_reads_five_views_and_check_routes_three(self):
        cv, cr = src("site", "scripts", "check-values.mjs"), src("site", "scripts", "check-routes.mjs")
        views = ['"/explore/demand-growth"', '"/explore/demand-growth?grid=us48&window=peak"', '"/explore/demand-growth?grid=pjm&window=ytd"',
                 '"/explore/demand-growth?grid=caiso&window=m08"', '"/explore/demand-growth?grid=ercot&window=h17"']
        for v in views:
            self.assertIn(v, cv)
        for v in views[:2] + views[3:4]:
            self.assertIn(v, cr)
        # the table's MW figures are written whole, as the check reads them
        self.assertIn(r"(^series\|eia930_demand_growth\|[^|]+\|(avg_demand_mw|peak_demand_mw|ytd_avg_demand_mw|growth_mw_))", cv)

    def test_the_method_note_says_what_the_explorer_draws(self):
        m = src("docs", "methods", "demand_growth.md")
        self.assertIn("## The explorer (session 404, 21 October 2026)", m)
        self.assertIn("`/explore/demand-growth`", m)


if __name__ == "__main__":
    unittest.main()
