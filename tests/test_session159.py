"""Session 159: the resource map finished (warehouse/connectors/resource_layers.py, site/app/resources).

  hydropower is held in the form its publisher publishes it: Oak Ridge National Laboratory's two assessments on
    HydroSource, each file by its own address with a plain request (HEAD and GET only, nothing posted, no form, the
    project's contact string and nothing else), under the connector's ceiling;
  a dam is a point with the file's own capacity, generation and capacity factor; an empty cell of the file stays empty
    and is never a zero; the owner's name and every e-mail address stay out of the web files;
  new stream-reach development is the file's own total a HUC10 watershed; a watershed for which the file gives no
    capacity (its code -9999) is not in the web file;
  the web files' values are the publisher's own (read back against the raw files where the raw store is on the machine);
  the gross capacity factor is named as not fetched, in one sentence;
  the queue overlay knows six grids and draws four: MISO reads "paused while terms are reviewed" and NYISO "NYISO's
    terms do not allow it", each with its operator's own sentence, quoted word for word from where the repository
    already holds it; a row of a grid that is not shown never reaches the page;
  the page stays in review; no em dash in the files this session wrote.
No network. The parts that need the raw store, openpyxl or the layer files skip when they are absent.
"""
import csv
import hashlib
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import resource_layers as rl  # noqa: E402

MANIFEST = os.path.join(ROOT, "site", "data", "resources", "manifest.json")
WEB = os.path.join(ROOT, "site", "data", "resources", "layers")
RAW = os.environ.get("ERW_RESOURCES_RAW") or r"C:\Users\lossa\Documents\erw\warehouse\raw\resources"
NYISO_RAW = r"C:\Users\lossa\Documents\erw\warehouse\raw\nyiso_load_queue"
EM_DASH = chr(0x2014)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
CONTACT = "ERW research project, github.com/SamuelEnrique/erw"
ORNL_KEYS = ["ornl_npd", "ornl_npd_fields", "ornl_npd_readme", "ornl_nsd_xlsx", "ornl_nsd_zip"]


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def squeeze(text):
    return re.sub(r"\s+", " ", text).strip()


def manifest():
    if not os.path.exists(MANIFEST):
        return None
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def layer(man, id):
    return next((l for l in man["layers"] if l["id"] == id), None)


def have(mod):
    try:
        __import__(mod)
        return True
    except Exception:
        return False


class Resp:
    def __init__(self, status=200, headers=None, body=b""):
        self.status_code = status
        self.headers = headers or {}
        self._body = body

    def iter_content(self, n):
        for i in range(0, len(self._body), n):
            yield self._body[i:i + n]

    def close(self):
        pass


class Recorder:
    """A session that answers from memory and keeps every call made of it: the method, the address, what was sent."""

    def __init__(self, bodies):
        self.bodies = bodies
        self.calls = []
        self.headers = {"User-Agent": rl.UA, "Accept": "*/*", "Accept-Encoding": "identity"}

    def head(self, url, **kw):
        self.calls.append(("HEAD", url, kw))
        return Resp(200, {"Content-Length": str(len(self.bodies[url]))})

    def get(self, url, **kw):
        self.calls.append(("GET", url, kw))
        return Resp(200, {"Content-Length": str(len(self.bodies[url]))}, self.bodies[url])

    def __getattr__(self, name):  # post, put, request: anything else is a failure of the test
        raise AssertionError(f"the connector called session.{name}: only head and get are plain requests")


