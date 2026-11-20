"""Session 8619 (chain 504, 19 November 2026): a second layer of the resource map is replicated, the sedimentary basins.

Energy Research Warehouse (ERW). replication/resources/replicate_basins.py reads EIA's own file and compares every
figure the map holds for the layer `oil_gas_basins`. The publisher's file is not kept in the repository, so the
comparison is tried here on a small file of the same kind built in the test (two basins whose names and areas are made
up and are in no page), and the kept outputs of the real run are held to what the run printed. Nothing here sets the
environment or makes a request.
"""

import csv
import importlib.util
import io
import os
import struct
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HERE = os.path.join(ROOT, "replication", "resources")
EM = chr(0x2014)


def load():
    spec = importlib.util.spec_from_file_location("replicate_basins", os.path.join(HERE, "replicate_basins.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def dbf_of(rows):
    """A dBase table of NAME (text), Area_sq_km and Area_sq_mi (numbers), as EIA's file holds them."""
    fields = [("NAME", "C", 24, 0), ("Area_sq_km", "N", 20, 6), ("Area_sq_mi", "N", 20, 6)]
    record_len = 1 + sum(f[2] for f in fields)
    header_len = 32 + 32 * len(fields) + 1
    out = bytearray(struct.pack("<B3BIHH20x", 3, 126, 11, 19, len(rows), header_len, record_len))
    for name, kind, length, dec in fields:
        out += name.encode("ascii").ljust(11, b"\x00") + kind.encode("ascii") + b"\x00" * 4 + bytes([length, dec]) + b"\x00" * 14
    out += b"\x0d"
    for name, km, mi in rows:
        out += b" " + name.encode("ascii").ljust(24) + ("%.6f" % km).rjust(20).encode("ascii") + ("%.6f" % mi).rjust(20).encode("ascii")
    return bytes(out)


def shp_of(boxes):
    """A shapefile of one square a row: (west, south, east, north) in degrees, each side cut into small steps."""
    out = bytearray(100)
    for i, (w, s, e, n) in enumerate(boxes):
        steps = 40
        ring = [(w + (e - w) * k / steps, n) for k in range(steps)] + [(e, n - (n - s) * k / steps) for k in range(steps)] \
            + [(e - (e - w) * k / steps, s) for k in range(steps)] + [(w, s + (n - s) * k / steps) for k in range(steps)] + [(w, n)]
        body = struct.pack("<i4dii", 5, w, s, e, n, 1, len(ring)) + struct.pack("<i", 0) + b"".join(struct.pack("<2d", x, y) for x, y in ring)
        out += struct.pack(">ii", i + 1, len(body) // 2) + body
    return bytes(out)


def zip_of(rows, boxes):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Basins.dbf", dbf_of(rows))
        z.writestr("Basins.shp", shp_of(boxes))
    return buf.getvalue()


class TheComparison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()
        cls.boxes = [(-100.0, 35.0, -99.0, 36.0), (-90.0, 30.0, -88.0, 31.0)]
        with zipfile.ZipFile(io.BytesIO(zip_of([("X", 1, 1), ("Y", 1, 1)], cls.boxes))) as z:
            areas = [cls.m.area_sq_mi(r) for r in cls.m.read_polygons(z.read("Basins.shp"))]
        cls.areas = areas
        cls.rows = [("NORTH FLAT", areas[0] * cls.m.SQ_KM_PER_SQ_MI, areas[0]), ("AB-CD SALT", areas[1] * cls.m.SQ_KM_PER_SQ_MI, areas[1])]
        cls.blob = zip_of(cls.rows, cls.boxes)

    def layer(self):
        feats = [{"properties": {"name": self.m.shown_name(n), "kind": "sedimentary basin", "value": round(mi, 6), "value_unit": "square miles", "NAME": n, "Area_sq_km": round(km, 6), "Area_sq_mi": round(mi, 6)}} for n, km, mi in self.rows]
        mis = [round(r[2], 6) for r in self.rows]
        return {"features": feats}, {"stats": {"n": 2, "min": min(mis), "mean": sum(mis) / 2, "max": max(mis)}, "features": 2, "unit": "square miles"}

    def test_a_square_degree_on_the_ellipsoid(self):
        # one degree by one degree at 35 to 36 north is about 3,900 square miles; two by one at 30 to 31 north about 8,200
        self.assertAlmostEqual(self.areas[0], 3900, delta=60)
        self.assertAlmostEqual(self.areas[1], 8200, delta=120)

    def test_a_layer_that_is_the_file_is_met_in_every_figure(self):
        layer, entry = self.layer()
        rows, differ, check = self.m.compare(self.blob, layer, entry)
        self.assertEqual(differ, 0, [r for r in rows if r["same"] == "NO"])
        self.assertEqual(len(rows), 1 + 2 * 6 + 6)
        self.assertEqual(len(check), 2)
        self.assertTrue(all(abs(c["difference_pct"]) < 0.01 and abs(c["sq_km_difference_pct"]) < 0.001 for c in check))

    def test_an_altered_area_and_an_altered_name_are_each_caught(self):
        layer, entry = self.layer()
        layer["features"][0]["properties"]["value"] += 1.0
        layer["features"][1]["properties"]["name"] = "AB-CD Salt"
        rows, differ, _ = self.m.compare(self.blob, layer, entry)
        self.assertEqual(differ, 2)
        self.assertEqual(sorted(r["figure"].split(":")[0] for r in rows if r["same"] == "NO"), ["AB-CD SALT", "NORTH FLAT"])

    def test_a_basin_missing_from_the_layer_and_one_the_file_does_not_hold_are_caught(self):
        layer, entry = self.layer()
        layer["features"][1]["properties"]["NAME"] = "ELSEWHERE"
        rows, differ, _ = self.m.compare(self.blob, layer, entry)
        said = [r["figure"] for r in rows if r["same"] == "NO"]
        self.assertIn("ELSEWHERE: a basin of the publisher's file", said)
        self.assertIn("AB-CD SALT: a basin of the map's layer", said)

    def test_the_layers_rule_for_a_name(self):
        self.assertEqual(self.m.shown_name("FORT WORTH"), "Fort Worth")
        self.assertEqual(self.m.shown_name("UINTA-PICEANCE"), "Uinta-Piceance")
        self.assertEqual(self.m.shown_name("TX-LA-MS SALT"), "Tx-La-Ms Salt")     # the rule as it is; data request 554 asks about this one


class TheKeptRun(unittest.TestCase):
    """What the run on EIA's own file wrote on 19 November 2026."""

    def rows(self, name):
        with open(os.path.join(HERE, name), encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def test_every_figure_is_the_publishers(self):
        rows = self.rows("oil_gas_basins_figures.csv")
        self.assertEqual(len(rows), 199)
        self.assertEqual({r["same"] for r in rows}, {"yes"})
        self.assertEqual(rows[0]["figure"], "basins, count")
        self.assertEqual(rows[0]["the_map"], "32")

    def test_every_basin_is_cross_checked(self):
        check = self.rows("crosscheck_basins.csv")
        self.assertEqual(len(check), 32)
        self.assertTrue(all(abs(float(c["difference_pct"])) <= 1 for c in check))
        self.assertTrue(all(abs(float(c["sq_km_difference_pct"])) <= 0.001 for c in check))
        self.assertEqual(check[0]["basin"], "VALLEY AND RIDGE")      # the widest gap first: 0.181 percent

    def test_the_file_is_named_by_its_sha256_and_is_the_layers(self):
        import json
        m = load()
        with open(os.path.join(ROOT, "site", "data", "resources", "manifest.json"), encoding="utf-8") as f:
            entry = [l for l in json.load(f)["layers"] if l["id"] == "oil_gas_basins"][0]
        self.assertEqual(m.SHA256, entry["source_sha256"])
        self.assertEqual(entry["source_bytes"], 440871)

    def test_no_em_dash(self):
        for p in ("replicate_basins.py", "oil_gas_basins_figures.csv", "crosscheck_basins.csv"):
            with open(os.path.join(HERE, p), encoding="utf-8") as f:
                self.assertNotIn(EM, f.read(), p)
        with open(os.path.abspath(__file__), encoding="utf-8") as f:
            self.assertNotIn(EM, f.read())


if __name__ == "__main__":
    unittest.main()
