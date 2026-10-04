"""Session 90: the fixes before the one deploy.

Energy Research Warehouse (ERW).

    b  the home page is never cached with a failed read in it (site/lib/supabase.ts `required`, run here by node with
       the database replaced by a stand-in), and the workflow warms the live pages before its route check
    c  /contracts reads a summary computed when the table is loaded (warehouse/supabase/load.py eqr_summary, migration 021)
    d  /shoulder opens on the latest month that holds every figure (site/lib/shoulder.ts)
    e  /storage/buildout writes MW and MWh without decimals (site/lib/buildout.ts)

    python -m unittest tests.test_session90 -v
"""

import json
import os
import re
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js, env=None, alias=False):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    cmd = [exe] + (["--import", "./scripts/alias-register.mjs"] if alias else []) + ["--input-type=module", "-e", js]
    e = {k: v for k, v in os.environ.items() if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "NEXT_PHASE")}
    e.update(env or {})
    r = subprocess.run(cmd, cwd=SITE, capture_output=True, text=True, timeout=120, env=e)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


# a stand-in for the database: `plan` is the list of answers fetch gives, in order; the last one repeats
STANDIN = """
const plan = %s; let calls = 0;
globalThis.fetch = async () => { const a = plan[Math.min(calls, plan.length - 1)]; calls++;
  if (a === "down") throw new Error("connect ECONNREFUSED");
  return { ok: a.status === 200, status: a.status, text: async () => a.body ?? "", json: async () => a.rows ?? [] }; };
const realSetTimeout = globalThis.setTimeout; const waits = [];
globalThis.setTimeout = (f, ms) => { waits.push(ms); return realSetTimeout(f, 0); };
const s = await import("./lib/supabase.ts");
const read = () => s.rest("series", { table_name: "eq.t" }, 900);
"""
KEYS = {"SUPABASE_URL": "http://standin.invalid", "SUPABASE_ANON_KEY": "standin"}
TIMEOUT = {"status": 500, "body": '{"code":"57014","message":"canceling statement due to statement timeout"}'}
GOOD = {"status": 200, "rows": [{"value": 1}]}