class TheFilesByTheirOwnAddresses(unittest.TestCase):
    def test_the_sources_are_the_publishers_own_file_addresses(self):
        for key in ORNL_KEYS:
            with self.subTest(source=key):
                src = rl.SOURCES[key]
                self.assertEqual(src["source"], "ornl")
                self.assertEqual(src["terms"], "ornl")
                self.assertTrue(src["url"].startswith("https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/"), src["url"])
                self.assertEqual(os.path.basename(src["url"]), os.path.basename(src["file"]))
                # a file's own address: no query, nothing of a form, no address of a person
                for bad in ("?", "gform", "gravityforms", "wp-admin", "@", "mailto"):
                    self.assertNotIn(bad, src["url"])
                self.assertIsNone(rl.FORBIDDEN.search(src["url"]))
        self.assertEqual(rl.TERMS["ornl"]["url"], "https://hydrosource.ornl.gov/data-use-policy/")

    def test_a_pull_is_head_and_get_and_sends_nothing_else(self):
        src = rl.SOURCES["ornl_npd_readme"]
        body = b"Technical Potential for Hydropower Capacity at Nonpowered Dams Readme\n"
        with tempfile.TemporaryDirectory() as raw:
            sess = Recorder({src["url"]: body})
            path = rl.fetch(sess, raw, src["source"], ";".join(src["layers"]), src["url"], src["file"])
            with open(path, "rb") as f:
                self.assertEqual(f.read(), body)
            self.assertEqual([c[0] for c in sess.calls], ["HEAD", "GET"])
            for method, url, kw in sess.calls:
                self.assertEqual(url, src["url"])
                for sent in ("data", "json", "params", "files", "auth", "cookies"):
                    self.assertNotIn(sent, kw, f"{method} sent {sent}")
                self.assertIsNone(EMAIL.search(json.dumps(kw.get("headers", {}))))
            rows = rl.read_ledger(raw)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["bytes"], str(len(body)))
            self.assertEqual(rows[0]["sha256"], hashlib.sha256(body).hexdigest())

    def test_the_only_contact_string_and_no_address(self):
        self.assertEqual(rl.UA, CONTACT)
        s = rl.http_session()
        self.assertEqual(dict(s.headers), {"User-Agent": CONTACT, "Accept": "*/*", "Accept-Encoding": "identity"})
        code = read("warehouse", "connectors", "resource_layers.py")
        self.assertIsNone(EMAIL.search(code), "an e-mail address in the connector")
        self.assertNotIn(".post(", code)
        self.assertNotIn("requests.post", code)

    def test_the_ceiling_refuses_the_archive_before_it_is_read(self):
        src = rl.SOURCES["ornl_nsd_zip"]
        with tempfile.TemporaryDirectory() as raw:
            rl.append_ledger(raw, {"source": "nlr", "layer": "x", "url": "https://example.org/x", "file": "x",
                                   "bytes": rl.CEILING_BYTES - 1000, "sha256": "0", "retrieved_at_utc": "t",
                                   "http_status": "200"})
            sess = Recorder({src["url"]: b"0" * 5000})
            with self.assertRaises(rl.CeilingRefused):
                rl.fetch(sess, raw, src["source"], "hydropower_nsd", src["url"], src["file"])
            self.assertEqual([c[0] for c in sess.calls], ["HEAD"], "the size is asked; the file is not read")
            self.assertFalse(os.path.exists(os.path.join(raw, "ornl", src["file"])))

    def test_what_is_left_and_what_is_not_held(self):
        self.assertNotIn("ornl_npd", rl.LEFT_SOURCES)
        self.assertNotIn("ornl_nsd", rl.LEFT_SOURCES)
        self.assertIn("hydropower_potential", rl.RETIRED_IDS)
        self.assertNotIn("hydropower_potential", rl.EXPECTED)
        for id in ("hydropower_npd", "hydropower_nsd"):
            self.assertEqual(rl.EXPECTED[id][0], "hydropower")
            self.assertIn(id, rl.BUILDERS)
        why = rl.NOT_HELD["wind_gross_capacity_factor"]
        self.assertIn("key issued to a named person", why)
        self.assertIn("no key is asked for", why)
        self.assertEqual(len(re.split(r"(?<=\.)\s+", why.strip())), 1, "one sentence")
        self.assertNotIn("wind_gross_capacity_factor", rl.BUILDERS)
        self.assertFalse(any("developer" in s["url"] or "api_key" in s["url"] for s in rl.SOURCES.values()))


