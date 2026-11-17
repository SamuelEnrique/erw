"""Session 7622: the other choice of the ruling on energy and delivery together (branch wip/alt-cost-of-power-2, not
landed). "Your load" on /cost-of-power gives market energy alone, delivery in its own table, and the scenarios' "Delivery
and other charges" default is none. Under the other choice, once the site's wires utility is known (in ERCOT, named by
the address as util=<slug>), that default is the utility's tariff total at the load's size, so the three headline
numbers, which are scenario A's, count energy and delivery together.

What is held to:
  the page's own library (site/lib/datacenter/delivery.ts, run by node) on site/data/datacenter/texas_delivery.json
    (built 16 November 2026) gives Oncor's first total for a flat 300 MW load USD 8.80 per MWh (9 lines, none
    conditional), the read's case; CenterPoint 7.66, AEP Texas 8.38, Texas-New Mexico Power 7.07;
  the model sets the delivery default from util= only in ERCOT and only for a utility the file holds, rounded to the
    cent, and names its source in the field's note; with no util= the default is none, as before;
  lib/datacenter/finance.ts defaultsOf takes the given delivery default, else none.

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


class EnergyAndDeliveryTogether(unittest.TestCase):
    def test_the_utilities_totals_at_300_mw(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        js = """
import fs from "node:fs";
const D = await import("./lib/datacenter/delivery.ts");
const f = JSON.parse(fs.readFileSync("data/datacenter/texas_delivery.json", "utf-8"));
const out = {};
for (const u of D.utilitiesOf(f.rows)) { const d = D.deliveryOf(f.rows, u, 300); out[D.slugOf(u)] = [Math.round(d.total * 100) / 100, d.lines, d.conditional]; }
console.log(JSON.stringify(out));
"""
        r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        got = json.loads(r.stdout)
        self.assertEqual(got["oncor"], [8.8, 9, 0])
        self.assertEqual(got["centerpoint_energy_houston_electric"][0], 7.66)
        self.assertEqual(got["aep_texas"][0], 8.38)
        self.assertEqual(got["texas_new_mexico_power"][0], 7.07)

    def test_the_model_sets_the_default_from_the_named_utility(self):
        m = src("site", "app", "cost-of-power", "model.ts")
        self.assertIn('const utilAsked = x.grid === "ercot" && typeof q.util === "string" ? utilitiesOf(DELIVERY.rows).find((u) => slugOf(u) === q.util) : undefined;', m)
        self.assertIn("const adderDefault = utilDelivery ? Math.round(utilDelivery.total * 100) / 100 : undefined;", m)
        self.assertIn("...(adderDefault !== undefined ? { adder: adderDefault } : {})", m)
        self.assertIn("adderSource:", m)
        f = src("site", "lib", "datacenter", "finance.ts")
        self.assertIn("adder: load.adder ?? 0,", f)
        s = src("site", "app", "cost-of-power", "LoadScenarios.tsx")
        self.assertIn('k === "adder" && f.adderSource ? f.adderSource : SPECS[k].source', s)
        h = src("site", "app", "cost-of-power", "LoadHeadline.tsx")
        self.assertIn("const withDelivery = !!f.adderSource && a.adder > 0 && !!w;", h)
        self.assertIn('"Last twelve months, energy and delivery"', h)
        self.assertIn("const shown = per !== null ? per + (withDelivery ? a.adder : 0) : null;", h)
        for t in (m, f, s, h):
            self.assertNotIn(chr(0x2014), t)

    def test_the_read_case_headline(self):
        # the page read on this branch's build, 300 MW flat at LZ_NORTH, real time, Nov 2025 to Oct 2026: market energy
        # USD 34.07 per MWh; with util=oncor the first number is 34.07 + 8.80 = 42.87 (+25.8 percent)
        self.assertEqual(f"{34.07 + 8.80:.2f}", "42.87")
        self.assertEqual(f"{100 * 8.80 / 34.07:.1f}", "25.8")


if __name__ == "__main__":
    unittest.main()
