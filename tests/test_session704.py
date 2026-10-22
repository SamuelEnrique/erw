"""Session 704: capacity on the All grids tab (docs/methods/siting.md). The capacity tables are internal and the
repository public: the site's file holds each market's newest period, auction and zones and no price; the tab draws
"license needed" in place for PJM, ISO-NE, MISO and NYISO, and "no capacity market" for ERCOT, CAISO and SPP (zero in the
all-in figure); the builder converts a price to USD per MWh offline, by the stated rule. No request, no model call."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
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
for (const r of S.hubRows(f.index)) {
  const c = S.capacityCell(f, r, { profile: 'datacenter' }), i = S.capacityCell(f, r, { profile: 'industry' });
  const a = S.allInCell(d, f, r, { profile: 'datacenter', lf: 0.9, strike: null });
  out[r.id] = { kind: 'zero' in c ? 'zero' : 'held' in c ? 'held' : c.words, entity: 'held' in c ? c.held.entity : null, industry: 'zero' in i ? 'zero' : 'held' in i ? 'held' : i.words, allin: 'v' in a ? 'v' : a.words };
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


class File(unittest.TestCase):
    def test_the_site_file_holds_no_price(self):
        cap = json.loads(src("site", "data", "siting", "capacity.json"))
        self.assertEqual(set(cap["markets"]), {"pjm_bra", "isone_fca", "miso_pra", "nyiso_icap_spot"})
        for m in cap["markets"].values():
            self.assertEqual(set(m), {"market", "table", "license", "unit", "period_start", "period_end", "auction", "zones"})
            self.assertEqual(m["license"], "internal")
        self.assertNotIn("value", src("site", "data", "siting", "capacity.json"))

    def test_the_offline_conversion(self):
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "iso_all_capacity_prices.csv")
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write("# fixture\nentity,variable,ts_utc,value,unit,market,x_period_end,x_auction\n")
                f.write("pjm:RTO,capacity_price,2028-06-01T00:00:00Z,325.0,USD/MW-day,pjm_bra,2029-05-31T00:00:00Z,BRA 2028/2029\n")
                f.write("nyiso:NYC,capacity_price,2026-10-01T00:00:00Z,12.6,USD/kW-month,nyiso_icap_spot,2026-10-31T00:00:00Z,Spot 10/2026\n")
            rows = [{"row": "pjm:grid", "market": "pjm_bra", "entity": "pjm:RTO", "period_start": "2028-06-01T00:00:00Z", "auction": "BRA 2028/2029"},
                    {"row": "nyiso:N.Y.C.", "market": "nyiso_icap_spot", "entity": "nyiso:NYC", "period_start": "2026-10-01T00:00:00Z", "auction": "Spot 10/2026"}]
            got = sp.cap_internal(p, rows)
        self.assertAlmostEqual(got["pjm:grid"]["usd_per_mwh_every_hour"], 325.0 * 365 / 8760)
        self.assertAlmostEqual(got["nyiso:N.Y.C."]["usd_per_mwh_every_hour"], 12.6 * 12000 / 8760)


class Tab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()

    def test_no_market_grids_are_zero_and_the_four_are_held(self):
        for rid, v in self.o.items():
            g = rid.split(":")[0]
            if g in ("ercot", "caiso", "spp"):
                self.assertEqual(v["kind"], "zero", rid)
            else:
                self.assertEqual(v["kind"], "held", rid)
                self.assertEqual(v["industry"], "not held", rid)   # interruptible: its utility's tariff is not held

    def test_the_zone_map(self):
        self.assertEqual(self.o["nyiso:N.Y.C."]["entity"], "nyiso:NYC")
        self.assertEqual(self.o["nyiso:LONGIL"]["entity"], "nyiso:LI")
        self.assertEqual(self.o["nyiso:HUD VL"]["entity"], "nyiso:G-J Locality")
        self.assertEqual(self.o["nyiso:WEST"]["entity"], "nyiso:NYCA")
        self.assertEqual(self.o["miso:INDIANA.HUB"]["entity"], "miso:Z6")
        self.assertEqual(self.o["pjm:grid"]["entity"], "pjm:RTO")
        self.assertEqual(self.o["isone:.Z.MAINE"]["entity"], "isone:System-wide")   # FCA 18 priced no zone of its own

    def test_all_in_follows_capacity(self):
        self.assertEqual(self.o["ercot:HB_HUBAVG"]["allin"], "v")
        self.assertEqual(self.o["caiso:TH_SP15_GEN-APND"]["allin"], "not held")   # its transmission is not held
        self.assertEqual(self.o["pjm:grid"]["allin"], "not held")

    def test_the_cell_draws_license_needed_in_place(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        # session 718's gate: since session 714 the cell is a tip (Tp), its data attribute passed through
        self.assertIn('<Tp tip={why} data={{ "license-held": table }}>license needed</Tp>', v)
        self.assertIn('<Words words="no capacity market"', v)


if __name__ == "__main__":
    unittest.main()
