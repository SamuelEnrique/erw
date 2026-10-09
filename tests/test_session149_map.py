"""Session 149, part B: the published boundaries of the curtailment page's places (warehouse/connectors/zone_boundaries.py).

Energy Research Warehouse (ERW). No request is made, no model is called and nothing is written under warehouse/output,
warehouse/raw or site/data (a build is trialled into a temporary folder).

    TheRules       the builder's request rules, read from the module: the one contact string, the ceiling enforced
                   before a request, MISO and PJM's Data Miner never asked, a site that answered with a refusal not
                   asked again
    TheSiteFile    site/data/curtailment/zone_shapes.json as committed: one entry for every place of the page and no
                   other, no place without a source row, a mapped place's centroid inside its shape, the counts, the
                   terms quoted, ERCOT's weather zones as its ZIP code table lists them
    TheRawStore    with the raw files on the machine (ERW_ZONE_RAW, or warehouse/raw/zone_boundaries; skipped cleanly
                   without them, as on GitHub's runner): every file is the one downloads.csv recorded, the ledger is
                   inside the ceiling, and a build from them gives the committed places and definitions again
    ThePage        the page's source: a tile says why it is a tile, the page stays in review

    python -m unittest tests.test_session149_map
"""

import csv
import hashlib
import json
import os
import re
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import zone_boundaries as zb  # noqa: E402

SHAPES = os.path.join(ROOT, "site", "data", "curtailment", "zone_shapes.json")
FREE = os.path.join(ROOT, "site", "data", "curtailment", "free_energy.json")
DASH = chr(0x2014)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def raw_dir():
    for d in (os.environ.get("ERW_ZONE_RAW"), zb.RAW_DIR):
        if d and os.path.exists(os.path.join(d, "requests.csv")):
            return d
    return None


def inside(point, geometry):
    """Is [lon, lat] inside a GeoJSON Polygon or MultiPolygon? Ray casting, holes counted."""
    def ring(p, r):
        x, y = p
        on = False
        for i in range(len(r)):
            (xi, yi), (xj, yj) = r[i], r[i - 1]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                on = not on
        return on
    polys = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
    return any(ring(point, p[0]) and not any(ring(point, h) for h in p[1:]) for p in polys)


