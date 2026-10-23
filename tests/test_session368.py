"""Session 368: /api/download pages by key, not by offset, and takes no row count.

The route's exact row count and its paging by offset passed the anon role's three-second statement timeout on the six
largest tables of the live set and sometimes on four more (session 328's finding; the night note of 20 October 2026,
item 3). The route now reads each page after the last row of the one before, on the primary key of the table's shape,
and ends when a page comes back short. Static tests of the route, and the check of the ten tables' whole files
(site/scripts/check-download.mjs) run against the site named by ERW_CHECK_DOWNLOAD_BASE (skipped when it is unset:
the check downloads about 140 MB and counts the live set by the database).
"""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


ROUTE = ("site", "app", "api", "download", "route.ts")
CHECK = ("site", "scripts", "check-download.mjs")
SIX = ["eia930_all_emissions", "carbon_intensity_hourly", "ercot_as_prices", "state_generation_mix_monthly",
       "eia930_all_generation", "iso_rtm_hub_prices"]
FOUR = ["eia_fuel_spot_prices", "iso_dam_hub_prices", "event_window_daily", "energy_projects"]


def code(text):
    """The route without its comments, so that a word in a comment is not read as code."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(re.sub(r"(^|\s)//.*$", "", line) for line in text.splitlines())


class TheRoutePagesByKey(unittest.TestCase):
    def setUp(self):
        self.r = src(*ROUTE)
        self.c = code(self.r)

    def test_no_count_and_no_offset(self):
        c = self.c
        self.assertNotIn("count=", c)
        self.assertNotIn("Prefer", c)
        self.assertNotIn("content-range", c)
        self.assertNotIn("offset", c)
        self.assertNotRegex(c, r"[?&]offset=")

    def test_the_key_is_each_shapes_primary_key_in_the_live_set(self):
        # warehouse/supabase/migrations: series (table_name, entity, variable, ts_utc, event) since 011; entities and events
        m001 = src("warehouse", "supabase", "migrations", "001_shapes.sql")
        m011 = src("warehouse", "supabase", "migrations", "011_series_event_key.sql")
        self.assertIn("primary key (table_name, entity, variable, ts_utc, event)", m011)
        self.assertIn("primary key (table_name, entity_id)", m001)
        self.assertIn("primary key (table_name, event_id)", m001)
        self.assertIn('const KEY: Record<string, string[]> = { series: ["entity", "variable", "ts_utc", "event"], '
                      'entities: ["entity_id"], events: ["event_id"] };', self.c)
        self.assertIn("&order=${order}&limit=${PAGE}", self.c)        # the order is the key's, a page at a time
        self.assertIn("const order = key.join(\",\");", self.c)

    def test_each_page_starts_after_the_last_row_and_a_short_page_of_the_last_range_ends(self):
        c = self.c
        body = c[c.index("async function* pages("):c.index("export async function GET")]
        self.assertIn("`&${key[0]}=gt.${enc(last.k0)}`", body)                           # one-column key
        self.assertIn("&ts_utc=gte.${enc(t)}&or=${enc(`(ts_utc.gt.${quoted(t)},event.gt.${quoted(ev)})`)}", body)
        self.assertIn("`&entity=eq.${enc(e)}&variable=gt.${enc(v)}`", body)
        self.assertIn("`&entity=gt.${enc(e)}`", body)
        self.assertIn("if (rows.length < PAGE) return;", body)
        self.assertIn("todo = rows.length === PAGE ? ranges(rows[rows.length - 1]) : todo.slice(1);", body)
        # the key is read under its own names, so the CSV's cells are what they were (event is not one of its columns)
        self.assertIn("key.map((k, i) => `k${i}:${k}`)", body)

    def test_anon_key_only(self):
        self.assertIn("process.env.SUPABASE_ANON_KEY", self.c)
        self.assertNotIn("SERVICE", self.r)

    def test_the_stream_is_pulled_not_pushed(self):
        c = self.c
        self.assertIn("async pull(ctl)", c)
        self.assertNotIn("async start(ctl)", c)
        self.assertIn("async cancel()", c)
        self.assertIn("if (n > ROW_CAP) throw new Error(", c)  # session 1009: the cap, MAX_ROWS or lower from the environment                      # past the limit: an error, never a short file

    def test_a_small_table_keeps_its_count_line(self):
        c = self.c
        self.assertIn("const counted = done ? `${n} rows` :", c)
        self.assertIn("`# Downloaded from the ERW site's live set (Supabase) at ${at}: ${counted}.\\n`", c)

    def test_the_checks_before_the_rows_stand(self):
        r = self.r
        self.assertLess(r.index("if (licenseNeeded(table)) return text("), r.index('const lim = await limited(req, "download", PER_HOUR, 3600);'))
        self.assertLess(r.index('const lim = await limited(req, "download", PER_HOUR, 3600);'), r.index("const it = pages("))
        self.assertIn("export const maxDuration = 300;", r)


class TheDataPageSaysTheLimit(unittest.TestCase):
    def test_the_sentence_names_the_routes_limit(self):
        r = src(*ROUTE)
        m = re.search(r"const MAX_ROWS = ([0-9_]+);", r)
        n = int(m.group(1).replace("_", ""))
        self.assertIn(f"up to {n:,} rows", src("site", "app", "data", "page.tsx"))


class TheCheck(unittest.TestCase):
    def test_it_reads_the_ten_tables_and_counts_by_the_database(self):
        c = src(*CHECK)
        for t in SIX + FOUR:
            self.assertIn(f'"{t}"', c)
        self.assertIn('Prefer: "count=exact"', c)
        self.assertIn("process.exit(bad ? 1 : 0);", c)
        self.assertNotIn("SERVICE", c)

    def test_against_a_site(self):
        base = os.environ.get("ERW_CHECK_DOWNLOAD_BASE")
        if not base:
            self.skipTest("ERW_CHECK_DOWNLOAD_BASE is not set")
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not on the path")
        p = subprocess.run([node, os.path.join(ROOT, *CHECK), base], cwd=os.path.join(ROOT, "site"),
                           capture_output=True, text=True, encoding="utf-8", timeout=3600)
        self.assertEqual(p.returncode, 0, p.stdout[-4000:] + p.stderr[-2000:])
        self.assertIn("10 of 10 files whole", p.stdout)


if __name__ == "__main__":
    unittest.main()