class TheFileAsItIsWritten(unittest.TestCase):
    def test_an_empty_cell_is_none_and_never_a_zero(self):
        self.assertIsNone(rl.as_number(""))
        self.assertIsNone(rl.as_number("   "))
        self.assertIsNone(rl.as_number(None))
        self.assertEqual(rl.as_number("0"), 0)
        self.assertEqual(rl.as_number("6.058"), 6.058)
        self.assertEqual(rl.as_number("1260"), 1260)
        self.assertIsInstance(rl.as_number("1260"), int)
        with self.assertRaises(ValueError):
            rl.as_number("n/a")

    def test_a_readme_section(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "readme.txt")
            with open(p, "w", encoding="utf-8") as f:
                f.write("Title\n\nCitation:\nA, B. 2025. The data.\n\n\nAbstract:\nOne line.\nA second line.\n\n"
                        "Dataset contacts:\nSomebody: somebody@example.org\n")
            self.assertEqual(rl.readme_section(p, "Abstract"), "One line. A second line.")
            self.assertEqual(rl.readme_section(p, "Citation"), "A, B. 2025. The data.")
            self.assertEqual(rl.readme_section(p, "No such heading"), "")

    def test_the_dams_builder_on_a_small_file(self):
        """Three dams written here in the publisher's own columns: one with no generation in the file."""
        cols = ["nididfull", "lat", "long", "dam_name", "dam_owner", "county", "state_abbr", "waterway", "inputdata",
                "cap_mw", "gen_mwh_yr", "cf_yr", "head_ft_yr", "q30_cfs"]
        dams = [["AA00001", "40.123456", "-90.654321", "FIRST DAM", "A PRIVATE PERSON", "Adams", "IL", "First River",
                 "Gage Flow, Historical Head", "6.058", "20450.149", "0.363", "66.17", "1260"],
                ["AA00002", "41.5", "-91.25", "SECOND DAM", "A COMPANY", "Brown", "IA", "Second Creek",
                 "Modeled Flow, Estimated Head", "0.001", "", "0", "10", "3"],
                ["AA00003", "39", "-89", "THIRD DAM", "", "Clark", "MO", "Third Fork", "Modeled Flow, Estimated Head",
                 "222.069", "821209.77", "0.384", "20.5", "90000"]]
        fields = [["Field Name", "Description", "Units", "Datatype"]] + [
            [c, {"cap_mw": "Nominal capacity", "gen_mwh_yr": "Annual average generation",
                 "cf_yr": "Median annual capacity factor (ratio of something); If 0, average value is <0.001."}.get(c, "About " + c),
             {"cap_mw": "MW", "gen_mwh_yr": "MWh", "head_ft_yr": "feet", "q30_cfs": "cfs"}.get(c, "unitless"), "text"]
            for c in cols if c != "long"] + [["lon", "Longitude, North American Datum 83", "decimal degrees", "numeric"]]
        readme = ("Readme\n\nCitation:\nSomebody. 2025. The dams.\n\nAbstract:\nEstimates at dams.\n\n"
                  "Methodology:\nA model.\n\nDataset contacts:\nSomebody: somebody@example.org\n")
        with tempfile.TemporaryDirectory() as tmp:
            raw, web, man = os.path.join(tmp, "raw"), os.path.join(tmp, "web"), os.path.join(tmp, "manifest.json")
            os.makedirs(os.path.join(raw, "ornl", "npd"))
            os.makedirs(os.path.join(raw, "ornl", "terms"))
            terms = os.path.join(raw, "ornl", "terms", rl.TERMS["ornl"]["file"])
            with open(terms, "w", encoding="utf-8") as f:
                f.write("<html><body>" + " ".join(rl.TERMS["ornl"]["quote"]) + "</body></html>")

            def put(key, text):
                src = rl.SOURCES[key]
                p = os.path.join(raw, "ornl", src["file"])
                with open(p, "w", encoding="utf-8", newline="") as f:
                    f.write(text)
                rl.append_ledger(raw, {"source": "ornl", "layer": "hydropower_npd", "url": src["url"], "file": src["file"],
                                       "bytes": os.path.getsize(p), "sha256": rl.sha256_file(p), "retrieved_at_utc": "2026-10-08T08:45:07Z",
                                       "http_status": "200", "terms_url": rl.TERMS["ornl"]["url"],
                                       "terms_file": "ornl/terms/" + rl.TERMS["ornl"]["file"], "terms_sha256": rl.sha256_file(terms)})
            put("ornl_npd", "\n".join(",".join(f'"{x}"' for x in r) for r in [cols] + dams) + "\n")
            put("ornl_npd_fields", "\n".join(",".join(f'"{x}"' for x in r) for r in fields) + "\n")
            put("ornl_npd_readme", readme)
            rl.BUILDERS["hydropower_npd"](raw, web, man)
            with open(os.path.join(web, "hydropower_npd.json"), encoding="utf-8") as f:
                out = json.load(f)
            with open(man, encoding="utf-8") as f:
                entry = json.load(f)["layers"][0]
        c = {name: i for i, name in enumerate(out["columns"])}
        self.assertEqual(out["columns"][:4], ["lon", "lat", "name", "value"])
        self.assertNotIn("dam_owner", c)
        self.assertEqual(len(out["rows"]), 3)
        by = {r[c["nididfull"]]: r for r in out["rows"]}
        self.assertEqual(by["AA00001"][c["value"]], 6.058)
        self.assertEqual(by["AA00001"][c["gen_mwh_yr"]], 20450.149)
        self.assertEqual((by["AA00001"][c["lon"]], by["AA00001"][c["lat"]]), (-90.6543, 40.1235))
        self.assertIsNone(by["AA00002"][c["gen_mwh_yr"]], "an empty generation stays empty")
        self.assertEqual(by["AA00002"][c["cf_yr"]], 0, "a zero the file writes is a zero")
        self.assertEqual(by["AA00003"][c["name"]], "THIRD DAM")
        text = json.dumps(out) + json.dumps(entry)
        self.assertIsNone(EMAIL.search(text), "an e-mail address reached the web file or the manifest")
        self.assertNotIn("A PRIVATE PERSON", text)
        self.assertEqual(entry["kind"], "points")
        self.assertEqual(entry["unit"], "MW")
        self.assertEqual(entry["stats"], {"n": 3, "min": 0.001, "mean": (6.058 + 0.001 + 222.069) / 3, "max": 222.069})
        self.assertEqual(entry["total_cap_mw"], round(6.058 + 0.001 + 222.069, 3))
        self.assertEqual(entry["total_gen_mwh_yr"], round(20450.149 + 821209.77, 3), "the empty generation adds nothing")
        self.assertTrue(entry["publisher"].startswith("Oak Ridge National Laboratory"))
        self.assertIn("openly shared, without restriction", entry["terms_quote"])
        self.assertIn("Somebody. 2025. The dams.", entry["credit"])
        self.assertEqual([f for f, _ in entry["hover_fields"]][:2], ["gen_mwh_yr", "cf_yr"])
        self.assertEqual(entry["hover_fields"][0][1], "Annual average generation, MWh")
        self.assertEqual(entry["hover_fields"][1][1], "Median annual capacity factor")

    @unittest.skipUnless(have("openpyxl"), "openpyxl is not installed")
    def test_a_workbook_keeps_each_cell_in_its_own_column(self):
        import openpyxl
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "book.xlsx")
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "NSD"
            ws.append(["HUC10", "HUC10_NAME", "NUMREACH", "P_MW_Sum", "E_MWh_Sm"])
            ws.append([512010609, "A Creek", 1, 1.5, None])
            ws.append([None, None, None, None, None])
            ws.append([1705010103, "B River", 2, 46.133069, 0])
            wb.save(p)
            rows = rl.workbook_sheets(p, ["NSD"])["NSD"]
        self.assertEqual(rows[1], [512010609, "A Creek", 1, 1.5], "an empty cell at the end is dropped, none is shifted")
        self.assertEqual(rows[2], [1705010103, "B River", 2, 46.133069, 0])
        self.assertEqual(len(rows), 3)