class HomePageIsNeverCachedWithAFailedRead(unittest.TestCase):
    def run_plan(self, plan, tail, env=KEYS):
        return node(STANDIN % json.dumps(plan) + tail, env=env, alias=True)

    def test_a_failed_read_throws_where_attempt_gave_a_reason(self):
        d = self.run_plan([{"status": 503, "body": "upstream"}], """
const a = await s.attempt(read);
let threw = null; try { await s.required(read); } catch (e) { threw = { data: e instanceof s.DataError, msg: e.message }; }
console.log(JSON.stringify({ a, threw }));""")
        self.assertFalse(d["a"]["ok"])
        self.assertIn("HTTP 503", d["a"]["reason"])
        self.assertIsNotNone(d["threw"], "required returned where it must throw")
        self.assertTrue(d["threw"]["data"])
        self.assertIn("HTTP 503", d["threw"]["msg"])

    def test_a_statement_timeout_that_outlasts_the_tries_throws(self):
        d = self.run_plan([TIMEOUT], """
let threw = null; try { await s.required(read); } catch (e) { threw = e.message; }
console.log(JSON.stringify({ threw, calls, waits }));""")
        self.assertIn("57014", d["threw"])
        self.assertEqual(d["calls"], 3)
        self.assertEqual(d["waits"], [1000, 3000])

    def test_a_database_that_cannot_be_reached_throws(self):
        d = self.run_plan(["down"], """
let threw = null; try { await s.required(read); } catch (e) { threw = e.message; }
console.log(JSON.stringify({ threw }));""")
        self.assertIn("request failed", d["threw"])

    def test_a_read_that_succeeds_is_returned_as_before(self):
        d = self.run_plan([TIMEOUT, GOOD], """
const r = await s.required(read);
console.log(JSON.stringify({ r, calls }));""")
        self.assertEqual(d["r"], {"ok": True, "data": [{"value": 1}]})
        self.assertEqual(d["calls"], 2)

    def test_a_server_with_no_database_named_is_not_a_failed_read(self):
        d = self.run_plan([GOOD], """
const r = await s.required(read);
console.log(JSON.stringify({ r, calls }));""", env={})
        self.assertFalse(d["r"]["ok"])
        self.assertIn("not set on the server", d["r"]["reason"])
        self.assertEqual(d["calls"], 0)

    def test_a_stand_in_on_this_machine_is_a_fixture_and_nothing_else_is(self):
        tail = """
let r = null, threw = null; try { r = await s.required(read); } catch (e) { threw = e.message; }
console.log(JSON.stringify({ r, threw }));"""
        for url in ("http://localhost:54369", "http://127.0.0.1:54369"):
            d = self.run_plan([{"status": 503, "body": "upstream"}], tail, env={"SUPABASE_URL": url, "SUPABASE_ANON_KEY": "local"})
            self.assertIsNone(d["threw"], url)
            self.assertFalse(d["r"]["ok"])
        for url in ("https://abcd.supabase.co", "https://localhost.example.com", "http://localhostx:1"):
            d = self.run_plan([{"status": 503, "body": "upstream"}], tail, env={"SUPABASE_URL": url, "SUPABASE_ANON_KEY": "k"})
            self.assertIsNotNone(d["threw"], f"{url} was taken for a fixture")

    def test_the_build_sends_two_reads_at_a_time_and_a_request_sends_all(self):
        js = """
let now = 0, most = 0;
globalThis.fetch = async () => { now++; most = Math.max(most, now); await new Promise((r) => setTimeout(r, 20)); now--;
  return { ok: true, status: 200, text: async () => "", json: async () => [{ value: 1 }] }; };
const s = await import("./lib/supabase.ts");
const all = await Promise.all(Array.from({ length: 12 }, (_, i) => s.rest("series", { table_name: `eq.t${i}` }, 900)));
console.log(JSON.stringify({ most, rows: all.flat().length }));"""
        d = node(js, env={**KEYS, "NEXT_PHASE": "phase-production-build"}, alias=True)
        self.assertEqual(d, {"most": 2, "rows": 12})
        d = node(js, env=KEYS, alias=True)
        self.assertEqual(d, {"most": 12, "rows": 12})

    def test_the_build_waits_longer_for_a_cancelled_read(self):
        d = self.run_plan([TIMEOUT, TIMEOUT, TIMEOUT, TIMEOUT, GOOD], """
const r = await s.required(read);
console.log(JSON.stringify({ ok: r.ok, calls, waits }));""", env={**KEYS, "NEXT_PHASE": "phase-production-build"})
        self.assertTrue(d["ok"])
        self.assertEqual(d["calls"], 5)
        self.assertEqual(d["waits"], [1000, 3000, 5000, 8000])
        d = self.run_plan([TIMEOUT], """
let threw = null; try { await s.required(read); } catch (e) { threw = e.message; }
console.log(JSON.stringify({ threw, calls, waits }));""", env={**KEYS, "NEXT_PHASE": "phase-production-build"})
        self.assertEqual(d["calls"], 6)
        self.assertEqual(d["waits"], [1000, 3000, 5000, 8000, 12000])

    def test_every_read_of_the_home_page_is_required(self):
        page = src("site", "app", "page.tsx")
        self.assertNotRegex(page, r"\battempt\(", "the home page still turns a failed read into a reason")
        self.assertNotIn("attempt", re.search(r'import \{([^}]*)\} from "@/lib/supabase"', page).group(1))
        # every reader the page calls is inside required(...): rest, series, newest and the named readers
        calls = re.findall(r"required\(", page)
        self.assertGreaterEqual(len(calls), 13)
        for reader in ("latestPrices", "storageUnits", "deals", "datacenters", "catalogue"):
            self.assertIn(f"required({reader})", page)
            self.assertNotRegex(page, rf"(?<![.\w]){reader}\(", f"{reader} is called outside required")
        for m in re.finditer(r"\b(series|newest|rest)(<[^>]*>)?\(", page):
            line = page[page.rfind("\n", 0, m.start()) + 1:page.find("\n", m.end())]
            self.assertIn("required(", line, f"a read outside required: {line.strip()}")
        self.assertIn("export const revalidate = 900", page)

    def test_nothing_catches_the_throw_between_the_page_and_the_cache(self):
        # an error file beside the home page would catch the throw and the fallback would be cached in the page's place
        for f in ("error.tsx", "error.js", "global-error.tsx", "loading.tsx"):
            self.assertFalse(os.path.exists(os.path.join(SITE, "app", f)), f"site/app/{f} would stand between the home page's throw and the cache")
        self.assertNotIn("<Suspense", src("site", "app", "page.tsx"))


