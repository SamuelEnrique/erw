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


# ---------------------------------------------------------------- data request 30: the archive keys revisions by vintage

sys.path.insert(0, os.path.join(REPO, "warehouse", "archive"))
import archive as A  # noqa: E402
import restore as R  # noqa: E402
import pandas as pd  # noqa: E402


def lines_of(rows):
    """Archive lines as archive.py wrote them before session 8013: _key_sha without the vintage."""
    df = pd.DataFrame(rows, columns=["_run_id", "_archived_at", "_op", "entity", "variable", "ts_utc", "value",
                                     "vintage"]).fillna("")
    ups = df["_op"] == "upsert"
    keys = pd.Series([""] * len(df))
    keys[ups.to_numpy()] = A.hexes(A.key_hashes(df[ups], "series"))
    df.insert(3, "_key_sha", keys.to_numpy())
    return df


class TheVintageKey(unittest.TestCase):
    def test_the_header_line_is_read_as_the_validator_reads_it(self):
        self.assertTrue(A.keeps_revisions(["Source: x", "Revisions: kept, one row per vintage (decision 77)"]))
        self.assertTrue(A.keeps_revisions("a\n# Revisions: kept, one row per vintage"))
        self.assertFalse(A.keeps_revisions(["Source: x"]))
        self.assertFalse(A.keeps_revisions(float("nan")))

    def test_the_key_carries_the_vintage_only_when_the_table_keeps_revisions(self):
        df = pd.DataFrame({"entity": ["a", "a"], "variable": ["v", "v"], "ts_utc": ["2030", "2030"],
                           "value": ["1", "2"], "vintage": ["2020", "2021"]})
        old, new = A.key_hashes(df, "series"), A.key_hashes(df, "series", True)
        self.assertEqual(old[0], old[1])
        self.assertNotEqual(new[0], new[1])

    def test_old_lines_restore_every_vintage(self):
        lines = lines_of([["r1", "t1", "upsert", "a", "v", "2030", "1", "2020"],
                          ["r1", "t1", "upsert", "a", "v", "2030", "2", "2021"],
                          ["r1", "t1", "upsert", "b", "v", "2030", "3", "2021"]])
        rows = R.rekey_revisions(lines)
        self.assertEqual(sorted(rows["value"]), ["1", "2", "3"])

    def test_a_later_upsert_of_the_same_vintage_replaces_it(self):
        lines = lines_of([["r1", "t1", "upsert", "a", "v", "2030", "1", "2020"],
                          ["r2", "t2", "upsert", "a", "v", "2030", "9", "2020"]])
        self.assertEqual(list(R.rekey_revisions(lines)["value"]), ["9"])

    def test_an_old_delete_removes_every_earlier_vintage_of_its_observation(self):
        lines = lines_of([["r1", "t1", "upsert", "a", "v", "2030", "1", "2020"],
                          ["r1", "t1", "upsert", "a", "v", "2030", "2", "2021"],
                          ["r1", "t1", "upsert", "b", "v", "2030", "3", "2021"]])
        gone = lines.iloc[0]["_key_sha"]
        dl = pd.DataFrame([{"_run_id": "r2", "_archived_at": "t2", "_op": "delete", "_key_sha": gone}])
        later = lines_of([["r3", "t3", "upsert", "a", "v", "2030", "5", "2022"]])
        rows = R.rekey_revisions(pd.concat([lines, dl, later], ignore_index=True).fillna(""))
        self.assertEqual(sorted(rows["value"]), ["3", "5"])

    def test_a_new_delete_removes_one_vintage(self):
        lines = lines_of([["r1", "t1", "upsert", "a", "v", "2030", "1", "2020"],
                          ["r1", "t1", "upsert", "a", "v", "2030", "2", "2021"]])
        one = A.hexes(A.key_hashes(lines.iloc[[0]], "series", True))[0]
        dl = pd.DataFrame([{"_run_id": "r2", "_archived_at": "t2", "_op": "delete", "_key_sha": one}])
        rows = R.rekey_revisions(pd.concat([lines, dl], ignore_index=True).fillna(""))
        self.assertEqual(list(rows["value"]), ["2"])


if __name__ == "__main__":
    unittest.main()
