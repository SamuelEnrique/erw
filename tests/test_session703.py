"""Session 703: transmission and the four peaks on the All grids tab (docs/methods/siting.md). ERCOT's four-peak charge
at the Commission's newest approved rate, as "Your load" takes it: a flat load's firm charge is the rate over 8,760 hours,
the figure "Your load"'s matrix row shows; a load off at the peaks pays nothing, computed from its weights; every other
grid is "not held"; the all-in figure is drawn only where each part is held or zero by design; the gaps file lists every
cell the warehouse cannot fill. No request, no model call."""
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
const out = { rate: f.rate, rows: {} };
for (const prof of ['datacenter', 'flexible', 'electrolyzer', 'industry']) {
  const x = { profile: prof, lf: S.PROFILES[prof].lf, strike: S.PROFILES[prof].strike };
  for (const id of ['ercot:HB_HUBAVG', 'ercot:LZ_NORTH', 'caiso:TH_SP15_GEN-APND', 'pjm:grid', 'miso:INDIANA.HUB']) {
    const r = S.rowOf(f, id);
    const c = S.cpCharge(d, f, r, x), a = S.allInCell(d, f, r, x), e = S.profileCell(d, f, r, x, f.cp);
    out.rows[prof + '|' + id] = { c, a, e: 'why' in e ? null : e.per, key: S.sitingStat(f, 'allgrids|tx|' + id + '|' + S.profileKey(x), d) ?? null };
  }
}
const model = (ts, behind) => { const t = Date.parse(ts) - behind * 3600000, y = new Date(t).getUTCFullYear(); return { y, i: Math.floor((t - Date.UTC(y, 0, 1)) / 3600000) }; };
out.hours = f.cp.summers.flatMap((s) => s.intervals).every((iv) => JSON.stringify(S.hourOf(iv.ts, 6)) === JSON.stringify(model(iv.ts, 6)));
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


class FourPeaks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()
        cls.d = json.loads(src("site", "data", "datacenter", "texas_delivery.json"))

    def test_the_rate_is_your_load_s_newest_approved(self):
        rates = sorted((r for r in self.d["matrix"] if r["quantity"] == "postage_stamp_rate" and r["status"] == "approved" and r["matrix"] != "B"), key=lambda r: r["year"])
        self.assertEqual(self.o["rate"], {"year": rates[-1]["year"], "value": rates[-1]["value"]})

    def test_a_flat_load_s_firm_charge_is_the_matrix_row_of_your_load(self):
        want = self.o["rate"]["value"] * 1000 / 8760   # page.tsx MatrixCell: the rate over 8,760 hours, a flat load
        for rid in ("ercot:HB_HUBAVG", "ercot:LZ_NORTH"):
            c = self.o["rows"][f"datacenter|{rid}"]["c"]
            self.assertAlmostEqual(c["firm"], want, places=9)
            self.assertAlmostEqual(c["own"], want, places=9)
            self.assertEqual(c["share"], 1)
            self.assertEqual(c["curtailing"], 0)

    def test_a_load_off_at_the_peaks_pays_nothing_computed_from_its_hours(self):
        c = self.o["rows"]["flexible|ercot:HB_HUBAVG"]["c"]
        self.assertEqual([iv["w"] for iv in c["intervals"]], [0, 0, 0, 0])
        self.assertEqual(c["own"], 0)
        self.assertEqual(self.o["rows"]["flexible|ercot:HB_HUBAVG"]["key"], 0)

    def test_the_intervals_fall_in_the_hours_model_ts_finds(self):
        self.assertTrue(self.o["hours"])

    def test_other_grids_are_not_held_and_say_why(self):
        for prof in ("datacenter", "flexible"):
            c = self.o["rows"][f"{prof}|caiso:TH_SP15_GEN-APND"]["c"]
            self.assertEqual(c["words"], "not held")
            self.assertIn("large-load tariff", c["why"])
            self.assertEqual(self.o["rows"][f"{prof}|miso:INDIANA.HUB"]["c"]["words"], "paused")

    def test_all_in_is_energy_plus_transmission_where_capacity_is_zero_by_design(self):
        for prof in ("datacenter", "flexible", "electrolyzer", "industry"):
            r = self.o["rows"][f"{prof}|ercot:HB_HUBAVG"]
            self.assertAlmostEqual(r["a"]["v"], r["e"] + r["c"]["own"], places=9)
            self.assertIn("missing", self.o["rows"][f"{prof}|caiso:TH_SP15_GEN-APND"]["a"])
            self.assertIn("missing", self.o["rows"][f"{prof}|pjm:grid"]["a"])


class Gaps(unittest.TestCase):
    def test_the_gaps_file_lists_the_transmission_cells_by_grid(self):
        g = src("docs", "reviews", "siting-gaps.md")
        for grid in ("CAISO", "NYISO", "ISO-NE", "SPP", "MISO", "PJM"):
            self.assertIn(f"| {grid} | Transmission", g)
        self.assertNotIn(chr(0x2014), g)

    def test_the_tab_draws_the_keys(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        for k in ("check={`allgrids|tx|${r.id}|${k}`}", "check={`allgrids|tx|${r.id}|firm|${k}`}", "check={`allgrids|tx|${r.id}|curtailing|${k}`}", "check={`allgrids|allin|${r.id}|${profileKey(x)}`}"):
            self.assertIn(k, v)


if __name__ == "__main__":
    unittest.main()