class WorkflowWarmsTheLivePages(unittest.TestCase):
    def test_the_warm_step_runs_before_the_route_check(self):
        wf = src(".github", "workflows", "code-branch.yml")
        warm, check = wf.find("node scripts/warm-live.mjs http://localhost:3049"), wf.find("node scripts/check-routes.mjs http://localhost:3049")
        self.assertGreater(warm, 0)
        self.assertGreater(check, warm, "the route check runs before the pages are warmed")
        self.assertGreater(warm, wf.find("npm run build"))

    def test_it_asks_for_the_pages_the_snapshot_reads(self):
        d = node("import { LIVE_PAGES } from './scripts/snapshot-live.mjs'; import fs from 'node:fs';"
                 "const w = fs.readFileSync('./scripts/warm-live.mjs', 'utf8');"
                 "console.log(JSON.stringify({ n: LIVE_PAGES.length, home: LIVE_PAGES[0], uses: w.includes('import { LIVE_PAGES } from \"./snapshot-live.mjs\"') }));")
        self.assertEqual(d, {"n": 20, "home": "/", "uses": True})

    def test_it_fails_when_a_page_never_answers(self):
        exe = shutil.which("node")
        if not exe:
            self.skipTest("node is not on this machine")
        # nothing listens on this port: every page fails three times; the waits are not sat through (a preload makes them instant)
        pre = os.path.join(ROOT, "runs", "session90_nowait.mjs")
        os.makedirs(os.path.dirname(pre), exist_ok=True)
        with open(pre, "w", encoding="utf-8") as f:
            f.write("const t = globalThis.setTimeout; globalThis.setTimeout = (f, ms, ...a) => t(f, Math.min(ms, 1), ...a);\n")
        r = subprocess.run([exe, "--import", "file:///" + pre.replace(os.sep, "/"), "scripts/warm-live.mjs", "http://127.0.0.1:9"],
                           cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 1, r.stdout[-500:] + r.stderr[-500:])
        self.assertIn("20 never answered 200", r.stdout)


