"""Session 729 (chain 062): the tracker's facilities placed by their utility. Where the tracker names a utility and that
name is one utility of eia861_utility_sales exactly (after the builder's written normalisation, UTILITY_NORM_RULES, which
lib/siting.ts applies the same), whose sales rows sit inside one grid of the tab, the facility is placed by it, after
its county and before its state; never by a fuzzy match. The three ways, the normalisation in both languages, and the
file holding nothing of the held table. No request, no model call, no database read."""
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import siting_page as sp  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


NAMES = ["Oncor Electric Delivery Company LLC", "Oncor Electric Delivery Co", "CenterPoint Energy", "Town of Concord - (MA)", "Kansas City Power & Light Co",
         "Consolidated Edison Co-NY Inc", "The Narragansett Electric Co", "Austin Energy", "PG&E", "Pacific Gas & Electric Co.", "Duke Energy Carolinas, LLC", ""]

SCRIPT = """
const S = await import('./lib/siting.ts');
import fs from 'node:fs';
const f = JSON.parse(fs.readFileSync('data/siting/facilities.json', 'utf8'));
const idx = JSON.parse(fs.readFileSync('data/datacenter/index.json', 'utf8'));
const names = %s;
const out = {
  norms: names.map((n) => S.normUtility(n)),
  nNames: Object.keys(f.utilities.names).length, rules: f.utilities.rules,
  county: S.facilitySite(f, idx, 'TX', 'Shackelford County', 'Austin Energy'),
  utility: S.facilitySite(f, idx, 'TX', '', 'Austin Energy'),
  utilityNoState: S.facilitySite(f, idx, '', '', 'Austin Energy'),
  wires: S.facilitySite(f, idx, 'TX', '', 'Oncor Electric Delivery Company LLC'),
  state: S.facilitySite(f, idx, 'TX', '', 'A Utility No Table Names'),
  none: S.facilitySite(f, idx, 'AL', '', 'A Utility No Table Names'),
  nyUtility: S.facilitySite(f, idx, '', '', 'Consolidated Edison Co-NY Inc'),
  fuzzy: S.facilitySite(f, idx, '', '', 'Austin'),
  countyFirst: S.facilitySite(f, idx, 'TX', 'Harris County', 'Entergy Texas Inc.'),
  austinGrid: f.utilities.names[S.normUtility('Austin Energy')] ?? null,
  oncorGrid: f.utilities.names[S.normUtility('Oncor Electric Delivery Company LLC')] ?? null,
};
process.stdout.write(JSON.stringify(out));
""" % json.dumps(NAMES)


def run():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
    if r.returncode != 0 and ("Unknown file extension" in r.stderr or "strip" in r.stderr):
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout)


class TheNormalisation(unittest.TestCase):
    def test_the_rules_in_python(self):
        n = sp.norm_utility
        self.assertEqual(n("Oncor Electric Delivery Company LLC"), "oncor electric delivery")
        self.assertEqual(n("Oncor Electric Delivery Co"), "oncor electric delivery")
        self.assertEqual(n("Town of Concord - (MA)"), "town of concord")
        self.assertEqual(n("Kansas City Power & Light Co"), "kansas city power and light")
        self.assertEqual(n("The Narragansett Electric Co"), "narragansett electric")
        self.assertEqual(n("Consolidated Edison Co-NY Inc"), "consolidated edison co ny")
        self.assertEqual(n("Pacific Gas & Electric Co."), "pacific gas and electric")
        self.assertEqual(n("PG&E"), "pg and e")              # an abbreviation is not the full name: no match, by design
        self.assertEqual(n(""), "")
        self.assertEqual(len(sp.UTILITY_NORM_RULES), 8)


class TheThreeWays(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()

    def test_both_languages_normalise_alike(self):
        self.assertEqual(self.o["norms"], [sp.norm_utility(n) for n in NAMES])
        self.assertEqual(self.o["rules"], sp.UTILITY_NORM_RULES)

    def test_the_file_maps_names_to_one_grid(self):
        self.assertGreater(self.o["nNames"], 1000)
        self.assertEqual(self.o["austinGrid"]["grid"], "ercot")
        # Oncor has no sales row and serves counties placed in ERCOT and in SPP: left out, by the written rule
        self.assertIsNone(self.o["oncorGrid"])

    def test_county_then_utility_then_state_then_none(self):
        o = self.o
        self.assertEqual(o["county"]["how"], "county")                       # the county places it before the utility
        self.assertEqual((o["utility"]["how"], o["utility"]["grid"]), ("utility", "ercot"))
        self.assertEqual((o["utilityNoState"]["how"], o["utilityNoState"]["grid"]), ("utility", "ercot"))   # no state needed
        self.assertEqual(o["state"]["how"], "state")                         # an unknown utility falls to the state
        self.assertIn("is not one utility of EIA-861", o["state"]["why"])
        self.assertIsNone(o["none"])                                         # no county, no utility, no state in one grid
        self.assertEqual((o["nyUtility"]["how"], o["nyUtility"]["grid"]), ("utility", "nyiso"))
        self.assertIsNone(o["fuzzy"])                                        # "Austin" alone is not an exact name
        self.assertEqual(o["wires"]["how"], "state")                         # Oncor: not placed by name, so Texas places it
        # Harris County's utilities bill in two grids, so the county does not place it; the named utility (Entergy Texas,
        # MISO) places it before the state would (ERCOT): the way the chain asks, the utility before the state
        self.assertEqual((o["countyFirst"]["how"], o["countyFirst"]["grid"]), ("utility", "miso"))


class TheTrackerAndTheFile(unittest.TestCase):
    def test_the_tracker_passes_the_utility_and_labels_the_way(self):
        b = src("site", "app", "datacenters", "Body.tsx")
        self.assertIn('x.utility ?? ""),', b)
        t = src("site", "app", "datacenters", "DatacentersTable.tsx")
        self.assertIn('f.siting.how === "utility" ? "its utility"', t)
        self.assertIn("data-facility-siting={f.siting.how}", t)

    def test_the_file_holds_nothing_of_the_held_table(self):
        raw = src("site", "data", "siting", "facilities.json")
        f = json.loads(raw)
        self.assertEqual(set(f), {"built", "tables", "year", "state_share", "states", "counties", "county_rows", "utilities"})
        self.assertNotIn("datacenter_facilities", f["tables"])
        self.assertNotIn("datacenter:", raw)
        self.assertNotIn("FACILITIES_TABLE", src("warehouse", "derived", "siting_page.py"))
        for n, v in f["utilities"]["names"].items():
            self.assertEqual(n, sp.norm_utility(n), n)      # every key is already normalised
            self.assertIn(v["grid"], sp.BA_GRIDS.values())

    def test_no_em_dash(self):
        for p in (("site", "lib", "siting.ts"), ("warehouse", "derived", "siting_page.py"), ("site", "app", "datacenters", "Body.tsx"), ("site", "app", "datacenters", "DatacentersTable.tsx")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
