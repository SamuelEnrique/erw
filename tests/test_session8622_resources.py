"""Session 8622 (chain 504, 19 November 2026): a fourth layer of the resource map is replicated, the wind sites.

Energy Research Warehouse (ERW). replication/resources/replicate_wind_sites.py reads the laboratory's supply curve
table and compares every figure the map holds for the layer `wind_capacity_factor`, each to the rounding the web file
keeps. The publisher's file is not kept in the repository, so the comparison is tried here on rows made up for the
test (three sites that are in no page), and the kept outputs of the real run are held to what the run printed. Nothing
here sets the environment or makes a request.
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
    spec = importlib.util.spec_from_file_location("replicate_wind_sites", os.path.join(HERE, "replicate_wind_sites.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def source():
    def row(gid, lat, lon, cf, speed, mw, area, state):
        return {"sc_point_gid": gid, "latitude": lat, "longitude": lon, "capacity_factor_ac": cf, "resource": speed, "capacity_ac_mw": mw, "area_developable_sq_km": area, "state": state}
    return [row("11", "40.123456", "-100.654321", "0.41234567", "8.3549", "282.0", "128.3401", "Made Up"), row("12", "41.0", "-101.0", "0.3", "7.0", "60.0", "30.0", "Made Up"),
            row("13", "30.5", "-90.5", "0.25004", "6.1251", "6.0", "2.96", "Elsewhere")]


def layer_of(rows, m):
    out = [[round(float(s["longitude"]), 3), round(float(s["latitude"]), 3), s["sc_point_gid"], round(float(s["capacity_factor_ac"]), 4), round(float(s["resource"]), 2), int(float(s["capacity_ac_mw"])), round(float(s["area_developable_sq_km"]), 1)] for s in rows]
    v = [float(s["capacity_factor_ac"]) for s in rows]
    return {"columns": list(m.COLUMNS), "rows": out}, {"stats": {"n": len(v), "min": min(v), "mean": sum(v) / len(v), "max": max(v)}, "unit": "ratio"}


class TheComparison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_a_layer_that_is_the_file_rounded_is_met_in_every_figure(self):
        rows = source()
        layer, entry = layer_of(rows, self.m)
        n, differ = self.m.compare(rows, layer, entry)
        self.assertEqual(differ, [])
        self.assertEqual(n, 2 + 3 * 7 + 5)

    def test_a_figure_one_unit_of_its_rounding_away_is_caught(self):
        rows = source()
        layer, entry = layer_of(rows, self.m)
        layer["rows"][0][3] += 0.0001      # the capacity factor, one unit of the fourth decimal
        layer["rows"][1][4] += 0.01        # the wind speed, one unit of the second
        layer["rows"][2][6] += 0.1         # the area, one unit of the first
        _, differ = self.m.compare(rows, layer, entry)
        self.assertEqual(sorted(d["figure"].split(" (")[0] for d in differ), ["site 11: value", "site 12: resource", "site 13: area_developable_sq_km"])

    def test_a_figure_kept_to_more_decimals_than_the_web_file_keeps_is_caught(self):
        rows = source()
        layer, entry = layer_of(rows, self.m)
        layer["rows"][0][4] = 8.3549       # the source's own digits where the web file keeps two
        _, differ = self.m.compare(rows, layer, entry)
        self.assertEqual([d["figure"] for d in differ], ["site 11: resource"])

    def test_a_site_missing_and_a_site_the_file_does_not_hold_are_caught(self):
        rows = source()
        layer, entry = layer_of(rows, self.m)
        layer["rows"][2][2] = "99"
        _, differ = self.m.compare(rows, layer, entry)
        said = [d["figure"] for d in differ]
        self.assertIn("site 99: a site of the publisher's file", said)
        self.assertIn("site 13: a site of the map's layer", said)

    def test_the_summary_by_state_and_the_pages_box(self):
        check = {c["state"]: c for c in self.m.by_state(source())}
        self.assertEqual(check["Made Up"]["sites"], 2)
        self.assertEqual(check["Made Up"]["capacity_ac_mw"], 342.0)
        self.assertEqual(check["Made Up"]["inside_the_pages_box"], "yes")
        outside = self.m.by_state([dict(source()[0], latitude="60.0", state="Far North")])[0]
        self.assertEqual(outside["inside_the_pages_box"], "NO")


class TheKeptRun(unittest.TestCase):
    """What the run on the laboratory's own file wrote on 19 November 2026."""

    def test_no_figure_differs_and_the_count_is_said(self):
        with open(os.path.join(HERE, "wind_capacity_factor_figures_differ.csv"), encoding="utf-8") as f:
            lines = f.read().splitlines()
        self.assertTrue(lines[0].startswith("# 395703 figures of the layer compared with the publisher's file (sha256 ef13116bd66f3115"))
        self.assertEqual(len(lines), 2)

    def test_every_state_lies_inside_the_box_the_datasets_page_states(self):
        with open(os.path.join(HERE, "crosscheck_wind_sites.csv"), encoding="utf-8", newline="") as f:
            check = list(csv.DictReader(f))
        self.assertEqual(len(check), 49)
        self.assertEqual({c["inside_the_pages_box"] for c in check}, {"yes"})
        self.assertEqual(sum(int(c["sites"]) for c in check), 56528)

    def test_the_file_is_named_by_its_sha256_and_is_the_layers(self):
        m = load()
        with open(os.path.join(ROOT, "site", "data", "resources", "manifest.json"), encoding="utf-8") as f:
            entry = [l for l in json.load(f)["layers"] if l["id"] == "wind_capacity_factor"][0]
        self.assertEqual(m.SHA256, entry["source_sha256"])
        self.assertEqual(entry["source_bytes"], 12829421)
        self.assertEqual(entry["stats"]["n"], 56528)

    def test_no_em_dash(self):
        for p in ("replicate_wind_sites.py", "wind_capacity_factor_figures_differ.csv", "crosscheck_wind_sites.csv"):
            with open(os.path.join(HERE, p), encoding="utf-8") as f:
                self.assertNotIn(EM, f.read(), p)
        with open(os.path.abspath(__file__), encoding="utf-8") as f:
            self.assertNotIn(EM, f.read())


if __name__ == "__main__":
    unittest.main()
