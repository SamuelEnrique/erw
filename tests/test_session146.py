"""Session 146: the natural resource layers (warehouse/connectors/resource_layers.py).

  the ceiling refuses a download before it starts (the size is asked first, the running total is the ledger's),
    and a server that states no size is read with the remaining budget as a hard stop;
  a paused publisher is never requested; the only contact string sent is the project's, with no address in it;
  the grid encoding round-trips, and an empty cell stays empty;
  a level is never finer than its source;
  the reduction is the mean of the source's own cells, with the half rule, on a small raster made here;
  every layer of the manifest has a unit, a vintage, a terms quote and a file that exists, and each grid level's
    file is what the manifest says it is;
  every terms quote is in the saved terms page word for word (only on a machine that holds the raw store);
  no em dash in the files this session wrote.
No network. The tests that need numpy, rasterio or the layer files skip when they are absent.
"""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import resource_layers as rl  # noqa: E402

MANIFEST = os.path.join(ROOT, "site", "data", "resources", "manifest.json")
WEB = os.path.join(ROOT, "site", "public", "resources-data")
RAW = os.environ.get("ERW_RESOURCES_RAW") or r"C:\Users\lossa\Documents\erw\warehouse\raw\resources"
EM_DASH = chr(0x2014)


def have(mod):
    try:
        __import__(mod)
        return True
    except Exception:
        return False


def manifest():
    if not os.path.exists(MANIFEST):
        return None
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


class Resp:
    def __init__(self, status=200, headers=None, chunks=()):
        self.status_code = status
        self.headers = headers or {}
        self._chunks = chunks

    def iter_content(self, n):
        for c in self._chunks:
            yield c

    def close(self):
        pass


class Server:
    """A publisher that states a size (or none) and counts what is asked of it."""

    def __init__(self, size=None, chunks=()):
        self.size, self.chunks = size, chunks
        self.heads, self.gets, self.reads = 0, 0, 0

    def head(self, url, **kw):
        self.heads += 1
        return Resp(200, {"Content-Length": str(self.size)} if self.size is not None else {})

    def get(self, url, headers=None, **kw):
        self.gets += 1
        if headers and "Range" in headers:
            return Resp(200, {})
        self.reads += 1
        return Resp(200, {}, self.chunks)


