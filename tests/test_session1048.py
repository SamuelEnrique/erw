"""Session 1048 (chain 072): an ERCOT node's county and load zone, from ercot_node_places (public: the county and zone
ERCOT's CDR gives every unit at the node's station), in the node list (two columns that sort, filter and go into the
download) and the node's panel, with ERCOT's transmission project phases in its county (ercot_transmission_projects,
public). A node the table does not place is blank and sorts last; nothing is placed by a guess. The builder's functions
are read on small files written here; the tab's file holds what the builder wrote from the tables. No request, no model
call."""
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load(name, *parts):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PLACES = ("# a test file\n# Placed 2 of 4 resource nodes; left out: 1 whose station no CDR unit carries, 1 whose units disagree.\n"
          "entity_id,entity_type,name,geo,x_station,x_county,x_zone,retrieved_at\n"
          "ercot_node:A_ALL,generator,A_ALL,US-TX,A,FAYETTE,SOUTH,2026-10-23T06:46:36Z\n"
          "ercot_node:B_RN,generator,B_RN,US-TX,B,HARRIS,HOUSTON,2026-10-23T06:46:36Z\n")
PROJECTS = ("# a test file\n# Workbook: TPIT AS OF 7/13/2026; 4 project phases\n"
            "event_id,event_date,status,x_title,x_kv,x_owner,x_county_start,x_county_end\n"
            "ercot_tpit:1:1,2028-01-01,future,Line one,138,LCRATSC,Fayette,Bastrop\n"
            "ercot_tpit:2:2,2027-06-01,planned,Line two,345,LCRATSC,Bastrop,Fayette\n"
            "ercot_tpit:3:3,2020-01-01,completed,Old line,69,LCRATSC,Fayette,Fayette\n"
            "ercot_tpit:4:4,9999-01-01,future,No date,138,CNP,Harris,\n")


class Builder(unittest.TestCase):
    def setUp(self):
        self.m = load("siting_page_1048", "warehouse", "derived", "siting_page.py")
        self.d = tempfile.TemporaryDirectory()
        self.lp, self.tp = os.path.join(self.d.name, "places.csv"), os.path.join(self.d.name, "projects.csv")
        with open(self.lp, "w", encoding="utf-8") as f:
            f.write(PLACES)
        with open(self.tp, "w", encoding="utf-8") as f:
            f.write(PROJECTS)

    def tearDown(self):
        self.d.cleanup()

    def test_places_are_the_table_s_and_its_own_words(self):
        places, meta = self.m.node_places(self.lp)
        self.assertEqual(places, {"A_ALL": ("FAYETTE", "SOUTH"), "B_RN": ("HARRIS", "HOUSTON")})
        self.assertEqual((meta["table"], meta["placed"]), ("ercot_node_places", 2))
        self.assertTrue(meta["words"].startswith("Placed 2 of 4"))

    def test_a_county_s_projects_by_status_and_the_earliest_date(self):
        p = self.m.county_projects(self.tp, {"FAYETTE", "HARRIS", "TRAVIS"})
        f = p["counties"]["FAYETTE"]
        # either end in the county; the one with both ends counted once
        self.assertEqual((f["future"], f["planned"], f["completed"], f["cancelled"]), (1, 1, 1, 0))
        self.assertEqual((f["next"]["date"], f["next"]["title"], f["next"]["kv"]), ("2027-06-01", "Line two", "345"))
        # ERCOT's 9999-01-01 is no date: no earliest date
        self.assertIsNone(p["counties"]["HARRIS"]["next"])
        self.assertNotIn("TRAVIS", p["counties"])
        self.assertEqual(p["workbook"], "TPIT AS OF 7/13/2026")