class TheRules(unittest.TestCase):
    def test_the_one_contact_string_and_no_address(self):
        self.assertEqual(zb.CONTACT, "ERW research project, github.com/SamuelEnrique/erw")
        code = src("warehouse", "connectors", "zone_boundaries.py")
        self.assertNotIn("@", code)                       # no e-mail address anywhere in the builder
        self.assertEqual(len(re.findall(r"User-Agent", code)), 1)
        self.assertIn('headers={"User-Agent": CONTACT, "Accept": "*/*"}', code)

    def test_the_ceiling_is_thirty_requests_and_200_mb(self):
        self.assertEqual((zb.MAX_REQUESTS, zb.MAX_BYTES), (30, 200 * 1024 * 1024))

    def test_miso_and_pjm_are_never_asked(self):
        for url in ("https://www.misoenergy.org/x", "https://cdn.misoenergy.org/x", "https://dataminer2.pjm.com/feed", "https://api.pjm.com/api/v1/x"):
            self.assertIsNotNone(zb.allowed(url), url)
        for _key, _op, url, _file, terms, _what in zb.SOURCES:
            self.assertIsNone(zb.allowed(url), url)
            self.assertNotRegex(url + terms, r"misoenergy|pjm\.com")

    def test_a_request_past_the_ceiling_or_to_a_forbidden_host_is_not_sent(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(zb.urllib.request, "urlopen", side_effect=AssertionError("a request was sent")):
            self.assertIsNone(zb.get(tmp, "miso", "https://www.misoenergy.org/x", "x.html", ""))
            self.assertFalse(os.path.exists(os.path.join(tmp, "requests.csv")))
            for i in range(zb.MAX_REQUESTS):
                zb.append_csv(os.path.join(tmp, "requests.csv"), zb.REQ_COLS, {"n": i + 1, "requested_at_utc": "", "operator": "x", "url": "u", "status": 200, "bytes": 1, "file": "", "error": ""})
            self.assertIsNone(zb.get(tmp, "ercot", "https://www.ercot.com/x", "x.html", zb.ERCOT_TERMS))
            self.assertEqual(zb.spent(tmp), (zb.MAX_REQUESTS, zb.MAX_REQUESTS))

    def test_a_refusal_is_recorded_and_not_asked_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            err = zb.urllib.error.HTTPError("https://www.ercot.com/x", 403, "Forbidden", None, None)
            with mock.patch.object(zb.urllib.request, "urlopen", side_effect=err) as sent, mock.patch.object(zb, "SOURCES", [("k", "ercot", "https://www.ercot.com/x", "x.html", zb.ERCOT_TERMS, "a file")]):
                self.assertEqual(zb.pull(tmp), 1)
                self.assertEqual(zb.pull(tmp), 0)             # the second time it is left, not asked
                self.assertEqual(sent.call_count, 1)
            rows = zb.read_csv(os.path.join(tmp, "requests.csv"))
            self.assertEqual([(r["status"], r["error"], r["file"]) for r in rows], [("403", "HTTP 403 Forbidden", "")])
            self.assertFalse(os.path.exists(os.path.join(tmp, "ercot", "x.html")))


class TheSiteFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.z, cls.free = load(SHAPES), load(FREE)

    def places(self):
        return {(g, loc["id"]) for g, grid in self.free["grids"].items() for loc in grid["locations"] if loc["kind"] != "average"}

    def test_one_entry_for_every_place_of_the_page_and_no_other(self):
        held = {(g, p) for g, ps in self.z["places"].items() for p in ps}
        self.assertEqual(held, self.places())
        c = self.z["counts"]
        self.assertEqual(c["places"], len(held))
        self.assertEqual(c["mapped"] + c["tiles"], c["places"])
        self.assertEqual(c["mapped"], sum(1 for ps in self.z["places"].values() for p in ps.values() if p["status"] == "mapped"))

    def test_no_place_without_a_source_row(self):
        searched = {"caiso", "ercot", "nyiso"}
        for g, ps in self.z["places"].items():
            for pid, p in ps.items():
                self.assertIn(p["status"], ("mapped", "tile"), (g, pid))
                if p["status"] == "mapped":
                    self.assertIn(p["source"], self.z["sources"], (g, pid))
                    continue
                self.assertTrue(p["reason"].endswith("."), (g, pid))
                for s in p["sources"]:
                    self.assertIn(s, self.z["sources"], (g, pid))
                if g in searched:
                    self.assertTrue(p["sources"], (g, pid))
                else:                                          # a grid that was not searched says so, and claims no source
                    self.assertEqual(p["sources"], [], (g, pid))
                    self.assertIn("was not searched", p["reason"], (g, pid))

    def test_a_mapped_place_has_its_centroid_inside_its_published_shape(self):
        mapped = [(g, pid, p) for g, ps in self.z["places"].items() for pid, p in ps.items() if p["status"] == "mapped"]
        self.assertEqual(len(mapped), self.z["counts"]["mapped"])
        for g, pid, p in mapped:
            self.assertIn(p["geometry"]["type"], ("Polygon", "MultiPolygon"), (g, pid))
            self.assertTrue(inside(p["centroid"], p["geometry"]), (g, pid))
            self.assertTrue(p["drawn"] and p["terms_url"] and p["centroid_method"], (g, pid))

    def test_no_point_and_no_shape_for_a_tile(self):
        for g, ps in self.z["places"].items():
            for pid, p in ps.items():
                if p["status"] == "tile":
                    self.assertFalse({"geometry", "centroid", "lat", "lon"} & set(p), (g, pid))
        for grid in self.free["grids"].values():              # and the page's own file still holds no coordinate
            for loc in grid["locations"]:
                self.assertIsNone(loc["lat"])
                self.assertIsNone(loc["lon"])

    def test_every_source_is_a_file_with_its_hash_and_its_terms(self):
        for sid, s in self.z["sources"].items():
            self.assertRegex(s["sha256"], r"^[0-9a-f]{64}$", sid)
            self.assertRegex(s["retrieved_at_utc"], r"^2026-10-\d\dT\d\d:\d\d:\d\dZ$", sid)
            self.assertTrue(s["url"].startswith("https://") and s["finding"], sid)
            self.assertTrue(s["terms_quote"] or s.get("terms_note"), sid)
            self.assertNotRegex(s["url"], r"misoenergy|pjm\.com", sid)
        quotes = {s["terms_url"]: s["terms_quote"] for s in self.z["sources"].values() if s["terms_quote"]}
        self.assertIn("credit the California ISO", quotes[zb.CAISO_TERMS])
        self.assertIn("may be used, reproduced, and redistributed", quotes[zb.ERCOT_TERMS])
        self.assertIn("does not confer any license", quotes[zb.NYISO_TERMS])
        self.assertIn("as a stand-alone file is strictly prohibited", self.z["nyiso_images"]["terms_quote"])

    def test_the_pull_is_inside_its_ceiling(self):
        p = self.z["pull"]
        self.assertLessEqual(p["requests"], 30)
        self.assertLessEqual(p["bytes"], 200 * 1024 * 1024)
        self.assertEqual(p["user_agent"], zb.CONTACT)

    def test_weather_zones_are_ercots_zip_codes_as_its_table_lists_them(self):
        w = self.z["definitions"]["ercot_weather_zones"]
        self.assertEqual(w["status"], "defined, not drawn")
        self.assertEqual(sorted(w["zones"]), ["COAST", "EAST", "FWEST", "NCENT", "NORTH", "SCENT", "SOUTH", "WEST"])
        seen = {}
        for code, zone in w["zones"].items():
            for zip_code in zone["zip_codes"]:
                self.assertRegex(zip_code, r"^\d{5}$")
                self.assertNotIn(zip_code, seen, f"{zip_code} is in {code} and {seen.get(zip_code)}")
                seen[zip_code] = code
        self.assertEqual(len(seen) + len(w["rows_not_assigned"]), w["rows_listed"])   # every row is in one zone or flagged
        for r in w["rows_not_assigned"]:                       # a row whose name and code disagree is in no zone
            self.assertNotIn(r["zip_code"], seen)
        self.assertNotIn("geometry", json.dumps(w))            # defined, and not drawn: no shape was made up for them

    def test_no_em_dash(self):
        for parts in (("site", "data", "curtailment", "zone_shapes.json"), ("warehouse", "connectors", "zone_boundaries.py"), ("tests", "test_session149_map.py")):
            self.assertNotIn(DASH, src(*parts), parts)


class TheRawStore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_dir()
        if cls.raw is None:
            raise unittest.SkipTest("the raw files of the zone boundary pull are not on this machine (ERW_ZONE_RAW or warehouse/raw/zone_boundaries)")

    def test_every_file_is_the_one_recorded(self):
        n = 0
        for op in sorted(os.listdir(self.raw)):
            path = os.path.join(self.raw, op, "downloads.csv")
            if not os.path.exists(path):
                continue
            with open(path, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(list(rows[0]), ["url", "file", "bytes", "sha256", "retrieved_at_utc", "terms_url"])
            for r in rows:
                with open(os.path.join(self.raw, op, r["file"]), "rb") as f:
                    body = f.read()
                self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (int(r["bytes"]), r["sha256"]), r["file"])
                n += 1
        self.assertGreaterEqual(n, 10)

    def test_the_ledger_is_inside_the_ceiling_and_asks_no_forbidden_host(self):
        rows = zb.read_csv(os.path.join(self.raw, "requests.csv"))
        self.assertLessEqual(len(rows), zb.MAX_REQUESTS)
        self.assertLessEqual(sum(int(r["bytes"] or 0) for r in rows), zb.MAX_BYTES)
        self.assertEqual([int(r["n"]) for r in rows], list(range(1, len(rows) + 1)))
        for r in rows:
            self.assertNotRegex(r["url"], r"misoenergy|pjm\.com")

    def test_a_build_from_the_raw_files_gives_the_committed_file_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "zone_shapes.json")
            self.assertEqual(zb.build(self.raw, out, FREE), 0)
            new, old = load(out), load(SHAPES)
        for k in ("about", "rule", "counts", "grids", "places", "definitions", "sources", "nyiso_images"):
            self.assertEqual(new[k], old[k], k)

    def test_the_zip_code_table_is_read_as_the_workbook_lists_it(self):
        zones, flagged, rows = zb.weather_zones(os.path.join(self.raw, "ercot", "Appendix_D_Profile_Decision_Tree_050124.xlsx"))
        self.assertEqual(rows, 2476)                           # the worksheet's own Count column ends at 2476
        self.assertEqual(sum(len(z["zip_codes"]) for z in zones.values()) + len(flagged), rows)
        self.assertEqual(zones["NCENT"]["name"], "North Central")
        self.assertIn("75001", zones["NCENT"]["zip_codes"])    # the worksheet's third row
        self.assertEqual(flagged, [{"zip_code": "79097", "weather_zone_name": "Far West", "weather_zone_code": "NORTH"}])


