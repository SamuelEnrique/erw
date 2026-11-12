"""Session 1880: the Attention and Friction indices' faults of 12 November 2026 (docs/reviews/attention-faults-2026-11-11.md),
fixed in site/lib/attention.ts, site/app/attention/AttentionView.tsx and site/components/tool/SeriesChart.tsx.

Energy Research Warehouse (ERW). No request is made, no model is called and nothing is written. The environment is
read, never set.

    PureFunctions  site/scripts/test-attention-view.mjs (Node runs site/lib/attention.ts with the site's alias loader on
                   data/attention.json and the week files): the list under the United States (row 1), no week after the
                   build's (3), the week that holds the build partial (4), the week kept among the cell's (5), the line
                   of a missing cell (6), every new key read back with its source (8), the map's table (9), the places'
                   lists (10), the places summed under All energy (11).
    TheView        the components, read from their source (this session does not build): each fixed row drawn as the
                   functions give it, every figure keyed with a source, every existing data-check key kept.
    TheCheck       scripts/check-values.mjs reads the new keys back from the file the page reads.

    python -m pytest tests/test_session1880.py
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
LOADER = ["--import", "./scripts/alias-register.mjs"]
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)
MINE = (
    ("site", "lib", "attention.ts"), ("site", "app", "attention", "AttentionView.tsx"), ("site", "components", "tool", "SeriesChart.tsx"),
    ("site", "scripts", "test-attention-view.mjs"), ("site", "scripts", "check-values.mjs"), ("tests", "test_session1880.py"),
)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class PureFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, *LOADER, "scripts/test-attention-view.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        cls.code, cls.out, cls.err = r.returncode, r.stdout, r.stderr

    def test_the_node_tests_pass(self):
        self.assertEqual(self.code, 0, self.out[-3000:] + self.err[-1000:])
        self.assertNotIn("FAIL", self.out)
        m = re.search(r"(\d+) of (\d+) passed", self.out)
        self.assertTrue(m and m.group(1) == m.group(2), self.out[-500:])

    def test_each_fixed_row_has_its_node_tests(self):
        for row in (1, 3, 4, 5, 6, 8, 9, 10, 11):
            self.assertRegex(self.out, rf"(?m)^ok   row {row}[ :(]", f"row {row} has a passing node test")


class TheView(unittest.TestCase):
    view = src("site", "app", "attention", "AttentionView.tsx")
    chart = src("site", "components", "tool", "SeriesChart.tsx")
    lib = src("site", "lib", "attention.ts")

    def test_row_1_the_list_is_filtered_by_the_lib_and_counted_against_the_cell(self):
        self.assertNotIn('s.state !== "" || true', self.view + self.lib)
        self.assertIn("inCell(s, sectorKey, geo, onlyOpposition, place)", self.view)
        self.assertIn("data-attention-list-count={list.length}", self.view)
        self.assertIn(": the ones that name a state.", self.view)
        self.assertNotIn("Under the United States the list shows", self.view)

    def test_rows_3_and_5_the_picker_offers_the_cells_weeks_to_the_build(self):
        self.assertIn("cellWeeks(f, sector, gi)", self.view)
        self.assertIn("setWeek(chooseWeek(weeksWithStories, week))", self.view)
        self.assertIn("weekOptions(weeksWithStories, week)", self.view)
        self.assertIn('none ? " (no story)" : ""', self.view)
        self.assertIn("openingWeek(f)", self.view)

    def test_row_4_partial_is_the_lib_rule_and_the_line_chart_hatches_it(self):
        self.assertNotIn("i === f.weeks.length - 1", self.view)
        self.assertIn("isPartial(f, i)", self.view)
        self.assertIn("{weekWords(f, i)}", self.view)
        self.assertIn("data-partial-column={i}", self.chart)

    def test_row_6_a_missing_cell_is_one_line(self):
        self.assertIn('data-attention-none="1">{noCellLine(sectorKey, geo, wk, STATES)}', self.view)
        self.assertNotIn(': "none"}', self.view)

    def test_row_8_every_figure_has_a_key_and_a_source(self):
        nums = re.findall(r"<Num\b[^>]*>", self.view)
        self.assertGreaterEqual(len(nums), 4)
        for n in nums:
            self.assertIn("check=", n)
            self.assertIn("source=", n)
        for fn in ("risingKey(", "placeKey(", "fileKey(", "seriesKey("):
            self.assertIn(fn, self.view)
        self.assertNotIn("pct(r.before)", self.view)
        self.assertNotIn("whole(p.stories)", self.view)

    def test_row_9_the_map_has_a_chart_and_table_toggle(self):
        self.assertIn('data-attention-map-toggle="1"', self.view)
        self.assertIn("data-attention-map-table={mapTableRows.length}", self.view)
        self.assertIn('className={mapTable ? "hidden" : ""}', self.view)

    def test_row_10_the_rising_rows_open_their_stories(self):
        for k in ("sector:${r.key}", "state:${r.key}", "place:${p.place}|${p.state}"):
            self.assertIn(f"data-attention-open={{`{k}`}}", self.view)
        self.assertIn('data-attention-place-clear="1"', self.view)

    def test_row_11_the_places_come_from_the_lib(self):
        self.assertIn("placesOf(f, week, sector)", self.view)

    def test_row_12_the_card_gives_the_counts(self):
        self.assertIn("saysOnCard = false }: Props)", self.chart, "the card's says is off unless a page asks")
        self.assertIn('{saysOnCard && says ? <div className="mt-0.5 max-w-[14rem] whitespace-normal text-ink" data-chart-card-says="1">{says(hover)}</div> : null}', self.chart)
        self.assertEqual(self.view.count("saysOnCard"), 2)
        self.assertIn("<title>{says ? says(i) :", self.chart, "the title stays")

    def test_row_13_the_inputs_stand_left_of_the_results_at_lg(self):
        self.assertIn('className="lg:grid lg:grid-cols-[13rem_minmax(0,1fr)] lg:gap-8" data-attention-layout="1"', self.view)
        self.assertIn("lg:sticky lg:top-2", self.view)
        self.assertIn('<div className="min-w-0" data-attention-results="1">', self.view)

    def test_every_existing_key_is_kept(self):
        # the session 3405 keys: series|<table>|attention:<sector>:<geo>|<variable>|<week>, built by seriesKey
        self.assertIn("seriesKey = (table: string, entity: string, variable: string, week: string) => `series|${table}|${entity}|${variable}|${week}`", self.lib)
        for v in ('"stories"', '"attention_index"', '"friction_index"', '"tone_mean"'):
            self.assertIn(v, self.view)
        self.assertIn("S(ATT, `attention:${r.key}:all`, \"attention_index\"", self.view)
        self.assertIn("S(ATT, `attention:energy:US-${r.key}`, \"attention_index\"", self.view)
        self.assertIn('export type { AttentionFile } from "@/lib/attention";', self.view, "page.tsx imports the type from the view")

    def test_no_em_or_en_dash(self):
        for p in MINE:
            t = src(*p)
            self.assertNotIn(EM_DASH, t, p)
            self.assertNotIn(EN_DASH, t, p)


class TheCheck(unittest.TestCase):
    def test_check_values_reads_the_new_keys_from_the_file(self):
        t = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "attention_rising" || p[0] === "attention_place" || p[0] === "attention_file") {', t)
        self.assertIn("return A.attentionStat(file, check);", t)


if __name__ == "__main__":
    unittest.main()
