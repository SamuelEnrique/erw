"""Session 706: headroom on the All grids tab (docs/methods/siting.md). Demand growth: the last twelve months' mean
demand over the twelve before, from "Your load"'s EIA-930 file, weighted by each month's hours and recomputed here;
generation under construction due in the twelve months after the EIA-860M vintage, by grid, recomputed from the table
where it is on this machine; installed capacity over the last year's peak only for a grid that is whole states. No
request, no model call."""
import calendar
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


SCRIPT = """
const F = await import('./scripts/siting-files.mjs');
const S = await import('./lib/siting.ts');
const d = await F.dc(); const f = F.files();
const out = {};
for (const g of ['ercot', 'caiso', 'nyiso', 'isone', 'spp', 'miso', 'pjm']) {
  const id = S.hubRows(f.index).find((r) => r.grid === g).id;
  out[g] = { g: S.demandGrowth(f.demand, g), c: S.capacityOverPeak(f.demand, f.headroom, g), key: S.sitingStat(f, 'allgrids|demand|' + id, d) ?? null,
    planned: S.sitingStat(f, 'allgrids|planned|' + id, d) ?? null, ratio: S.sitingStat(f, 'allgrids|capratio|' + id, d) ?? null };
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


def months_back(end, k):
    y, m = int(end[:4]), int(end[5:7]) - k
    while m <= 0:
        y, m = y - 1, m + 12
    return y, m


class Headroom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()
        cls.d = json.loads(src("site", "data", "demand_growth.json"))
        cls.h = json.loads(src("site", "data", "siting", "headroom.json"))

    def test_demand_growth_is_the_hour_weighted_twelve_months(self):
        ba = {"ercot": "ERCO", "pjm": "PJM", "nyiso": "NYIS"}
        for g, b in ba.items():
            a = self.d["areas"][b]["years"]

            def mean(end):
                s = h = 0.0
                for k in range(12):
                    y, m = months_back(end, k)
                    hrs = calendar.monthrange(y, m)[1] * 24
                    s += a[str(y)][f"avg_demand_mw_m{m:02d}"] * hrs
                    h += hrs
                return s / h
            to = self.d["ytd_through"]
            y, m = months_back(to, 12)
            want = 100 * (mean(to) / mean(f"{y}-{m:02d}") - 1)
            self.assertAlmostEqual(self.o[g]["g"]["pct"], want, places=9)
            self.assertAlmostEqual(self.o[g]["key"], want, places=9)

    def test_capacity_over_peak_only_for_whole_states(self):
        for g in ("ercot", "caiso", "spp", "miso", "pjm"):
            self.assertIn("why", self.o[g]["c"], g)
            self.assertIsNone(self.o[g]["ratio"], g)
        for g in ("nyiso", "isone"):
            c = self.o[g]["c"]
            peak = self.d["areas"]["NYIS" if g == "nyiso" else "ISNE"]["years"][str(self.d["last_year"])]["peak_demand_mw"]
            self.assertAlmostEqual(c["pct"], 100 * self.h["capacity"][g]["mw"] / peak, places=9)
        self.assertEqual(self.h["capacity"]["isone"]["states"], ["CT", "MA", "ME", "NH", "RI", "VT"])

    def test_planned_generation_matches_the_table_where_it_is_here(self):
        p = os.path.join(ROOT, "warehouse", "output", "eia860m_planned_generators.csv")
        c = os.path.join(ROOT, "runs", "archive_restore", "eia_state_capacity_annual.csv")
        main = os.path.join(os.path.dirname(ROOT), "erw")
        if not os.path.exists(p):
            p = os.path.join(main, "warehouse", "output", "eia860m_planned_generators.csv")
        if not os.path.exists(c):
            c = os.path.join(main, "runs", "archive_restore", "eia_state_capacity_annual.csv")
        if not (os.path.exists(p) and os.path.exists(c)):
            raise unittest.SkipTest("the planned generators or the state capacity table is not on this machine")
        again = sp.headroom_file(p, c)
        self.assertEqual({k: v for k, v in again.items() if k != "built"}, {k: v for k, v in self.h.items() if k != "built"})
        self.assertEqual(self.o["ercot"]["planned"], self.h["planned"]["ercot"]["construction_mw"])

    def test_the_tab_draws_the_keys(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        for k in ("check={`allgrids|demand|${r.id}`}", "check={`allgrids|planned|${r.id}`}", "check={`allgrids|capratio|${r.id}`}"):
            self.assertIn(k, v)


if __name__ == "__main__":
    unittest.main()
