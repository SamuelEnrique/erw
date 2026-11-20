"""Session 8623 (chain 504, 19 November 2026): a fifth layer of the resource map is replicated, the lease areas.

Energy Research Warehouse (ERW). replication/resources/replicate_leases.py reads BOEM's own archive and compares every
figure the map holds for the layer `offshore_wind_leases`. The publisher's file is not kept in the repository, so the
comparison is tried here on rows made up for the test (three outlines that are in no page), and the kept outputs of
the real run are held to what the run printed. Nothing here sets the environment or makes a request.
"""

import csv
import importlib.util
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HERE = os.path.join(ROOT, "replication", "resources")
EM = chr(0x2014)


def load():
    spec = importlib.util.spec_from_file_location("replicate_leases", os.path.join(HERE, "replicate_leases.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def square(w, s, e, n, steps=30):
    return [[(w + (e - w) * k / steps, n) for k in range(steps)] + [(e, n - (n - s) * k / steps) for k in range(steps)] + [(e - (e - w) * k / steps, s) for k in range(steps)] + [(w, s + (n - s) * k / steps) for k in range(steps)] + [(w, n)]]


def made_up(m):
    shapes = [square(-74.0, 39.0, -73.8, 39.1), square(-73.0, 40.0, -72.9, 40.05), square(-72.0, 41.0, -71.99, 41.01)]
    acres = [m.area_sq_mi(s) * m.ACRES_PER_SQ_MI for s in shapes]
    outlines = [
        {"LEASE_NUMB": "ZZ 0001", "LEASE_NU_1": "ZZ 0001 - First Made Up LLC", "LEASE_TYPE": "Commercial", "COMPANY": "First Made Up LLC", "ACRES": round(acres[0]), "STATE": "ZZ", "PROJECT_NA": ""},
        {"LEASE_NUMB": "ZZ 0001", "LEASE_NU_1": "ZZ 0001 - First Made Up LLC", "LEASE_TYPE": "Easement", "COMPANY": "First Made Up LLC", "ACRES": round(acres[1] / 2), "STATE": "ZZ", "PROJECT_NA": "A project"},
        {"LEASE_NUMB": "ZZ 0002", "LEASE_NU_1": "ZZ 0002 - A Cable Company", "LEASE_TYPE": "Commercial", "COMPANY": "A Cable Company", "ACRES": 0.0, "STATE": "ZZ", "PROJECT_NA": ""},
    ]
    blocks = [{"LEASE_NUMB": "ZZ 0001", "LEASE_TYPE": "Commercial"}, {"LEASE_NUMB": "ZZ 0001", "LEASE_TYPE": "Easement"}, {"LEASE_NUMB": "ZZ 0002", "LEASE_TYPE": "Right-of-Way Grant"}]
    feats = [{"properties": {"name": r["LEASE_NU_1"], "kind": "lease area (%s)" % r["LEASE_TYPE"], "value": r["ACRES"] or None, "value_unit": "acres", "LEASE_NUMB": r["LEASE_NUMB"], "LEASE_NU_1": r["LEASE_NU_1"],
                             "LEASE_TYPE": r["LEASE_TYPE"], "COMPANY": r["COMPANY"], "ACRES": r["ACRES"], "STATE": r["STATE"], "PROJECT_NA": r["PROJECT_NA"] or None}} for r in outlines]
    held = [r["ACRES"] for r in outlines if r["ACRES"]]
    entry = {"stats": {"n": len(held), "min": min(held), "mean": sum(held) / len(held), "max": max(held)}, "features": 3, "unit": "acres"}
    return outlines, shapes, blocks, {"features": feats}, entry


class TheComparison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_a_layer_that_is_the_file_is_met_in_every_figure(self):
        outlines, shapes, blocks, layer, entry = made_up(self.m)
        rows, differ, check = self.m.compare(outlines, shapes, blocks, layer, entry)
        self.assertEqual(differ, 0, [r for r in rows if r["same"] == "NO"])
        self.assertEqual(len(rows), 1 + 3 * (4 + 7) + 6)

    def test_an_area_of_zero_in_the_source_is_none_on_the_map_and_a_zero_shown_is_caught(self):
        outlines, shapes, blocks, layer, entry = made_up(self.m)
        self.assertIsNone(layer["features"][2]["properties"]["value"])
        layer["features"][2]["properties"]["value"] = 0
        rows, differ, _ = self.m.compare(outlines, shapes, blocks, layer, entry)
        self.assertEqual([r["figure"].split(":")[0] for r in rows if r["same"] == "NO"], ["ZZ 0002"])

    def test_two_outlines_of_one_lease_are_each_met_in_the_tables_order(self):
        outlines, shapes, blocks, layer, entry = made_up(self.m)
        layer["features"][0], layer["features"][1] = layer["features"][1], layer["features"][0]      # the two outlines of lease ZZ 0001, swapped
        _, differ, _ = self.m.compare(outlines, shapes, blocks, layer, entry)
        self.assertGreater(differ, 0)                                                                # the easement is not the lease

    def test_an_altered_kind_and_an_altered_field_are_each_caught(self):
        outlines, shapes, blocks, layer, entry = made_up(self.m)
        layer["features"][0]["properties"]["kind"] = "lease area (Research)"
        layer["features"][1]["properties"]["COMPANY"] = "Another Company"
        rows, differ, _ = self.m.compare(outlines, shapes, blocks, layer, entry)
        self.assertEqual(differ, 2)

    def test_the_cross_checks(self):
        outlines, shapes, blocks, layer, entry = made_up(self.m)
        check = self.m.compare(outlines, shapes, blocks, layer, entry)[2]
        by = {(c["lease"], c["type_in_the_outlines_table"]): c for c in check}
        self.assertLess(abs(by[("ZZ 0001", "Commercial")]["difference_pct"]), 0.1)        # its ACRES are its outline's area
        self.assertGreater(by[("ZZ 0001", "Easement")]["difference_pct"], 90)             # its ACRES are half its outline's area
        self.assertEqual(by[("ZZ 0001", "Easement")]["types_agree"], "yes")               # a lease with an easement has both types in the blocks table
        self.assertEqual(by[("ZZ 0002", "Commercial")]["types_agree"], "NO")              # a right-of-way grant called commercial
        self.assertEqual(by[("ZZ 0002", "Commercial")]["difference_pct"], "")             # no area, nothing to compare


class TheKeptRun(unittest.TestCase):
    """What the run on BOEM's own archive wrote on 19 November 2026."""

    def rows(self, name):
        with open(os.path.join(HERE, name), encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def test_every_figure_is_the_publishers(self):
        rows = self.rows("offshore_wind_leases_figures.csv")
        self.assertEqual(len(rows), 1129)
        self.assertEqual({r["same"] for r in rows}, {"yes"})

    def test_what_the_cross_checks_found(self):
        check = self.rows("crosscheck_leases.csv")
        self.assertEqual(len(check), 51)
        held = [c for c in check if c["difference_pct"] != ""]
        self.assertEqual(len(held), 46)
        self.assertEqual([c["lease"] for c in held if abs(float(c["difference_pct"])) > 1], ["OCS-A 0517"])
        self.assertEqual(sorted(c["lease"] for c in check if c["types_agree"] == "NO"), ["OCS-A 0497", "OCS-A 0506"])

    def test_the_file_is_named_by_its_sha256_and_is_the_layers(self):
        m = load()
        with open(os.path.join(ROOT, "site", "data", "resources", "manifest.json"), encoding="utf-8") as f:
            entry = [l for l in json.load(f)["layers"] if l["id"] == "offshore_wind_leases"][0]
        self.assertEqual(m.SHA256, entry["source_sha256"])
        self.assertEqual(entry["source_bytes"], 1031812)

    def test_no_em_dash(self):
        for p in ("replicate_leases.py", "offshore_wind_leases_figures.csv", "crosscheck_leases.csv"):
            with open(os.path.join(HERE, p), encoding="utf-8") as f:
                self.assertNotIn(EM, f.read(), p)
        with open(os.path.abspath(__file__), encoding="utf-8") as f:
            self.assertNotIn(EM, f.read())


if __name__ == "__main__":
    unittest.main()
