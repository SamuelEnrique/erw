"""Session 708: the utility on the All grids tab (docs/methods/siting.md). For each row's state inside its grid, the
utility selling most to industry in the newest EIA-861 year, its industrial revenue per MWh and its sales growth,
recomputed here from the table where it is on this machine; Delivery rows never chosen; ERCOT nodes and PJM say why.
No request, no model call."""
import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
MAIN = os.path.join(os.path.dirname(ROOT), "erw")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import siting_page as sp  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


SCRIPT = """
const F = await import('./scripts/siting-files.mjs');
const S = await import('./lib/siting.ts');
const d = await F.dc(); const f = F.files();
const out = {};
for (const id of ['ercot:HB_HUBAVG', 'ercot:7RNCHSLR_ALL', 'caiso:TH_SP15_GEN-APND', 'isone:.Z.MAINE', 'isone:.H.INTERNAL_HUB', 'spp:SPPSOUTH_HUB', 'miso:TEXAS.HUB', 'pjm:grid']) {
  const c = S.utilityCell(f, S.rowOf(f, id));
  out[id] = 'why' in c ? c : { state: c.state, ba: c.ba, utility: c.u.utility, rev: c.rev, growth: c.growth, key: S.sitingStat(f, 'allgrids|utilrev|' + id, d) ?? null, gkey: S.sitingStat(f, 'allgrids|utilgrowth|' + id, d) ?? null };
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


class Utility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()
        cls.u = json.loads(src("site", "data", "siting", "utility.json"))

    def test_the_file_is_the_table_s_where_it_is_here(self):
        for d in (os.path.join(ROOT, "runs", "archive_restore"), os.path.join(MAIN, "runs", "archive_restore"), os.path.join(ROOT, "warehouse", "output")):
            p = os.path.join(d, "eia861_utility_sales.csv")
            if os.path.exists(p):
                break
        else:
            raise unittest.SkipTest("eia861_utility_sales is not on this machine")
        again = sp.utility_file(p)
        own = ("built", "county", "territory_table")   # session 718 adds the counties' utilities to the file
        self.assertEqual({k: v for k, v in again.items() if k not in own}, {k: v for k, v in self.u.items() if k not in own})

    def test_no_delivery_row_is_chosen(self):
        for k, v in self.u["by"].items():
            if v:
                self.assertIn(v["service"], ("Bundled", "Energy"), k)

    def test_the_row_figures_and_keys(self):
        r = self.o["ercot:HB_HUBAVG"]
        u = self.u["by"]["TX|ERCO"]
        self.assertEqual((r["state"], r["ba"], r["utility"]), ("TX", "ERCO", u["utility"]))
        self.assertAlmostEqual(r["rev"], u["revenue_usd"] / u["sales_mwh"], places=9)
        self.assertAlmostEqual(r["growth"], 100 * (u["sales_mwh"] / u["sales_prior_mwh"] - 1), places=9)
        self.assertEqual((r["key"], r["gkey"]), (r["rev"], r["growth"]))
        self.assertEqual(self.o["miso:TEXAS.HUB"]["ba"], "MISO")       # Texas inside MISO is Entergy's, not ERCOT's
        self.assertEqual(self.o["isone:.H.INTERNAL_HUB"]["state"], "MA")
        self.assertEqual(self.o["spp:SPPSOUTH_HUB"]["state"], "OK")

    def test_nodes_and_pjm_say_why(self):
        self.assertIn("TSP", self.o["ercot:7RNCHSLR_ALL"]["why"])
        self.assertEqual(self.o["pjm:grid"]["state"], "PA")   # session 718: PJM's row reads Allegheny County's utilities

    def test_the_tab_draws_the_keys(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn("check={`allgrids|utilrev|${r.id}`}", v)
        self.assertIn("check={`allgrids|utilgrowth|${r.id}`}", v)


if __name__ == "__main__":
    unittest.main()
