"""Session 7622: the other choice of the ruling on a Texas row's transmission rate on the All grids tab (branch
wip/alt-cost-of-power-3, not landed). The four-peak transmission part of a Texas row's all-in figure is at the
Commission's rate for every wires utility together; under the other choice a row whose wires utility is known takes
that utility's own rate.

What is held to:
  the utilities' own rates, USD per kW of four-peak demand a year, are their tariff lines' transmission component for a
    flat 100 MW load times 8.76 (site/data/datacenter/texas_delivery.json, built 16 November 2026): Oncor 75.1301,
    CenterPoint 60.5785, AEP Texas 71.4725, Texas-New Mexico Power 61.8823; the Commission's 2026 rate is 75.527270;
  the rows whose wires utility is known (data/siting/utility.json's delivery-only companies, matched by the name's first
    word) are ercot:HB_HOUSTON and ercot:LZ_HOUSTON (CenterPoint) and ercot:LZ_AEN (Oncor), and no other ERCOT row;
  so the transmission part of those rows moves by the rates' ratio: CenterPoint's rows -19.79 percent, Oncor's -0.53;
  cpCharge takes the utility's rate in place of the Commission's and names the utility; the hover says which.

No request, no model call. Skips when node is absent."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-1500:])
    return json.loads(r.stdout)


class TheUtilitysOwnRate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.got = node("""
import fs from "node:fs";
const D = await import("./lib/datacenter/delivery.ts");
const S = await import("./lib/siting.ts");
const f = JSON.parse(fs.readFileSync("data/datacenter/texas_delivery.json", "utf-8"));
const utility = JSON.parse(fs.readFileSync("data/siting/utility.json", "utf-8"));
const rates = Object.fromEntries(D.utilitiesOf(f.rows).map((u) => [u, D.deliveryOf(f.rows, u, 100).components.find((c) => c.kind === "transmission").perMwh * 8760 / 1000]));
const files = { utility, utilRates: rates };
const ids = Object.keys(utility.county ?? {}).filter((k) => k.startsWith("ercot:"));
const rows = Object.fromEntries(ids.map((id) => [id, S.txUtilityOf(files, { id, grid: "ercot", region: id.slice(6), label: id, kind: "zone" })]));
const comm = S.newestRate(f.matrix);
console.log(JSON.stringify({ rates, rows, comm }));
""")

    def test_the_rates(self):
        r = self.got["rates"]
        self.assertEqual({k: f"{v:.4f}" for k, v in r.items()}, {"Oncor": "75.1301", "CenterPoint Energy Houston Electric": "60.5785",
                                                                 "AEP Texas": "71.4725", "Texas-New Mexico Power": "61.8823"})
        self.assertEqual((self.got["comm"]["year"], f"{self.got['comm']['value']:.6f}"), ("2026", "75.527270"))

    def test_the_rows_whose_utility_is_known(self):
        known = {k: v for k, v in self.got["rows"].items() if v}
        self.assertEqual(known, {"ercot:HB_HOUSTON": "CenterPoint Energy Houston Electric", "ercot:LZ_HOUSTON": "CenterPoint Energy Houston Electric", "ercot:LZ_AEN": "Oncor"})

    def test_the_change(self):
        c = self.got["comm"]["value"]
        self.assertEqual(f"{100 * (self.got['rates']['CenterPoint Energy Houston Electric'] / c - 1):.2f}", "-19.79")
        self.assertEqual(f"{100 * (self.got['rates']['Oncor'] / c - 1):.2f}", "-0.53")

    def test_the_code(self):
        s = src("site", "lib", "siting.ts")
        self.assertIn("const rate: Rate = utility ? { year: f.rate.year, value: f.utilRates![utility] } : f.rate;", s)
        self.assertIn("...(utility ? { utility } : {})", s)
        self.assertIn("utilRates: UTILITY_TX_RATES", src("site", "lib", "sitingdata.ts"))
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn("'s own transmission rate, the row's wires utility", v)
        for t in (s, v):
            self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()