class TestCeiling(unittest.TestCase):
    def test_refused_before_the_download(self):
        with tempfile.TemporaryDirectory() as d:
            s = Server(size=5000)
            with self.assertRaises(rl.CeilingRefused):
                rl.fetch(s, d, "pub", "layer", "https://example.org/a.zip", "a.zip", ceiling=4000)
            self.assertEqual(s.heads, 1)
            self.assertEqual(s.gets, 0, "nothing of the file may be read once its size passes the ceiling")
            self.assertFalse(os.path.exists(os.path.join(d, "pub", "a.zip")))
            self.assertEqual(rl.ledger_total(rl.read_ledger(d)), 0)

    def test_the_running_total_is_the_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            a = Server(size=600, chunks=[b"x" * 600])
            rl.fetch(a, d, "pub", "layer", "https://example.org/a.zip", "a.zip", ceiling=1000)
            self.assertEqual(rl.ledger_total(rl.read_ledger(d)), 600)
            b = Server(size=401, chunks=[b"y" * 401])
            with self.assertRaises(rl.CeilingRefused):
                rl.fetch(b, d, "pub", "layer", "https://example.org/b.zip", "b.zip", ceiling=1000)
            self.assertEqual(b.reads, 0)
            c = Server(size=400, chunks=[b"z" * 400])
            rl.fetch(c, d, "pub", "layer", "https://example.org/c.zip", "c.zip", ceiling=1000)
            self.assertEqual(rl.ledger_total(rl.read_ledger(d)), 1000)
            row = rl.read_ledger(d)[-1]
            self.assertEqual(row["sha256"], rl.sha256_file(os.path.join(d, "pub", "c.zip")))

    def test_a_file_already_held_is_not_read_again(self):
        with tempfile.TemporaryDirectory() as d:
            a = Server(size=10, chunks=[b"0123456789"])
            rl.fetch(a, d, "pub", "layer", "https://example.org/a.zip", "a.zip", ceiling=1000)
            again = Server(size=10, chunks=[b"0123456789"])
            rl.fetch(again, d, "pub", "layer", "https://example.org/a.zip", "a.zip", ceiling=1000)
            self.assertEqual((again.heads, again.gets), (0, 0))
            self.assertEqual(rl.ledger_total(rl.read_ledger(d)), 10)

    def test_no_stated_size_stops_before_the_ceiling(self):
        with tempfile.TemporaryDirectory() as d:
            s = Server(size=None, chunks=[b"x" * 300, b"x" * 300, b"x" * 300])
            with self.assertRaises(rl.CeilingRefused):
                rl.fetch(s, d, "pub", "layer", "https://example.org/a.json", "a.json", ceiling=700)
            self.assertFalse(os.path.exists(os.path.join(d, "pub", "a.json")))
            self.assertFalse(os.path.exists(os.path.join(d, "pub", "a.json.part")))
            total = rl.ledger_total(rl.read_ledger(d))
            self.assertEqual(total, 600, "what was read is counted, and it is under the ceiling")
            self.assertLessEqual(total, 700)

    def test_a_paused_publisher_is_never_requested(self):
        with tempfile.TemporaryDirectory() as d:
            for url in ("https://www.misoenergy.org/x.zip", "https://dataminer2.pjm.com/feed/x"):
                s = Server(size=10, chunks=[b"0123456789"])
                with self.assertRaises(rl.Paused):
                    rl.fetch(s, d, "pub", "layer", url, "x.zip", ceiling=1000)
                self.assertEqual((s.heads, s.gets), (0, 0))

    def test_the_only_contact_string(self):
        self.assertEqual(rl.UA, "ERW research project, github.com/SamuelEnrique/erw")
        self.assertEqual(rl.CEILING_BYTES, 4 * 1024 ** 3)
        with open(os.path.join(ROOT, "warehouse", "connectors", "resource_layers.py"), encoding="utf-8") as f:
            code = f.read()
        self.assertNotRegex(code, r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}", "no e-mail address in the connector")
        for src in rl.SOURCES.values():
            self.assertIsNone(rl.FORBIDDEN.search(src["url"]))
            self.assertIn(src["terms"], rl.TERMS)
        if have("requests"):
            h = dict(rl.http_session().headers)
            self.assertEqual(h["User-Agent"], rl.UA)
            self.assertNotIn("@", " ".join(f"{k} {v}" for k, v in h.items()))

    def test_an_archive_member_cannot_leave_its_folder(self):
        import zipfile
        with tempfile.TemporaryDirectory() as d:
            z = os.path.join(d, "bad.zip")
            with zipfile.ZipFile(z, "w") as f:
                f.writestr("../outside.txt", "x")
            with self.assertRaises(RuntimeError):
                rl.unpack(z)
            self.assertFalse(os.path.exists(os.path.join(d, "outside.txt")))


