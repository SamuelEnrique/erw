"""Session 403 (the chain of 20 October 2026, afternoon): the ERCOT peak premium explorer, /explore/ercot-peak-premium,
platform tool 5's first signature explorer, in review. The thesis chart live by hub, year and month from the two derived
tables as they stand, its freshness read from the catalogue, the shared frame for the explorers that follow
(components/explore/Explore.tsx, lib/explore/), the check-values keys and the floor of a restricted run. Energy Research
Warehouse (ERW)."""
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
PAGE = ("site", "app", "explore", "ercot-peak-premium", "page.tsx")
NEW = [PAGE, ("site", "components", "explore", "Explore.tsx"), ("site", "lib", "explore", "index.ts"),
       ("site", "lib", "explore", "fresh.ts"), ("site", "lib", "explore", "peakpremium.ts")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_eval(code):
    """Run a module snippet with node from site/ (node strips the types of a .ts file that imports nothing)."""
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node is not on the path")
    out = subprocess.run([node, "--no-warnings", "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr[-2000:])
    return json.loads(out.stdout)


class ThePage(unittest.TestCase):
    def setUp(self):
        self.p = src(*PAGE)

    def test_it_is_in_review_and_not_in_the_menu(self):
        rel = src("site", "lib", "release.ts")
        self.assertIn('"/explore/ercot-peak-premium": "review",', rel)
        self.assertNotIn("/explore/", src("site", "lib", "pages.ts"))
        # the older explorer's redirect to the ERCOT tab of /prices stands (removing it is a ruling)
        self.assertIn('{ source: "/explorer/ercot-peak-premium", destination: "/prices?tab=ercot", permanent: true }', src("site", "next.config.ts"))
        self.assertIn('"/explorer/ercot-peak-premium": "review",', rel)

    def test_it_reads_the_two_tables_and_every_figure_carries_its_row_key(self):
        p = self.p
        self.assertIn("const table = month ? MONTHLY : ANNUAL;", p)
        self.assertIn("const key = (variable: string, y: number) => `series|${table}|${hub}|${variable}|${isoKey(periodTs(y, month))}`;", p)
        self.assertEqual(p.count("<Num "), 1)                                   # one figure writer, N, keyed by the row it shows
        self.assertIn("<Num check={key(v, y)} raw={x}>{fig(x, unit)}</Num>", p)
        tables = set(re.findall(r'table_name: `eq\.\$\{(\w+)\}`', p))
        self.assertEqual(tables, {"ANNUAL", "table", "MONTHLY"})
        pp = src("site", "lib", "explore", "peakpremium.ts")
        self.assertIn('export const ANNUAL = "ercot_peak_premium_annual";', pp)
        self.assertIn('export const MONTHLY = "ercot_peak_premium_monthly";', pp)

    def test_it_draws_through_the_shared_charts_only(self):
        p = self.p
        imports = re.findall(r'from "([^"]+)"', p)
        for i in imports:
            self.assertFalse(i.startswith("./") or "echarts" in i, i)
        self.assertIn('import { BoxChart } from "@/components/BoxChart";', p)
        self.assertIn('import { LineChart, type Line } from "@/components/LineChart";', p)
        self.assertNotIn("<svg", p)

    def test_the_definition_freshness_method_and_downloads_are_the_shared_frame(self):
        p, f = self.p, src("site", "components", "explore", "Explore.tsx")
        self.assertIn("The peak premium is how much higher and how much wider", p)
        self.assertIn('method={{ href: "/data/methods/ercot_peak_premium", label: "ERCOT peak premium" }}', p)
        self.assertIn("<TableDownloads tables={tables} />", f)
        self.assertIn("<SourceLine tables={tables} note={sourceNote} />", f)
        self.assertIn("const f = await freshness(tables);", f)
        self.assertIn("<strong>Stale since {longDay(r.lastRun)}. </strong>", f)
        self.assertIn('data-fresh="unread"', f)
        # the newest date is read, never written: no date of the tables in the page's or the frame's source
        for s in (p, f):
            self.assertIsNone(re.search(r"(29|28) September|2026-09|September 2026", s))
        self.assertIn("lastInput(header.data)", p)

    def test_a_value_the_tables_do_not_hold_falls_back_and_is_said(self):
        p = self.p
        self.assertIn('const [hub, badHub] = choose(sp, "hub", hubs,', p)
        self.assertIn("data-asked-unknown", p)
        self.assertIn('href: PATH, defaults:', p)

    def test_the_shared_helpers_are_split_by_where_they_run(self):
        i, fr = src("site", "lib", "explore", "index.ts"), src("site", "lib", "explore", "fresh.ts")
        self.assertNotIn("server-only", i)                   # a client component may import the helpers
        self.assertIsNone(re.search(r"^import ", i, re.M))
        self.assertIn('import "server-only";', fr)
        self.assertIn("const cat = await attempt(catalogue);", fr)

    def test_no_em_dash_in_what_this_session_wrote(self):
        for parts in NEW + [("docs", "methods", "ercot_peak_premium.md"), ("tests", "test_session403.py")]:
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


class TheHelpers(unittest.TestCase):
    def test_partial_periods_and_the_header_line(self):
        r = node_eval(
            'const m = await import("./lib/explore/peakpremium.ts");'
            'console.log(JSON.stringify([m.partialMonth(2026, 9, 2592), m.partialMonth(2025, 3, 2972), m.partialMonth(2025, 11, 2884),'
            ' m.partialMonth(2024, 2, 2784), m.fullYear(2024), m.fullYear(2025), m.periodTs(2015, null), m.periodTs(2021, 2),'
            ' m.lastInput(["Retrieved: x", "Last input interval: 2026-09-28T04:45:00Z; the current year"]), m.lastInput(["none"]),'
            ' m.valueOf([{entity: "e", variable: "v", ts_utc: "2015-01-01T00:00:00+00:00", value: 7.64}], "v", "2015-01-01T00:00:00Z")]))')
        self.assertEqual(r, [True, False, False, False, 35136, 35040, "2015-01-01T00:00:00Z", "2021-02-01T00:00:00Z",
                             "2026-09-28T04:45:00Z", None, 7.64])

    def test_choose_and_periods(self):
        r = node_eval(
            'const m = await import("./lib/explore/index.ts");'
            'console.log(JSON.stringify([m.choose({hub: "x"}, "hub", ["a", "b"], "a"), m.choose({}, "hub", ["a"], "a"), m.choose({hub: ["b", "a"]}, "hub", ["a", "b"], "a"),'
            ' m.periodOf("2026-09-01T00:00:00+00:00", "P1M"), m.periodOf("2026-01-01T00:00:00Z", "P1Y"), m.longDay("2026-09-29T00:55:55+00:00"),'
            ' m.longTime("2026-09-28T04:45:00Z"), m.isoKey("2025-01-01T00:00:00+00:00")]))')
        self.assertEqual(r, [["a", True], ["a", False], ["b", False], "September 2026", "2026", "29 September 2026",
                             "28 September 2026 04:45 UTC", "2025-01-01T00:00:00Z"])

    def test_every_past_month_of_the_table_is_complete_by_the_rule(self):
        path = os.path.join(ROOT, "warehouse", "output", "ercot_peak_premium_monthly.csv")
        if not os.path.exists(path):
            self.skipTest("the monthly table is not on this machine")
        with open(path, encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(line for line in f if not line.startswith("#")) if r["variable"] == "n_intervals"]
        newest = max(r["ts_utc"] for r in rows)
        cells = [[int(r["ts_utc"][:4]), int(r["ts_utc"][5:7]), int(float(r["value"])), r["ts_utc"] == newest] for r in rows]
        got = node_eval(
            'const m = await import("./lib/explore/peakpremium.ts");'
            f'const c = {json.dumps(cells)};'
            'console.log(JSON.stringify(c.filter(([y, mo, n, last]) => m.partialMonth(y, mo, n) !== last).slice(0, 5)))')
        self.assertEqual(got, [])


class TheChecks(unittest.TestCase):
    def test_check_values_reads_four_views_and_check_routes_the_page(self):
        cv = src("site", "scripts", "check-values.mjs")
        for page in ('"/explore/ercot-peak-premium"', '"/explore/ercot-peak-premium?hub=ercot%3AHB_WEST&from=2018&to=2024"',
                     '"/explore/ercot-peak-premium?month=8"', '"/explore/ercot-peak-premium?hub=ercot%3AHB_HOUSTON&month=2&from=2020&to=2021"'):
            self.assertIn(page, cv)
        self.assertIn('"/explore/ercot-peak-premium",  /* session 403 */', src("site", "scripts", "check-routes.mjs"))

    def test_a_restricted_run_that_passes_sets_only_its_pages_floors(self):
        cv = src("site", "scripts", "check-values.mjs")
        block = cv[cv.index('if (process.env.CHECK_VALUES_WRITE_FLOOR === "1") {'):cv.index("if (bad || n < 10) process.exit(1);")]
        self.assertIn('if (bad || n < 10) console.log("the floor file was not written: the run did not pass");', block)
        self.assertIn("else if (ONLY.length) {", block)
        self.assertIn("const merged = { ...kept.floor };", block)
        self.assertIn("for (const [page, count] of perPage) merged[page] = Math.min(10, count);", block)

    def test_the_method_note_says_what_the_explorer_draws(self):
        m = src("docs", "methods", "ercot_peak_premium.md")
        self.assertIn("## The explorer (session 403, 21 October 2026)", m)
        self.assertIn("`/explore/ercot-peak-premium`", m)


if __name__ == "__main__":
    unittest.main()
