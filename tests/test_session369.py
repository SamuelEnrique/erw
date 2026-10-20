"""Session 369 (the chain of 20 October 2026, day): two gate faults. Energy Research Warehouse (ERW).

(a) /learn/problems/know-your-grid asked questions 1 and 2 of the newest UTC day the demand table held in full and summed
eia930_all_generation on it, which ends a day earlier: from 19 October 2026 the page wrote 0 MWh and 0 percent from gas.
Now both the page and check-values choose the day with one function, site/lib/gridday.ts: the newest UTC day both tables
hold in full (24 hours, both grids, each variable asked), and the page names that day beside the figures.

(b) queue/todo/008: every key check-values reports for an event page names the date its figure belongs to, and is
compared only with the row of that date (site/scripts/event-dates.mjs). The September 2022 case passes; a swapped date
fails.

Real rows only: tests/fixtures/session369/*.json were read once from the ERW live set with the anon key (reads only);
each file names its source and retrieval time. No request, no write, no model.

    python -m unittest tests.test_session369 -v
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FIX = os.path.join(ROOT, "tests", "fixtures", "session369")
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def fixture(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return json.load(f)


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    if not os.path.isdir(os.path.join(ROOT, "site", "node_modules")):
        raise unittest.SkipTest("the site's packages are not here")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"),
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheFixtures(unittest.TestCase):
    def test_each_names_its_source_and_retrieval(self):
        for name in ("caiso_heat_2022.json", "know_your_grid_hours.json"):
            f = fixture(name)
            self.assertIn("ERW live set", f["source"])
            self.assertRegex(f["retrieved_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class TheDayBothTablesHold(unittest.TestCase):
    """(a): on the rows of 20 October 2026, demand ends on the 19th and generation on the 18th."""

    @classmethod
    def setUpClass(cls):
        # the rows are read by node from the fixture itself (inlined, they pass Windows' limit on a command line)
        path = json.dumps(os.path.join(FIX, "know_your_grid_hours.json"))
        cls.out = node(
            "const fs = await import('node:fs'); const G = await import('./lib/gridday.ts');"
            " const held = JSON.parse(fs.readFileSync(" + path + ", 'utf-8')).held;"
            "const E = G.KNOW_YOUR_GRID.entities;"
            "const less = held.map((h) => h.table === 'eia930_all_generation' ? { ...h, rows: h.rows.filter((r) => !(r.entity === 'eia930:ERCO'"
            " && r.variable === 'net_generation_natural_gas_mw' && r.ts_utc.startsWith('2026-10-18T05'))) } : h);"
            "console.log(JSON.stringify({ both: G.newestCommonFullDay(held, E), demand: G.newestCommonFullDay([held[0]], E),"
            " until: G.newestCommonFullDay(held, E, '2026-10-17'), hourOut: G.newestCommonFullDay(less, E), none: G.newestCommonFullDay([], E) ?? null,"
            " key: G.dayKey('know-your-grid', '2026-10-18'), tables: G.KNOW_YOUR_GRID.tables.map((t) => t.table) }));")

    def test_the_newest_day_both_hold(self):
        self.assertEqual(self.out["both"], "2026-10-18")
        self.assertEqual(self.out["demand"], "2026-10-19")   # the old rule: the demand table's day, where generation has no row

    def test_a_day_missing_one_hour_of_one_variable_is_not_full(self):
        self.assertEqual(self.out["hourOut"], "2026-10-17")
        self.assertEqual(self.out["until"], "2026-10-17")
        self.assertIsNone(self.out["none"])

    def test_the_key_and_the_tables(self):
        self.assertEqual(self.out["key"], "fullday|know-your-grid|2026-10-18")
        self.assertEqual(self.out["tables"], ["eia930_all_demand", "eia930_all_generation"])


class OneFunctionForThePageAndTheCheck(unittest.TestCase):
    def test_the_page_and_the_check_import_it(self):
        p = src("site", "lib", "problems.ts")
        self.assertIn('import { dayKey, KNOW_YOUR_GRID, newestCommonFullDay } from "@/lib/gridday";', p)
        self.assertIn("const d0 = newestCommonFullDay(", p)
        self.assertNotIn("hours(E, d) === 24", p)          # the demand table's own day is gone
        self.assertIn("day: dayNote", p)
        check = src("site", "scripts", "check-values.mjs")
        self.assertIn('const G = await import("../lib/gridday.ts");', check)
        self.assertIn("return G.newestCommonFullDay(held, G.KNOW_YOUR_GRID.entities, d);", check)

    def test_the_page_names_the_day_beside_the_figures(self):
        page = src("site", "app", "learn", "problems", "[slug]", "page.tsx")
        self.assertIn("<Num check={q.day.k} raw={q.day.d}>{q.day.d}</Num>", page)
        self.assertIn("data-day", page)


class TheEventDates(unittest.TestCase):
    """(b): the September 2022 paragraph of /events/caiso-heat-2022 against its real rows."""

    @classmethod
    def setUpClass(cls):
        f = fixture("caiso_heat_2022.json")
        cls.rows, html = f["rows"], f["paragraph_html"]
        # a swapped date: the page writes 2022-09-01 beside the window's highest hour (the figure of 2022-09-06)
        swapped = html.replace("MW on <!-- -->2022-09-06<!-- -->", "MW on <!-- -->2022-09-01<!-- -->", 1)
        assert swapped != html
        js = (
            "const ED = await import('./scripts/event-dates.mjs'); const rows = " + json.dumps(cls.rows) + ";"
            "const re = /<span data-check=\"([^\"]+)\" data-raw=\"([^\"]*)\"[^>]*>([\\s\\S]*?)<\\/span>/g;"
            "const judge = (html) => { const ms = [...html.matchAll(re)]; return ms.map((m, i) => { const check = m[1];"
            " const [, , entity, variable] = check.split('|'); const own = rows.filter((r) => r.entity === entity && r.variable === variable);"
            " const written = ED.besideOf(html, ms, i); return { check, written, ...ED.compareDated({ check, raw: m[2], written }, own) }; }); };"
            "const k = (v, d) => `series|event_window_daily|eia930:CISO|${v}|${d}T00:00:00+00:00|caiso_heat_2022`;"
            "const own = (v) => rows.filter((r) => r.variable === v);"
            "console.log(JSON.stringify({ page: judge(" + json.dumps(html) + "), swapped: judge(" + json.dumps(swapped) + "),"
            " hi: ED.compareDated({ check: k('demand_max_mw', '2022-09-06'), raw: '51104', written: '2022-09-06' }, own('demand_max_mw')),"
            " rise: ED.compareDated({ check: k('demand_max_mw', '2022-09-01'), raw: '46868', written: '2022-09-01' }, own('demand_max_mw')),"
            " keySwap: ED.compareDated({ check: k('demand_max_mw', '2022-09-01'), raw: '51104', written: null }, own('demand_max_mw')),"
            " pctSwap: ED.compareDated({ check: k('demand_max_pct_vs_baseline', '2022-09-06'), raw: '34.7362', written: null }, own('demand_max_pct_vs_baseline')),"
            " row: ED.rowOfKey(k('demand_max_mw', '2022-09-01'), own('demand_max_mw')),"
            " labels: [ED.dateLabel(ED.keyDate(k('demand_max_mw', '2022-09-06'))), ED.dateLabel(ED.keyDate('es|caiso_heat_2022|eia930:CISO|demand_mwh|pooled|est')),"
            "  ED.dateLabel(ED.keyDate('es|caiso_heat_2022|eia930:CISO|demand_mwh|day|2022-09-01|est'))],"
            " pages: ['/events', '/events/caiso-heat-2022', '/eventsx', '/learn/problems/when-the-grid-broke'].map(ED.isEventPage) }));"
        )
        cls.out = node(js)

    def test_the_real_rows_say_both_figures_are_right(self):
        mw = {r["ts_utc"][:10]: r["value"] for r in self.rows if r["variable"] == "demand_max_mw"}
        pct = {r["ts_utc"][:10]: r["value"] for r in self.rows if r["variable"] == "demand_max_pct_vs_baseline"}
        self.assertEqual(max(mw, key=mw.get), "2022-09-06")      # the window's highest hour
        self.assertEqual(max(pct, key=pct.get), "2022-09-01")    # the largest rise against the baseline
        self.assertEqual((mw["2022-09-06"], mw["2022-09-01"]), (51104, 46868))

    def test_the_september_2022_case_passes(self):
        page = self.out["page"]
        self.assertEqual(len(page), 3)
        self.assertEqual([(x["written"], x["label"], x["pass"]) for x in page],
                         [("2022-09-06", "2022-09-06", True), ("2022-09-01", "2022-09-01", True), ("2022-09-06", "2022-09-06", True)])
        self.assertTrue(self.out["hi"]["pass"])
        self.assertTrue(self.out["rise"]["pass"])

    def test_a_swapped_date_fails(self):
        first = self.out["swapped"][0]
        self.assertFalse(first["pass"])
        self.assertIn("writes 2022-09-01 beside the figure of 2022-09-06", first["why"])
        self.assertEqual([x["pass"] for x in self.out["swapped"][1:]], [True, True])   # the other two figures are untouched
        self.assertFalse(self.out["keySwap"]["pass"])        # the highest-MW figure under the largest-rise day's key
        self.assertIn("the row of 2022-09-01 holds 46868", self.out["keySwap"]["why"])
        self.assertFalse(self.out["pctSwap"]["pass"])        # the largest-rise figure under the highest-MW day's key

    def test_a_key_reads_its_own_date_only(self):
        self.assertEqual(self.out["row"]["ts_utc"][:10], "2022-09-01")
        self.assertEqual(self.out["row"]["value"], 46868)

    def test_every_key_names_its_date(self):
        self.assertEqual(self.out["labels"], ["2022-09-06", "the event's window (pooled)", "2022-09-01"])
        self.assertEqual(self.out["pages"], [True, True, False, False])

    def test_the_check_uses_it(self):
        check = src("site", "scripts", "check-values.mjs")
        self.assertIn('import * as ED from "./event-dates.mjs";', check)
        self.assertIn("const written = ev ? ED.besideOf(html, ms, i) : null;", check)
        self.assertIn("const d = ED.compareDated({ check, raw, written: w }, rows);", check)
        self.assertIn("of = ` of ${d.label}", check)


class TheTodo(unittest.TestCase):
    def test_moved_to_done_with_the_session(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT, "queue", "todo", "008-code-check-values-event-dates.md")))
        done = src("queue", "done", "008-code-check-values-event-dates.md")
        self.assertIn("session 369", done.splitlines()[0].lower())

    def test_no_em_dash(self):
        for parts in (("site", "lib", "gridday.ts"), ("site", "scripts", "event-dates.mjs"), ("site", "lib", "problems.ts"),
                      ("site", "scripts", "check-values.mjs"), ("tests", "test_session369.py"), ("tests", "fixtures", "session369", "caiso_heat_2022.json"),
                      ("site", "app", "learn", "problems", "[slug]", "page.tsx")):
            self.assertNotIn(DASH, src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
