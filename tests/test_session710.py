"""Session 710: the screen of the All grids tab (docs/methods/siting.md). Sort by any column, a row with no figure or
a held one last, never sorted by a held figure; filters by grid, kind, an energy band and every cost part held; every
input in the address and read back; A and B side by side, B less A, the year all-in and its MWh, each a key. No request,
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
const F = await import('./scripts/siting-files.mjs');
const S = await import('./lib/siting.ts');
const d = await F.dc(); const f = F.files();
const hubs = S.hubRows(f.index);
const q = { view: 'allgrids', sort: 'allin', grid: 'ercot,caiso', kind: 'zone', lo: '30', hi: '40', held: '1', a: 'ercot:HB_HUBAVG', b: 'nyiso:N.Y.C.', profile: 'flexible' };
const x = S.sitingInputs(q);
const back = S.sitingInputs(Object.fromEntries(new URL('http://h' + S.sitingHref(x)).searchParams));
const all = S.sitingInputs({ view: 'allgrids', sort: 'allin' });
const sorted = S.screen(d, f, hubs, all).map((r) => [r.id, S.columnValue(d, f, r, all, 'allin')]);
const cap = S.screen(d, f, hubs, S.sitingInputs({ view: 'allgrids', sort: 'capacity' })).map((r) => [r.grid, S.columnValue(d, f, r, all, 'capacity')]);
const filtered = S.screen(d, f, hubs, x).map((r) => [r.id, r.kind, S.columnValue(d, f, r, x, 'energy'), S.columnValue(d, f, r, x, 'allin')]);
const k = S.profileKey(all), yk = S.yearKey(all);
const a = S.rowOf(f, 'ercot:HB_HUBAVG'), b = S.rowOf(f, 'caiso:TH_SP15_GEN-APND');
const ya = S.yearOf(d, f, a, all);
const out = { x, back, sorted, cap, filtered, ya, energyA: S.columnValue(d, f, a, all, 'energy'), energyB: S.columnValue(d, f, b, all, 'energy'),
  diff: S.sitingStat(f, 'allgrids|diff|energy|ercot:HB_HUBAVG|caiso:TH_SP15_GEN-APND|' + k, d), year: S.sitingStat(f, 'allgrids|year|ercot:HB_HUBAVG|' + yk, d),
  mwh: S.sitingStat(f, 'allgrids|mwh|ercot:HB_HUBAVG|' + yk, d), col: S.sitingStat(f, 'allgrids|col|carbon|ercot:HB_HUBAVG|' + k, d) };
process.stdout.write(JSON.stringify(out));
"""


def run():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=900, encoding="utf-8")
    if r.returncode != 0 and "Unknown file extension" in r.stderr:
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


class Screen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()

    def test_every_input_is_in_the_address_and_reads_back(self):
        self.assertEqual(self.o["back"], self.o["x"])
        x = self.o["x"]
        self.assertEqual((x["sort"], x["dir"], x["grids"], x["kind"], x["band"], x["held"], x["a"], x["b"]), ("allin", "desc", ["ercot", "caiso"], "zone", [30, 40], True, "ercot:HB_HUBAVG", "nyiso:N.Y.C."))

    def test_the_sort_puts_rows_with_no_figure_last(self):
        vals = [v for _, v in self.o["sorted"]]
        held = [v for v in vals if v is not None]
        self.assertEqual(held, sorted(held, reverse=True))
        self.assertTrue(all(v is None for v in vals[len(held):]))
        self.assertEqual(len(vals), 48)

    def test_a_held_capacity_is_never_sorted_by_its_value(self):
        for g, v in self.o["cap"]:
            self.assertEqual(v is None, g in ("pjm", "isone", "miso", "nyiso"), g)

    def test_the_filters(self):
        for rid, kind, energy, allin in self.o["filtered"]:
            self.assertTrue(rid.startswith(("ercot:", "caiso:")))
            self.assertEqual(kind, "zone")
            self.assertTrue(30 <= energy <= 40)
            self.assertIsNotNone(allin)

    def test_a_and_b_keys(self):
        self.assertAlmostEqual(self.o["diff"], self.o["energyB"] - self.o["energyA"], places=9)
        ya = self.o["ya"]
        self.assertAlmostEqual(ya["mwh"], 100 * 0.9 * 8760, places=6)       # a datacenter: 100 MW drawing 0.9 every hour
        self.assertAlmostEqual(ya["usd"], ya["mwh"] * ya["allin"], places=3)
        self.assertEqual((self.o["year"], self.o["mwh"]), (ya["usd"], ya["mwh"]))
        self.assertIsNotNone(self.o["col"])

    def test_the_tab_draws_it(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        for k in ("<Headline x={x} /><AbPanel x={x} />", "check={`allgrids|diff|${c.id}|${ra.id}|${rb.id}|${k}`}", "check={`allgrids|year|${r.id}|${yk}`}", "The order is the column&apos;s, not a ranking of sites."):
            self.assertIn(k, v)
        self.assertIn('data-allgrids-screen="1"', src("site", "app", "cost-of-power", "AllGridsForm.tsx"))


if __name__ == "__main__":
    unittest.main()
