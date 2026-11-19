"""Session 8604 (chain 504, 19 November 2026): the reader's read of the Grid tool's map, and the faults it found,
each fixed at its cause.

Energy Research Warehouse (ERW). Five cases a named reader would bring were taken in a browser on a build
(docs/reviews/grid-map-read-2026-11-19.md). What is held here, row by row of that read:
- row 1: a tie's hover names the one table its megawatts come from, not the tables of demand and carbon intensity;
- row 2: a tie's two names stand once, in the head; who reported is said by code;
- row 3: with a grid chosen that is none of the seven, the fold under the map says its twelve months are not held,
  not "Click a grid";
- row 4: "California's evening" shows the newest whole Pacific day for which the batteries are reported, and names a
  newer whole day it passed over; with no report at all, the newest whole day, as before;
- row 8: a region's hover names the other footprints that hold the point under the pointer;
- row 9: the states' outlines are drawn, and the hover names the state under the pointer;
- row 10: the panel says an authority's local time from the index's time zone, when the index is on the site.
The browser's proof is site/scripts/check-grid-map.mjs. Nothing here sets the environment or makes a request.
"""

import json
import os
import re
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
class TheEveningsDay(unittest.TestCase):
    """Row 4. A week of 168 hours from 2026-11-11T00:00Z: the whole Pacific days are 11 to 16 November (the 10th and the 17th are cut)."""

    @classmethod
    def setUpClass(cls):
        cls.d = node("import { eveningDay, wholePacificDays } from './lib/networkV3.ts';"
                     "const hours = Array.from({ length: 168 }, (_, i) => new Date(Date.parse('2026-11-11T00:00:00Z') + i * 3600000).toISOString().replace('.000Z', 'Z'));"
                     "const days = wholePacificDays(hours);"
                     "const upto = (n) => hours.map((_, i) => (i < n ? 100 : null));"                 # batteries reported for the first n hours of the week
                     "const of = (b) => { const e = eveningDay(hours, b); return e ? [e.day, e.idx[0], e.idx.length, e.passed] : null; };"
                     "const gap = upto(168); gap[60] = null;"                                         # one hour of 13 November not reported
                     "console.log(JSON.stringify({ days: days.map((d) => [d.day, d.idx.length, hours[d.idx[0]]]), all: of(upto(168)), none: of(upto(0)), missing: of(undefined),"
                     " lag: of(upto(128)), lag2: of(upto(100)), gap: of(gap), short: eveningDay(hours.slice(0, 20), upto(20)) }));")

    def test_the_whole_pacific_days_of_the_week(self):
        self.assertEqual([d[0] for d in self.d["days"]], ["2026-11-16", "2026-11-15", "2026-11-14", "2026-11-13", "2026-11-12", "2026-11-11"])
        self.assertTrue(all(d[1] == 24 for d in self.d["days"]))
        self.assertEqual(self.d["days"][0][2], "2026-11-16T08:00:00Z")          # midnight Pacific, in standard time

    def test_with_every_hour_reported_it_is_the_newest_whole_day_as_before(self):
        self.assertEqual(self.d["all"], ["2026-11-16", 128, 24, []])

    def test_with_no_report_at_all_it_is_the_newest_whole_day_as_before(self):
        self.assertEqual(self.d["none"], ["2026-11-16", 128, 24, []])
        self.assertEqual(self.d["missing"], ["2026-11-16", 128, 24, []])

    def test_a_newer_day_with_no_report_is_passed_over_and_named(self):
        # the batteries end where 16 November (Pacific) begins: the 15th is shown and the 16th named
        self.assertEqual(self.d["lag"], ["2026-11-15", 104, 24, ["2026-11-16"]])
        # they end during the 14th: the 13th is shown, and the three newer days named, newest first
        self.assertEqual(self.d["lag2"], ["2026-11-13", 56, 24, ["2026-11-16", "2026-11-15", "2026-11-14"]])

    def test_one_hour_missing_does_not_pass_a_day_over(self):
        self.assertEqual(self.d["gap"], ["2026-11-16", 128, 24, []])

    def test_a_week_with_no_whole_day(self):
        self.assertIsNone(self.d["short"])

    def test_the_story_reads_the_rule_and_says_what_it_passed(self):
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn("const e = eveningDay(snap.hours, live.batteries.CISO);", n)
        self.assertIn("this is the newest day that holds them.", n)
        self.assertIn('setFailed("The live week holds no complete Pacific day.");', n)          # as before, when there is none
        self.assertIn("title: `California's evening, ${d} (Pacific)`", n)                       # the title's form is as it was


