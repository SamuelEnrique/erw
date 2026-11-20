"""Audit of "What a generator earns", finding 4 (session 9841, docs/reviews/generator-model-audit-2026-11-20.md): an energy
contract "as generated" pays its price on the last twelve months' energy in every year of its term
(site/lib/seller/finance.ts, contractYear: cshare x cprice x energyKw, no year in it), while the plant's own output falls
by the degradation rate (revenueInYear, and the production credit, creditInYear, both degrade). For solar, 0.7 percent
a year over a 35-year PPA: the contract is paid for energy the plant no longer makes.

1. The page's library (run by Node), the default case (ERCOT solar, hub average, the public hourly file's last twelve
   months: R = 59.8523 per kW, E = 2.5799 MWh per kW): the breakeven PPA price is USD 58.36 per MWh, as the note says,
   and in year 35 the contract is paid on 2.5799 MWh per kW while the plant makes 2.5799 x 0.993^34.
2. Paid only for what the plant makes (the volume degraded as the plant's own), the price at which NPV is zero is
   USD 61.50 per MWh. It passes on main: it shows the fault. Nothing is written."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "seller", "finance.ts").replace("\\", "/")
R, E = 59.8523, 2.5799


class ContractPaysUndegradedEnergy(unittest.TestCase):
    def test_breakeven_ppa_counts_energy_the_plant_no_longer_makes(self):
        js = ("const F = await import(process.argv[1]);"
              "const a = F.defaultsOf({ capex: 1375, fom: 12.5, life: 35, deg: 0.7 });"
              f"const R = {R}, E = {E};"
              "const c = { kind: 'energy', energyKw: E, shape: 'generated', flat: null };"
              "const p = F.breakevenPpa(a, R, c, 100);"
              "const k = { ...a, cshare: 100, cprice: p };"
              "const at = (t) => F.incomeInYear(k, R, t, c);"
              # the same contract paid on the plant's own degrading volume: NPV zero by bisection
              "const flowsDeg = (price) => { const ds = F.debtService(a), out = [-a.capex * (1 - a.share / 100)];"
              "  for (let t = 1; t <= a.life; t++) out.push(price * E * (1 - a.deg / 100) ** (t - 1) - a.fom - (t <= F.debtYears(a) ? ds : 0)); return out; };"
              "let lo = 0, hi = 1000; for (let i = 0; i < 200; i++) { const m = (lo + hi) / 2; if (F.npv(a.hurdle, flowsDeg(m)) < 0) lo = m; else hi = m; }"
              "console.log(JSON.stringify({ deg: a.deg, life: a.life, p, y1: at(1), y35: at(35), npvAt: F.npv(a.hurdle, F.flows(k, R, c)), pDeg: lo }));")
        out = subprocess.run(["node", "--input-type=module", "-e", js, LIB], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual((r["deg"], r["life"]), (0.7, 35))
        self.assertAlmostEqual(r["p"], 58.36, places=2)                   # the note's figure
        self.assertAlmostEqual(r["npvAt"], 0.0, places=6)
        self.assertAlmostEqual(r["y1"], r["y35"], places=9)               # the contract pays the same in year 35 as in year 1
        self.assertAlmostEqual(r["y35"], r["p"] * E, places=6)            # on the undegraded energy
        self.assertAlmostEqual(r["pDeg"], 61.50, places=1)                # paid on what the plant makes
        self.assertGreater(r["pDeg"] - r["p"], 3.0)


if __name__ == "__main__":
    unittest.main()
