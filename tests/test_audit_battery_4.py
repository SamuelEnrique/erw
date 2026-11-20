"""Audit of "What a battery earns", finding 4 (session 9840, docs/reviews/battery-model-audit-2026-11-20.md): degradation is
applied as a cut to the whole revenue, 2.6 percent a year (site/lib/battery/finance.ts, revenueInYear), but Lazard's 2.6
percent is a fade of the battery's energy capacity, and the model itself says revenue does not follow capacity one for one.

1. battery_stack.solve_day on every day of the page's last twelve months at 4 hours, at 4 x 0.974 (a year of fade) and
   at 4 x 0.974^19 (year 20): the faded battery keeps 98.9 and 79.3 percent of its revenue (session 9840), where the
   page keeps 97.4 and 60.6.
2. The page's own library (finance.ts, run by Node) gives R x 0.974^(t - 1) under both of its methods: the revenue cut,
   and the capacity fade with no augmentation ("revenue follows the capacity").
It passes on the code as it is: it shows the fault. Nothing is written."""
import csv
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import battery_stack as bs  # noqa: E402

CSV = os.path.join(ROOT, "site", "public", "battery", "erw_2026_battery_dispatch.csv")


def days():
    out = {}
    with open(CSV, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    ix = {c: i for i, c in enumerate(rows[0])}
    for r in rows[1:]:
        if r[ix["in_last_twelve"]] != "1":
            continue
        d = r[ix["local_day"]]
        e, a = out.setdefault(d, ([], {k: [] for k in ("regup", "regdn", "rrs", "ecrs", "nspin")}))
        e.append(float(r[ix["price_energy_usd_mwh"]]))
        for k in a:
            a[k].append(float(r[ix[f"price_{k}_usd_mw"]]))
    return out


def revenue(ds, hours):
    tot = 0.0
    for d, (energy, prices) in ds.items():
        prods = [p for p in bs.MARKETS["ercot"]["products"] if p["first"] is None or p["first"] <= d]
        spec = tuple((p["up"], bs.required_hours(p, d)[0]) for p in prods)
        tot += bs.solve_day(energy, [prices[p["key"]] for p in prods], spec, hours)["total"]
    return tot / 1000


class Degradation(unittest.TestCase):
    def test_model_revenue_does_not_follow_capacity(self):
        ds = days()
        r0 = revenue(ds, 4.0)
        self.assertAlmostEqual(r0, 81.4022, places=3)
        r1 = revenue(ds, 4.0 * 0.974)
        r19 = revenue(ds, 4.0 * 0.974 ** 19)
        self.assertGreater(r1 / r0, 0.985, f"a year of fade keeps {100 * r1 / r0:.2f} percent")    # 98.91 measured
        self.assertGreater(r19 / r0, 0.75, f"year 20 keeps {100 * r19 / r0:.2f} percent")         # 79.34 measured
        self.assertLess(0.974 ** 19, 0.61)                                                         # the page keeps 60.62

    def test_page_cuts_revenue_one_for_one(self):
        js = ("const F = await import(process.argv[1]);"
              "const d = F.defaultsOf({ capex: 1110, fom: 22 });"
              "const fade = { ...d, method: 1, aug: 0 };"
              "console.log(JSON.stringify([2, 20].map((t) => [F.revenueInYear(d, 81.4022, t), F.revenueInYear(fade, 81.4022, t)])));")
        lib = "file:///" + os.path.join(ROOT, "site", "lib", "battery", "finance.ts").replace("\\", "/")
        out = subprocess.run(["node", "--input-type=module", "-e", js, lib], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        (c2, f2), (c20, f20) = json.loads(out.stdout.strip().splitlines()[-1])
        for v, t in ((c2, 2), (f2, 2), (c20, 20), (f20, 20)):
            self.assertAlmostEqual(v, 81.4022 * 0.974 ** (t - 1), places=6)


if __name__ == "__main__":
    unittest.main()