class TheFile(unittest.TestCase):
    def test_the_tab_file_places_what_the_table_places(self):
        n = json.loads(src("site", "data", "siting", "nodes.json"))
        pl = n["places"]
        self.assertEqual(pl["table"], "ercot_node_places")
        placed = [k for k in n["nodes"] if "county" in k]
        self.assertEqual(len(placed), pl["matched"])
        self.assertEqual(pl["of"], len(n["nodes"]))
        self.assertTrue(all(k.get("zone") in {"COASTAL", "HOUSTON", "NORTH", "PANHANDLE", "SOUTH", "WEST"} for k in placed))
        self.assertTrue(all(("county" in k) == ("zone" in k) for k in n["nodes"]))
        # every county of a placed node with projects is the projects file's, upper case as the places table writes it
        self.assertTrue(set(n["projects"]["counties"]) <= {k["county"] for k in placed})
        self.assertEqual(n["projects"]["table"], "ercot_transmission_projects")


SCRIPT = """
const S = await import('./lib/siting.ts');
const rows = [{ node: 'A', county: 'HARRIS', zone: 'HOUSTON' }, { node: 'B', county: '', zone: '' }, { node: 'C', county: 'BEXAR', zone: 'SOUTH' }];
const c = S.nodeColumns(rows.map((r) => ({ ...r, id: `ercot:${r.node}`, cls: 'solar', types: '', per: null, basis: null, days: 0, due: 0, allin: null, why: '', spread: null, swing: null })));
process.stdout.write(JSON.stringify({ sorts: S.NODE_SORTS, county: S.sortNodes(rows, 'county', 'asc').map((r) => r.node),
  zoneDesc: S.sortNodes(rows, 'zone', 'desc').map((r) => r.node), back: S.nodeRowsOf(c).map((r) => [r.county, r.zone]) }));
"""


def run():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
    if r.returncode != 0 and "Unknown file extension" in r.stderr:
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


class TheList(unittest.TestCase):
    def test_county_and_zone_sort_with_the_unplaced_last(self):
        o = run()
        self.assertEqual(o["sorts"][:4], ["node", "cls", "county", "zone"])
        self.assertEqual(o["county"], ["C", "A", "B"])
        self.assertEqual(o["zoneDesc"], ["C", "A", "B"])          # blank last either way
        self.assertEqual(o["back"], [["HARRIS", "HOUSTON"], ["", ""], ["BEXAR", "SOUTH"]])

    def test_the_list_filters_and_downloads_them(self):
        v = src("site", "app", "cost-of-power", "AllGridsNodes.tsx")
        for s in ('data-node-zone="1"', 'data-node-county="1"', 'q.set("ncounty", co)', 'q.set("nzone", zo)',
                  '"node,class,county,zone,energy_usd_mwh,', "r.node, r.cls, r.county, r.zone,"):
            self.assertIn(s, v)

    def test_the_panel_names_the_place_or_says_it_is_not_placed(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn('data-node-place="1"', v)
        self.assertIn('words="not placed"', v)
        self.assertIn("allgrids|nodeprojects|${id}|future", v)
        self.assertIn("county={q.ncounty", v)
        self.assertNotIn("No table of the warehouse places an ERCOT settlement point in a county", v)
        s = src("site", "lib", "siting.ts")
        self.assertIn('p[1] === "nodeprojects"', s)


class TheReplication(unittest.TestCase):
    def test_the_county_s_phases_counted_again(self):
        m = load("repl_siting_1048", "warehouse", "replication", "siting.py")
        places = [{"entity_id": "ercot_node:X_ALL", "x_county": "FAYETTE"}]
        rows = [{"status": "future", "x_county_start": "Fayette", "x_county_end": "Bastrop"},
                {"status": "future", "x_county_start": "Fayette", "x_county_end": "Fayette"},
                {"status": "planned", "x_county_start": "Lee", "x_county_end": "Fayette"},
                {"status": "cancelled", "x_county_start": "Fayette", "x_county_end": ""},
                {"status": "completed", "x_county_start": "Lee", "x_county_end": "Lee"}]
        got = m.project_figures(places, rows, node="X_ALL")
        self.assertEqual(got, {"allgrids|nodeprojects|ercot:X_ALL|future": 2.0, "allgrids|nodeprojects|ercot:X_ALL|planned": 1.0,
                               "allgrids|nodeprojects|ercot:X_ALL|completed": 0.0})
        self.assertEqual(m.project_figures(places, rows, node="Y_ALL"), {})


if __name__ == "__main__":
    unittest.main()
