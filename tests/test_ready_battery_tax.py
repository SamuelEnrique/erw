"""Session 11408, readied for the owner's ruling (weekend page part 3.4, battery choice 8; the battery audit of 20
November, finding 8, docs/reviews/battery-model-audit-2026-11-20.md, carried from wip/audit-battery-8): the NPV to
equity after federal income tax (21 percent), with 5-year MACRS depreciation (half-year convention) on a basis cut by
half the investment tax credit, the debt's interest deductible and a loss used as it arises.

1. The page's library (site/lib/battery/finance.ts, run by Node) equals an independent mirror written here, at the
   page's headline revenue read from the public dispatch file (USD 80.4016 per kW, the file of 26 November):
   NPV -583.94 per kW with no credit (it was -704.23 with no tax), -276.74 with the 30 percent credit.
2. The credit's default is still 0; the headline revenue, coverage and toll do not move.
3. The decision and the note's section 12 say the NPV is after tax, word for word alike."""
import csv
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "battery", "finance.ts").replace("\\", "/")
CSV = os.path.join(ROOT, "site", "public", "battery", "erw_2026_battery_dispatch.csv")
NOTE = os.path.join(ROOT, "docs", "methods", "battery_earns_algorithm.md")
DECISIONS = os.path.join(ROOT, "site", "lib", "decisions.ts")
MACRS5 = [0.20, 0.32, 0.192, 0.1152, 0.1152, 0.0576]


def headline():
    with open(CSV, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    ix = {c: i for i, c in enumerate(rows[0])}
    tot = sum(float(r[ix["revenue_total_usd"]]) for r in rows[1:] if r[ix["in_last_twelve"]] == "1")
    return round(tot / 1000, 4)


def page(R):
    js = ("const F = await import(process.argv[1]);"
          "const a = F.defaultsOf({ capex: 1110, fom: 22 }); const R = Number(process.argv[2]);"
          "console.log(JSON.stringify({ a, base: F.npv(a.hurdle, F.flows(a, R)), credit: F.npv(a.hurdle, F.flows({ ...a, itc: 30 }, R)),"
          " cov: F.coverage(a, R), toll: F.breakevenToll(a), tax: F.TAX_RATE }));")
    out = subprocess.run(["node", "--input-type=module", "-e", js, LIB, str(R)], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return json.loads(out.stdout.strip().splitlines()[-1])


def mirror(a, R, itc, tax=0.21):
    rate, share, n = a["rate"] / 100, a["share"] / 100, min(a["term"], a["life"])
    ds = a["capex"] * share * rate / (1 - (1 + rate) ** -n)
    bal, basis = a["capex"] * share, a["capex"] * (1 - itc / 2)
    fl = [-a["capex"] * (1 - share) + a["capex"] * itc]
    for t in range(1, a["life"] + 1):
        rev = R * (1 - a["deg"] / 100) ** (t - 1)
        interest = bal * rate if t <= n else 0.0
        bal -= (ds - interest) if t <= n else 0.0
        dep = basis * MACRS5[t - 1] if t <= len(MACRS5) else 0.0
        fl.append(rev - a["fom"] - (ds if t <= n else 0.0) - tax * (rev - a["fom"] - interest - dep))
    return sum(f / (1 + a["hurdle"] / 100) ** t for t, f in enumerate(fl))


class AfterTax(unittest.TestCase):
    def test_the_library_is_after_tax(self):
        R = headline()
        self.assertAlmostEqual(R, 80.4016, places=4)
        p = page(R)
        self.assertEqual((p["a"]["itc"], p["tax"]), (0, 21))
        self.assertAlmostEqual(p["base"], mirror(p["a"], R, 0.0), places=6)
        self.assertAlmostEqual(p["credit"], mirror(p["a"], R, 0.30), places=6)
        self.assertAlmostEqual(p["base"], -583.94, places=2)
        self.assertAlmostEqual(p["credit"], -276.74, places=2)
        self.assertAlmostEqual(p["cov"], 2.5829, places=4)    # coverage does not move
        self.assertAlmostEqual(p["toll"], 4.1887, places=4)   # nor the toll

    def test_the_words_say_after_tax(self):
        words = "after the debt payments and federal income tax at 21 percent with 5-year depreciation"
        with open(NOTE, encoding="utf-8") as f:
            note = f.read()
        with open(DECISIONS, encoding="utf-8") as f:
            dec = f.read()
        self.assertIn("14. The NPV is to equity, " + words, note)
        self.assertIn("The NPV is to equity, " + words, dec)
        self.assertNotIn("No tax, no tax credit", note)


if __name__ == "__main__":
    unittest.main()
