"""Session 180: the network as a map, and the boundary connector behind it (warehouse/connectors/eia_ba_boundaries.py).

What is held to: the builder turns a GeoJSON of shapes into the site's file with exact matching only (a shape is a
grid's when its code is the grid's EIA-930 code, never by name), lists every grid with no shape and every shape with no
grid, joins a grid's parts, drops a speck, orders the largest first so a smaller grid is drawn on top, and writes a
provenance record (address, retrieval time, sha256 of the raw file, license words, tolerance); it refuses a raw file
with no logged request, a code field it was not given, and a result over its ceiling. The request step refuses, before
any request, a paused publisher's host, a path a robots file disallows, a request past the ceiling and one sent sooner
than the robots file's delay. The site holds a boundary file only together with its row in the source registry: on
10 October 2026 it holds neither, and the page says so. The fixture is made-up squares, not boundaries.
No request and no model call is made here; the environment is read, never set.
"""
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_ba_boundaries as BA  # noqa: E402

FX = os.path.join(ROOT, "tests", "fixtures", "session180")
RAW = os.path.join(FX, "squares.geojson")
SITE_FILE = os.path.join(ROOT, "site", "public", "network", "ba_boundaries.json")
EM = chr(0x2014)
TMP = None
# the builder needs shapely and pyproj: on this machine's venv, not in requirements.txt (as warehouse/connectors/resource_layers.py)
HAVE_GEO = importlib.util.find_spec("shapely") is not None and importlib.util.find_spec("pyproj") is not None


def setUpModule():
    global TMP
    TMP = tempfile.mkdtemp(prefix="erw180_")


def tearDownModule():
    shutil.rmtree(TMP, ignore_errors=True)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def log_for(raw, name="requests.csv", sha=None):
    """A request log whose one row holds the raw file's sha256 (a fixture's: no request was made)."""
    with open(raw, "rb") as f:
        body = f.read()
    path = os.path.join(TMP, name)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=BA.LOG_COLS, lineterminator="\n")
        w.writeheader()
        w.writerow({"n": 1, "url": "fixture://squares.geojson", "status": "200", "bytes": len(body), "seconds": "0.0", "retrieved_utc": "2026-10-10T00:00:00Z",
                    "sha256": sha or hashlib.sha256(body).hexdigest(), "saved_as": "squares.geojson", "note": "a test fixture"})
    return path


def run_build(out, *more, raw=RAW, requests=None, code="BA_CODE"):
    argv = ["build", "--raw", raw, "--requests", requests or log_for(raw), "--out", out, "--code-field", code, "--name-field", "NAME",
            "--publisher", "TEST FIXTURE", "--title", "Made-up squares", "--vintage", "none", "--license-quoted", "none: a fixture", "--terms-url", "fixture://none",
            "--source", "fixture:session180", *more]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code_ = BA.main(argv)
    return code_, buf.getvalue()


