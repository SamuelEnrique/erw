"""Session 11408, readied for the owner's ruling (weekend page part 3.4, generator choice 4; the generator audit of 20
November, finding 4, docs/reviews/generator-model-audit-2026-11-20.md, carried from wip/audit-generator-4): an
as-generated PPA is paid only on the energy the plant makes, which falls by the degradation rate each year.

Through site/lib/seller/finance.ts (run by Node) at the default solar case (ERCOT, USD 59.8523 per kW, 2.5799 MWh per
kW): the breakeven PPA price is 61.51 per MWh (it was 58.36), NPV at it is zero, and the contract pays in year 35
0.993^34 of year 1; an independent bisection on degrading flows gives the same price; a block contract does not fall."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "seller", "finance.ts").replace("\\", "/")
R, E = 59.8523, 2.5799


class ContractPaysTheEnergyMade(unittest.TestCase):
    def test_breakeven_on_the_energy_made(self):
        js = ("const F = await import(process.argv[1]);"
              "const a = F.defaultsOf({ capex: 1375, fom: 12.5, life: 35, deg: 0.7 });"
              f"const R = {R}, E = {E};"
              "const c = { kind: 'energy', energyKw: E, shape: 'generated', flat: null };"
              "const blk = { kind: 'energy', energyKw: E, shape: 'block', flat: 20 };"
              "const p = F.breakevenPpa(a, R, c, 100);"
              "const k = { ...a, cshare: 100, cprice: p };"
              "const flowsDeg = (price) => { const ds = F.debtService(a), out = [-a.capex * (1 - a.share / 100)];"
              "  for (let t = 1; t <= a.life; t++) out.push(price * E * (1 - a.deg / 100) ** (t - 1) - a.fom - (t <= F.debtYears(a) ? ds : 0)); return out; };"
              "let lo = 0, hi = 1000; for (let i = 0; i < 200; i++) { const m = (lo + hi) / 2; if (F.npv(a.hurdle, flowsDeg(m)) < 0) lo = m; else hi = m; }"
              "console.log(JSON.stringify({ p, y1: F.contractYear(k, c, 1), y35: F.contractYear(k, c, 35), b1: F.contractYear(k, blk, 1), b35: F.contractYear(k, blk, 35),"
              " npvAt: F.npv(a.hurdle, F.flows(k, R, c)), pDeg: lo }));")
        out = subprocess.run(["node", "--input-type=module", "-e", js, LIB], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertAlmostEqual(r["p"], 61.51, places=2)
        self.assertAlmostEqual(r["p"], r["pDeg"], places=6)
        self.assertAlmostEqual(r["npvAt"], 0.0, places=6)
        self.assertAlmostEqual(r["y35"], r["y1"] * 0.993 ** 34, places=9)
        self.assertAlmostEqual(r["b35"], r["b1"], places=9)     # a block keeps its volume


if __name__ == "__main__":
    unittest.main()