class ContractsSummary(unittest.TestCase):
    ROWS = [
        # event_date, rate, product, delivery BA, quarter
        ("2026-04-02", "41.5", "Energy", "PJM", "2026_Q2"),
        ("2026-04-20", "", "ENERGY", "PJM", "2026_Q2"),
        ("2026-05-01", "", "Capacity", "", "2026_Q2"),
        ("2026-05-09T00:00:00Z", "12", "CAPACITY", "MISO", "2026_Q2"),
        ("2025-12-31", "3", "Tolling Energy", "CISO", "2026_Q2"),
        ("2026-06-30", "", "energy", "MISO", "2026_Q2"),
    ]

    def frame(self):
        return pd.DataFrame([{"event_id": f"e{i}", "event_date": d, "x_rate": r, "x_product_name": p,
                              "x_point_of_delivery_balancing_authority": ba, "x_quarter": q} for i, (d, r, p, ba, q) in enumerate(self.ROWS)])

    def test_the_counts_the_page_states(self):
        import load
        s = load.eqr_summary(self.frame())
        self.assertEqual((s["rows"], s["priced"], s["first"], s["last"], s["quarters"]), (6, 3, "2025-12-31", "2026-06-30", ["2026_Q2"]))
        self.assertEqual(s["by_month"], [{"month": "2025-12", "rows": 1, "priced": 1}, {"month": "2026-04", "rows": 2, "priced": 1},
                                         {"month": "2026-05", "rows": 2, "priced": 1}, {"month": "2026-06", "rows": 1, "priced": 0}])
        # product names are counted in capitals, most rows first, then by name
        self.assertEqual(s["by_product"], [{"product": "ENERGY", "rows": 3, "priced": 1}, {"product": "CAPACITY", "rows": 2, "priced": 1},
                                           {"product": "TOLLING ENERGY", "rows": 1, "priced": 1}])
        self.assertEqual(s["by_ba"], [{"ba": "MISO", "rows": 2}, {"ba": "PJM", "rows": 2}, {"ba": "CISO", "rows": 1}, {"ba": "not stated", "rows": 1}])
        self.assertEqual(sum(m["rows"] for m in s["by_month"]), s["rows"])
        json.dumps(s)  # plain numbers and text: it goes to the database as JSON

    def test_an_empty_table_is_a_summary_of_nothing(self):
        import load
        s = load.eqr_summary(self.frame().iloc[0:0])
        self.assertEqual((s["rows"], s["priced"], s["first"], s["last"], s["by_month"]), (0, 0, None, None, []))

    def test_it_is_the_shape_the_page_reads(self):
        import load
        s = load.eqr_summary(self.frame())
        ts = src("site", "lib", "contracts.ts")
        fields = re.search(r"export type Summary = \{(.*?)\};", ts, re.S).group(1)
        for k in s:
            self.assertRegex(fields, rf"\b{k}\b", f"the page's Summary has no field {k}")
        d = node("import * as c from './lib/contracts.ts';"
                 f"const s = {json.dumps(s)};"
                 "console.log(JSON.stringify({ q: c.quarters(s), filed: c.filedQuarter(s) }));")
        self.assertEqual(d["filed"], "2026-Q2")
        self.assertEqual(d["q"], [{"quarter": "2026-Q2", "rows": 5, "priced": 2}, {"quarter": "2025-Q4", "rows": 1, "priced": 1}])

    def test_the_loader_stores_it_when_the_table_is_loaded_and_the_page_reads_one_row(self):
        loader = src("warehouse", "supabase", "load.py")
        self.assertIn('client.rpc("eqr_summary_store", {"p_summary": eqr_summary(df)})', loader)
        self.assertLess(loader.find("if ok and name == EQR"), loader.find("hashes[name] = digest"), "a table whose summary could not be stored must not be marked loaded")
        m = src("warehouse", "supabase", "migrations", "021_eqr_summary.sql")
        body = m[m.find("create or replace function public.internal_eqr_summary"):]
        self.assertIn("select summary into s from erw_private.eqr_summary", body)
        self.assertNotIn("public.events", body, "the page's function still counts the contract rows on every request")
        self.assertIn("p_token <> secret", body)
        # only the service key stores; the public key reads, with the token
        self.assertIn("revoke all on function public.eqr_summary_store(jsonb) from anon, authenticated;", m)
        self.assertIn("grant execute on function public.eqr_summary_store(jsonb) to service_role;", m)
        self.assertNotIn("grant execute on function public.eqr_summary_store(jsonb) to anon", m)
        self.assertIn('rpc<Summary>("internal_eqr_summary"', src("site", "app", "contracts", "read.ts"))


