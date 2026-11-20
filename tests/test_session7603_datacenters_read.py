"""Session 7603 (chain 305, part C, the portable laptop): the datacenter tracker (`/datacenters`) read as its reader, a
fund analyst sizing datacenter load in one utility's territory (docs/reviews/datacenters-read-2026-11-16.md).

1. "The facilities against each grid" (view=grids) printed "license needed" in every cell, the grid's own peak hour
   and capacity and ERCOT's reserve margin among them, though the component's rule is that a grid's public figures
   stay: `heldBy` read the key's first word, dcgrid, as datacenter_facilities (held whole). The peak and the capacity
   are grid_peak_vs_capacity's and the margin ercot_cdr_reserve_margins': both public in site/data/license_status.json.
   Num.tsx and check-holds.mjs (its mirror) now ask those tables; the facilities' columns stay held.
2. ERCOT's table of reports wrote "March 2026 (as written; the report is of 2026)" beside the report of 24 April 2026:
   the note named the year alone. It now names the report's month and year ("the report is of April 2026").
Energy Research Warehouse (ERW)."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
DASHES = (chr(0x2014), chr(0x2013))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheGridsPublicFigures(unittest.TestCase):
    def test_num_asks_the_grid_tables(self):
        s = src("site", "components", "Num.tsx")
        self.assertIn('else if (head === "dcgrid" && (p[1] === "peak_mw" || p[1] === "capacity_mw")) table = "grid_peak_vs_capacity";', s)
        self.assertIn('else if (head === "dcgrid" && p[1] === "reserve_margin") table = "ercot_cdr_reserve_margins";', s)
        # before the first-word map, which still sends every other dcgrid key (the facilities) to the held table
        self.assertLess(s.index('table = "grid_peak_vs_capacity"'), s.index("else if (head in KEY_TABLE) table = KEY_TABLE[head];"))
        self.assertIn('dcgrid: "datacenter_facilities"', s)

    def test_check_holds_mirrors_it(self):
        s = src("site", "scripts", "check-holds.mjs")
        self.assertIn('else if (head === "dcgrid" && (p[1] === "peak_mw" || p[1] === "capacity_mw")) table = "grid_peak_vs_capacity";', s)
        self.assertIn('else if (head === "dcgrid" && p[1] === "reserve_margin") table = "ercot_cdr_reserve_margins";', s)

    def test_the_two_tables_are_public(self):
        lic = json.loads(src("site", "data", "license_status.json"))["all"]   # every table; "tables" holds the held ones
        self.assertEqual(lic["grid_peak_vs_capacity"]["status"], "public")
        self.assertEqual(lic["ercot_cdr_reserve_margins"]["status"], "public")
        self.assertEqual(lic["datacenter_facilities"]["status"], "license needed")

    def test_the_facilities_columns_stay_held(self):
        s = src("site", "app", "datacenters", "FacilitiesVsGrid.tsx")
        self.assertIn('held ? hold : l ? <Num key="f" check={gridKey("facilities", g)}', s)
        self.assertIn('held ? hold : share === null ? none', s)


class TheReportsMonth(unittest.TestCase):
    def test_the_note_names_the_reports_month(self):
        lib = src("site", "lib", "largeload.ts")
        self.assertIn("export function reportMonth(r: Report): string {", lib)
        self.assertIn("return `${MONTHS[Number(r.day.slice(5, 7)) - 1]} ${r.day.slice(0, 4)}`;", lib)
        page = src("site", "app", "datacenters", "LargeLoad.tsx")
        self.assertIn('" (as written; the report is of " + reportMonth(r) + ")"', page)
        self.assertNotIn('" (as written; the report is of " + r.day.slice(0, 4) + ")"', page)

    def test_no_dash(self):
        for p in (("site", "components", "Num.tsx"), ("site", "scripts", "check-holds.mjs"), ("site", "lib", "largeload.ts"), ("site", "app", "datacenters", "LargeLoad.tsx")):
            text = src(*p)
            for ch in DASHES:
                self.assertNotIn(ch, text, p)


if __name__ == "__main__":
    unittest.main()
