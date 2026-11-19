"""Session 8013 (chain 505): notes on three layers of the resource map, data requests 554 to 556, in a new file.

The layer files and manifest.json are not changed (chain 505's rule: add, never change); the answers are in
site/data/resources/layer_notes_added.json, built by warehouse/derived/resource_layer_notes.py.
"""

import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "warehouse", "derived"))
import resource_layer_notes as rln  # noqa: E402

FILE = os.path.join(REPO, "site", "data", "resources", "layer_notes_added.json")


def load():
    with open(FILE, encoding="utf-8") as f:
        return json.load(f)


class TheRule(unittest.TestCase):
    def test_state_codes_keep_capitals_and_small_words_are_small(self):
        self.assertEqual(rln.name_as_written("TX-LA-MS SALT"), "TX-LA-MS Salt")
        self.assertEqual(rln.name_as_written("VALLEY AND RIDGE"), "Valley and Ridge")
        self.assertEqual(rln.name_as_written("UINTA-PICEANCE"), "Uinta-Piceance")
        self.assertEqual(rln.name_as_written("FORT WORTH"), "Fort Worth")
        self.assertEqual(rln.name_as_written("THE BASIN"), "The Basin")

    def test_decimals(self):
        self.assertEqual(rln.decimals(5.65), 2)
        self.assertEqual(rln.decimals(102.0), 0)
        self.assertEqual(rln.decimals(3), 0)
        self.assertIsNone(rln.decimals("416"))


class TheFile(unittest.TestCase):
    def test_three_layers_each_with_its_request_and_source(self):
        d = load()
        self.assertEqual(set(d["layers"]), {"oil_gas_basins", "wind_capacity_factor", "offshore_wind_leases"})
        self.assertEqual([d["layers"][k]["request"] for k in ("oil_gas_basins", "wind_capacity_factor",
                                                              "offshore_wind_leases")], [554, 555, 556])
        for k, v in d["layers"].items():
            self.assertTrue(v["source"].get("source_sha256"), k)

    def test_basins_listed_are_exactly_where_the_rule_differs_from_the_layer(self):
        with open(os.path.join(REPO, "site", "data", "resources", "layers", "oil_gas_basins.json"),
                  encoding="utf-8") as f:
            layer = json.load(f)
        want = sorted(p["NAME"] for p in (x["properties"] for x in layer["features"])
                      if rln.name_as_written(p["NAME"]) != p["name"])
        got = [r["NAME"] for r in load()["layers"]["oil_gas_basins"]["names_that_differ"]]
        self.assertEqual(got, want)

    def test_wind_sentence_names_every_rounding_measured(self):
        w = load()["layers"]["wind_capacity_factor"]
        dk = w["decimals_kept"]
        for col, words in (("lon", "coordinates"), ("value", "the capacity factor"), ("resource", "the wind speed"),
                           ("area_developable_sq_km", "the developable area")):
            self.assertIn(f"{words} to {dk[col]}", w["reduction_all_roundings"])

    def test_leases_listed_keep_both_tables(self):
        rows = load()["layers"]["offshore_wind_leases"]["outlines_whose_type_the_blocks_do_not_give"]
        for r in rows:
            self.assertNotIn(r["outline_type"], r["block_types"])
            self.assertEqual(r["kind_in_layer"], f"lease area ({r['outline_type']})")

    def test_the_layers_and_the_manifest_are_not_changed_by_this_file(self):
        # the request's figures are where the replication found them: the two names as str.title wrote them
        with open(os.path.join(REPO, "site", "data", "resources", "layers", "oil_gas_basins.json"),
                  encoding="utf-8") as f:
            names = {x["properties"]["name"] for x in json.load(f)["features"]}
        self.assertIn("Tx-La-Ms Salt", names)
        with open(os.path.join(REPO, "site", "data", "resources", "manifest.json"), encoding="utf-8") as f:
            m = json.load(f)
        red = [l for l in m["layers"] if l["id"] == "wind_capacity_factor"][0]["reduction"]
        self.assertNotIn("wind speed", red)


if __name__ == "__main__":
    unittest.main()