class ThePage(unittest.TestCase):
    def test_a_tile_says_why_it_is_a_tile(self):
        s = src("site", "app", "curtailment", "Sections.tsx")
        self.assertIn('data-shape={z?.status ?? "tile"}', s)
        self.assertIn("const text = `${counted}. ${z?.reason ?? NO_BOUNDARY}`;", s)
        self.assertIn("title={text}", s)
        self.assertIn('<Blank words="no boundary published" why={zones.grids[c.grid] ?? NO_BOUNDARY} />', s)
        self.assertIn("A schematic, not a map", s)             # nothing the page showed is dropped
        self.assertIn('import zoneJson from "@/data/curtailment/zone_shapes.json";', src("site", "app", "curtailment", "page.tsx"))

    def test_the_page_stays_in_review_and_the_live_list_is_unchanged(self):
        r = src("site", "lib", "release.ts")
        self.assertRegex(r, r'"/curtailment": "review"')
        # session 166 (the owner's instruction of 8 October 2026): the three pages that were open are in review; no page is live
        for path in ("/cost-of-power/battery", "/network", "/storage"):
            self.assertRegex(r, rf'"{path}": "review"')
        self.assertEqual(re.findall(r'"(/[^"]*)": "live"', r), [])

    def test_the_method_note_states_the_rule_and_quotes_the_terms(self):
        m = src("docs", "methods", "curtailment.md")
        self.assertIn("the mark is the centre of the zone's published boundary, not a hub's location", m)
        for q in ("credit the California ISO", "may be used, reproduced, and redistributed", "does not confer any license"):
            self.assertIn(q, m)
        self.assertNotIn(DASH, m)


if __name__ == "__main__":
    unittest.main()