@unittest.skipUnless(HAVE_GEO, "shapely and pyproj are not installed here: the builder cannot run")
class TheBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = os.path.join(TMP, "built.json")
        cls.code, cls.said = run_build(cls.out)
        with open(cls.out, encoding="utf-8") as f:
            cls.file = json.load(f)
        with open(os.path.join(ROOT, "site", "data", "grid_network.json"), encoding="utf-8") as f:
            cls.nodes = json.load(f)["nodes"]

    def test_it_matches_by_code_only(self):
        self.assertEqual(self.code, 0, self.said)
        ids = [r["id"] for r in self.file["regions"]]
        self.assertEqual(sorted(ids), ["BANC", "BPAT", "CISO", "ERCO", "MISO", "PJM", "SWPP"])
        self.assertEqual(self.file["matched"], 7)
        self.assertEqual(self.file["nodes"], len(self.nodes))
        # the square named "ISO New England" has no code: its name never matches it to ISNE
        self.assertNotIn("ISNE", ids)
        self.assertIn("ISNE", [n["id"] for n in self.file["nodes_without_shape"]])

    def test_every_node_and_every_shape_is_accounted_for(self):
        without = [n["id"] for n in self.file["nodes_without_shape"]]
        self.assertEqual(len(without) + self.file["matched"], len(self.nodes))
        self.assertEqual(set(without) | {r["id"] for r in self.file["regions"]}, {n["id"] for n in self.nodes})
        self.assertEqual([x["code"] for x in self.file["shapes_without_node"]], ["", "ZZZZ"])
        self.assertIn("no shape: ISNE", self.said)
        self.assertIn("no node: ZZZZ", self.said)

    def test_the_largest_is_first_so_the_smaller_is_drawn_on_top(self):
        areas = [r["area_km2"] for r in self.file["regions"]]
        self.assertEqual(areas, sorted(areas, reverse=True))
        ids = [r["id"] for r in self.file["regions"]]
        self.assertLess(ids.index("CISO"), ids.index("BANC"))
        self.assertEqual(ids[-1], "BANC")
        self.assertIn("largest area first", self.file["order"])

    def test_a_grid_in_two_features_is_one_shape_and_the_speck_is_dropped(self):
        erco = next(r for r in self.file["regions"] if r["id"] == "ERCO")
        self.assertEqual(len(erco["rings"]), 1)
        xs = [p[0] for p in erco["rings"][0]]
        ys = [p[1] for p in erco["rings"][0]]
        self.assertEqual((min(xs), max(xs), min(ys), max(ys)), (-101, -96, 28, 33))
        self.assertEqual(erco["rings"][0][0], erco["rings"][0][-1])
        self.assertEqual(self.file["provenance"]["simplification"]["parts_dropped"], 1)
        self.assertTrue(-101 < erco["point"][0] < -96 and 28 < erco["point"][1] < 33)

    def test_the_provenance_record(self):
        p = self.file["provenance"]
        with open(RAW, "rb") as f:
            body = f.read()
        self.assertEqual(p["raw_sha256"], hashlib.sha256(body).hexdigest())
        self.assertEqual(p["raw_bytes"], len(body))
        self.assertEqual(p["url"], "fixture://squares.geojson")
        self.assertEqual(p["retrieved_utc"], "2026-10-10T00:00:00Z")
        self.assertEqual(p["code_field"], "BA_CODE")
        self.assertEqual(p["simplification"]["tolerance_degrees"], 0.02)
        for k in ("source", "publisher", "title", "vintage", "license_quoted", "terms_url", "built_utc", "builder"):
            self.assertTrue(p[k], k)

    def test_the_committed_fixture_file_is_what_the_builder_writes(self):
        with open(os.path.join(FX, "ba_boundaries_fixture.json"), encoding="utf-8") as f:
            kept = json.load(f)
        self.assertEqual(kept["regions"], self.file["regions"])
        self.assertEqual(kept["matched"], self.file["matched"])
        self.assertIn("FIXTURE", kept["provenance"]["publisher"])

    def test_it_refuses_a_raw_file_with_no_logged_request(self):
        out = os.path.join(TMP, "no_log.json")
        code, said = run_build(out, requests=log_for(RAW, "other.csv", sha="0" * 64))
        self.assertEqual(code, 1)
        self.assertIn("REFUSED", said)
        self.assertFalse(os.path.exists(out))

    def test_it_never_guesses_the_code_field(self):
        out = os.path.join(TMP, "no_field.json")
        code, said = run_build(out, code="EIA_CODE")
        self.assertEqual(code, 1)
        self.assertIn("no property named 'EIA_CODE'", said)
        self.assertIn("BA_CODE: 7 of", said)   # it says what each property would match, and chooses none
        self.assertIn("NAME: 0 of", said)
        self.assertFalse(os.path.exists(out))

    def test_it_refuses_a_result_over_its_ceiling(self):
        out = os.path.join(TMP, "too_big.json")
        code, said = run_build(out, "--max-out-bytes", "1000")
        self.assertEqual(code, 1)
        self.assertIn("over the ceiling", said)
        self.assertFalse(os.path.exists(out))


class TheRequestStep(unittest.TestCase):
    """Every refusal comes before a request is made: none of these reaches a network."""

    def pull(self, name, rows=0, stamp="2026-10-10T00:00:00Z", host="example.org"):
        d = os.path.join(TMP, name)
        os.makedirs(d, exist_ok=True)
        BA.write_log(d, [{"n": i + 1, "url": f"https://{host}/f{i}", "status": "200", "bytes": 10, "seconds": "0.1", "retrieved_utc": stamp, "sha256": "", "saved_as": "", "note": ""}
                         for i in range(rows)])
        return d

    def test_the_contact_string_is_the_ruled_one(self):
        self.assertEqual(BA.CONTACT, "ERW research project, github.com/SamuelEnrique/erw")
        self.assertNotIn("@", BA.CONTACT)

    def test_a_paused_publisher_is_never_asked(self):
        with self.assertRaises(SystemExit) as e:
            BA.get("https://www.misoenergy.org/anything", "x.json", self.pull("paused"), 5, 10**6)
        self.assertIn("paused publisher", str(e.exception))

    def test_a_robots_file_that_disallows_the_path_stops_the_request(self):
        robots = os.path.join(TMP, "robots_no.txt")
        with open(robots, "w", encoding="utf-8") as f:
            f.write("User-agent: *\nDisallow: /api/\n")
        self.assertFalse(BA.robots_allows(robots, "https://example.org/api/file.json"))
        self.assertTrue(BA.robots_allows(robots, "https://example.org/datasets/file.json"))
        with self.assertRaises(SystemExit) as e:
            BA.get("https://example.org/api/file.json", "x.json", self.pull("robots"), 5, 10**6, robots=robots)
        self.assertIn("disallows", str(e.exception))

    def test_the_ceiling_of_requests_and_of_bytes(self):
        with self.assertRaises(SystemExit) as e:
            BA.get("https://example.org/sixth", "x.json", self.pull("five", rows=5), 5, 10**6)
        self.assertIn("the ceiling is 5", str(e.exception))
        with self.assertRaises(SystemExit) as e:
            BA.get("https://example.org/more", "x.json", self.pull("bytes", rows=2), 5, 20)
        self.assertIn("bytes already read", str(e.exception))

    def test_a_request_sooner_than_the_delay_is_refused(self):
        import time
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self.assertRaises(SystemExit) as e:
            BA.get("https://example.org/next", "x.json", self.pull("gap", rows=1, stamp=now), 5, 10**6, min_gap=60)
        self.assertIn("the delay asked is 60 s", str(e.exception))