class TheManifest(unittest.TestCase):
    def setUp(self):
        self.man = manifest()
        if self.man is None:
            self.skipTest("no manifest on this machine")

    def web(self, name):
        p = os.path.join(WEB, name)
        if not os.path.exists(p):
            self.skipTest("the layer files are not on this machine")
        with open(p, encoding="utf-8") as f:
            return json.load(f)

    def test_hydropower_is_held_and_its_publisher_is_oak_ridge(self):
        missing = self.man.get("missing", [])
        self.assertFalse([m for m in missing if "hydro" in (m["id"] + m["title"]).lower()], "hydropower is still named as missing")
        for id in ("hydropower_npd", "hydropower_nsd"):
            with self.subTest(layer=id):
                l = layer(self.man, id)
                self.assertIsNotNone(l)
                self.assertEqual(l["group"], "hydropower")
                self.assertEqual(l["unit"], "MW")
                self.assertTrue(l["publisher"].startswith("Oak Ridge National Laboratory"))
                self.assertNotIn("Geological Survey", l["publisher"])
                self.assertIn("it is not a USGS layer", l["notes_for_method"])
                self.assertEqual(l["terms_url"], "https://hydrosource.ornl.gov/data-use-policy/")
                self.assertIn("Data hosted on HydroSource is openly shared, without restriction, in accordance with Department of "
                              "Energy's Public Access Plan.", l["terms_quotes"])
                self.assertTrue(l["source_url"].startswith("https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/"))
                self.assertTrue(l["vintage"].strip())
                self.assertIn("was not filled", l["notes_for_method"])
                self.assertIsNone(EMAIL.search(json.dumps(l)), "an e-mail address in the manifest entry")
                self.assertRegex(l["source_sha256"], r"^[0-9a-f]{64}$")

    def test_the_gross_capacity_factor_is_named_as_not_fetched(self):
        m = [x for x in self.man.get("missing", []) if x["id"] == "wind_gross_capacity_factor"]
        self.assertEqual(len(m), 1)
        self.assertEqual(m[0]["group"], "wind")
        self.assertEqual(m[0]["title"], "Gross capacity factor")
        self.assertEqual(m[0]["reason"], rl.NOT_HELD["wind_gross_capacity_factor"])
        held = layer(self.man, "wind_capacity_factor")
        self.assertIsNotNone(held)
        self.assertNotIn("gross", held["title"].lower())

    def test_the_dams_file_is_what_the_manifest_says(self):
        l = layer(self.man, "hydropower_npd")
        f = self.web(l["file"])
        c = {name: i for i, name in enumerate(f["columns"])}
        self.assertEqual(l["kind"], "points")
        self.assertEqual(len(f["rows"]), l["rows"])
        self.assertEqual(len({r[c["nididfull"]] for r in f["rows"]}), l["rows"], "every dam once")
        caps = [r[c["value"]] for r in f["rows"]]
        self.assertTrue(all(isinstance(v, (int, float)) and v > 0 for v in caps))
        self.assertEqual(min(caps), l["stats"]["min"])
        self.assertEqual(max(caps), l["stats"]["max"])
        self.assertAlmostEqual(sum(caps) / len(caps), l["stats"]["mean"], places=9)
        self.assertAlmostEqual(sum(caps), l["total_cap_mw"], places=6)
        self.assertEqual((l["legend"]["min"], l["legend"]["max"]), (l["stats"]["min"], l["stats"]["max"]))
        self.assertNotIn("dam_owner", c)
        for field, words in l["hover_fields"]:
            self.assertIn(field, c)
            self.assertTrue(words.strip())
        for r in f["rows"]:   # the file's own place: the conterminous states, nothing placed by hand
            self.assertTrue(-125 <= r[c["lon"]] <= -66 and 24 <= r[c["lat"]] <= 50, r[:3])
        self.assertIsNone(EMAIL.search(json.dumps(f)))

    def test_the_watersheds_file_is_what_the_manifest_says(self):
        l = layer(self.man, "hydropower_nsd")
        fc = self.web(l["file"])
        feats = fc["features"]
        self.assertEqual(l["kind"], "shapes")
        self.assertEqual(len(feats), l["features"])
        self.assertEqual(len(feats), l["watersheds_with_capacity"])
        self.assertEqual(l["watersheds_in_file"], l["watersheds_with_capacity"] + l["watersheds_no_reach"] + l["watersheds_coded_minus_999"])
        codes = [f["properties"]["HUC10"] for f in feats]
        self.assertEqual(len(set(codes)), len(codes), "every watershed once")
        vals = []
        for f in feats:
            p = f["properties"]
            self.assertRegex(p["HUC10"], r"^\d{10}$")
            self.assertEqual(p["kind"], "HUC10 watershed")
            self.assertEqual(p["value_unit"], "MW")
            self.assertEqual(p["value"], p["P_MW_Sum"], "the value drawn is the file's own total for the watershed")
            self.assertGreater(p["value"], 0)
            self.assertGreaterEqual(p["NUMREACH"], 1)
            self.assertIn(p["HUC10"], p["name"])
            for v in p.values():   # a no-value code of the file is never a number in the web file
                self.assertNotIn(v, (-9999, -999))
            self.assertIn(f["geometry"]["type"], ("Polygon", "MultiPolygon"))
            vals.append(p["value"])
        self.assertEqual(min(vals), l["stats"]["min"])
        self.assertEqual(max(vals), l["stats"]["max"])
        self.assertAlmostEqual(sum(vals), l["total_p_mw"], places=2)
        without = [f["properties"]["HUC10"] for f in feats if f["properties"]["E_MWh_Sm"] is None]
        self.assertEqual(sorted(without), l["watersheds_without_energy"])
        self.assertEqual(len(feats) - len(without), l["watersheds_with_energy"])
        self.assertIsNone(EMAIL.search(json.dumps(fc)))

    def test_the_web_files_hold_the_publishers_own_figures(self):
        """Read back against the raw files, where the raw store is on the machine."""
        npd_raw = os.path.join(RAW, "ornl", "npd", "TechPotentialNPDs.csv")
        if not os.path.exists(npd_raw):
            self.skipTest("the raw store is not on this machine")
        l = layer(self.man, "hydropower_npd")
        self.assertEqual(rl.sha256_file(npd_raw), l["source_sha256"], "the raw file is the one the manifest names")
        with open(npd_raw, encoding="utf-8-sig", newline="") as f:
            src = {r["nididfull"]: r for r in csv.DictReader(f)}
        out = self.web(l["file"])
        c = {name: i for i, name in enumerate(out["columns"])}
        self.assertEqual(len(out["rows"]), len(src))
        for r in out["rows"]:
            s = src[r[c["nididfull"]]]
            self.assertEqual(r[c["value"]], float(s["cap_mw"]))
            self.assertEqual(r[c["gen_mwh_yr"]], float(s["gen_mwh_yr"]))
            self.assertEqual(r[c["cf_yr"]], float(s["cf_yr"]))
            self.assertEqual(r[c["name"]], s["dam_name"].strip())
            self.assertAlmostEqual(r[c["lon"]], float(s["long"]), delta=0.00005001)
            self.assertAlmostEqual(r[c["lat"]], float(s["lat"]), delta=0.00005001)
        book = os.path.join(RAW, "ornl", "nsd", "ORNL_NHAAP_NSD_SR_All_v1.xlsx")
        if not (os.path.exists(book) and have("openpyxl")):
            return
        rows = [r for r in rl.workbook_sheets(book, ["NSD"])["NSD"] if isinstance(r[0], (int, float))]
        want = {str(int(r[0])).zfill(10): r for r in rows}
        fc = self.web(layer(self.man, "hydropower_nsd")["file"])
        got = {f["properties"]["HUC10"]: f["properties"] for f in fc["features"]}
        self.assertEqual(set(got), set(want), "the watersheds drawn are the workbook's, no more and no fewer")
        for code, p in got.items():
            self.assertAlmostEqual(p["value"], want[code][3], places=6)
            self.assertEqual(p["NUMREACH"], want[code][2])
            self.assertIn(want[code][1], p["name"])

    def test_the_ledger_stays_under_the_ceiling(self):
        if not os.path.exists(rl.ledger_path(RAW)):
            self.skipTest("the raw store is not on this machine")
        rows = rl.read_ledger(RAW)
        self.assertLess(rl.ledger_total(rows), rl.CEILING_BYTES)
        ornl = [r for r in rows if r["source"] == "ornl"]
        if not ornl:
            self.skipTest("Oak Ridge's files are not in this raw store")
        urls = {rl.SOURCES[k]["url"] for k in ORNL_KEYS} | {rl.TERMS["ornl"]["url"]}
        for r in ornl:
            self.assertEqual(r["http_status"], "200")
            self.assertIn(r["url"], urls)
            self.assertRegex(r["sha256"], r"^[0-9a-f]{64}$")
        page = os.path.join(RAW, "ornl", "terms", rl.TERMS["ornl"]["file"])
        text = rl.html_text(page)
        for q in rl.TERMS["ornl"]["quote"]:
            self.assertIn(squeeze(q), text, "a quote of the data use policy is not in the saved page")


