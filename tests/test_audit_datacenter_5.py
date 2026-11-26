"""Audit of "What a datacenter pays", finding 5 (session 10203, docs/reviews/datacenter-model-audit-2026-11-26.md): the
scenarios' contract (site/lib/datacenter/finance.ts, contractYear and marketYear) is a share of the energy at a fixed
price in every hour, so it is shaped like the load. A lab's contract is most often a solar or wind PPA settled at a hub,
which delivers in its own hours.

1. Through the page's library (run by Node): at a 50 percent share and any price the year's cost is exactly
   (1 - s) K + s E c, whatever the hours; and from the generator page's own public file (ERCOT's solar fleet at the hub
   average, real time) solar's capture price over its twelve months sits more than USD 5 per MWh under a flat load's
   mean, so a hub-settled solar PPA costs a flat load more than the page's arithmetic. Passes on main: it shows the gap.
2. The fix on this branch, words only: the contract share's note says the contract is shaped like the load and that a
   solar or wind contract is not priced here; the note's list says the measured gap. Fails on main."""
import csv
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "datacenter", "finance.ts").replace("\\", "/")
JS = """
const F = await import(process.argv[1]);
const w = { per: 34.07, cost: 298465.22, energy: 8760, held: 8760, flatCost: 298465.22, down: 0, bad: null, of: 0 };
const a = { ...F.defaultsOf({ run: F.FLAT, gpu: 1.3, pue: 1.56 }), cshare: 50, cprice: 30 };
console.log(JSON.stringify({ bill: F.bill(a, w), expect: 0.5 * w.cost + 0.5 * w.energy * 30 }));
"""


class ContractShape(unittest.TestCase):
    def test_contract_takes_the_loads_shape(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertAlmostEqual(r["bill"], r["expect"], places=6)

    def test_solar_captures_less_than_a_flat_load_pays(self):
        sp = sw = fp = 0.0
        n = 0
        with open(os.path.join(ROOT, "site", "public", "seller", "erw_2026_generator_hourly.csv"), encoding="utf-8") as fh:
            for r in csv.DictReader(l for l in fh if not l.startswith("#")):
                if r["in_last_twelve"] != "1":
                    continue
                p, q = float(r["price_usd_mwh"]), float(r["solar_mwh"])
                fp += p
                n += 1
                if q != -99999:
                    sp += p * q
                    sw += q
        self.assertGreater(fp / n - sp / sw, 5.0)          # USD 8.93 per MWh over October 2025 to September 2026

    def test_the_contract_says_its_shape(self):
        with open(os.path.join(ROOT, "site", "lib", "datacenter", "finance.ts"), encoding="utf-8") as f:
            self.assertIn("The contract is shaped like the load, the same share in every hour; a solar or wind contract settled at a hub delivers in its own hours", f.read())
        with open(os.path.join(ROOT, "docs", "methods", "datacenter_pays_algorithm.md"), encoding="utf-8") as f:
            self.assertIn("ERCOT's solar fleet captured USD 23.27 per MWh at the hub average against a flat load's 32.20", f.read())


if __name__ == "__main__":
    unittest.main()
