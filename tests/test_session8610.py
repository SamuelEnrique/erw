"""Session 8610 (chain 504, 19 November 2026): the region tabs made ready for a source no authority has ever printed.

Energy Research Warehouse (ERW). Data request 551 found the region files writing 0 where EIA publishes no series at
all (storage for New York and the Mid-Atlantic, wind for the Carolinas and Florida, coal for New England). The data
machine's answer (the contract's line of 19 November, session 8011): such a source is null all through the region's
mix file (its averages, its energy, its share, its hourly array) and named in a new key, sources_not_printed. The
files in that form were not on main when this was written. What is held here, on a made-up file in that form:
- the latest hour gives such a source as not held, and its share as nothing;
- the table of shares draws it as a row, blank in both cells, after the sources that are held: never 0.0% and 0 MWh;
- the hover says no authority of the region has ever reported it, and that it is blank, not zero;
- net load (demand less wind and solar) leaves out a never-printed wind or solar and the page says so; an hour of a
  source that is reported and not held still leaves that hour blank; the file given is not changed;
- the replication reads the same form by the same rule.
The figures below are made up for the tests and are in no page. Nothing here sets the environment or makes a request.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)

# a region of two months in the announced form: solar and storage never printed; wind reported, one of its hours not held
FILE = ("const day = (v) => Array.from({ length: 24 }, () => v);"
        "const month = (demand, wind) => ({ avg: { demand: day(demand), wind, solar: null, storage: null, nuclear: day(40) }, side: 'made up', days_held: 30, days_in_month: 30,"
        " nuclear_mwh: 28800, nuclear_share_pct: 80, wind_mwh: 7200, wind_share_pct: 20, solar_mwh: null, solar_share_pct: null, storage_mwh: null, storage_share_pct: null, net_generation_mwh: 36000 });"
        "const gap = day(10); gap[12] = null;"
        "const file = { grid: 'XX', name: 'Made up', tz: 'America/Chicago', built: '2026-11-19T12:00:00Z', join: null, first: '2025-10', upto: '2026-10', sources: ['nuclear', 'wind', 'solar', 'storage'],"
        " months: { '2025-10': month(100, day(10)), '2026-10': month(120, gap) }, years: {}, sources_not_printed: ['solar', 'storage', 'no_such_source', 7],"
        " hourly: { hours: { start: '2026-11-01T00:00:00Z', step_hours: 1, n: 3 }, nuclear: [40, 41, 42], wind: [10, null, 12], solar: null, storage: null, demand: [60, 61, 62], net_generation: [50, 41, 54], net_imports: [10, 20, 8] } };")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


@unittest.skipUnless(NODE, "node is not installed")
class TheFormTheDataMachineAnnounced(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = node("import { notPrinted, whyBlank, latestHour, lastHours, netLoadFile, readMix } from './lib/gridregions.ts'; import * as mix from './lib/mix2.ts';" + FILE +
                     "const m = readMix(file); const now = latestHour(m); const h = lastHours(m, 35); const n = netLoadFile(m);"
                     "const net = (f, k) => mix.netLoad(f.months[k]);"
                     "console.log(JSON.stringify({ never: notPrinted(m), none: [notPrinted({}), notPrinted(null), notPrinted({ sources_not_printed: 'solar' })], now: now.sources.filter((s) => ['wind', 'solar', 'storage', 'nuclear'].includes(s.key)),"
                     " drawn: ['nuclear', 'wind', 'solar', 'storage'].filter((k) => h.get(k).some((v) => v !== null)), absent: n.absent, raw: net(m, '2025-10').slice(0, 2), fixed: net(n.file, '2025-10').slice(0, 2),"
                     " gapHour: [net(n.file, '2026-10')[11], net(n.file, '2026-10')[12]], untouched: m.months['2025-10'].avg.solar === null && n.file !== m, storageLeft: n.file.months['2025-10'].avg.storage,"
                     " same: netLoadFile({ ...m, sources_not_printed: ['storage'] }).file !== undefined && netLoadFile({ ...m, sources_not_printed: ['storage'] }).absent.length === 0,"
                     " why: [whyBlank('Solar', 'Made up', true), whyBlank('Wind', 'Made up', false), whyBlank('Wind', 'Made up', false, 'this period')], shares: mix.shares(m.months['2026-10']).map((s) => [s.key, s.share, s.mwh]).filter((s) => ['solar', 'storage', 'wind'].includes(s[0])) }));")

    def test_the_sources_named_are_the_pages_own_and_nothing_else(self):
        self.assertEqual(self.d["never"], ["solar", "storage"])              # a key the page does not know, and a number, are left out
        self.assertEqual(self.d["none"], [[], [], []])

    def test_the_latest_hour_gives_them_as_not_held_with_no_share(self):
        by = {s["key"]: s for s in self.d["now"]}
        self.assertEqual((by["solar"]["mw"], by["solar"]["share_pct"]), (None, None))
        self.assertEqual((by["storage"]["mw"], by["storage"]["share_pct"]), (None, None))
        self.assertEqual((by["wind"]["mw"], by["nuclear"]["mw"]), (12, 42))   # the newest hour that holds a net generation is the third

    def test_the_hour_by_hour_chart_draws_only_what_is_held(self):
        self.assertEqual(self.d["drawn"], ["nuclear", "wind"])

    def test_net_load_leaves_out_a_never_printed_source_and_nothing_else(self):
        self.assertEqual(self.d["absent"], ["solar"])                        # storage is no part of net load
        self.assertEqual(self.d["raw"], [None, None])                        # by the seven grids' rule alone the month would be blank
        self.assertEqual(self.d["fixed"], [90, 90])                          # demand 100 less wind 10, no solar to take away
        self.assertEqual(self.d["gapHour"], [110, None])                     # wind is reported and one of its hours is not held: that hour stays blank
        self.assertTrue(self.d["untouched"])
        self.assertIsNone(self.d["storageLeft"])
        self.assertTrue(self.d["same"])

    def test_the_hover_says_why(self):
        self.assertEqual(self.d["why"][0], "No balancing authority of Made up has reported solar to EIA in any hour held since July 2018, so the region's file holds none. It is blank, not zero.")
        self.assertEqual(self.d["why"][1], "Wind is not held for Made up in this hour.")
        self.assertEqual(self.d["why"][2], "Wind is not held for Made up in this period.")

    def test_the_grids_own_shares_would_read_zero_which_is_why_the_table_does_not_use_them_for_such_a_source(self):
        by = {s[0]: s for s in self.d["shares"]}
        self.assertEqual(by["solar"][1:], [0, 0])
        self.assertEqual(by["wind"][1:], [20, 7200])


class TheTables(unittest.TestCase):
    def setUp(self):
        self.v = src("site", "components", "grid", "RegionViews.tsx")

    def test_the_shares_table_draws_a_null_source_blank_after_the_held_ones(self):
        self.assertIn("mix.shares(p).filter((s) => p[`${s.key}_mwh`] !== undefined && p[`${s.key}_mwh`] !== null)", self.v)
        self.assertIn("...mix.SOURCES.filter((s) => p[`${s.key}_mwh`] === null).map((s) => ({ key: s.key, cells: [", self.v)
        self.assertEqual(self.v.count('whyBlank(s.label, region.name, never.includes(s.key), "this period")'), 2)

    def test_the_latest_hours_table_says_why(self):
        self.assertIn('<NH key="m" words="not held" why={whyBlank(label(s.key), region.name, never.includes(s.key))} />', self.v)
        self.assertIn("const never = notPrinted(mixFile);", self.v)

    def test_the_net_load_says_what_it_is_without(self):
        self.assertIn("const forNet = netLoadFile(mixFile);", self.v)
        self.assertIn("mix.acrossYears(forNet.file as unknown as mix.GridFile, calAsked)", self.v)
        self.assertIn('data-net-load-without={forNet.absent.join(",")}', self.v)
        self.assertIn("so net load here is demand less", self.v)

    def test_the_seven_grids_rule_is_not_changed(self):
        lib = src("site", "lib", "mix2.ts")
        self.assertIn("return Array.from({ length: 24 }, (_, h) => (d[h] == null || w[h] == null || s[h] == null ? null : Math.round((d[h]! - w[h]! - s[h]!) * 10) / 10));", lib)
        self.assertNotIn("sources_not_printed", lib)


class TheReplication(unittest.TestCase):
    def test_it_reads_the_same_form_by_the_same_rule(self):
        r = src("replication", "grid", "replicate_regions.py")
        self.assertIn('never = [k for k in (mix.get("sources_not_printed") or []) if k in ("wind", "solar")]', r)
        self.assertIn('w = [0.0] * 24 if "wind" in never and avg.get("wind") is None else (avg.get("wind") or [])', r)
        self.assertIn("None if mwh is None or not total else mwh / total * 100", r)
        self.assertIn("net_load_without", src("replication", "grid", "regions_figures.mjs"))

    def test_a_blank_on_one_side_only_is_not_met(self):
        spec = importlib.util.spec_from_file_location("replicate_regions", os.path.join(ROOT, "replication", "grid", "replicate_regions.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        t = m.Tally()
        self.assertTrue(t.check("X", "solar, MWh", m.num("not held"), None, 0.5))
        self.assertFalse(t.check("X", "solar, MWh", m.num("0"), None, 0.5))  # the page drawing zero where the file holds nothing

    def test_the_contract_says_the_form(self):
        c = src("docs", "state", "page_files_regions.md")
        self.assertIn("sources_not_printed", c)
        self.assertIn("is `null` in that region's mix file", c)

    def test_no_em_dash(self):
        for p in (("site", "components", "grid", "RegionViews.tsx"), ("site", "lib", "gridregions.ts"), ("site", "scripts", "check-grid-regions.mjs"), ("replication", "grid", "replicate_regions.py"), ("tests", "test_session8610.py")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()