@unittest.skipUnless(NODE, "node is not installed")
class TheTiesHover(unittest.TestCase):
    def test_who_reported_is_said_by_code_and_the_names_stand_once(self):
        got = node("import { flowTip } from './lib/networkMap.ts';"
                   "const long = 'LG&E and KU Services Company as agent for Louisville Gas and Electric Company and Kentucky Utilities Company';"
                   "const t = flowTip({ from: 'LGEE', to: 'PJM', fromName: long, toName: 'PJM Interconnection, LLC', mw: 457, when: '2026-11-17 04:00 UTC', unit: 'hour', a: 'LGEE', b: 'PJM', aName: long, bName: 'PJM Interconnection, LLC', side: null });"
                   "console.log(JSON.stringify([t.head, t.lines, [t.head, ...t.lines].join(' ').split(long).length - 1]));")
        self.assertEqual(got[1][2], "Reported by LGEE, the first of the two by code; where LGEE filed nothing for this hour, by PJM. The file does not mark which.")
        self.assertEqual(got[2], 1)                                               # the long name once, in the head
        self.assertTrue(got[0].endswith("to PJM Interconnection, LLC (PJM)"))

    def test_a_ties_megawatts_come_from_the_interchange_table_alone(self):
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn('flowTable: isDayView ? "eia930_daily_interchange" : view.kind === "live" ? "eia930_all_interchange" : "eia930_event_hourly_interchange" };', n)
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertIn('source: frame?.flowTable ?? frame?.tables ?? "" };', m)


class ThePageAroundTheReadersCases(unittest.TestCase):
    def setUp(self):
        self.n = src("site", "app", "network", "Network.tsx")
        self.m = src("site", "app", "network", "NetworkMap.tsx")

    def test_a_grid_chosen_with_no_twelve_months_says_so(self):
        self.assertIn("<p className=\"mt-2\" data-neighbours-not-held={pick.id}>Not held for {pick.name}: ", self.n)
        self.assertIn('<p className="mt-2 text-muted">Click a grid, or choose one above.</p>', self.n)     # with no grid chosen, as before
        self.assertLess(self.n.index("data-neighbours-not-held"), self.n.index("Click a grid, or choose one above."))

    def test_the_other_footprints_under_the_pointer(self):
        self.assertIn("document.elementsFromPoint(e.clientX, e.clientY)", self.m)
        self.assertIn("lines.push(`Also covers this point: ${hover.also.map((id) => names.get(id) ?? id).join(\"; \")}`);", self.m)

    def test_the_states_lines_name_nothing_and_answer_no_pointer(self):
        block = self.m.split("data-state-lines={states.length}")[0].rsplit("<g ", 1)[1]
        self.assertIn('pointerEvents="none"', block)
        self.assertIn('fill="none"', block)
        self.assertIn('import("us-atlas/states-10m.json")', self.m)                # read with the map, not with the page
        self.assertNotIn("<text", self.m)                                          # names are on hover only
        self.assertIn("lines.push(`State under the pointer: ${hover.state}`);", self.m)
        # the network's own chunk does not read the states
        self.assertNotIn("us-atlas", self.n)

    def test_the_local_time_from_the_index(self):
        self.assertIn("(LOCAL_TZ[pick.id] ?? baRegions?.[pick.id]?.tz) ? <>{localTime(ts, (LOCAL_TZ[pick.id] ?? baRegions?.[pick.id]?.tz) as string)} local time</>", self.n)
        self.assertIn("(its local time is not held)", self.n)                      # without the index, as before

    def test_the_read_is_written_and_every_row_has_a_state(self):
        read = src("docs", "reviews", "grid-map-read-2026-11-19.md")
        rows = re.findall(r"^\| (\d+) \| .* \| (fixed|data machine|ruling|not a fault|waiting)[^|]*\|$", read, re.M)
        self.assertGreaterEqual(len(rows), 12)
        self.assertEqual([int(r[0]) for r in rows], list(range(1, len(rows) + 1)))
        for case in ("transmission planner", "power trader", "student", "siting analyst", "battery developer"):
            self.assertIn(case, read)
        self.assertNotIn(EM, read)

    def test_no_em_dash(self):
        for parts in (("site", "lib", "networkV3.ts"), ("site", "lib", "networkMap.ts"), ("site", "app", "network", "NetworkMap.tsx"), ("site", "app", "network", "Network.tsx"),
                      ("site", "components", "grid", "BaRegions.tsx"), ("site", "scripts", "check-grid-map.mjs"), ("tests", "test_session8604.py")):
            self.assertNotIn(EM, src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
