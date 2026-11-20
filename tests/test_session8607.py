"""Session 8607 (chain 504, 19 November 2026): the resource map reads the list of layers the data machine adds
beside the first.

Energy Research Warehouse (ERW). Data request 542 asked for the coal fields, uranium and critical minerals in the
resource map's form. The data machine answered with a second list, site/data/resources/manifest_added.json, in the
first's form (chain 501's rule: an existing page file is not changed), holding the coal fields and naming the other
two as missing with why. What is held here:
- the two lists are read as one: the first's layers, then each added layer the first does not hold; the first wins a
  name; the missing lists joined without a repeat and without a layer that is now held;
- an added layer's hover fields may be written as the field alone; its words are then the field's own name;
- with no second list the page is as it was; a second list that cannot be read is said and the first stands;
- a held coal layer takes the place of the greyed "Coal fields", and a missing entry's own reason is the one shown.
The lists below are made up for the tests and are in no page. Nothing here sets the environment or makes a request.
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


FIRST = ("{ built_at_utc: '2026-10-08T08:52:45Z', layers: [{ id: 'wind_speed_100m', group: 'wind', title: 'Wind speed at 100 m', kind: 'grid' }, { id: 'oil_gas_plays', group: 'oil and gas', title: 'Plays', kind: 'shapes', file: 'plays.json' }],"
         " missing: [{ id: 'wind_gross_capacity_factor', group: 'wind', title: 'Gross capacity factor', reason: 'Not fetched: a key is needed.' }] }")
ADDED = ("{ built_at_utc: '2026-11-19T13:50:58Z', layers: [{ id: 'coal_fields', group: 'coal', title: 'Coal fields', kind: 'shapes', file: 'coal_fields.json', measure: 'Where coal lies in the ground', hover_fields: ['PROVINCE', 'RANK'] },"
         " { id: 'oil_gas_plays', group: 'oil and gas', title: 'Another list tries to rename the plays', kind: 'shapes', file: 'other.json' }],"
         " missing: [{ id: 'uranium_deposits', group: 'uranium', title: 'Uranium deposits', reason: 'Not fetched: the host disallows every path.' }, { id: 'wind_gross_capacity_factor', group: 'wind', title: 'Said twice' },"
         " { id: 'coal_fields', group: 'coal', title: 'Named as missing and held' }] }")


@unittest.skipUnless(NODE, "node is not installed")
class TheTwoListsAsOne(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = node("import { mergeManifests, toggleGroups, measureLine } from './lib/resources.ts';"
                     f"const first = {FIRST}, added = {ADDED};"
                     "const m = mergeManifests(first, added);"
                     "const groups = toggleGroups(m);"
                     "const of = (id) => (groups.find((g) => g.id === id)?.items ?? []).map((it) => (it.held ? ['held', it.layer.id, measureLine(it.layer)] : ['not held', it.label, it.reason]));"
                     "console.log(JSON.stringify({ ids: m.layers.map((l) => l.id), plays: m.layers.find((l) => l.id === 'oil_gas_plays').title, missing: m.missing.map((x) => [x.id, x.title]), built: [m.built_at_utc, m.added_built_at_utc],"
                     " alone: mergeManifests(first, null) === first, undef: mergeManifests(first, undefined) === first, odd: mergeManifests(first, { layers: 'no', missing: [null] }).layers.length,"
                     " coal: of('coal'), uranium: of('uranium'), minerals: of('critical_minerals'), before: toggleGroups(first).find((g) => g.id === 'coal').items.map((it) => [it.held, it.label]) }));")

    def test_the_firsts_layers_then_the_added_ones_it_does_not_hold(self):
        self.assertEqual(self.d["ids"], ["wind_speed_100m", "oil_gas_plays", "coal_fields"])

    def test_the_first_list_wins_a_name(self):
        self.assertEqual(self.d["plays"], "Plays")

    def test_the_missing_lists_joined_without_a_repeat_or_a_layer_now_held(self):
        self.assertEqual(self.d["missing"], [["wind_gross_capacity_factor", "Gross capacity factor"], ["uranium_deposits", "Uranium deposits"]])

    def test_each_list_keeps_its_own_day(self):
        self.assertEqual(self.d["built"], ["2026-10-08T08:52:45Z", "2026-11-19T13:50:58Z"])

    def test_with_no_second_list_the_first_is_handed_back_as_it_is(self):
        self.assertTrue(self.d["alone"])
        self.assertTrue(self.d["undef"])
        self.assertEqual(self.d["odd"], 2)                                  # a second list that is not a list of layers adds nothing

    def test_the_held_coal_layer_takes_the_place_of_the_greyed_switch(self):
        self.assertEqual(self.d["before"], [[False, "Coal fields"]])        # as session 8603 left it: named, greyed
        self.assertEqual(self.d["coal"], [["held", "coal_fields", "Where coal lies in the ground."]])

    def test_a_missing_entrys_own_reason_is_the_one_shown(self):
        self.assertEqual(self.d["uranium"], [["not held", "Uranium deposits", "Not fetched: the host disallows every path."]])
        self.assertEqual(self.d["minerals"][0][0:2], ["not held", "Critical mineral deposits"])
        self.assertIn("No layer of critical mineral deposits is among the resource files", self.d["minerals"][0][2])   # nothing said of it: session 8603's words stand


@unittest.skipUnless(NODE, "node is not installed")
class TheHoversFields(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = node("import { hoverPairs } from './lib/resources.ts';"
                     "console.log(JSON.stringify({ pairs: hoverPairs([['gen_mwh_yr', 'Annual average generation, MWh']]), alone: hoverPairs(['PROVINCE', 'NAME', 'AGE', 'RANK']), mixed: hoverPairs([['a', 'A word'], 'gen_mwh_yr', 7, ['x'], '  ', null]),"
                     " none: hoverPairs([]) ?? null, absent: hoverPairs(undefined) ?? null, wrong: hoverPairs('PROVINCE') ?? null }));")

    def test_a_pair_is_kept_as_it_is(self):
        self.assertEqual(self.d["pairs"], [["gen_mwh_yr", "Annual average generation, MWh"]])

    def test_a_field_alone_reads_as_its_own_name(self):
        self.assertEqual(self.d["alone"], [["PROVINCE", "Province"], ["NAME", "Name"], ["AGE", "Age"], ["RANK", "Rank"]])

    def test_anything_else_is_left_out(self):
        self.assertEqual(self.d["mixed"], [["a", "A word"], ["gen_mwh_yr", "Gen mwh yr"]])
        self.assertIsNone(self.d["none"])
        self.assertIsNone(self.d["absent"])
        self.assertIsNone(self.d["wrong"])


class TheServersReader(unittest.TestCase):
    def setUp(self):
        self.s = src("site", "lib", "resourcesdata.ts")

    def test_the_first_list_is_read_as_before_and_the_second_only_when_it_is_there(self):
        self.assertIn('fs.readFileSync(path.join(process.cwd(), "data", "resources", "manifest.json"), "utf8")', self.s)
        self.assertIn('const addedPath = path.join(process.cwd(), "data", "resources", "manifest_added.json");', self.s)
        self.assertIn("if (fs.existsSync(addedPath)) {", self.s)
        self.assertIn("raw = mergeManifests(raw, JSON.parse(fs.readFileSync(addedPath, \"utf8\")) as Manifest);", self.s)

    def test_a_second_list_that_cannot_be_read_is_said_and_the_first_stands(self):
        self.assertIn("could not be read on the server", self.s)
        self.assertIn("the first list's layers are drawn.", self.s)
        self.assertIn("return { manifest: { built_at_utc: raw.built_at_utc, added_built_at_utc: raw.added_built_at_utc, layers, missing }, reason };", self.s)

    def test_an_added_layers_file_is_served_and_checked_like_any_other(self):
        # the loop that drops a layer whose file is not on the server runs on the joined list, and the files' addresses come from the same reader
        self.assertLess(self.s.index("raw = mergeManifests("), self.s.index("for (const l of raw.layers ?? []) {"))
        self.assertIn("return [...new Set(readManifest().manifest.layers.flatMap(filesOf).map(stemOf))];", self.s)

    def test_the_page_says_the_second_lists_day_and_takes_the_fields_in_both_forms(self):
        v = src("site", "app", "resources", "view.tsx")
        self.assertIn("hover_fields: hoverPairs(l.hover_fields),", v)
        self.assertIn("data-added-list={manifest.added_built_at_utc}", v)
        self.assertIn("Layers added beside it, in a list of their own, built", v)


class TheRest(unittest.TestCase):
    def test_the_first_list_is_not_changed_and_no_added_file_is_committed_by_this_session(self):
        first = json.loads(src("site", "data", "resources", "manifest.json"))
        self.assertEqual(len(first["layers"]), 14)
        self.assertEqual(first["built_at_utc"], "2026-10-08T08:52:45Z")
        tracked = subprocess.run(["git", "ls-files", "site/data/resources/manifest_added.json"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if tracked:                                                         # once the data machine's branch has landed
            added = json.loads(src("site", "data", "resources", "manifest_added.json"))
            self.assertIn("layers", added)

    def test_the_release_gate_is_not_touched(self):
        self.assertNotIn("session 8607", src("site", "lib", "release.ts"))

    def test_no_em_dash(self):
        for p in (("site", "lib", "resources.ts"), ("site", "lib", "resourcesdata.ts"), ("site", "app", "resources", "view.tsx"), ("tests", "test_session8607.py")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()