class WhatTheSiteHolds(unittest.TestCase):
    def registry(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def test_a_boundary_file_and_its_registry_row_come_together_or_not_at_all(self):
        rows = [r for r in self.registry() if "balancing_authorit" in r["source"] or "control_area" in r["source"]]
        if not os.path.exists(SITE_FILE):
            # 10 October 2026: the five requests reached no boundary file, so none is shipped and none is registered
            self.assertEqual(rows, [], "a boundary source is registered but the site holds no boundary file")
            return
        with open(SITE_FILE, encoding="utf-8") as f:
            file = json.load(f)
        p = file["provenance"]
        self.assertRegex(p["raw_sha256"], r"^[0-9a-f]{64}$")
        self.assertNotIn("FIXTURE", p["publisher"].upper(), "the fixture's squares must never be shipped")
        self.assertTrue(p["license_quoted"] and p["url"].startswith("https://") and p["retrieved_utc"])
        self.assertIn(p["source"], [r["source"] for r in rows])
        self.assertEqual(next(r for r in rows if r["source"] == p["source"])["license"], "public")
        self.assertLessEqual(os.path.getsize(SITE_FILE), 400_000)
        self.assertEqual(file["matched"], len(file["regions"]))

    def test_the_registry_has_its_columns_and_no_row_was_lost(self):
        rows = self.registry()
        self.assertEqual(list(rows[0].keys()), ["source", "publisher", "report", "report_url", "document_list", "license", "tables", "first_seen", "last_seen"])
        self.assertGreaterEqual(len(rows), 307)

    def test_the_page_draws_nothing_it_does_not_hold(self):
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertIn("The boundary file is not yet held", m)
        self.assertIn('r.status === 404 ? ({ state: "absent" }', m)
        self.assertNotIn("squares", m)   # the fixture is the tests' own
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn('const shape: Shape = v3 ? ownShape ?? parseShape(search) : "network";', n)
        lib = src("site", "lib", "networkMap.ts")
        self.assertIn('return p.get(SHAPE_KEY) === "map" ? "map" : "network";', lib)
        self.assertIn('if (shape !== "map") return query;', lib)

    def test_the_method_note_holds_the_methodology_and_the_page_face_does_not(self):
        note = src("docs", "methods", "grid_network.md")
        for words in ("## The map (session 180)", "The boundary file is not yet held", "Matching is exact", "Overlaps are real", "What is simplified", "What the colors are not",
                      "Crawl-delay: 60", "numberMatched"):
            self.assertIn(words, note)
        page = src("site", "app", "network", "page.tsx")
        self.assertNotIn("What the colors are not", page)

    def test_the_page_stays_in_review(self):
        self.assertIn('"/network": "review"', src("site", "lib", "release.ts"))

    def test_no_em_dash(self):
        for parts in (("warehouse", "connectors", "eia_ba_boundaries.py"), ("site", "app", "network", "NetworkMap.tsx"), ("site", "app", "network", "Network.tsx"),
                      ("site", "lib", "networkMap.ts"), ("site", "scripts", "check-network-map.mjs"), ("docs", "methods", "grid_network.md"),
                      ("tests", "test_session180.py"), ("tests", "fixtures", "session180", "make_squares_180.py"), ("tests", "fixtures", "session180", "squares.geojson")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))
        report = os.path.join(ROOT, "archive", "sessions", "SESSION_180_REPORT.md")
        if os.path.exists(report):
            self.assertNotIn(EM, src("archive", "sessions", "SESSION_180_REPORT.md"))


if __name__ == "__main__":
    unittest.main()
