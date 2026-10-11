"""Session 193: the map's areas derived from counties (warehouse/connectors/eia_ba_boundaries.py counties).

No published boundary of the balancing authorities answered in three pulls, so the file the map reads is the ERW's own
derivation: each county given to one balancing authority from EIA-861, and labeled as derived wherever it is drawn.
The rule is tested on made-up workbooks and made-up county shapes this file writes (no request, nothing read from
site/node_modules); the shipped file, its county list, its registry row, the page's label and the Method note are
read as they are.
"""

import csv
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_ba_boundaries as BA  # noqa: E402

SITE_FILE = os.path.join(ROOT, "site", "public", "network", "ba_boundaries.json")
COUNTY_FILE = os.path.join(ROOT, "site", "public", "network", "ba_counties.csv")
OWN = [("warehouse", "connectors", "eia_ba_boundaries.py"), ("site", "app", "network", "NetworkMap.tsx"), ("site", "app", "network", "Network.tsx"),
       ("site", "lib", "networkMap.ts"), ("docs", "methods", "grid_network.md"), ("tests", "test_session193.py"), ("site", "scripts", "check-network-map.mjs")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def geoms(*pairs):
    return [{"id": code, "properties": {"name": name}} for code, name in pairs]


INDEX, _ = BA.county_index(geoms(("51159", "Richmond"), ("51760", "Richmond"), ("51710", "Norfolk"), ("51036", "Charles City"), ("35013", "Doña Ana"),
                                 ("22071", "Orleans"), ("29510", "St. Louis"), ("29189", "St. Louis"), ("48201", "Harris"), ("48157", "Fort Bend"), ("48339", "Montgomery")))


class CountyNames(unittest.TestCase):
    def test_a_name_is_compared_without_accents_case_or_its_kind(self):
        self.assertEqual(BA.county_key("Doña Ana"), BA.county_key("Dona Ana County"))
        self.assertEqual(BA.county_key("Saint Louis"), BA.county_key("St. Louis"))
        self.assertEqual(BA.county_key("Orleans Parish"), "orleans")
        self.assertEqual(BA.county_key("Charles City"), "charlescity")            # "City" is part of this county's name

    def test_an_exact_name_or_nothing(self):
        self.assertEqual(BA.county_code(INDEX, "NM", "Dona Ana"), "35013")
        self.assertEqual(BA.county_code(INDEX, "LA", "Orleans"), "22071")
        self.assertEqual(BA.county_code(INDEX, "VA", "Charles City"), "51036")
        self.assertIsNone(BA.county_code(INDEX, "VA", "Richmont"))               # one letter off: not matched, never guessed
        self.assertIsNone(BA.county_code(INDEX, "TX", "Orleans"))                # the name of another state's county

    def test_a_county_and_a_city_of_one_name(self):
        self.assertEqual(BA.county_code(INDEX, "VA", "Richmond"), "51159")       # the plain name is the county
        self.assertEqual(BA.county_code(INDEX, "VA", "Richmond City"), "51760")  # "<name> City" is the independent city
        self.assertEqual(BA.county_code(INDEX, "VA", "Norfolk City"), "51710")
        self.assertEqual(BA.county_code(INDEX, "MO", "St Louis City"), "29510")
        self.assertEqual(BA.county_code(INDEX, "MO", "St. Louis"), "29189")


class TheRule(unittest.TestCase):
    def test_customers_are_split_evenly_and_the_largest_takes_the_county(self):
        terr = {("1", "TX"): {"Harris", "Fort Bend"}, ("2", "TX"): {"Harris"}, ("3", "TX"): {"Montgomery", "Harris"}}
        weight = {("1", "TX"): {"ERCO": 1000.0}, ("2", "TX"): {"MISO": 400.0}, ("3", "TX"): {"MISO": 100.0}}
        given, left = BA.assign_counties(terr, weight, INDEX)
        self.assertEqual(given["48201"], ("ERCO", round(500 / 950, 4), 2))        # 500 of utility 1 against 400 + 50
        self.assertEqual(given["48157"], ("ERCO", 1.0, 1))
        self.assertEqual(given["48339"], ("MISO", 1.0, 1))
        self.assertEqual(left["ties"], [])

    def test_a_utility_without_a_code_gives_nothing_and_is_counted(self):
        given, left = BA.assign_counties({("1", "TX"): {"Harris"}, ("9", "TX"): {"Harris", "Fort Bend"}}, {("1", "TX"): {"ERCO": 10.0}}, INDEX)
        self.assertEqual(list(given), ["48201"])
        self.assertEqual(left["utility_states_without_a_code"], 1)

    def test_without_a_customer_the_code_most_utilities_name_and_a_tie_is_no_assignment(self):
        terr = {("1", "TX"): {"Harris"}, ("2", "TX"): {"Harris"}, ("3", "TX"): {"Harris"}, ("4", "TX"): {"Fort Bend"}, ("5", "TX"): {"Fort Bend"}}
        weight = {("1", "TX"): {"ERCO": 0.0}, ("2", "TX"): {"ERCO": 0.0}, ("3", "TX"): {"MISO": 0.0}, ("4", "TX"): {"ERCO": 0.0}, ("5", "TX"): {"MISO": 0.0}}
        given, left = BA.assign_counties(terr, weight, INDEX)
        self.assertEqual(given["48201"], ("ERCO", None, 2))
        self.assertNotIn("48157", given)
        self.assertEqual(left["ties"], ["48157"])

    def test_a_name_that_is_not_in_the_shapes_is_listed_and_not_placed(self):
        given, left = BA.assign_counties({("1", "TX"): {"Harris", "Atlantis"}}, {("1", "TX"): {"ERCO": 10.0}}, INDEX)
        self.assertEqual(given["48201"], ("ERCO", 1.0, 1))                        # the whole of it: the unknown name takes no share
        self.assertEqual(left["county_names_not_in_the_shapes"], ["TX: Atlantis"])


def workbook(sheet, rows):
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet
    for r in rows:
        ws.append(r)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def sales(rows):
    head = [["Utility Characteristics"] + [""] * 23, [""] * 24, ["Data Year", "Utility Number", "Utility Name", "Part", "Service Type", "Data Type", "State", "Ownership", "BA Code"] + [""] * 15]
    return head + [[2025, u, f"utility {u}", part, kind, "O", st, "x", code] + [0] * 14 + [cust] for u, part, kind, st, code, cust in rows]


def made_up_zip(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("Service_Territory_2025.xlsx", workbook("Counties_States", [["Data Year", "Utility Number", "Utility Name", "Short Form", "State", "County"],
                   [2025, 1, "wires", "", "TX", "Harris"], [2025, 1, "wires", "", "TX", "Fort Bend"], [2025, 2, "coop", "", "TX", "Harris"],
                   [2025, 3, "small", "Y", "TX", "Montgomery"], [2025, 4, "marketer", "", "TX", "Montgomery"]]))
        z.writestr("Sales_Ult_Cust_2025.xlsx", workbook("States", sales([(2, "A", "Bundled", "TX", "MISO", 400), (4, "B", "Energy", "TX", "ERCO", 99999)])
                                                        + [["A note under the table that is not a row of data"]]))
        z.writestr("Delivery_Companies_2025.xlsx", workbook("Delivery Companies", sales([(1, "C", "Delivery", "TX", "ERCO", 1000)])))
        z.writestr("Short_Form_2025.xlsx", workbook("861S", [["Data Year", "Utility Number", "Utility Name", "Ownership", "State", "BA Code", "Revenue", "Sales", "Total Customers"],
                                                             [2025, 3, "small", "Municipal", "TX", "MISO", 1, 2, 30]]))


# two squares side by side and one apart, as a TopoJSON topology: the middle border is one shared arc
TOPO = {"type": "Topology", "transform": {"scale": [1, 1], "translate": [-96, 29]},
        "arcs": [[[1, 0], [0, 1]], [[1, 1], [-1, 0], [0, -1], [1, 0]], [[1, 0], [1, 0], [0, 1], [-1, 0]], [[4, 0], [1, 0], [0, 1], [-1, 0], [0, -1]]],
        "objects": {"counties": {"type": "GeometryCollection", "geometries": [
            {"type": "Polygon", "id": "48201", "properties": {"name": "Harris"}, "arcs": [[0, 1]]},
            {"type": "Polygon", "id": "48157", "properties": {"name": "Fort Bend"}, "arcs": [[2, -1]]},
            {"type": "Polygon", "id": "48339", "properties": {"name": "Montgomery"}, "arcs": [[3]]}]}}}


class TheFiles(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="erw193_")
        self.zip = os.path.join(self.dir, "f8612025.zip")
        made_up_zip(self.zip)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def args(self, **over):
        shapes, net, log = (os.path.join(self.dir, n) for n in ("counties.json", "network.json", "requests.csv"))
        with open(shapes, "w", encoding="utf-8") as f:
            json.dump(TOPO, f)
        with open(net, "w", encoding="utf-8") as f:
            json.dump({"nodes": [{"id": "ERCO", "name": "Texas"}, {"id": "PJM", "name": "PJM"}]}, f)
        sha = hashlib.sha256(open(self.zip, "rb").read()).hexdigest()
        with open(log, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=BA.LOG_COLS, lineterminator="\n")
            w.writeheader()
            w.writerow({"n": 1, "url": "https://example.gov/f8612025.zip", "status": "200", "bytes": 1, "seconds": "0.1", "retrieved_utc": "2026-10-11T07:40:07Z",
                        "sha256": over.pop("sha", sha), "saved_as": "x", "note": ""})
        a = dict(zip=self.zip, requests=log, year="2025", county_shapes=shapes, county_shapes_name="made-up shapes", county_shapes_origin="this test",
                 network=net, out=os.path.join(self.dir, "out", "ba_boundaries.json"), assignments=os.path.join(self.dir, "out", "ba_counties.csv"),
                 tolerance=0.0, digits=3, max_out_bytes=400_000, source="erw:balancing_authority_counties", vintage="2025", license_quoted="public domain words", terms_url="https://example.gov/terms")
        a.update(over)
        return types.SimpleNamespace(**a)

    def test_the_workbooks_are_read_as_the_rule_says(self):
        terr, weight = BA.read_861(self.zip, "2025")
        self.assertEqual(terr[("1", "TX")], {"Harris", "Fort Bend"})
        self.assertEqual(weight[("1", "TX")], {"ERCO": 1000.0})                   # the delivery companies' file: Texas's wires
        self.assertEqual(weight[("2", "TX")], {"MISO": 400.0})
        self.assertEqual(weight[("3", "TX")], {"MISO": 30.0})                     # the short form
        self.assertNotIn(("4", "TX"), weight)                                     # Part B, a marketer's energy: no weight

    def test_shared_borders_join_into_one_area(self):
        polys = BA.topo_polygons(TOPO)
        self.assertEqual(sorted(polys), ["48157", "48201", "48339"])
        self.assertEqual([round(polys[c].area, 6) for c in ("48201", "48157", "48339")], [1.0, 1.0, 1.0])
        from shapely.ops import unary_union
        both = unary_union([polys["48201"], polys["48157"]])
        self.assertEqual((both.geom_type, round(both.area, 6), len(both.interiors)), ("Polygon", 2.0, 0))

    def test_the_file_says_it_is_derived_and_draws_only_the_pages_grids(self):
        a = self.args()
        self.assertEqual(BA.counties(a), 0)
        f = json.load(open(a.out, encoding="utf-8"))
        p = f["provenance"]
        self.assertIs(p["derived"], True)
        self.assertEqual(p["label"], BA.DERIVED_LABEL)
        self.assertIn("not a boundary", p["label"])
        self.assertRegex(p["raw_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual((p["url"], p["retrieved_utc"], p["source"]), ("https://example.gov/f8612025.zip", "2026-10-11T07:40:07Z", "erw:balancing_authority_counties"))
        self.assertEqual([r["id"] for r in f["regions"]], ["ERCO"])               # Harris (1000 / 2 against 400) and Fort Bend
        self.assertEqual((f["regions"][0]["counties"], f["regions"][0]["counties_with_another_code"], f["regions"][0]["least_share_of_a_county"]), (2, 1, round(500 / 900, 4)))
        self.assertEqual(len(f["regions"][0]["rings"]), 1)                        # the two squares, joined
        self.assertEqual(f["shapes_without_node"], [{"code": "MISO", "name": "", "counties": 1}])     # a code that is not a grid is listed, not drawn
        self.assertEqual([n["id"] for n in f["nodes_without_shape"]], ["PJM"])
        self.assertEqual((f["matched"], f["nodes"]), (1, 2))
        k = p["counts"]
        self.assertEqual((k["counties_given_a_code"], k["counties_drawn"], k["counties_whose_utilities_name_several_codes"], k["utility_states_without_a_code"]), (3, 2, 1, 1))
        with open(a.assignments, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        self.assertTrue(lines[0].startswith("# Energy Research Warehouse (ERW)") and "DERIVED" in lines[0])
        rows = list(csv.DictReader(ln for ln in lines if not ln.startswith("#")))
        self.assertEqual([(r["county_code"], r["ba_code"], r["drawn"]) for r in rows], [("48157", "ERCO", "yes"), ("48201", "ERCO", "yes"), ("48339", "MISO", "no")])

    def test_a_zip_with_no_logged_request_is_not_built_from(self):
        a = self.args(sha="0" * 64)
        self.assertEqual(BA.counties(a), 1)
        self.assertFalse(os.path.exists(a.out))

    def test_a_result_over_the_ceiling_is_not_written(self):
        a = self.args(max_out_bytes=100)
        self.assertEqual(BA.counties(a), 1)
        self.assertFalse(os.path.exists(a.out))


class WhatIsShipped(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SITE_FILE, encoding="utf-8") as f:
            cls.file = json.load(f)
        with open(COUNTY_FILE, encoding="utf-8") as f:
            cls.head = [ln for ln in f if ln.startswith("#")]
        with open(COUNTY_FILE, encoding="utf-8") as f:
            cls.counties = {r["county_code"]: r for r in csv.DictReader(ln for ln in f if not ln.startswith("#"))}
        with open(os.path.join(ROOT, "site", "data", "grid_network.json"), encoding="utf-8") as f:
            cls.nodes = {n["id"] for n in json.load(f)["nodes"]}

    def test_the_file_is_derived_and_says_so(self):
        p = self.file["provenance"]
        self.assertIs(p["derived"], True)
        self.assertEqual(p["label"], BA.DERIVED_LABEL)
        self.assertEqual(p["raw_sha256"], "f59f6c732bf685fe0a1591b32227f5ce572dc0dfd26bb5caaeed128ac4e3a396")
        self.assertEqual(p["url"], "https://www.eia.gov/electricity/data/eia861/zip/f8612025.zip")
        self.assertTrue(p["license_quoted"].startswith("U.S. government publications are in the public domain"))
        self.assertIn("split evenly", p["rule"])
        self.assertIn("DERIVED", self.file["what"])
        self.assertIn("Census Bureau", p["county_shapes"]["origin"])

    def test_every_region_is_a_grid_of_the_page_once_and_the_counts_add_up(self):
        ids = [r["id"] for r in self.file["regions"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(set(ids) <= self.nodes)
        self.assertEqual((self.file["matched"], self.file["nodes"]), (len(ids), len(self.nodes)))
        self.assertEqual(len(self.file["nodes_without_shape"]) + len(ids), len(self.nodes))
        k = self.file["provenance"]["counts"]
        self.assertEqual(k["counties_drawn"], sum(r["counties"] for r in self.file["regions"]))
        self.assertEqual(k["counties_drawn"], sum(1 for r in self.counties.values() if r["drawn"] == "yes"))
        self.assertEqual(k["counties_given_a_code"], len(self.counties))
        self.assertEqual(k["counties_whose_utilities_name_one_code"] + k["counties_whose_utilities_name_several_codes"], k["counties_given_a_code"])
        self.assertEqual((len(ids), k["counties_drawn"], k["counties_of_the_lower_48_and_dc"], k["counties_of_the_lower_48_not_drawn"]), (44, 3067, 3107, 40))
        self.assertLessEqual(os.path.getsize(SITE_FILE), 400_000)

    def test_a_code_that_is_not_a_grid_is_listed_and_not_drawn(self):
        other = {x["code"]: x["counties"] for x in self.file["shapes_without_node"]}
        self.assertEqual(other["WACM"], 37)
        self.assertTrue(all(c not in self.nodes for c in other))
        self.assertEqual({r["drawn"] for r in self.counties.values() if r["ba_code"] == "WACM"}, {"no"})

    def test_texas_delivery_utilities_are_in_the_rule(self):
        # the first build left the delivery companies' file out, and Harris County (Houston) went to MISO
        for code, name in (("48201", "Harris"), ("48157", "Fort Bend"), ("48329", "Midland"), ("48303", "Lubbock")):
            self.assertEqual((self.counties[code]["county"], self.counties[code]["ba_code"]), (name, "ERCO"))

    def test_some_counties_anyone_can_check(self):
        for code, name, ba in (("36061", "New York", "NYIS"), ("06037", "Los Angeles", "LDWP"), ("25025", "Suffolk", "ISNE"), ("17031", "Cook", "PJM"),
                               ("47157", "Shelby", "TVA"), ("13121", "Fulton", "SOCO"), ("32003", "Clark", "NEVP"), ("12086", "Miami-Dade", "FPL")):
            self.assertEqual((self.counties[code]["county"], self.counties[code]["ba_code"]), (name, ba))

    def test_the_county_list_carries_its_source(self):
        text = "".join(self.head)
        for words in ("DERIVED", "not a published boundary", "f8612025.zip", "f59f6c732bf685fe0a1591b32227f5ce572dc0dfd26bb5caaeed128ac4e3a396", "Rule:", "docs/methods/grid_network.md"):
            self.assertIn(words, text)

    def test_the_registry_row(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), encoding="utf-8", newline="") as f:
            rows = [r for r in csv.DictReader(f) if r["source"] == self.file["provenance"]["source"]]
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["license"], rows[0]["tables"], rows[0]["first_seen"]), ("public", "", "2026-10-11"))
        self.assertIn("derived", rows[0]["publisher"])
        self.assertIn("not a published boundary", rows[0]["report"])


class ThePageAndTheNote(unittest.TestCase):
    def test_a_derived_file_is_never_drawn_without_its_label(self):
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertIn('const derived = held.state === "held" ? derivedLabel(held.file) : null;', m)
        self.assertIn('data-map-derived-label="1"', m)
        self.assertIn('data-map-derived={derived ? "1" : "0"}', m)
        # under the map, inside the frame: after the map's own block, so it covers no region
        self.assertLess(m.index("erw-flow-dash { animation"), m.index("data-map-derived-label"))
        self.assertNotIn("absolute bottom", m)
        lib = src("site", "lib", "networkMap.ts")
        self.assertIn("if (!f.provenance.derived) return null;", lib)
        self.assertIn('return f.provenance.label || "Derived map:', lib)          # a derived file with no words still says it is derived

    def test_the_legend_does_not_call_the_areas_published(self):
        n = src("site", "app", "network", "Network.tsx")
        self.assertNotIn("published boundary", n)
        self.assertIn("the line on the map says what that file is", n)

    def test_the_page_stays_in_review(self):
        self.assertIn('"/network": "review"', src("site", "lib", "release.ts"))

    def test_the_method_note_holds_the_third_pull_and_the_rule(self):
        note = src("docs", "methods", "grid_network.md")
        for words in ("**The third pull (session 193, 11 October 2026)", "Twelve requests were sent, 9,917,072 bytes", "`Location: https://atlas.eia.gov/search`", "`REG-CAL`", "`p1` to `p134`",
                      "0 of the page's 70 grids match", "`zip/f8612025.zip`", "**The derived map: counties (session 193).**", "split evenly", "44 of the page's 70 grids have an area",
                      "3,067 of the 3,107 counties", "`WACM`", "Not a boundary.", "A check that changed the rule", "Eighteen requests were left unspent"):
            self.assertIn(words, note)
        for words in ("## The map (session 180)", "The boundary file is not yet held", "**The second pull (session 180b, 10 October 2026)"):
            self.assertIn(words, note)                                             # the earlier accounts stay whole

    def test_no_em_dash(self):
        for parts in OWN:
            self.assertNotIn(chr(0x2014), src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
