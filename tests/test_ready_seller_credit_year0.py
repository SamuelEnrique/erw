"""Session 11408, readied for the owner's ruling (weekend page part 3.4, generator choice 3; the generator audit of 20
November, finding 3, docs/reviews/generator-model-audit-2026-11-20.md, carried from wip/audit-generator-3): one timing
for the investment tax credit on both pages, year 0 against the equity paid in, as the battery page takes it.

Both libraries (run by Node), the same 4-hour battery at USD 1,110 and a 30 percent credit: each adds 333 to year 0
and nothing to year 1, so both raise NPV by 333.00 (the generator page gave 297.32). The default solar plant's credit is
worth 412.50 (it was 368.30). A production credit still starts in year 1. The decision and the note say year 0."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SELLER = "file:///" + os.path.join(ROOT, "site", "lib", "seller", "finance.ts").replace("\\", "/")
BATTERY = "file:///" + os.path.join(ROOT, "site", "lib", "battery", "finance.ts").replace("\\", "/")


class OneCreditYear(unittest.TestCase):
    def test_both_pages_take_the_credit_at_year_0(self):
        js = ("const S = await import(process.argv[1]); const B = await import(process.argv[2]);"
              "const s = S.defaultsOf({ capex: 1110, fom: 22, life: 20, deg: 2.6 });"
              "const b = B.defaultsOf({ capex: 1110, fom: 22 });"
              "const so = S.defaultsOf({ capex: 1375, fom: 12.5, life: 35, deg: 0.7 });"
              "const c = { kind: 'energy', energyKw: 2.5799, shape: 'generated', flat: null };"
              "const R = 81.4022;"
              "const sd = S.flows({ ...s, itc: 30 }, R).map((v, i) => v - S.flows(s, R)[i]);"
              "const bd = B.flows({ ...b, itc: 30 }, R).map((v, i) => v - B.flows(b, R)[i]);"
              "const pd = S.flows({ ...so, ptc: 10 }, 59.8523, c).map((v, i) => v - S.flows(so, 59.8523, c)[i]);"
              "console.log(JSON.stringify({ sd: sd.slice(0, 3), bd: bd.slice(0, 3), pd: pd.slice(0, 2),"
              " sNpv: S.npv(12, S.flows({ ...s, itc: 30 }, R)) - S.npv(12, S.flows(s, R)),"
              " solar: S.npv(12, S.flows({ ...so, itc: 30 }, 59.8523, c)) - S.npv(12, S.flows(so, 59.8523, c)) }));")
        out = subprocess.run(["node", "--input-type=module", "-e", js, SELLER, BATTERY], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        for d in (r["sd"], r["bd"]):
            self.assertAlmostEqual(d[0], 333.0, places=6)
            self.assertAlmostEqual(d[1], 0.0, places=6)
        self.assertAlmostEqual(r["sNpv"], 333.0, places=6)
        self.assertAlmostEqual(r["solar"], 412.50, places=6)
        self.assertAlmostEqual(r["pd"][0], 0.0, places=9)                 # no production credit at year 0
        self.assertAlmostEqual(r["pd"][1], 10 * 2.5799, places=6)          # it starts in year 1

    def test_the_words_say_year_0(self):
        for p in (("site", "lib", "decisions.ts"), ("docs", "methods", "generator_earns_algorithm.md")):
            with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
                text = f.read()
            self.assertIn("the ITC arrives at year 0, as on the battery page", text)
            self.assertNotIn("the ITC arrives in year 1", text)


if __name__ == "__main__":
    unittest.main()
