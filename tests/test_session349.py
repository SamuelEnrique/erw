"""Session 349: the project map, phase two.

Energy Research Warehouse (ERW). What is held: a queue position whose county words name a place or a town of its
state is placed at that place's point, a name two places share is not used, and the county comes first; the card's
generator links hold to the generator tool's own snapshot; the map has a Queues tab drawing iso_queue_statistics with
checked figures; the data machine's daily run rebuilds the map's copy. The gazetteer rows are fixtures, not data.

    python -m unittest tests.test_session349 -v
"""

import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import energy_projects as ep  # noqa: E402


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class ThePlaces(unittest.TestCase):
    def setUp(self):
        self.county = {("CA", "kern"): (35.3, -118.7, "Kern County", "2025_Gaz_counties_national.txt")}
        self.places = {("CA", "rosamond"): (34.86, -118.16, "Rosamond CDP", "2025_Gaz_place_national.txt"),
                       ("ME", "lewiston"): (44.1, -70.2, "Lewiston city", "2025_Gaz_place_national.txt")}
        self.subs = {("VT", "colchester"): (44.55, -73.2, "Colchester town", "2025_Gaz_cousubs_national.txt")}

    def test_the_kind_of_place_is_not_part_of_its_name(self):
        self.assertEqual(ep.place_key("Austin city"), "austin")
        self.assertEqual(ep.place_key("Hartford town"), "hartford")
        self.assertEqual(ep.place_key("Milford CDP"), "milford")

    def test_a_county_first_then_a_place_then_a_town(self):
        self.assertEqual(ep.geocode("CA", "Kern", self.county, self.places, self.subs)[2], "county")
        lat, lon, prec, note = ep.geocode("CA", "ROSAMOND", self.county, self.places, self.subs)
        self.assertEqual((lat, prec), (34.86, "place"))
        self.assertIn("2025_Gaz_place_national.txt", note)
        lat, lon, prec, note = ep.geocode("VT", "Colchester", {}, self.places, self.subs)
        self.assertEqual(prec, "place")
        self.assertIn("county subdivision Colchester town (2025_Gaz_cousubs_national.txt)", note)

    def test_a_place_of_another_state_or_no_state_is_not_used(self):
        self.assertEqual(ep.geocode("NH", "Lewiston", {}, self.places, self.subs)[2], "none")
        self.assertEqual(ep.geocode("", "Lewiston", {}, self.places, self.subs)[2], "none")

    def test_without_the_place_files_it_is_as_before(self):
        self.assertEqual(ep.geocode("CA", "ROSAMOND", self.county)[2], "none")


class TheCard(unittest.TestCase):
    def test_the_generator_table_holds_to_the_tools_snapshot(self):
        lib = read("site", "lib", "projectmap.ts")
        block = lib[lib.index("export const GENERATOR_HELD"):lib.index("};", lib.index("export const GENERATOR_HELD"))]
        held = {g: set(re.findall(r'"([a-z]+)"', a)) for g, a in re.findall(r'(\w+): \[([^\]]*)\]', block)}
        snap = json.loads(read("site", "data", "merchant_snapshot.json"))
        want = {}
        for g, v in snap["isos"].items():
            if g == "miso":   # the generator tool leaves MISO blank while its terms are reviewed
                continue
            want[g] = {re.sub(r"_\d+h$", "", a) for m in v["months"].values() for a, x in m.items() if isinstance(x, dict)}
        self.assertEqual(held, want)

    def test_the_card_links_or_says_not_modeled(self):
        lib = read("site", "lib", "projectmap.ts")
        self.assertIn("/cost-of-power/seller?iso=${grid}&asset=${asset}", lib)
        self.assertIn("not modeled", lib)
        self.assertIn("data-generator-link", read("site", "app", "map", "ProjectMap.tsx"))


class TheQueuesTab(unittest.TestCase):
    def test_the_tab_and_its_checks(self):
        self.assertIn('["queues", "Queues"]', read("site", "lib", "tabs.ts"))
        view = read("site", "app", "map", "QueuesView.tsx")
        self.assertIn("series|${QUEUE_TABLE}|${r.entity}|${r.variable}|", view)
        self.assertIn("SeriesChart", read("site", "app", "map", "QueueCharts.tsx"))
        cv = read("site", "scripts", "check-values.mjs")
        self.assertIn('"/map?tab=queues"', cv)

    def test_the_unplaced_count_is_checked(self):
        self.assertIn('check="projects|count|queue|none"', read("site", "app", "map", "page.tsx"))


class TheDailyRun(unittest.TestCase):
    def test_the_data_machine_rebuilds_the_maps_copy(self):
        sh = read("warehouse", "run_data_machine.sh")
        self.assertIn('soft_step dm_project_map "$PYTHON" warehouse/scheduled.py project_map', sh)
        self.assertRegex(sh, r"site/data/map\.json site/data/map_v2\.json\)")


if __name__ == "__main__":
    unittest.main()
