"""Session 8621 (chain 504, 19 November 2026): a third layer of the resource map is replicated, the non-powered dams.

Energy Research Warehouse (ERW). replication/resources/replicate_dams.py reads Oak Ridge National Laboratory's own
table and compares every figure the map holds for the layer `hydropower_npd`. The publisher's file is not kept in the
repository, so the comparison is tried here on rows made up for the test (three dams that are in no page), and the
kept outputs of the real run are held to what the run printed. Nothing here sets the environment or makes a request.
"""

import csv
import importlib.util
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HERE = os.path.join(ROOT, "replication", "resources")
EM = chr(0x2014)
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
COLUMNS = ["lon", "lat", "name", "value", "gen_mwh_yr", "cf_yr", "state_abbr", "waterway", "nididfull", "county", "head_ft_yr", "q30_cfs", "inputdata"]


def load():
    spec = importlib.util.spec_from_file_location("replicate_dams", os.path.join(HERE, "replicate_dams.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def source():
    def row(i, lon, lat, name, mw, year, months):
        r = {"nididfull": "ZZ%05d" % i, "long": lon, "lat": lat, "dam_name": name, "cap_mw": mw, "gen_mwh_yr": year, "cf_yr": "0.5", "state_abbr": "ZZ", "waterway": "Made Up Creek", "county": "", "head_ft_yr": "12.5", "q30_cfs": "300", "inputdata": "Gage Flow"}
        r.update({"gen_mwh_" + m: v for m, v in zip(MONTHS, months)})
        return r
    return [row(1, "-90.12345678", "40.00004999", "FIRST DAM", "2.5", "1200", ["100"] * 12), row(2, "-91.5", "41.25", "SECOND DAM", "0.001", "6", ["1"] * 12), row(3, "-92.0", "42.0", "THIRD DAM", "10", "", ["5"] * 12)]


def layer_of(rows):
    out = []
    for s in rows:
        out.append([round(float(s["long"]), 4), round(float(s["lat"]), 4), s["dam_name"], float(s["cap_mw"]), float(s["gen_mwh_yr"]) if s["gen_mwh_yr"] else None, float(s["cf_yr"]), s["state_abbr"], s["waterway"], s["nididfull"],
                    s["county"] or None, float(s["head_ft_yr"]), float(s["q30_cfs"]), s["inputdata"]])
    caps = [float(s["cap_mw"]) for s in rows]
    return {"columns": COLUMNS, "rows": out}, {"stats": {"n": len(caps), "min": min(caps), "mean": sum(caps) / len(caps), "max": max(caps)}, "unit": "MW"}


class TheComparison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_a_layer_that_is_the_file_is_met_in_every_figure(self):
        rows = source()
        layer, entry = layer_of(rows)
        n, differ, check = self.m.compare(rows, layer, entry)
        self.assertEqual(differ, [])
        self.assertEqual(n, 1 + 3 * 13 + 5)

    def test_an_altered_capacity_a_moved_place_and_a_changed_name_are_each_caught(self):
        rows = source()
        layer, entry = layer_of(rows)
        layer["rows"][0][3] += 0.1          # the capacity
        layer["rows"][1][0] += 0.0002       # the longitude, two units of the fourth decimal
        layer["rows"][2][2] = "Third Dam"   # the name, in other letters
        n, differ, _ = self.m.compare(rows, layer, entry)
        self.assertEqual(sorted(d["figure"].split(" (")[0] for d in differ), ["ZZ00001: value", "ZZ00002: lon", "ZZ00003: name"])

    def test_a_place_is_the_sources_to_four_decimals_and_no_closer(self):
        rows = source()
        layer, entry = layer_of(rows)
        self.assertEqual(layer["rows"][0][0], -90.1235)
        self.assertEqual(self.m.compare(rows, layer, entry)[1], [])

    def test_a_blank_cell_is_none_and_never_zero(self):
        rows = source()
        layer, entry = layer_of(rows)
        layer["rows"][2][4] = 0.0           # the blank annual generation written as zero
        _, differ, _ = self.m.compare(rows, layer, entry)
        self.assertEqual([d["figure"] for d in differ], ["ZZ00003: gen_mwh_yr"])

    def test_a_dam_missing_from_the_layer_and_one_the_file_does_not_hold_are_caught(self):
        rows = source()
        layer, entry = layer_of(rows)
        layer["rows"][1][8] = "QQ99999"
        _, differ, _ = self.m.compare(rows, layer, entry)
        said = [d["figure"] for d in differ]
        self.assertIn("QQ99999: a dam of the publisher's file", said)
        self.assertIn("ZZ00002: a dam of the map's layer", said)

    def test_the_cross_check_sums_the_months_and_leaves_a_blank_year_out(self):
        rows = source()
        layer, entry = layer_of(rows)
        check = {c["dam"]: c for c in self.m.compare(rows, layer, entry)[2]}
        self.assertEqual(check["ZZ00001"]["sum_of_its_twelve_months"], 1200.0)
        self.assertEqual(check["ZZ00001"]["difference_mwh"], 0.0)
        self.assertEqual(check["ZZ00002"]["difference_mwh"], 6.0)          # twelve months of 1 against a year of 6
        self.assertEqual(check["ZZ00003"]["note"], "a month or the year is blank")
        self.assertEqual(check["ZZ00003"]["sum_of_its_twelve_months"], "")


class TheKeptRun(unittest.TestCase):
    """What the run on the laboratory's own file wrote on 19 November 2026."""

    def test_no_figure_differs_and_the_count_is_said(self):
        with open(os.path.join(HERE, "hydropower_npd_figures_differ.csv"), encoding="utf-8") as f:
            lines = f.read().splitlines()
        self.assertTrue(lines[0].startswith("# 34014 figures of the layer compared with the publisher's file (sha256 84635b4faecc332c"))
        self.assertEqual(lines[1], "figure,the_map,the_publisher")
        self.assertEqual(len(lines), 2)

    def test_every_dam_is_cross_checked(self):
        with open(os.path.join(HERE, "crosscheck_dams.csv"), encoding="utf-8", newline="") as f:
            check = list(csv.DictReader(f))
        self.assertEqual(len(check), 2616)
        self.assertEqual(check[0]["dam"], "IL50745")               # the widest gap in MWh first
        held = [c for c in check if c["difference_pct"] != ""]
        self.assertEqual(sum(abs(float(c["difference_pct"])) <= 5 for c in held), 2012)

    def test_the_file_is_named_by_its_sha256_and_is_the_layers(self):
        m = load()
        with open(os.path.join(ROOT, "site", "data", "resources", "manifest.json"), encoding="utf-8") as f:
            entry = [l for l in json.load(f)["layers"] if l["id"] == "hydropower_npd"][0]
        self.assertEqual(m.SHA256, entry["source_sha256"])
        self.assertEqual(entry["source_bytes"], 1594027)
        self.assertEqual(entry["stats"]["n"], 2616)
        self.assertAlmostEqual(entry["stats"]["n"] * entry["stats"]["mean"], 3939.3, delta=0.1)      # the capacities' sum; the readme: "nearly 4 GW"

    def test_no_em_dash(self):
        for p in ("replicate_dams.py", "hydropower_npd_figures_differ.csv", "crosscheck_dams.csv"):
            with open(os.path.join(HERE, p), encoding="utf-8") as f:
                self.assertNotIn(EM, f.read(), p)
        with open(os.path.abspath(__file__), encoding="utf-8") as f:
            self.assertNotIn(EM, f.read())


if __name__ == "__main__":
    unittest.main()