@unittest.skipUnless(have("numpy"), "numpy is not on this machine")
class TestGrid(unittest.TestCase):
    def test_the_encoding_round_trips(self):
        import numpy as np
        v = np.array([[0.0, 1.234, 7.5], [np.nan, 12.001, 65.534]])
        obj = {"nrows": 2, "ncols": 3, "scale": 0.001, "offset": 0.0, "nodata": rl.NODATA,
               "values": rl.encode_grid(v, 0.001)}
        back = rl.decode_grid(obj)
        self.assertTrue(np.isnan(back[1, 0]), "an empty cell stays empty")
        self.assertTrue(np.allclose(back[np.isfinite(v)], v[np.isfinite(v)], atol=0.0005))
        import base64
        raw = base64.b64decode(obj["values"])
        self.assertEqual(len(raw), 12)
        self.assertEqual(raw[2:4], (1234).to_bytes(2, "little"), "little-endian, row-major")
        self.assertEqual(raw[6:8], (65535).to_bytes(2, "little"))

    def test_a_value_that_does_not_fit_is_refused(self):
        import numpy as np
        with self.assertRaises(ValueError):
            rl.encode_grid(np.array([[70.0]]), 0.001)
        with self.assertRaises(ValueError):
            rl.encode_grid(np.array([[-1.0]]), 0.001)

    def test_a_level_is_never_finer_than_its_source(self):
        self.assertEqual(rl.allowed_levels(0.02), [0.2, 0.1, 0.05, 0.025])
        self.assertEqual(rl.allowed_levels(0.0277), [0.2, 0.1, 0.05])
        self.assertEqual(rl.allowed_levels(0.04), [0.2, 0.1, 0.05])
        self.assertEqual(rl.allowed_levels(0.1), [0.2, 0.1])
        self.assertEqual(rl.allowed_levels(0.5), [])

    def test_coarsen_sums_blocks(self):
        import numpy as np
        a = np.arange(16.0).reshape(4, 4)
        self.assertEqual(rl.coarsen(a, 2).tolist(), [[10.0, 18.0], [42.0, 50.0]])

    @unittest.skipUnless(have("rasterio") and have("pyproj"), "rasterio is not on this machine")
    def test_the_reduction_is_the_mean_with_the_half_rule(self):
        import numpy as np
        import rasterio
        from rasterio.transform import from_origin
        # a source of 0.1 degree cells, 4 by 4, over longitude -100.4 to -100.0 and latitude 40.4 to 40.0
        src = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, -9999, -9999, 12], [13, -9999, -9999, -9999]], "float32")
        with tempfile.TemporaryDirectory() as d:
            tif = os.path.join(d, "s.tif")
            with rasterio.open(tif, "w", driver="GTiff", height=4, width=4, count=1, dtype="float32",
                               crs="EPSG:4326", transform=from_origin(-100.4, 40.4, 0.1, 0.1), nodata=-9999) as ds:
                ds.write(src, 1)
            levels, legend, st, res = rl.build_grid("t", tif, 1, d, (-100.4, 40.0, -100.0, 40.4), 0.001)
            self.assertAlmostEqual(res, 0.1, places=6)
            self.assertEqual([l["cell_deg"] for l in levels], [0.2, 0.1], "no level finer than the source")
            with open(os.path.join(d, "t_0p2.json")) as f:
                g2 = rl.decode_grid(json.load(f))
            # north-west block: mean of 1, 2, 5, 6; north-east: 3, 4, 7, 8
            self.assertAlmostEqual(g2[0, 0], 3.5, places=3)
            self.assertAlmostEqual(g2[0, 1], 5.5, places=3)
            # south-west block: 9 and 13 valid of 4 cells: exactly half, kept, mean 11
            self.assertAlmostEqual(g2[1, 0], 11.0, places=3)
            # south-east block: 12 valid of 4 cells: under half, empty (never filled)
            self.assertTrue(np.isnan(g2[1, 1]))
            with open(os.path.join(d, "t_0p1.json")) as f:
                g1 = rl.decode_grid(json.load(f))
            want = np.where(src == -9999, np.nan, src)
            self.assertTrue(np.allclose(g1, want, equal_nan=True), "at the source's own cell size nothing changes")
            self.assertAlmostEqual(st["mean"], float(np.nanmean(want)), places=6)


