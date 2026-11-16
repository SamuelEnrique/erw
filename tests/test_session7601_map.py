"""Session 7601 (chain 305, part B): the project map (/map) at the done line.

The five parts, each held here: the tool's note (docs/methods/map.md); the replication (replication/map/: the page's
figures by its own functions, and again from EIA's own workbook and the live set's rows); the cross-check against EIA's
Electric Power Monthly; the decisions block on the page; and the faults the work found
(docs/reviews/map-faults-2026-11-16.md). The rows the replication reads are not in git (EIA's workbook is 14 MB; the
tracker's rows are held), so what runs here is the replication's own rules on rows made up for the test, and the
committed figures.
"""
import csv
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "map")
NODE = shutil.which("node")
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REP, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TheReplicationsOwnRules(unittest.TestCase):
    """replicate.py on rows made for the test: no file of EIA's, no row of the live set."""

    @classmethod
    def setUpClass(cls):
        cls.r = load("replicate")

    def test_every_technology_of_eias_has_one_group(self):
        r = self.r
        self.assertEqual(len(r.TECH_GROUP), 27)
        self.assertEqual(set(r.TECH_GROUP.values()), {"solar", "wind", "storage", "natural_gas", "coal", "nuclear", "hydro", "geothermal", "petroleum", "biomass", "other"})
        # the cross-check names the same 27 technologies, in EIA's words
        self.assertEqual(sorted(load("crosscheck").SAME), sorted(r.TECH_GROUP))

    def test_a_place_on_the_drawing(self):
        on = self.r.on_drawing
        self.assertTrue(on(30.2672, -97.7431), "Austin, Texas")
        self.assertTrue(on(61.2181, -149.9003), "Anchorage, in Alaska's box")
        self.assertTrue(on(21.3069, -157.8583), "Honolulu, in Hawaii's box")
        self.assertTrue(on(47.6062, -122.3321), "Seattle")
        self.assertTrue(on(25.7617, -80.1918), "Miami")
        self.assertFalse(on(18.4655, -66.1057), "San Juan: Puerto Rico has no place on the drawing")
        self.assertFalse(on(13.4443, 144.7937), "Guam")
        self.assertFalse(on(None, -97.0), "no latitude")

    def test_an_address_is_read_as_the_note_says(self):
        r = self.r
        opts = {"kind": r.KINDS, "grid": r.GRIDS, "tech": r.TECHS, "status": ["operating", "p", "u"], "state": ["na", "CA", "TX"]}
        c = r.choice_of("?kind=operating,planned&grid=ercot&tech=solar,battery&state=TX,CA&min=100&max=500", opts)
        self.assertEqual((c["kind"], c["grid"], c["tech"], c["state"], c["min"], c["max"]), ({"operating", "planned"}, {"ercot"}, {"solar", "battery"}, {"TX", "CA"}, 100.0, 500.0))
        self.assertIsNone(r.choice_of("", opts)["kind"], "absent: every one")
        self.assertEqual(r.choice_of("?kind=none", opts)["kind"], set(), "none: none")
        self.assertIsNone(r.choice_of("?grid=nowhere", opts)["grid"], "a list none of whose slugs is known: every one")
        self.assertEqual(r.choice_of("?grid=nowhere,ercot", opts)["grid"], {"ercot"}, "a slug not known is passed over")
        self.assertIsNone(r.choice_of("?kind=operating,planned,queue,datacenter", opts)["kind"], "every option chosen is no choice")
        self.assertIsNone(r.choice_of("?max=abc", opts)["max"], "letters are no size")

    def test_the_figures_of_a_view_on_six_rows(self):
        r = self.r
        rows = [r.Row("1:A", "operating", "ercot", "solar", "operating", "TX", 100.0, 30.0, -97.0), r.Row("1:B", "operating", "ercot", "battery", "operating", "TX", 0.4, 30.0, -97.0),
                r.Row("2:A", "planned", "outside", "wind", "u", "PR", 50.5, 18.2, -66.5), r.Row("q:1", "queue", "ercot", "queue_storage", "q-active", "TX", 250.26, None, None),
                r.Row("q:2", "queue", "spp", "hybrid", "q-none", "", None, 36.0, -97.5), r.Row("d:1", "datacenter", "none", "datacenter", "dc-planned", "VA", None, 38.9, -77.4)]
        opts = {"kind": r.KINDS, "grid": r.GRIDS, "tech": r.TECHS, "status": ["operating", "u", "q-active", "q-none", "dc-planned"], "state": ["na", "PR", "TX", "VA"]}
        f, chosen = r.figures_of("", rows, opts, opts["status"])
        self.assertEqual((f["(no choice)|rows"], f["(no choice)|units"], f["(no choice)|queue"], f["(no choice)|datacenters"]), (6, 3, 2, 1))
        self.assertAlmostEqual(f["(no choice)|units_mw"], 150.9)
        self.assertAlmostEqual(f["(no choice)|queue_mw"], 250.3, msg="a queue position's megawatts are kept to one decimal")
        self.assertEqual((f["(no choice)|datacenters_with_mw"], f["(no choice)|status|q-none|with_mw"]), (0, 0))
        self.assertNotIn("(no choice)|status|q-none|mw", f, "a status none of whose rows states megawatts has no sum")
        self.assertEqual((f["(no choice)|drawn"], f["(no choice)|not_drawn"]), (4, 2), "Puerto Rico and a row with no location are not drawn")
        g, _ = r.figures_of("?min=100", rows, opts, opts["status"])
        self.assertEqual(g["?min=100|rows"], 2, "both ends are counted in, and a row with no megawatts is left out when a size is asked for")
        h, _ = r.figures_of("?state=na", rows, opts, opts["status"])
        self.assertEqual(h["?state=na|rows"], 1)
        k, _ = r.figures_of("?kind=operating", rows, opts, opts["status"])
        self.assertNotIn("?kind=operating|tech|wind|planned|rows", k, "the table by technology holds the kinds chosen")

    def test_a_units_fields_from_a_line_of_the_workbook(self):
        r = self.r
        import tempfile
        tmp = tempfile.mkdtemp(prefix="erw7601_")
        try:
            with open(os.path.join(tmp, "units.csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# made for the test\n")
                w = csv.writer(f)
                w.writerow(["sheet", "kind", "plant_id", "generator_id", "plant_name", "plant_state", "nameplate_mw", "technology", "prime_mover", "status", "balancing_authority", "latitude", "longitude", "net_summer_mw", "year", "month"])
                w.writerow(["Operating", "operating", "10", "NA", "A battery", "TX", "100.5", "Batteries", "BA", "(OP) Operating", "ERCO", "30.1", "-97.2", "100", "2024", "5"])
                w.writerow(["Operating", "operating", "11", "1", "Pumped", "CA", "300", "Hydroelectric Pumped Storage", "PS", "(SB) Standby", "CISO", "36", "-119", "290", "1980", "1"])
                w.writerow(["Planned", "planned", "12", "2", "A wind farm", "PR", "40", "Onshore Wind Turbine", "WT", "(TS) Construction complete, but not yet in commercial operation", "NA", "18.1", "-66.2", "40", "2027", "3"])
                w.writerow(["Planned", "planned", "13", "3", "No technology", "AK", "2", "", "IC", "(P) Planned for installation, but regulatory approvals not initiated", "", "61", "-150", "2", "2028", "1"])
            u = r.read_units(tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual([(x.id, x.kind, x.grid, x.tech, x.status, x.state, x.tenths) for x in u],
                         [("10:NA", "operating", "ercot", "battery", "operating", "TX", 1005), ("11:1", "operating", "caiso", "storage", "operating", "CA", 3000),
                          ("12:2", "planned", "outside", "wind", "ts", "PR", 400), ("13:3", "planned", "outside", "unknown", "p", "AK", 20)])


class TheCommittedFigures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(REP, "page_figures.json"), encoding="utf-8") as f:
            cls.j = json.load(f)

    def test_the_units_are_all_inside_and_every_other_difference_is_named(self):
        t = self.j["tally"]
        self.assertEqual(t["units_alone"], t["units_alone_inside"], "every figure of the generating units is inside half a megawatt or half a row")
        self.assertGreaterEqual(t["units_alone"], 3700)
        self.assertEqual((t["outside"], t["one_side"]), (0, 0))
        self.assertEqual(t["figures"], t["inside"] + t["named"])
        self.assertEqual(self.j["views"], 123)
        named = [f for f in self.j["figures"] if not f["inside"]]
        self.assertEqual(len(named), t["named"])
        self.assertTrue(all(f.get("named") for f in named))
        self.assertTrue(all("queue" in f["key"] or "|rows" in f["key"] or "drawn" in f["key"] or "q-" in f["key"] or "without_mw" in f["key"] or "not_placed" in f["key"] for f in named), "a named difference is one the queue's rows can move")

    def test_the_rows_side_by_side(self):
        by = {r["kind"]: r for r in self.j["rows"]}
        for kind in ("operating", "planned"):
            self.assertEqual(by[kind]["in_both_with_a_field_that_differs"], 0)
            self.assertEqual((by[kind]["only_in_the_rows_read"], by[kind]["only_on_the_page"]), (1, 1), "one unit a kind differs in its id alone: EIA's generator id is the text NA")
        self.assertEqual(by["datacenter"]["rows_read"], by["datacenter"]["in_both"])
        self.assertEqual(self.j["eia_month"], "2026-09")

    def test_the_csv_holds_the_same_figures(self):
        with open(os.path.join(REP, "page_figures.csv"), encoding="utf-8", newline="") as f:
            head = f.readline()
            rows = list(csv.DictReader(f))
        self.assertTrue(head.startswith("# ERW replication of /map"))
        self.assertEqual(len(rows), self.j["tally"]["figures"])
        self.assertEqual(sum(1 for r in rows if r["inside"] == "no"), self.j["tally"]["named"])

    def test_no_row_of_a_held_table_is_committed(self):
        tracked = subprocess.run(["git", "ls-files", "replication/map"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        self.assertIn("replication/map/rows/.gitignore", tracked)
        self.assertEqual([p for p in tracked if p.startswith("replication/map/rows/") and not p.endswith(".gitignore")], [])
        text = src("replication", "map", "page_figures.json")
        self.assertNotIn("entity_id", text)
        self.assertNotRegex(text, r"https?://(?!www\.eia\.gov)", "no story's address, no source but EIA's")

    def test_the_do_file_says_the_headline_figures(self):
        do = src("replication", "map", "replicate.do")
        fig = {f["key"]: f["page"] for f in self.j["figures"]}
        for want in (f"{fig['file|counts|operating']:,}", f"{fig['file|counts|operating_mw']:,.1f}", f"{fig['file|counts|planned']:,}", f"{fig['file|counts|planned_mw']:,.1f}", f"{fig['file|counts|batteries']:,}"):
            self.assertIn(want, do)
        self.assertIn("This do-file has not been run", do)

    def test_the_cross_check_is_eias_table_as_read(self):
        with open(os.path.join(REP, "crosscheck_epm.csv"), encoding="utf-8", newline="") as f:
            head = f.readline()
            epm = list(csv.DictReader(f))
        self.assertIn("Electric Power Monthly, Table 6.1", head)
        self.assertIn("https://www.eia.gov/electricity/monthly/", head)
        self.assertGreaterEqual(len(epm), 30)
        with open(os.path.join(REP, "crosscheck.csv"), encoding="utf-8", newline="") as f:
            f.readline()
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 28, "27 technologies and their total")
        same = [r for r in rows[:-1] if abs(float(r["net_summer_less_eia_mw"])) < 0.05]
        self.assertEqual(len(same), 18)
        total = rows[-1]
        self.assertEqual(total["operating_units_on_the_map"], "28712")
        note = src("docs", "methods", "map.md")
        for cell in (total["nameplate_mw_on_the_map"], total["net_summer_mw_same_units_50_states_and_dc"], total["net_summer_less_eia_mw"]):
            self.assertIn(f"{float(cell):,.1f}", note, "the note's section 12 quotes the cross-check's own totals")


class TheNoteAndThePage(unittest.TestCase):
    def test_the_decisions_are_the_notes_and_none_is_grey(self):
        page = src("site", "app", "map", "Decisions.tsx")
        keys = re.findall(r'\{ key: "([a-z-]+)", session: "', page)
        # session 7537 (the read of 16 November): a twelfth, the distance from a point
        self.assertEqual(len(keys), 12)
        self.assertEqual(len(set(keys)), 12)
        self.assertEqual(page.count("def: "), 13)       # the type's field and twelve decisions
        self.assertEqual(page.count("source: "), 13)
        self.assertNotIn("text-muted", page, "what explains a line is in its hover: no grey text")
        self.assertIn("<strong>Default:</strong>", page)
        self.assertIn("<strong>Source:</strong>", page)
        note = src("docs", "methods", "map.md")
        table = note.split("## 14. The decisions of the tool")[1].split("## 15.")[0]
        self.assertEqual(len(re.findall(r"(?m)^\| [A-Z]", table)) - 1, 12, "the note's table holds the same twelve choices")
        self.assertIn("<MapDecisions />", src("site", "app", "map", "page.tsx"))

    def test_the_note_has_its_fifteen_sections_and_points_to_the_tables_notes(self):
        note = src("docs", "methods", "map.md")
        self.assertEqual(re.findall(r"(?m)^## (\d+)\. ", note), [str(i) for i in range(1, 16)])
        for other in ("energy_projects.md", "eia860m_operating_generators.md", "eia860m_planned_generators.md", "datacenter_facilities.md", "resources.md"):
            self.assertIn(other, note)
            self.assertTrue(os.path.isfile(os.path.join(ROOT, "docs", "methods", other)), other)
        tally = json.loads(src("replication", "map", "page_figures.json"))["tally"]
        self.assertIn(f"{tally['figures']:,} figures", note)
        self.assertIn(f"{tally['units_alone_inside']:,} of {tally['units_alone']:,}", note)

    def test_a_card_and_a_hover_write_megawatts_the_same_way(self):
        lib = src("site", "lib", "projectmap.ts")
        self.assertIn('{ key: "mw", label: "MW", value: mw === null ? "not stated" : `${one(mw)} MW${q ? " requested" : ""}` },', lib)
        self.assertIn('`${one(mw)} MW${kind === KIND.queue ? " requested" : ""}`', src("site", "app", "map", "ProjectMap.tsx"), "the hover's own line")


class TheFaultsFile(unittest.TestCase):
    def test_every_row_is_fixed_requested_or_written_for_a_ruling(self):
        doc = src("docs", "reviews", "map-faults-2026-11-16.md")
        rows = re.findall(r"(?m)^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| (fixed|data machine|ruling) \|$", doc)
        self.assertEqual([int(r[0]) for r in rows], list(range(1, 9)))
        for n, _, _, fix, state in rows:
            if state == "data machine":
                self.assertRegex(fix, r"Request row \d+", f"row {n}")
            if state == "ruling":
                self.assertIn("Default taken", fix, f"row {n}")
        for shot in ("map-top-1280.png", "map-top-390.png", "map-unit-card-1280.png", "map-decisions-390.png", "map-queues-390.png", "map-resources-1280.png"):
            self.assertTrue(os.path.isfile(os.path.join(ROOT, "docs", "reviews", "map-done-line", shot)), shot)

    def test_no_dash(self):
        for parts in (("docs", "methods", "map.md"), ("docs", "reviews", "map-faults-2026-11-16.md"), ("site", "app", "map", "Decisions.tsx"), ("site", "scripts", "map-figures.mjs"),
                      ("replication", "map", "replicate.py"), ("replication", "map", "fetch_rows.py"), ("replication", "map", "crosscheck.py"), ("replication", "map", "replicate.do"),
                      ("tests", "test_session7601_map.py")):
            text = src(*parts)
            self.assertNotIn(EM_DASH, text, parts[-1])
            self.assertNotIn(EN_DASH, text, parts[-1])


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePagesOwnFigures(unittest.TestCase):
    def test_the_figures_script_runs_and_agrees_with_the_files_own_counts(self):
        r = subprocess.run([NODE, "--no-warnings", "scripts/map-figures.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        j = json.loads(r.stdout)
        fig = {f["key"]: f["page"] for f in j["figures"]}
        self.assertEqual(j["views"], 123)
        self.assertEqual(fig["(no choice)|units"], fig["file|counts|units"])
        self.assertEqual(fig["(no choice)|queue"], fig["file|counts|queue"])
        self.assertEqual(fig["(no choice)|datacenters"], fig["file|counts|datacenter"])
        self.assertEqual(fig["(no choice)|rows"], fig["file|counts|rows"])
        self.assertEqual(fig["?kind=none|rows"], 0)
        self.assertEqual(fig["(no choice)|drawn"] + fig["(no choice)|not_drawn"], fig["(no choice)|rows"])


if __name__ == "__main__":
    unittest.main()
