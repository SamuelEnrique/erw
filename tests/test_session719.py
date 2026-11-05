"""Session 719: the datacenter tracker joins the All grids tab. A tracked facility is placed by its county where the
county's utilities bill inside one grid (the county's own row where the tab has one), else by its state where 85
percent or more of its retail sales are inside one grid, else not at all; the tracker never names a node. The link sets
the facility's MW as the load and its row as A. datacenter_facilities is held whole (license needed since 21 October
2026), so the site file is built from public tables only (every county of the service territories, every state) and
holds nothing of the tracker's rows; the tab names no facility and reads no database (session 716's rule). No request,
no model call."""
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
const S = await import('./lib/siting.ts');
import fs from 'node:fs';
const f = JSON.parse(fs.readFileSync('data/siting/facilities.json', 'utf8'));
const idx = JSON.parse(fs.readFileSync('data/datacenter/index.json', 'utf8'));
const out = {
  shackelford: S.facilitySite(f, idx, 'TX', 'Shackelford County'),
  harris: S.facilitySite(f, idx, 'TX', 'Harris County'),
  texasNoCounty: S.facilitySite(f, idx, 'TX', ''),
  california: S.facilitySite(f, idx, 'CA', ''),
  alabama: S.facilitySite(f, idx, 'AL', 'Jackson County'),
  ny: S.facilitySite(f, idx, 'NY', 'Rockland'),
  pa: S.facilitySite(f, idx, 'PA', ''),
};
out.href = S.facilityHref(out.shackelford, 1400);
out.big = S.facilityHref(out.shackelford, 50000);
process.stdout.write(JSON.stringify(out));
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


class Join(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()

    def test_by_county_then_by_state_then_none(self):
        # Harris County's utilities bill in ERCOT and MISO (Entergy Texas): the state places it in ERCOT, and the tab's own
        # row for Harris (LZ_HOUSTON) is ERCOT's, so it is the row
        self.assertEqual((self.o["harris"]["grid"], self.o["harris"]["row"], self.o["harris"]["how"]), ("ercot", "ercot:LZ_HOUSTON", "state"))
        self.assertEqual(self.o["shackelford"]["grid"], "ercot")
        self.assertEqual(self.o["texasNoCounty"]["how"], "state")     # 88 percent of Texas's sales are inside ERCOT
        self.assertIsNone(self.o["california"])                       # 79 percent inside CAISO: under the 85 percent rule
        self.assertIsNone(self.o["alabama"])                          # TVA's: no grid of the tab
        self.assertEqual(self.o["pa"]["row"], "pjm:grid")

    def test_the_link_sets_the_load_and_a(self):
        self.assertIn("mw=1400", self.o["href"])
        self.assertIn("a=ercot%3A", self.o["href"])
        self.assertNotIn("fac=", self.o["href"])                      # no facility in the address
        self.assertIn("mw=10000", self.o["big"])                      # bounded as the tab bounds the size

    def test_the_tracker_draws_the_link_and_the_tab_names_no_facility(self):
        t = src("site", "app", "datacenters", "DatacentersTable.tsx")
        self.assertIn("data-facility-siting={f.siting.how}", t)
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertNotIn("@/lib/supabase", v)
        self.assertNotRegex(v, r"\bfac\b")                           # no facility read from the address
        self.assertIn('"/cost-of-power?view=allgrids&mw=1400&a=ercot%3ALZ_NORTH"', src("site", "scripts", "check-values.mjs"))

    def test_the_file_holds_nothing_of_the_held_table(self):
        raw = src("site", "data", "siting", "facilities.json")
        f = json.loads(raw)
        self.assertEqual(set(f), {"built", "tables", "year", "state_share", "states", "counties", "county_rows"})
        self.assertNotIn("datacenter_facilities", f["tables"])
        self.assertNotIn("datacenter:", raw)
        self.assertGreater(len(f["counties"]), 1000)                  # every county in one grid, not the tracker's counties
        self.assertNotIn("FACILITIES_TABLE", src("warehouse", "derived", "siting_page.py"))   # the builder never reads it


if __name__ == "__main__":
    unittest.main()
