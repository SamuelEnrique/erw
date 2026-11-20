"""Session 8011, chain 501 (data request 553): the hover fields of the two point layers that name none, in each
publisher's own words, in a new file beside manifest.json (which is not changed)."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.join(ROOT, "site", "data", "resources")
ADDED = os.path.join(RES, "hover_fields_added.json")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class TheHoverFieldsAdded(unittest.TestCase):
    def setUp(self):
        self.d = load(ADDED)
        self.manifest = {l["id"]: l for l in load(os.path.join(RES, "manifest.json"))["layers"]}

    def test_only_layers_the_manifest_gives_no_list(self):
        for lid in self.d["layers"]:
            self.assertIn(lid, self.manifest)
            self.assertFalse(self.manifest[lid].get("hover_fields"))

    def test_every_column_is_in_the_layer_file(self):
        for lid, v in self.d["layers"].items():
            cols = load(os.path.join(RES, "layers", lid + ".json"))["columns"]
            for col, words in v["hover_fields"]:
                self.assertIn(col, cols)
                self.assertTrue(words.strip())

    def test_the_publishers_words(self):
        w = dict(self.d["layers"]["wind_capacity_factor"]["hover_fields"])
        self.assertEqual(w["resource"], "Annual average wind speed at the modeled turbine hub-height, meters/second")
        self.assertEqual(self.d["layers"]["wind_capacity_factor"]["name_column"]["source_column"], "sc_point_gid")
        g = dict(self.d["layers"]["geothermal_hydrothermal_sites"]["hover_fields"])
        self.assertEqual(g["Temp_C_Li"], "Most likely temperature (°C) of reservoir")

    def test_no_em_dash(self):
        with open(ADDED, encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
