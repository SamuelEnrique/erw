"""Session 1855 (chain 213): the datacenter tracker's faults 2, 3, 5, 6 and 9 of docs/reviews/datacenter-faults-2026-11-11.md,
and row 4's footnote.

Energy Research Warehouse (ERW). The facilities table is held whole, so the fixes are read from the components' source
and proved in Node on the pure function (lib/dcrollups.ts timeline) where one exists.
"""
import json
import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheHoldSaidOnce(unittest.TestCase):
    """Row 2: one sentence where the facilities would be, not two bare words and a list of 25 publishers."""

    def test_the_page_draws_the_held_paragraph_for_a_license_reason(self):
        p = src("site", "app", "datacenters", "page.tsx")
        self.assertIn('import { FacilitiesHeld } from "./Held";', p)
        self.assertIn('{isLicenseReason(res.reason) ? <FacilitiesHeld /> : <NoData what="datacenters" reason={res.reason} />}', p)

    def test_the_paragraph_says_how_many_since_when_and_why(self):
        h = src("site", "app", "datacenters", "Held.tsx")
        self.assertIn('data-facilities-held="1"', h)
        self.assertIn('check="catalogue|datacenter_facilities|n_rows"', h)
        self.assertIn("held from {LICENSE_FROM}", h)
        self.assertIn("the list, the rollups by grid and operator, the timeline and the charts are not drawn", h)
        self.assertIn('href="/data/methods/datacenter_facilities"', h)

    def test_the_beside_it_box_points_up_instead_of_listing_the_publishers(self):
        l = src("site", "app", "datacenters", "LargeLoad.tsx")
        self.assertIn('data-facilities-held-note="1"', l)
        self.assertIn("isLicenseReason(read.reason) ? (", l)
        self.assertIn("The facilities are held (license needed): the note above ERCOT&apos;s section says how many rows, since when and why.", l)
        # the other reasons keep their words
        self.assertIn("The table could not be read, so no number is shown: {read.reason}", l)


class TheHeldCellsOfTheGridTable(unittest.TestCase):
    """Rows 3 and 4: a held margin, peak or capacity is the placeholder with footnote 1, never the hold's words glued to a percent sign."""

    def test_every_held_cell_is_the_placeholder(self):
        f = src("site", "app", "datacenters", "FacilitiesVsGrid.tsx")
        self.assertIn('import { Num, heldBy } from "@/components/Num";', f)
        self.assertIn('rm ? heldBy(gridKey("reserve_margin", g)) ? hold : <span key="r">', f)
        self.assertIn('pc ? heldBy(gridKey("peak_mw", g)) ? hold : <Num key="p"', f)
        self.assertIn('pc ? heldBy(gridKey("capacity_mw", g)) ? hold : <Num key="c"', f)
        self.assertIn("license needed<sup>1</sup>", f)


class TheBarLabels(unittest.TestCase):
    """Row 5: the figures above narrow bars are staggered, so neighbours do not overlap."""

    def test_every_second_series_is_raised_when_bars_are_narrow(self):
        g = src("site", "components", "tool", "GroupedBars.tsx")
        self.assertIn("y={tops[k] - 6 - (bw < 40 && k % 2 ? 12 : 0)}", g)


class TheMapSentence(unittest.TestCase):
    """Row 6: the held count is not glued into the sentence."""

    def test_the_held_case_reads_as_a_sentence(self):
        m = src("site", "app", "map", "page.tsx")
        self.assertIn('import { Num, heldBy } from "@/components/Num";', m)
        self.assertIn('{heldBy("projects|count|queue|none") ? "Some" : <Num check="projects|count|queue|none"', m)
        self.assertIn('{heldBy("projects|count|queue|none") ? " Their count is held (license needed)." : ""}', m)


class TheTimelineReadsTheOldName(unittest.TestCase):
    """Row 9: a row built before chain 156 states the year as planned_year; the timeline reads it."""

    def test_in_source(self):
        d = src("site", "lib", "dcrollups.ts")
        self.assertIn('y = Number(r.extra?.energized_year ?? r.extra?.planned_year ?? "")', d)

    def test_in_node(self):
        script = (
            "import { timeline, timelineCells } from './lib/dcrollups.ts';\n"
            "const row = (id, state, extra, status = 'planned') => ({ entity_id: id, capacity_mw: null, status, operator: 'A', extra: { state, ...extra } });\n"
            "const rows = [row('a', 'TX', { first_story_at: '2026-10-14T13:49:13Z', planned_year: '2029' }), row('b', 'TX', { first_story_at: '2025-03-04T08:00:00Z', planned_year: '2028' }),\n"
            "  row('c', 'TX', { first_story_at: '2026-10-05T10:40:36Z', energized_year: '2028' }), row('d', 'OH', { first_story_at: '2026-09-25T09:24:00Z' }), row('e', 'OH', { planned_year: '2028' })];\n"
            "const t = timeline(rows);\n"
            "console.log(JSON.stringify({ ids: t.map((x) => x.id), waits: t.map((x) => x.wait), grid: timelineCells(t, 'grid') }));\n"
        )
        path = os.path.join(SITE, "test-session1855.mjs")
        with open(path, "w", encoding="utf-8") as f:
            f.write(script)
        try:
            r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "test-session1855.mjs"], cwd=SITE, capture_output=True, text=True, timeout=120)
        finally:
            os.remove(path)
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        got = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(got["ids"], ["b", "c", "a"])   # by first report; d has no year, e no first story
        self.assertEqual(got["waits"], [3, 2, 3])
        self.assertEqual(got["grid"], [{"value": "ERCOT", "count": 3, "median": 3}])


if __name__ == "__main__":
    unittest.main()