class ShoulderOpensOnACompleteMonth(unittest.TestCase):
    JS = """
import * as s from './lib/shoulder.ts';
const row = (variable, month, entity = 'iso:ercot') => ({ entity, variable, ts_utc: `${month}-01T00:00:00Z`, value: 1 });
const full = (m, e) => s.REQUIRED.map((v) => row(v, m, e));
const fleet = ['fleet_mw', 'fleet_mwh', 'fleet_hours', 'shoulder_hours_covered', 'shoulder_hours_needed', 'shoulder2_hours_needed'];
const noFleet = (m, e) => s.REQUIRED.filter((v) => !fleet.includes(v)).map((v) => row(v, m, e));
const rows = [...full('2026-07'), ...full('2026-08'), ...noFleet('2026-09'), ...noFleet('2025-06', 'iso:caiso_own')];
const months = { ercot: ['2026-07', '2026-08', '2026-09'], 'caiso-own': ['2025-06'] };
const complete = Object.fromEntries(s.GRIDS.map((g) => [g.slug, s.completeMonths(rows, g)]));
console.log(JSON.stringify({
  complete,
  open: s.choices({}, months, complete).month,
  named: s.choices({ month: '2026-09' }, months, complete).month,
  wrong: s.choices({ month: '1999-01' }, months, complete).month,
  none: s.choices({ grid: 'caiso-own' }, months, complete).month,
  empty: s.choices({ grid: 'caiso' }, months, complete).month,
  old: s.choices({}, months).month,
}));
"""

    def test_the_page_opens_on_the_latest_month_that_holds_every_figure(self):
        d = node(self.JS)
        self.assertEqual(d["complete"]["ercot"], ["2026-07", "2026-08"])
        self.assertEqual(d["open"], "2026-08", "the page opens on a month without its fleet")
        self.assertEqual(d["named"], "2026-09", "a month the reader names is shown, complete or not")
        self.assertEqual(d["wrong"], "2026-08")
        self.assertEqual(d["none"], "2025-06", "a grid with no complete month opens on its newest")
        self.assertIsNone(d["empty"])
        self.assertEqual(d["old"], "2026-09")

    def test_the_figures_required_are_the_ones_the_sentence_and_headlines_state(self):
        page = src("site", "app", "shoulder", "page.tsx")
        head = page[page.find('data-summary="1"'):page.find('<ToolSection title="The average day">')]
        second = page[page.find("<HeadlineRow>", page.find('id="worst"')):page.find("{v.worst.length === 0")]
        stated = set(re.findall(r'v\.get\("([a-z0-9_]+)"\)', head + second))
        required = set(node("import { REQUIRED } from './lib/shoulder.ts'; console.log(JSON.stringify(REQUIRED));"))
        # held for some grids only, and the page says so in words where they are absent
        optional = {"curtailed_mwh_per_day", "shoulder_runs_to_midnight", "shoulder2_runs_to_midnight"}
        self.assertEqual(stated - optional, required - {"days_held"}, "REQUIRED and the figures the page states have drifted apart")
        self.assertIn("choices(q, months, complete)", page)
        self.assertIn("opening(months[g.slug] ?? [], complete[g.slug] ?? [])", page, "the grid links still open the newest month")

    def test_on_the_table_as_built(self):
        path = os.path.join(ROOT, "warehouse", "output", "shoulder_hours_monthly.csv")
        if not os.path.exists(path):
            self.skipTest("shoulder_hours_monthly is not on this machine")
        with open(path, encoding="utf-8") as f:
            skip = sum(1 for line in f if line.startswith("#"))
        df = pd.read_csv(path, skiprows=skip, usecols=["entity", "variable", "ts_utc"], dtype=str)
        required = node("import { REQUIRED } from './lib/shoulder.ts'; console.log(JSON.stringify(REQUIRED));")
        for entity in ("iso:ercot", "iso:caiso", "iso:caiso_own"):
            g = df[(df["entity"] == entity) & df["variable"].isin(required)]
            n = g.groupby(g["ts_utc"].str[:7])["variable"].nunique()
            complete = sorted(n[n == len(required)].index)
            held = sorted(df[(df["entity"] == entity) & (df["variable"] == "days_held")]["ts_utc"].str[:7].unique())
            self.assertTrue(complete, f"{entity}: no month holds every figure")
            self.assertLessEqual(complete[-1], held[-1])
            # the month the page opens on holds its fleet; any later month held does not hold every figure
            self.assertFalse(set(m for m in held if m > complete[-1]) & set(complete))


