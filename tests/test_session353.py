"""Session 353 (the chain of 20 October 2026, night): /cost-of-power/seller. Two tax credits in Financing (0 by default),
a settlement point at a node (node_basis_summary, ERCOT), and the PPA's shape (as generated, the default, or a flat
block). Every default figure is what it was. Energy Research Warehouse (ERW)."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    if not os.path.isdir(os.path.join(ROOT, "site", "node_modules")):
        raise unittest.SkipTest("the site's packages are not here")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheArithmetic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = node("""
const F = await import('./lib/seller/finance.ts');
const d = F.defaultsOf({ capex: 1375, fom: 12.5, life: 35, deg: 0.7 });
const R = 59.85, E = 2.58, c = { kind: 'energy', energyKw: E };
const old = { ...d }; delete old.itc; delete old.ptc;
const npv = (a, cc = c) => F.npv(a.hurdle, F.flows(a, R, cc));
const k = { ...d, cshare: 50, cprice: 40 };
const blk = { ...c, shape: 'block', flat: 30 }, gen = { ...c, shape: 'generated', flat: 30 };
const itc = { ...d, itc: 30 }, ptc = { ...d, ptc: 25 };
console.log(JSON.stringify({
  same: JSON.stringify(F.flows(d, R, c)) === JSON.stringify(F.flows(old, R, c)),
  sameGen: JSON.stringify(F.flows(k, R, c)) === JSON.stringify(F.flows(k, R, gen)),
  itcGain: npv(itc) - npv(d), itcYear1: F.flows(itc, R, c)[1] - F.flows(d, R, c)[1],
  ptcY1: F.flows(ptc, R, c)[1] - F.flows(d, R, c)[1], ptcY2: F.flows(ptc, R, c)[2] - F.flows(d, R, c)[2],
  ptcY11: F.flows(ptc, R, c)[11] - F.flows(d, R, c)[11],
  cov: [F.coverage(itc, R, c), F.coverage(d, R, c)],
  blockY1: F.incomeInYear(k, R, 1, blk), genY1: F.incomeInYear(k, R, 1, gen),
  toll: F.incomeInYear(k, R, 1, { kind: 'toll', energyKw: E, shape: 'block', flat: 30 }) === F.incomeInYear(k, R, 1, { kind: 'toll', energyKw: E }),
  beZero: F.npv(itc.hurdle, F.flows({ ...itc, cshare: 100, cprice: F.breakevenPpa(itc, R, c) }, R, c)),
  bars0: F.sensitivity(d, R, c).map((b) => b.key), barsItc: F.sensitivity(itc, R, c).map((b) => b.key),
  params: ['ai', 'bx', 'az'].map(F.isScenarioParam),
}));
""")

    def test_the_default_is_what_it_was(self):
        self.assertTrue(self.out["same"])        # an older set of assumptions, without the credits, gives the same flows to the digit
        self.assertTrue(self.out["sameGen"])     # "generated" is the contract as it was
        self.assertEqual(sorted(self.out["bars0"]), sorted(["capex", "share", "rate", "term", "fom", "deg", "life", "hurdle"]))   # no credit's row at none

    def test_the_credits(self):
        self.assertAlmostEqual(self.out["itcYear1"], 0.3 * 1375, places=9)   # the ITC in year 1
        self.assertAlmostEqual(self.out["ptcY1"], 25 * 2.58, places=9)
        self.assertAlmostEqual(self.out["ptcY2"], 25 * 2.58 * 0.993, places=9)  # falling with the degradation
        self.assertAlmostEqual(self.out["ptcY11"], 0, places=9)              # ten years only
        self.assertAlmostEqual(self.out["cov"][0], self.out["cov"][1], places=12)   # not counted in coverage
        self.assertAlmostEqual(self.out["beZero"], 0, places=6)              # the breakeven PPA price reads the credit
        self.assertIn("itc", self.out["barsItc"])
        self.assertGreater(self.out["itcGain"], 0)
        self.assertEqual(self.out["params"], [True, True, False])

    def test_the_block(self):
        # a block: all the market revenue, the contract on the share, the hub's flat price paid on the share's energy
        self.assertAlmostEqual(self.out["blockY1"], 0.5 * 2.58 * 40 + 59.85 - 0.5 * 2.58 * 30, places=9)
        self.assertAlmostEqual(self.out["genY1"], 0.5 * 2.58 * 40 + 0.5 * 59.85, places=9)
        self.assertTrue(self.out["toll"])        # a toll has no shape


class ThePage(unittest.TestCase):
    def test_defaults_and_offers(self):
        fin = src("site", "lib", "seller", "finance.ts")
        self.assertIn("ppa: costs.life, itc: 0, ptc: 0 };", fin)
        self.assertIn("export const PTC_YEARS = 10;", fin)
        model = src("site", "app", "cost-of-power", "seller", "model.ts")
        self.assertIn('export const CREDITS_OF = (asset: string): ScenarioKey[] => (asset === "solar" || asset === "wind" ? ["itc", "ptc"] : asset === "battery" ? ["itc"] : []);', model)
        self.assertIn('const shape: "generated" | "block" = q.ps === "block" && fuel ? "block" : "generated";', model)
        self.assertIn("const nodeOffered = iso === \"ercot\" && mainHub && nbClass !== null && !win;", model)
        self.assertIn("const variable = `dam_${nbClass}_basis_${nbAsked}`;", model)
        self.assertIn("if (node && facts.twelve && !win) facts.twelve = {", model)
        scen = src("site", "app", "cost-of-power", "seller", "SellerScenarios.tsx")
        self.assertIn("for (const p of [\"a\", \"b\"] as View[]) for (const k of CREDIT_KEYS) if (!credits.includes(k)) start[p][k] = d[k];", scen)
        page = src("site", "app", "cost-of-power", "seller", "page.tsx")
        self.assertIn('<ParamChoice name="nb" value={M.nbAsked ?? ""} dflt=""', page)
        self.assertIn('<ParamChoice name="ps" value={M.shape} dflt="generated"', page)
        self.assertIn("check={`series|node_basis_summary|ercot:${cg.main}|${M.node!.variable}|${r.ts}`}", page)
        comp = src("site", "components", "tool", "ParamChoice.tsx")
        self.assertIn("if (id === dflt) q.delete(name); else q.set(name, id);", comp)
        form = src("site", "app", "cost-of-power", "seller", "SellerForm.tsx")
        self.assertIn('<span className="mb-1 block font-semibold">Settlement point</span>', form)
        self.assertIn('<optgroup label="Load zones">', form)

    def test_no_em_dash(self):
        for parts in (("site", "lib", "seller", "finance.ts"), ("site", "app", "cost-of-power", "seller", "model.ts"), ("site", "app", "cost-of-power", "seller", "page.tsx"),
                      ("site", "app", "cost-of-power", "seller", "SellerScenarios.tsx"), ("site", "app", "cost-of-power", "seller", "SellerForm.tsx"),
                      ("site", "components", "tool", "ParamChoice.tsx"), ("tests", "test_session353.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
