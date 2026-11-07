"""Session 2244 (chain 156): the datacenter tracker by grid, the facilities against what each grid holds
(site/lib/dcrollups.ts gridLoads and shareOfPeak, site/app/datacenters/FacilitiesVsGrid.tsx).

Node runs the functions on rows shaped as the live set serves datacenter_facilities; the component's source is read
for the owner's rule on licensed figures (the hold's words with a footnote, never an empty cell) and the reserve
margin's placeholder where no source the ERW reads holds one.
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def fac(i, state, mw, status, **x):
    return {"entity_id": f"datacenter:{i}", "capacity_mw": mw, "status": status, "operator": "x", "extra": {"state": state, **x}}


ROWS = [fac(1, "TX", 1200, "planned"), fac(2, "TX", 222, "under_construction"), fac(3, "TX", 50, "operating"),
        fac(4, "TX", None, "planned"), fac(5, "TX", 900, "withdrawn"), fac(6, "LA", None, "planned"), fac(7, "", 100, "planned")]


class GridLoads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = node("const R = await import('./lib/dcrollups.ts');"
                     f"const ls = R.gridLoads({json.dumps(ROWS)});"
                     "const e = ls.find((l) => l.grid === 'ERCOT'), m = ls.find((l) => l.grid === 'MISO');"
                     "console.log(JSON.stringify({ls, share: R.shareOfPeak(e, 83597), none: R.shareOfPeak(m, 120000),"
                     " nopeak: R.shareOfPeak(e, null), key: R.gridKey('share_of_peak', 'ERCOT')}));")

    def test_the_counted_facilities_by_status(self):
        e = next(x for x in self.r["ls"] if x["grid"] == "ERCOT")
        self.assertEqual((e["facilities"], e["withMw"], e["without"]), (4, 3, 1))   # the withdrawn one is not counted
        self.assertEqual((e["planned"], e["underConstruction"], e["operating"]), (1200, 222, 50))
        self.assertEqual({x["grid"] for x in self.r["ls"]}, {"ERCOT", "MISO"})     # no US state: no grid, not counted

    def test_the_share_of_the_peak(self):
        self.assertEqual(self.r["share"], round(1000 * 1422 / 83597) / 10)
        self.assertIsNone(self.r["none"])     # MISO's facilities state no MW
        self.assertIsNone(self.r["nopeak"])
        self.assertEqual(self.r["key"], "dcgrid|share_of_peak|ERCOT")


class TheSources(unittest.TestCase):
    def read(self, *p):
        with open(os.path.join(SITE, *p), encoding="utf-8") as f:
            return f.read()

    def test_the_owners_rule_for_licensed_figures(self):
        s = self.read("app", "datacenters", "FacilitiesVsGrid.tsx")
        self.assertIn("license needed<sup>1</sup>", s)   # a held cell says so, with its footnote
        self.assertIn("not held<sup>2</sup>", s)          # a reserve margin no source holds says so too
        self.assertIn("NERC&apos;s assessments of the others are not read while NERC&apos;s terms are not.", s)
        for k in ("peak_mw", "capacity_mw", "reserve_margin", "share_of_peak", "planned", "operating"):
            self.assertIn(f'gridKey("{k}", g)', s)
        self.assertNotIn("—", s)

    def test_the_page_and_the_check(self):
        self.assertIn("<FacilitiesVsGrid read={facs} held={facsHeld} />", self.read("app", "datacenters", "page.tsx"))
        self.assertIn('if (p[0] === "dcgrid") {', self.read("scripts", "check-values.mjs"))


if __name__ == "__main__":
    unittest.main()