class BuildoutWritesWholeMegawatts(unittest.TestCase):
    def test_mw_and_mwh_have_no_decimals_and_hours_keep_two(self):
        d = node("import * as b from './lib/buildout.ts';"
                 "console.log(JSON.stringify({ a: b.written('battery_operating_mw', 54489.3), b: b.written('battery_operating_mwh', 150437.5),"
                 " c: b.written('battery_operating_mwh_per_mw', 2.7609), d: b.written('battery_mwh_per_solar_mw', 0.8312), e: b.written('battery_operating_units', 812),"
                 " f: b.written('battery_planned_mw_online_2027', 21034.25), g: b.written('battery_operating_mw_net_added_12m', 17689.1), h: b.written('solar_operating_mw', 160012.6) }));")
        self.assertEqual(d, {"a": "54,489", "b": "150,438", "c": "2.76", "d": "0.83", "e": "812", "f": "21,034", "g": "17,689", "h": "160,013"})

    def test_the_whole_variables_are_the_tables_mw_and_mwh(self):
        path = os.path.join(ROOT, "tests", "fixtures", "session69", "storage_buildout_monthly.csv")
        with open(path, encoding="utf-8") as f:
            skip = sum(1 for line in f if line.startswith("#"))
        units = dict(pd.read_csv(path, skiprows=skip, usecols=["variable", "unit"], dtype=str).drop_duplicates().itertuples(index=False))
        whole = node(f"import {{ WHOLE }} from './lib/buildout.ts'; console.log(JSON.stringify({json.dumps(sorted(units))}.filter((v) => WHOLE.test(v))));")
        self.assertEqual(sorted(whole), sorted(v for v, u in units.items() if u in ("MW", "MWh")))
        # the value check reads the same variables as whole numbers
        m = re.search(r"const whole = /(.*)/\.test\(check\);", src("site", "scripts", "check-values.mjs")).group(1)
        rx = re.compile(m.replace(r"\|", "\x00").replace("|", "|").replace("\x00", r"\|"))
        for v, u in units.items():
            key = f"series|storage_buildout_monthly|us:total|{v}|2026-08-01T00:00:00Z"
            self.assertEqual(bool(rx.search(key)), u in ("MW", "MWh"), v)

    def test_the_page_writes_every_value_through_written(self):
        parts = src("site", "app", "storage", "buildout", "parts.tsx")
        self.assertIn("{written(row.variable, row.value)}", parts)
        self.assertIn("${whole(p.value)} ${unit}", parts)
        self.assertNotRegex(src("site", "app", "storage", "buildout", "page.tsx"), r"\bshown\(|toFixed\(")

    def test_the_model_on_its_fixture(self):
        exe = shutil.which("node")
        if not exe:
            self.skipTest("node is not on this machine")
        r = subprocess.run([exe, "scripts/test-buildout.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-1500:])
        self.assertIn("ERCOT has 18,205 MW of batteries holding 30,020 MWh, an average of 1.65 hours, up from 11,046 MW a year ago.", r.stdout)


class House(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        # the two build-out check scripts are not in the list: each has held one since session 69, in the pattern that
        # looks for one on the page
        for rel in ("tests/test_session90.py", "site/lib/supabase.ts", "site/app/page.tsx", "site/scripts/warm-live.mjs", "site/lib/shoulder.ts",
                    "site/app/shoulder/page.tsx", "site/lib/buildout.ts", "site/app/storage/buildout/parts.tsx", "warehouse/supabase/load.py",
                    "warehouse/supabase/migrations/021_eqr_summary.sql", ".github/workflows/code-branch.yml", "site/app/contracts/read.ts"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