class TheQueueGridByGrid(unittest.TestCase):
    def setUp(self):
        self.lib = read("site", "lib", "resources.ts")
        self.data = read("site", "lib", "resourcesdata.ts")
        self.map = read("site", "app", "resources", "ResourceMap.tsx")
        m = re.search(r"export const QUEUE_GRIDS: QueueGrid\[\] = \[(.*?)\n\];", self.lib, re.S)
        self.assertIsNotNone(m, "QUEUE_GRIDS is not in site/lib/resources.ts")
        self.grids = m.group(1)

    def entry(self, id):
        m = re.search(r'id: "%s", label: "([^"]+)", shown: (true|false), words: "([^"]*)",\s*why: "((?:[^"\\]|\\.)*)"' % id, self.grids)
        self.assertIsNotNone(m, id)
        return {"label": m.group(1), "shown": m.group(2) == "true", "words": m.group(3), "why": m.group(4).replace('\\"', '"')}

    def test_six_grids_and_four_are_drawn(self):
        self.assertEqual(re.findall(r'id: "([a-z]+)"', self.grids), ["ercot", "spp", "caiso", "isone", "miso", "nyiso"])
        for id in ("ercot", "spp", "caiso", "isone"):
            self.assertTrue(self.entry(id)["shown"], id)
        self.assertNotIn("PJM", self.grids)

    def test_miso_reads_its_fixed_words_with_the_sentence_of_its_terms(self):
        g = self.entry("miso")
        self.assertFalse(g["shown"])
        self.assertEqual(g["words"], "paused while terms are reviewed")
        quote = re.search(r'"(You agree not use any automated means[^"]*)"', g["why"])
        self.assertIsNotNone(quote)
        self.assertIn(quote.group(1), squeeze(read("docs", "methods", "miso_pause.md")), "not the sentence the pause quotes")
        with open(os.path.join(ROOT, "warehouse", "metadata", "paused_sources.csv"), encoding="utf-8", newline="") as f:
            paused = {r["scope"]: r for r in csv.DictReader(f)}
        self.assertIn("miso", paused, "the pause is lifted: a person turns the switch in QUEUE_GRIDS, and this test follows")
        self.assertEqual(paused["miso"]["terms_quoted"], quote.group(1))
        self.assertIn("4 October 2026", g["why"])
        self.assertEqual(paused["miso"]["paused_on"], "2026-10-04")

    def test_nyiso_reads_what_its_terms_say_with_the_sentences_of_its_notice(self):
        g = self.entry("nyiso")
        self.assertFalse(g["shown"])
        self.assertEqual(g["words"], "NYISO's terms do not allow it")
        quotes = re.findall(r'"([^"]{40,})"', g["why"])
        self.assertEqual(len(quotes), 2)
        report = squeeze(read("archive", "sessions", "SESSION_149_REPORT.md"))
        for q in quotes:
            self.assertIn(q, report, "not a sentence session 149 quoted from NYISO's legal notice")
        self.assertIn("does not confer any license or ownership interest", quotes[0])
        self.assertIn("All Rights Reserved.", quotes[1])
        # the same words the connector of NYISO's load queue holds (session 149's ruling)
        self.assertIn('HELD_WORDS = "NYISO\'s terms do not allow it"', read("warehouse", "connectors", "nyiso_load_queue.py"))
        if os.path.isdir(NYISO_RAW):   # the notice as saved on 7 October 2026, where it is on the machine
            saved = [f for f in os.listdir(NYISO_RAW) if f.endswith("_legal-notice.html")]
            if saved:
                text = rl.html_text(os.path.join(NYISO_RAW, sorted(saved)[-1])).replace("'", "\u2019")
                for q in quotes:
                    self.assertIn(q.replace("'", "\u2019"), text, "not in the saved legal notice word for word")

    def test_a_row_of_a_grid_that_is_not_shown_never_reaches_the_page(self):
        self.assertIn("src:extra->>source_table", self.data)
        body = self.data[self.data.index("export async function queue()"):self.data.index("type FacilityRow")]
        left_out = body.index("if (!grid.shown) { withheld += 1; continue; }")
        for later in ("points.push(", "byCounty.set(", "vintages.push("):
            self.assertGreater(body.index(later), left_out, f"{later} runs before a grid that is not shown is left out")
        self.assertIn("withheld, grids: [...grids.values()]", body)
        # the face: the two lines come from the one list, and the counts from what the overlay sends
        self.assertIn("R.QUEUE_GRIDS.filter((g) => !g.shown)", self.map)
        self.assertIn("R.queueLine(g)", self.map)
        self.assertIn("queue.grids.filter((g) => g.shown && g.rows > 0)", self.map)
        for words in ("paused while terms are reviewed", "NYISO's terms do not allow it"):
            self.assertNotIn(words, self.map, "the words are written once, in lib/resources.ts")

    def test_the_method_note_states_it_grid_by_grid(self):
        page = read("site", "app", "resources", "page.tsx")
        self.assertIn("QUEUE_GRIDS.filter((g) => !g.shown).map(", page)
        self.assertIn("data-method-queue-grid", page)
        doc = read("docs", "methods", "resources.md")
        for words in ("MISO: paused while terms are reviewed", "NYISO: its terms do not allow it", "You agree not use any automated means",
                      "does not confer any license or", "answered \"202\""):
            self.assertIn(squeeze(words), squeeze(doc))


