"""Session 707: carbon on the All grids tab (docs/methods/siting.md). Each row's eGRID subregion and its rate, the
plants' CO2 over their net generation as eGRID sums them (a plant reporting no CO2 adds generation only), recomputed
here from the plant table where it is on this machine; three subregions pinned; a profile that runs in some hours gets
the grid's hourly intensity over those hours where it covers 90 percent of them. No request, no model call."""
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
for (const prof of ['datacenter', 'electrolyzer']) for (const id of ['ercot:HB_HUBAVG', 'caiso:TH_SP15_GEN-APND', 'nyiso:WEST', 'nyiso:N.Y.C.', 'nyiso:LONGIL', 'pjm:grid', 'spp:SPPSOUTH_HUB', 'miso:INDIANA.HUB']) {
  const x = { profile: prof, lf: S.PROFILES[prof].lf, strike: S.PROFILES[prof].strike };
  const c = S.carbonCell(d, f, S.rowOf(f, id), x);
  out[prof + '|' + id] = 'why' in c ? c : { sub: c.sub.id, kg: c.kg, lb: c.lb, hourly: c.hourly, key: S.sitingStat(f, 'allgrids|carbon|' + id, d) ?? null };
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


def lb(a):
    return a["co2_tons"] * 2000 / a["gen_mwh"]


class Carbon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()
        cls.c = json.loads(src("site", "data", "siting", "carbon.json"))

    def test_three_subregions_reproduce_from_the_plant_table(self):
        p = None
        for d in (os.path.join(ROOT, "runs", "archive_restore"), os.path.join(MAIN, "runs", "archive_restore"), os.path.join(ROOT, "warehouse", "output")):
            if os.path.exists(os.path.join(d, "egrid_power_plants.csv")):
                p = os.path.join(d, "egrid_power_plants.csv")
                break
        if not p:
            raise unittest.SkipTest("egrid_power_plants is not on this machine")
        e = pd.read_csv(p, skiprows=sp.header_rows(p), dtype=str)
        for sub in ("ERCT", "CAMX", "NYUP"):
            x = e[e["egrid_subregion"] == sub]
            gen = pd.to_numeric(x["net_generation_mwh"], errors="coerce")
            co2 = pd.to_numeric(x["co2_tons"], errors="coerce")[gen.notna()]
            want = co2.sum(skipna=True) * 2000 / gen.sum()
            self.assertAlmostEqual(lb(self.c["areas"][sub]), want, places=2, msg=sub)

    def test_the_pinned_rates_of_egrid2023(self):
        # the file's own figures on 22 October 2026 (eGRID2023, data year 2023), lb per MWh to one decimal
        self.assertEqual(self.c["data_year"], 2023)
        for sub, want in (("ERCT", 733.9), ("CAMX", 428.5), ("NYUP", 242.1)):
            self.assertAlmostEqual(round(lb(self.c["areas"][sub]), 1), want, msg=sub)

    def test_each_row_s_subregion_and_its_figure(self):
        want = {"ercot:HB_HUBAVG": "ERCT", "caiso:TH_SP15_GEN-APND": "CAMX", "nyiso:WEST": "NYUP", "nyiso:N.Y.C.": "NYCW", "nyiso:LONGIL": "NYLI",
                "pjm:grid": "PJM", "spp:SPPSOUTH_HUB": "SPSO", "miso:INDIANA.HUB": "RFCW"}
        for rid, sub in want.items():
            r = self.o[f"datacenter|{rid}"]
            self.assertEqual(r["sub"], sub, rid)
            self.assertAlmostEqual(r["lb"], lb(self.c["areas"][sub]), places=9)
            self.assertAlmostEqual(r["kg"], r["lb"] * 0.45359237, places=9)
            self.assertEqual(r["key"], r["kg"])
            self.assertIsNone(r["hourly"])   # a datacenter runs every hour: the annual rate

    def test_the_electrolyzer_gets_the_hourly_rate_where_held(self):
        for rid in ("ercot:HB_HUBAVG", "caiso:TH_SP15_GEN-APND", "nyiso:N.Y.C."):
            h = self.o[f"electrolyzer|{rid}"]["hourly"]
            self.assertIsNotNone(h, rid)
            self.assertGreaterEqual(h["hours"], 0.9 * h["of"])
        for rid in ("pjm:grid", "miso:INDIANA.HUB"):
            self.assertIsNone(self.o[f"electrolyzer|{rid}"]["hourly"], rid)

    def test_the_tab_draws_the_keys(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        for k in ("check={`allgrids|carbon|${r.id}`}", "check={`allgrids|carbonlb|${r.id}`}", "check={`allgrids|carbonh|${r.id}|${k}`}"):
            self.assertIn(k, v)


if __name__ == "__main__":
    unittest.main()
