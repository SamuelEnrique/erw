"""Audit of "What a generator earns", finding 3 (session 9841, docs/reviews/generator-model-audit-2026-11-20.md): the two
pages that share one scenario block take the same investment tax credit in different years. The generator page in year
1 (site/lib/seller/finance.ts, creditInYear; its decision "the ITC arrives in year 1"), the battery page at year 0
against the equity paid in (site/lib/battery/finance.ts, flows). At 12 percent a year apart is 12 percent of the credit.

1. Both libraries (run by Node) with a 30 percent credit on the same 4-hour battery (capital USD 1,110 per kW): the
   battery page adds USD 333.00 to the year-0 flow; the generator page adds 333.00 to the year-1 flow.
2. Discounted at 12 percent the generator page's credit is worth 297.32 per kW, 35.68 less than the battery page's.
It passes on main: it shows the fault. Nothing is written."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SELLER = "file:///" + os.path.join(ROOT, "site", "lib", "seller", "finance.ts").replace("\\", "/")
BATTERY = "file:///" + os.path.join(ROOT, "site", "lib", "battery", "finance.ts").replace("\\", "/")


class CreditYear(unittest.TestCase):
    def test_same_credit_two_years(self):
        js = ("const S = await import(process.argv[1]); const B = await import(process.argv[2]);"
              "const s = S.defaultsOf({ capex: 1110, fom: 22, life: 20, deg: 2.6 });"
              "const b = B.defaultsOf({ capex: 1110, fom: 22 });"
              "const R = 81.4022;"
              "const sd = S.flows({ ...s, itc: 30 }, R).map((v, i) => v - S.flows(s, R)[i]);"
              "const bd = B.flows({ ...b, itc: 30 }, R).map((v, i) => v - B.flows(b, R)[i]);"
              "console.log(JSON.stringify({ sd: sd.slice(0, 3), bd: bd.slice(0, 3),"
              " sNpv: S.npv(12, S.flows({ ...s, itc: 30 }, R)) - S.npv(12, S.flows(s, R)), bNpv: B.npv(12, B.flows({ ...b, itc: 30 }, R)) - B.npv(12, B.flows(b, R)) }));")
        out = subprocess.run(["node", "--input-type=module", "-e", js, SELLER, BATTERY], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertAlmostEqual(r["bd"][0], 333.0, places=6)      # the battery page: at year 0
        self.assertAlmostEqual(r["bd"][1], 0.0, places=6)
        self.assertAlmostEqual(r["sd"][0], 0.0, places=6)        # the generator page: in year 1
        self.assertAlmostEqual(r["sd"][1], 333.0, places=6)
        self.assertAlmostEqual(r["bNpv"], 333.0, places=6)
        self.assertAlmostEqual(r["sNpv"], 297.32, places=2)


if __name__ == "__main__":
    unittest.main()
