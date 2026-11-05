"""Session 500: the deal tracker and the datacenter tracker on their public rows (chain 023).

With session 499's reader, a table held by row is read for its public rows; the deal views and /datacenters show them
as they show every row, with their sources, and a line (components/tool/HeldRows.tsx) says how many rows are held, a
count recomputed by check-values (held|<shape>|<table>|rows). With no table marked `hold: "row"` today, the line draws
nothing and the pages are as they were: the tests read that from the status file and the code paths.
"""

import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheLine(unittest.TestCase):
    def test_the_line_draws_nothing_unless_held_by_row(self):
        t = src("site", "components", "tool", "HeldRows.tsx")
        self.assertIn("if (!licenseNeeded(table) || !licenseByRow(table)) return null;", t)
        self.assertIn("held|${shape}|${table}|rows", t)
        self.assertIn("heldRowCount(shape, table)", t)

    def test_the_count_is_a_count_never_a_row(self):
        d = src("site", "lib", "data.ts")
        body = d[d.index("export async function heldRowCount"):]
        self.assertIn("restHeldRowCount(shape, { table_name: `eq.${table}` }, HOURLY)", body)
        s = src("site", "lib", "supabase.ts")
        body = s[s.index("export async function restHeldRowCount"):s.index("async function restCountRaw")]
        self.assertIn("restCountRaw(table, heldRowsQuery(query), revalidate)", body)

    def test_check_values_recomputes_the_count(self):
        c = src("site", "scripts", "check-values.mjs")
        i = c.index('if (p[0] === "held") {')
        body = c[i:i + 500]
        self.assertIn('or: "(extra->>row_license.is.null,extra->>row_license.neq.public)"', body)
        self.assertIn("table_name: `eq.${p[2]}`", body)
        self.assertIn("q(p[1],", body)
        # the same filter as the site's reader
        self.assertIn("${ROW_LICENSE_FILTER}.is.null,${ROW_LICENSE_FILTER}.neq.${ROW_LICENSE_PUBLIC}", src("site", "lib", "supabase.ts"))


class ThePages(unittest.TestCase):
    PAGES = {
        ("site", "app", "deals", "page.tsx"): 'table="energy_deals"',
        ("site", "app", "deals", "v2", "view.tsx"): 'table="energy_deals"',
        ("site", "app", "deals", "comparables", "view.tsx"): 'table="energy_deals"',
        ("site", "app", "datacenters", "page.tsx"): 'table="datacenter_facilities"',
    }

    def test_each_view_draws_the_line_beside_its_rows(self):
        for p, table in self.PAGES.items():
            t = src(*p)
            self.assertIn("<HeldRows ", t, p)
            self.assertIn(table, t, p)

    def test_the_held_whole_paths_are_kept(self):
        # held whole (today): the catalogue's words and session 465's line, unchanged
        for p in (("site", "app", "deals", "page.tsx"), ("site", "app", "deals", "v2", "view.tsx"), ("site", "app", "deals", "comparables", "view.tsx")):
            t = src(*p)
            self.assertIn("isLicenseReason(", t, p)
            self.assertIn("<DealsHeld />", t, p)

    def test_no_table_is_marked_by_row_today(self):
        status = json.loads(src("site", "data", "license_status.json"))
        for t in ("energy_deals", "datacenter_facilities", "datacenter_projects", "datacenter_operator_sites"):
            self.assertEqual(status["tables"][t]["status"], "license needed", t)
            self.assertNotEqual(status["tables"][t].get("hold"), "row", t)

    def test_the_method_notes_say_how_a_row_is_shown(self):
        for p, key in ((("docs", "methods", "energy_deals.md"), "held|events|energy_deals|rows"),
                       (("docs", "methods", "datacenter_facilities.md"), "held|entities|datacenter_facilities|rows")):
            t = src(*p)
            self.assertIn("## Held by row: how a row is shown (sessions 499 and 500)", t)
            self.assertIn(key, t)
            self.assertIn("`row_license`", t)

    def test_no_em_dash(self):
        for p in (("site", "components", "tool", "HeldRows.tsx"), ("tests", "test_session500.py"),
                  ("docs", "methods", "energy_deals.md"), ("docs", "methods", "datacenter_facilities.md"),
                  *self.PAGES.keys()):
            t = src(*p)
            self.assertNotIn(chr(0x2014), t, p)
            self.assertNotIn(chr(0x2013), t, p)


if __name__ == "__main__":
    unittest.main()
