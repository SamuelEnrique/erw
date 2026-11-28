"""Session 11408, readied for the owner's ruling (weekend page part 3.4, battery choice 4; the battery audit of 20
November, finding 4, docs/reviews/battery-model-audit-2026-11-20.md, carried from wip/audit-battery-4): the revenue
cut's default is the model's own loss under Lazard's 2.6 percent capacity fade, 1.1 percent a year, not 2.6.

1. battery_stack.solve_day on every day of the page's last twelve months (the public dispatch file), 4 hours against
   4 x 0.974 hours: the faded battery keeps 1 - 1.1 percent of its revenue, to a tenth of a point.
2. The page's library (run by Node): the revenue cut defaults to 1.1, the fade method keeps 2.6, and the default NPV is
   USD -658.47 per kW at the headline 80.4016 (it was -704.23).
3. The decision and the note's section 12 say 1.1, word for word alike."""
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
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "battery", "finance.ts").replace("\\", "/")
R = 80.4016


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
            v = float(r[ix[f"price_{k}_usd_mw"]])
            a[k].append(v)
    return out


def revenue(ds, hours):
    tot = 0.0
    for d, (energy, prices) in ds.items():
        prods = [p for p in bs.MARKETS["ercot"]["products"] if (p["first"] is None or p["first"] <= d) and prices[p["key"]][0] != -999]
        spec = tuple((p["up"], bs.required_hours(p, d)[0]) for p in prods)
        tot += bs.solve_day(energy, [prices[p["key"]] for p in prods], spec, hours)["total"]
    return tot / 1000


class ModelFade(unittest.TestCase):
    def test_a_year_of_fade_costs_the_model_about_1_1_percent(self):
        ds = days()
        r0 = revenue(ds, 4.0)
        self.assertAlmostEqual(r0, R, delta=0.01)
        r1 = revenue(ds, 4.0 * 0.974)
        self.assertAlmostEqual(100 * (1 - r1 / r0), 1.1, delta=0.1)

    def test_the_page_defaults_to_the_model_fade(self):
        js = ("const F = await import(process.argv[1]);"
              "const d = F.defaultsOf({ capex: 1110, fom: 22 });"
              f"console.log(JSON.stringify({{ deg: d.deg, fade: d.fade, npv: F.npv(d.hurdle, F.flows(d, {R})) }}));")
        out = subprocess.run(["node", "--input-type=module", "-e", js, LIB], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual((r["deg"], r["fade"]), (1.1, 2.6))
        self.assertAlmostEqual(r["npv"], -658.47, places=2)

    def test_the_words_say_1_1(self):
        words = "15. Revenue falls by 1.1 percent a year for degradation, what the model itself loses"
        with open(os.path.join(ROOT, "docs", "methods", "battery_earns_algorithm.md"), encoding="utf-8") as f:
            self.assertIn(words, f.read())
        with open(os.path.join(ROOT, "site", "lib", "decisions.ts"), encoding="utf-8") as f:
            self.assertIn(words[4:], f.read())


if __name__ == "__main__":
    unittest.main()
