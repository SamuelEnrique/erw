"""Session 718: the data machine's tables of chain 043 wired into the All grids tab. The time to connect from
interconnection_durations, recomputed here from the table where it is on this machine; capacity above the peak for every
grid from grid_peak_vs_capacity; a row whose name is a place reads its county's utilities from
utility_service_territories, kept inside the row's grid. No request, no model call."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


SCRIPT = """
const F = await import('./scripts/siting-files.mjs');
const S = await import('./lib/siting.ts');
const d = await F.dc(); const f = F.files();
const out = {};
for (const id of ['ercot:HB_HOUSTON', 'ercot:HB_HUBAVG', 'nyiso:N.Y.C.', 'nyiso:LONGIL', 'caiso:TH_SP15_GEN-APND', 'pjm:grid']) {
  const c = S.utilityCell(f, S.rowOf(f, id));
  out[id] = 'why' in c ? c : { county: c.county ? c.county.county : null, utility: c.u ? c.u.utility : null, rev: c.rev, names: c.county ? c.county.utilities.map((u) => u.name) : null, key: S.sitingStat(f, 'allgrids|utilrev|' + id, d) ?? null };
}
process.stdout.write(JSON.stringify(out));
"""


def run():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=600, encoding="utf-8")
    if r.returncode != 0 and "Unknown file extension" in r.stderr:
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


class Wired(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()

    def test_the_three_tables_are_the_files_sources(self):
        self.assertEqual(json.loads(src("site", "data", "siting", "connect.json"))["table"], "interconnection_durations")
        h = json.loads(src("site", "data", "siting", "headroom.json"))
        self.assertEqual(h["peak_capacity_table"], "grid_peak_vs_capacity")
        self.assertEqual(set(h["peak_capacity"]), {"ercot", "caiso", "nyiso", "isone", "spp", "miso", "pjm"})
        self.assertEqual(json.loads(src("site", "data", "siting", "utility.json"))["territory_table"], "utility_service_territories")

    def test_a_county_s_utilities_stay_inside_the_row_s_grid(self):
        h = self.o["ercot:HB_HOUSTON"]
        self.assertEqual(h["county"], "Harris")
        self.assertIn("CenterPoint Energy", h["names"])                 # listed: the county's wires utility
        self.assertNotEqual(h["utility"], "Entergy Texas Inc.")         # MISO's, not ERCOT's: never priced for an ERCOT row
        self.assertEqual(self.o["nyiso:N.Y.C."]["utility"], "Consolidated Edison Co-NY Inc")
        self.assertEqual(self.o["caiso:TH_SP15_GEN-APND"]["utility"], "Southern California Edison Co")
        self.assertIsNone(self.o["nyiso:LONGIL"]["key"])                 # no sales row inside NYISO: named, not priced
        self.assertIsNone(self.o["ercot:HB_HUBAVG"]["county"])           # not a place: the state's stand-in

    def test_the_durations_where_the_table_is_here(self):
        import sys
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
        import siting_page as sp
        for d in (os.path.join(ROOT, "runs", "archive_restore"), os.path.join(os.path.dirname(ROOT), "erw", "runs", "archive_restore")):
            p = os.path.join(d, "interconnection_durations.csv")
            if os.path.exists(p):
                again = sp.connect_from_durations(p)
                self.assertEqual({k: v for k, v in again.items() if k != "built"}, {k: v for k, v in json.loads(src("site", "data", "siting", "connect.json")).items() if k != "built"})
                return
        raise unittest.SkipTest("interconnection_durations is not on this machine")


if __name__ == "__main__":
    unittest.main()