class TestManifest(unittest.TestCase):
    def setUp(self):
        self.man = manifest()
        if self.man is None:
            self.skipTest("the manifest is not on this machine")

    def test_every_layer_is_described(self):
        ids = [l["id"] for l in self.man["layers"]]
        self.assertEqual(len(ids), len(set(ids)))
        for l in self.man["layers"]:
            with self.subTest(layer=l["id"]):
                for k in ("id", "group", "title", "kind", "unit", "publisher", "source_title", "source_url",
                          "terms_url", "terms_quote", "vintage", "retrieved_at_utc", "extent", "reduction",
                          "legend", "notes_for_method"):
                    self.assertIn(k, l)
                for k in ("title", "publisher", "source_url", "terms_url", "terms_quote", "vintage",
                          "retrieved_at_utc", "reduction"):
                    self.assertTrue(str(l[k]).strip(), k)
                self.assertIn(l["kind"], ("grid", "shapes", "points"))
                if l["kind"] == "grid" or l.get("value_label", "").startswith("no quantity") is False:
                    if l["kind"] == "grid":
                        self.assertTrue(l["unit"].strip(), "a grid has a unit")
                self.assertTrue(l["source_url"].startswith("https://"))
                self.assertNotIn("@", l["source_url"])
                files = [v["file"] for v in l["levels"]] if l["kind"] == "grid" else [l["file"]]
                self.assertTrue(files)
                for f in files:
                    p = os.path.join(WEB, f)
                    if not os.path.isdir(WEB):
                        self.skipTest("the layer files are not on this machine")
                    self.assertTrue(os.path.exists(p), f)
        for m in self.man.get("missing", []):
            self.assertTrue(m["id"] and m["group"] and m["title"] and m["reason"].strip())
            self.assertNotIn(m["id"], ids)

    def test_each_grid_level_is_what_the_manifest_says(self):
        if not have("numpy"):
            self.skipTest("numpy is not on this machine")
        import numpy as np
        grids = [l for l in self.man["layers"] if l["kind"] == "grid"]
        if not grids or not os.path.isdir(WEB):
            self.skipTest("no grid layer on this machine")
        for l in grids:
            cells = [v["cell_deg"] for v in l["levels"]]
            self.assertTrue(all(c + 1e-9 >= l["source_cell_deg"] for c in cells),
                            f"{l['id']}: a level finer than its source ({l['source_cell_deg']})")
            for v in l["levels"]:
                with self.subTest(layer=l["id"], cell=v["cell_deg"]):
                    p = os.path.join(WEB, v["file"])
                    self.assertEqual(os.path.getsize(p), v["bytes"])
                    with open(p, encoding="utf-8") as f:
                        g = json.load(f)
                    self.assertEqual((g["ncols"], g["nrows"]), (v["ncols"], v["nrows"]))
                    self.assertEqual((g["dlon"], g["dlat"], g["nodata"], g["encoding"]),
                                     (v["cell_deg"], v["cell_deg"], 65535, "uint16-le-base64"))
                    a = rl.decode_grid(g)
                    ok = np.isfinite(a)
                    self.assertTrue(ok.any())
                    self.assertGreaterEqual(a[ok].min(), l["source_stats"]["min"] - g["scale"])
                    self.assertLessEqual(a[ok].max(), l["source_stats"]["max"] + g["scale"])
                    chk = [c for c in l["checks"] if c["cell_deg"] == v["cell_deg"]][0]
                    self.assertEqual(int(ok.sum()), chk["cells_with_value"])
                    self.assertAlmostEqual(float(a[ok].mean()), chk["mean_of_cells"], delta=g["scale"])
                    # the level's mean, weighted by the source cells in each cell, is the source's mean
                    self.assertAlmostEqual(chk["mean_weighted_by_source_cells"], chk["source_mean_of_kept_cells"],
                                           delta=g["scale"])

    def test_shapes_and_points_hold_the_fields_the_page_reads(self):
        if not os.path.isdir(WEB):
            self.skipTest("the layer files are not on this machine")
        for l in self.man["layers"]:
            with self.subTest(layer=l["id"]):
                if l["kind"] == "shapes":
                    with open(os.path.join(WEB, l["file"]), encoding="utf-8") as f:
                        g = json.load(f)
                    self.assertEqual(g["type"], "FeatureCollection")
                    self.assertEqual(len(g["features"]), l["features"])
                    for ft in g["features"]:
                        for k in ("name", "kind", "value", "value_unit"):
                            self.assertIn(k, ft["properties"])
                        self.assertTrue(ft["properties"]["kind"])
                elif l["kind"] == "points":
                    with open(os.path.join(WEB, l["file"]), encoding="utf-8") as f:
                        g = json.load(f)
                    self.assertEqual(g["columns"][:2], ["lon", "lat"])
                    self.assertEqual(len(g["rows"]), l["rows"])
                    for r in g["rows"]:
                        self.assertEqual(len(r), len(g["columns"]))
                        self.assertTrue(-180 <= r[0] <= 180 and -90 <= r[1] <= 90)

    def test_every_terms_quote_is_in_the_saved_page(self):
        if not os.path.isdir(RAW):
            self.skipTest("the raw store is not on this machine")
        for l in self.man["layers"]:
            with self.subTest(layer=l["id"]):
                p = os.path.join(RAW, l["terms_file"])
                self.assertTrue(os.path.exists(p), p)
                self.assertEqual(rl.sha256_file(p), l["terms_sha256"])
                text = rl.html_text(p)
                self.assertIn(" ".join(l["terms_quote"].split()), text)


class TestNoEmDash(unittest.TestCase):
    def test_none_in_the_files_of_this_session(self):
        paths = [os.path.join(ROOT, "warehouse", "connectors", "resource_layers.py"),
                 os.path.join(ROOT, "warehouse", "connectors", "resource_layers.requirements.txt"),
                 os.path.join(ROOT, "docs", "methods", "resources.md"), MANIFEST, os.path.abspath(__file__)]
        if os.path.isdir(WEB):
            paths += [os.path.join(WEB, f) for f in os.listdir(WEB)]
        for p in paths:
            if not os.path.exists(p):
                continue
            with open(p, encoding="utf-8") as f:
                self.assertNotIn(EM_DASH, f.read(), p)


if __name__ == "__main__":
    unittest.main()
