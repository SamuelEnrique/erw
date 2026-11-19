"""Session 8605 (chain 504, 19 November 2026): the reader's read of the Grid tool's region views on the data machine's
real files, and the faults it found, each fixed at its cause.

Energy Research Warehouse (ERW). The thirteen regions' files reached main at about 13:35 UTC; five cases a named
reader would bring were then taken in a browser on a build (docs/reviews/grid-map-read-2026-11-19.md, rows 18 on).
What is held here, row by row of that read:
- row 18: the region's hour by hour chart draws each hour as its own column, a source above zero up from zero and a
  source below zero down from zero, and an hour not held is a gap (the first chart drew a comb, the second a block);
- row 19: the months a region's mix file does not hold are counted under the month chips and named on hover, with
  the data machine's rule;
- row 20: a month the trade reports hold in part is said so, with the file's hours;
- row 21: where one of a region's balancing authorities files no battery series, the Storage row says so on hover.
The figures below are made up for the tests and are in no page. The browser's proof is
site/scripts/check-grid-regions.mjs. Nothing here sets the environment or makes a request.
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


@unittest.skipUnless(NODE, "node is not installed")
class TheHoursStack(unittest.TestCase):
    """Row 18."""

    @classmethod
    def setUpClass(cls):
        cls.d = node("import { hourStack, lastHours } from './lib/gridregions.ts';"
                     "const f = { hourly: { hours: { start: '2026-10-13T05:00:00Z', step_hours: 1, n: 4 }, nuclear: [10, 11, null, 13], demand: [20, 21, 22, 23] } };"
                     "const h = lastHours(f, 35);"
                     "console.log(JSON.stringify({ day: hourStack([100, 40, 0, 25]), night: hourStack([100, -5, 30, -20]), gap: hourStack([null, 7, undefined, -3]), none: hourStack([null, null]),"
                     " x: h.x, t: h.t, nuclear: h.get('nuclear'), absent: h.get('wind') }));")

    def test_sources_above_zero_stack_up_from_zero(self):
        self.assertEqual(self.d["day"]["bands"], [[0, 100], [100, 140], None, [140, 165]])
        self.assertEqual((self.d["day"]["top"], self.d["day"]["bottom"]), (165, 0))

    def test_a_source_below_zero_goes_down_from_zero_and_is_not_hidden_in_the_stack(self):
        self.assertEqual(self.d["night"]["bands"], [[0, 100], [-5, 0], [100, 130], [-25, -5]])
        self.assertEqual((self.d["night"]["top"], self.d["night"]["bottom"]), (130, -25))

    def test_an_hour_a_source_does_not_hold_is_no_band_and_moves_nothing(self):
        self.assertEqual(self.d["gap"]["bands"], [None, [0, 7], None, [-3, 0]])
        self.assertEqual(self.d["none"], {"bands": [None, None], "top": 0, "bottom": 0})

    def test_the_hours_carry_their_own_time(self):
        self.assertEqual(self.d["x"][0], "2026-10-13 05")
        self.assertEqual(self.d["t"][0], 1791867600000)                       # 2026-10-13T05:00:00Z
        self.assertEqual([b - a for a, b in zip(self.d["t"], self.d["t"][1:])], [3600000] * 3)
        self.assertEqual(self.d["nuclear"], [10, 11, None, 13])               # the hour not held stays blank

    def test_the_chart_draws_by_that_rule_and_says_not_held(self):
        s = src("site", "components", "grid", "RegionHours.tsx")
        self.assertIn("hourStack(layers.map((l) => l.values[i]))", s)
        self.assertIn('"not held"', s)
        self.assertIn("if (!band) continue;", s)                              # no column for an hour not held
        self.assertIn("data-hours-card", s)
        self.assertIn("<DataTable", s)                                        # the same hours as a table
        v = src("site", "components", "grid", "RegionViews.tsx")
        self.assertIn("<RegionHours id={`erw-region-hours-${code}`}", v)
        self.assertNotIn("StackedArea", v)


@unittest.skipUnless(NODE, "node is not installed")
class TheMonthsNotHeld(unittest.TestCase):
    """Row 19."""

    @classmethod
    def setUpClass(cls):
        cls.d = node("import { monthsNotHeld } from './lib/gridregions.ts';"
                     "const f = (keys) => ({ months: Object.fromEntries(keys.map((k) => [k, {}])) });"
                     "console.log(JSON.stringify({ gaps: monthsNotHeld(f(['2025-11', '2026-01', '2026-02', '2026-05'])), whole: monthsNotHeld(f(['2025-12', '2026-01', '2026-02'])),"
                     " one: monthsNotHeld(f(['2026-03'])), none: monthsNotHeld(f([])), odd: monthsNotHeld(f(['2026-01', 'note', '2026-03'])) }));")

    def test_the_months_between_the_first_and_the_newest_that_are_absent(self):
        self.assertEqual(self.d["gaps"], {"span": 7, "missing": ["2025-12", "2026-03", "2026-04"], "after": []})

    def test_a_file_with_every_month_has_none(self):
        self.assertEqual(self.d["whole"], {"span": 3, "missing": [], "after": []})
        self.assertEqual(self.d["one"], {"span": 1, "missing": [], "after": []})
        self.assertEqual(self.d["none"], {"span": 0, "missing": [], "after": []})

    def test_a_key_that_is_no_month_is_not_counted(self):
        self.assertEqual(self.d["odd"], {"span": 3, "missing": ["2026-02"], "after": []})

    def test_the_whole_months_since_the_newest_held_and_before_the_month_of_the_build(self):
        d = node("import { monthsNotHeld } from './lib/gridregions.ts';"
                 "const f = (keys, built) => ({ built, months: Object.fromEntries(keys.map((k) => [k, {}])) });"
                 "console.log(JSON.stringify({ stale: monthsNotHeld(f(['2025-11', '2025-12'], '2026-03-19T12:02:00Z')), fresh: monthsNotHeld(f(['2026-01', '2026-02'], '2026-03-19T12:02:00Z')),"
                 " same: monthsNotHeld(f(['2026-03'], '2026-03-19T12:02:00Z')), odd: monthsNotHeld(f(['2025-12'], 'soon')) }));")
        self.assertEqual(d["stale"], {"span": 2, "missing": [], "after": ["2026-01", "2026-02"]})     # the month of the build is in progress and is not counted
        self.assertEqual(d["fresh"]["after"], [])
        self.assertEqual(d["same"]["after"], [])
        self.assertEqual(d["odd"]["after"], [])
        v = src("site", "components", "grid", "RegionViews.tsx")
        self.assertIn("data-months-after={gaps.after.length}", v)
        self.assertIn("the newest month held is", v)

    def test_the_page_counts_them_and_gives_the_rule_on_hover(self):
        v = src("site", "components", "grid", "RegionViews.tsx")
        self.assertIn("data-months-not-held={gaps.missing.length}", v)
        self.assertIn("at least 90 percent of its days hold every hour of every source", v)
        self.assertIn("never drawn as zero", v)
        self.assertIn("at least 90 percent of its days are complete", src("docs", "methods", "regions_pages.md"))   # the rule is the data machine's


@unittest.skipUnless(NODE, "node is not installed")
class ThePartMonth(unittest.TestCase):
    """Row 20."""

    @classmethod
    def setUpClass(cls):
        cls.d = node("import { partMonth } from './lib/gridregions.ts';"
                     "const n = (own) => ({ net_imports_mwh: [1, 1], their_report_mwh: [1, 1], gap_mwh: [0, 0], hours_own: own, hours_their: [744, 400], hours_both: own });"
                     "const f = { months: ['2026-10', '2026-11'], hours_in_month: [744, 721], net_imports_mwh: [2, null], neighbors: { A: n([744, 336]), B: n([519, 228]) } };"
                     "const short = { ...f, neighbors: { B: n([519, null]) } };"
                     "const silent = { ...f, hours_in_month: undefined };"
                     "console.log(JSON.stringify({ whole: partMonth(f, '2026-10'), part: partMonth(f, '2026-11'), short: partMonth(short, '2026-10'), blank: partMonth(short, '2026-11'),"
                     " silent: partMonth(silent, '2026-11'), other: partMonth(f, '2019-01') }));")

    def test_a_whole_month_says_nothing(self):
        self.assertIsNone(self.d["whole"])

    def test_a_month_in_progress_gives_the_most_hours_of_the_regions_own_report(self):
        self.assertEqual(self.d["part"], {"hours": 336, "of": 721})

    def test_a_month_one_side_reported_in_part(self):
        self.assertEqual(self.d["short"], {"hours": 519, "of": 744})
        self.assertEqual(self.d["blank"], {"hours": 0, "of": 721})

    def test_nothing_is_said_when_the_file_does_not_say_the_months_hours(self):
        self.assertIsNone(self.d["silent"])
        self.assertIsNone(self.d["other"])

    def test_the_page_says_it_beside_the_table_and_under_the_chart(self):
        v = src("site", "components", "grid", "RegionViews.tsx")
        self.assertIn("data-part-month=", v)
        self.assertIn("data-part-month-chart=", v)
        self.assertIn("is a part of a month", v)


@unittest.skipUnless(NODE, "node is not installed")
class TheStorageRow(unittest.TestCase):
    """Row 21."""

    @classmethod
    def setUpClass(cls):
        cls.d = node("import { NO_BATTERY_SERIES, storageNote } from './lib/gridregions.ts';"
                     "console.log(JSON.stringify({ who: NO_BATTERY_SERIES, cal: storageNote({ name: 'California', bas: ['BANC', 'CISO', 'IID', 'LDWP', 'TIDC'] }), ny: storageNote({ name: 'New York', bas: ['NYIS'] }),"
                     " mida: storageNote({ name: 'Mid-Atlantic', bas: ['OVEC', 'PJM'] }), tex: storageNote({ name: 'Texas', bas: ['ERCO'] }) }));")

    def test_the_three_grids_are_the_storage_pages_three(self):
        self.assertEqual(self.d["who"], {"CISO": "CAISO", "NYIS": "NYISO", "PJM": "PJM"})
        page = src("site", "app", "storage", "page.tsx")
        self.assertIn("CAISO reports no battery series in EIA-930. NYISO and PJM report none in either.", page)

    def test_a_region_with_other_authorities_says_whose_figure_the_row_is(self):
        self.assertEqual(self.d["cal"], "CAISO files no battery series in Form EIA-930. This row holds what California's other 4 balancing authorities report, not CAISO's batteries. CAISO's own battery data is on the Storage page.")
        self.assertEqual(self.d["mida"], "PJM files no battery series in Form EIA-930. This row holds what Mid-Atlantic's other balancing authority reports, not PJM's batteries.")

    def test_a_region_of_one_authority(self):
        self.assertEqual(self.d["ny"], "NYISO files no battery series in Form EIA-930. It is New York's one balancing authority, so this row is the figure the region's file holds, not NYISO's batteries.")

    def test_a_region_whose_authorities_all_file_says_nothing(self):
        self.assertIsNone(self.d["tex"])

    def test_the_row_carries_the_hover_in_both_tables(self):
        v = src("site", "components", "grid", "RegionViews.tsx")
        self.assertIn('data-storage-note="1"', v)
        self.assertEqual(v.count("{named(s.key)}"), 3)                       # the latest hour's rows, the shares' rows, and (session 8610) the shares' blank rows


class TheRest(unittest.TestCase):
    def test_the_release_gate_is_not_touched(self):
        s = src("site", "lib", "release.ts")
        self.assertNotIn("session 8605", s)

    def test_the_trade_chart_has_a_label_a_year(self):
        """Row 22: a step of six months put the labels on one another at 390 px, and so did the chart's own thinning; a label a year stands apart."""
        v = src("site", "components", "grid", "RegionViews.tsx")
        self.assertIn('<Lines x={last} unit="MWh" zero every={12} name=', v)
        self.assertNotIn("every={6}", v)

    def test_the_check_reads_the_three_from_the_file(self):
        s = src("site", "scripts", "check-grid-regions.mjs")
        for name in ("monthsNotHeld(mixFile)", "partMonth(trade, month)", "storageNote(withNone)", "data-hours-card"):
            self.assertIn(name, s)

    def test_no_em_dash(self):
        for p in (("site", "components", "grid", "RegionHours.tsx"), ("site", "components", "grid", "RegionViews.tsx"), ("site", "lib", "gridregions.ts"), ("tests", "test_session8605.py")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()