class ThePage(unittest.TestCase):
    def test_it_stays_in_review(self):
        release = read("site", "lib", "release.ts")
        self.assertRegex(release, r'"/resources":\s*"review"')
        self.assertNotRegex(release, r'"/resources[^"]*":\s*"live"')

    def test_the_hover_lists_the_fields_the_manifest_names(self):
        lib, comp, page = read("site", "lib", "resources.ts"), read("site", "app", "resources", "ResourceMap.tsx"), read("site", "app", "resources", "page.tsx")
        self.assertIn("hover_fields?: [string, string][]", lib)
        self.assertIn("hover_fields:", page)
        self.assertIn("function listed(l: R.Layer", comp)
        self.assertIn("v === null || v === undefined || v === \"\" ? []", comp, "a field the source leaves empty is left out, not shown as a zero")
        # no layer is named in the map's code: hydropower is drawn from the manifest like every other layer
        self.assertNotIn("hydropower_n", comp)

    def test_the_frame_time_script_measures_a_laptop_window_with_everything_on(self):
        s = read("site", "scripts", "frametime-resources.mjs")
        for part in ('flag("--size", "")', "const EVERYTHING = [...(manifest.layers ?? []).map((l) => l.id), ...OVERLAY_IDS]",
                     '`--window-size=${SIZE[0]},${SIZE[1]}`', '"--headless=new"', "a window on the screen"):
            self.assertIn(part, s)

    def test_the_checks_cover_hydropower_and_the_two_lines(self):
        s = read("site", "scripts", "check-resources.mjs")
        for part in ("hydropower_npd", "hydropower_nsd", "data-queue-grid", "MISO: paused while terms are reviewed",
                     "NYISO's terms do not allow it", "wind:wind_gross_capacity_factor"):
            self.assertIn(part, s)

    def test_the_method_document_has_its_sections(self):
        doc = read("docs", "methods", "resources.md")
        for part in ("## Session 159 (8 October 2026)", "(`hydropower_npd`)", "(`hydropower_nsd`)", "Oak Ridge National Laboratory",
                     "openly shared, without restriction", "**Gross capacity factor** (`wind_gross_capacity_factor`)"):
            self.assertIn(part, doc)
        self.assertIsNone(EMAIL.search(doc), "an e-mail address in the method document")
        self.assertNotIn("**Hydropower potential** (`hydropower_potential`)", doc)


class TestNoEmDash(unittest.TestCase):
    def test_none_in_the_files_of_this_session(self):
        files = [("warehouse", "connectors", "resource_layers.py"), ("docs", "methods", "resources.md"),
                 ("site", "data", "resources", "manifest.json"), ("site", "lib", "resources.ts"), ("site", "lib", "resourcesdata.ts"),
                 ("site", "app", "resources", "page.tsx"), ("site", "app", "resources", "ResourceMap.tsx"),
                 ("site", "scripts", "check-resources.mjs"), ("site", "scripts", "frametime-resources.mjs"),
                 ("site", "scripts", "test-resources.mjs"), ("tests", "test_session159.py"),
                 ("site", "data", "resources", "layers", "hydropower_npd.json"), ("site", "data", "resources", "layers", "hydropower_nsd.json")]
        for parts in files:
            p = os.path.join(ROOT, *parts)
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    self.assertNotIn(EM_DASH, f.read(), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
