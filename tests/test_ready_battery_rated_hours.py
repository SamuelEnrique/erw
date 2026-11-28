"""Session 11408, readied for the owner's ruling (weekend page part 3.4, battery choice 10; the battery audit of 20
November, finding 10, docs/reviews/battery-model-audit-2026-11-20.md, carried from wip/audit-battery-10): a battery of
D hours delivers its rated power for D hours from full, as the page says (it stores D / sqrt(0.86)).

1. warehouse/derived/battery_stack.py: on a day that fills and empties the battery, solve_day delivers exactly D MWh
   per MW at 2, 4 and 8 hours (it delivered D x sqrt(0.86) until now), and check_day passes.
2. Re-solved on every day of the public dispatch file's last twelve months (November 2025 to October 2026) at 4 hours:
   USD 82.98 per kW, against the file's 80.40; no day delivers more than 4 MWh per MW; every day passes check_day.
   The table and the public file are rebuilt at landing by the desk.
3. The page's hover and the note say what is stored and what is delivered."""
import math
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import battery_stack as bs  # noqa: E402


class RatedHours(unittest.TestCase):
    def test_a_full_cycle_delivers_the_duration(self):
        energy = [0.0] * 12 + [100.0] * 12   # cheap mornings, dear evenings: fill, then empty
        for d in (2, 4, 8):
            sol = bs.solve_day(energy, [], (), d)
            self.assertAlmostEqual(sol["delivered"], d, places=6)
            self.assertAlmostEqual(max(sol["soc"]), d / math.sqrt(0.86), places=6)
            self.assertEqual(bs.check_day(sol, (), d), [])

    def test_the_default_case_re_solved(self):
        import csv
        csvp = os.path.join(ROOT, "site", "public", "battery", "erw_2026_battery_dispatch.csv")
        days = {}
        with open(csvp, encoding="utf-8") as f:
            rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
        ix = {c: i for i, c in enumerate(rows[0])}
        for r in rows[1:]:
            if r[ix["in_last_twelve"]] != "1":
                continue
            e, a = days.setdefault(r[ix["local_day"]], ([], {k: [] for k in ("regup", "regdn", "rrs", "ecrs", "nspin")}))
            e.append(float(r[ix["price_energy_usd_mwh"]]))
            for k in a:
                a[k].append(float(r[ix[f"price_{k}_usd_mw"]]))
        tot, most, bad = 0.0, 0.0, 0
        for d, (energy, prices) in days.items():
            prods = [p for p in bs.MARKETS["ercot"]["products"] if (p["first"] is None or p["first"] <= d) and prices[p["key"]][0] != -999]
            spec = tuple((p["up"], bs.required_hours(p, d)[0]) for p in prods)
            sol = bs.solve_day(energy, [prices[p["key"]] for p in prods], spec, 4)
            tot += sol["total"]
            most = max(most, sol["delivered"])
            bad += bool(bs.check_day(sol, spec, 4))
        self.assertAlmostEqual(tot / 1000, 82.98, places=2)
        self.assertLessEqual(most, 4 + 1e-6)
        self.assertEqual(bad, 0)

    def test_the_words(self):
        with open(os.path.join(ROOT, "site", "app", "cost-of-power", "battery", "BatteryForm.tsx"), encoding="utf-8") as f:
            self.assertIn("a 4-hour battery delivers 4 MWh for each MW, and stores 4.31", f.read())
        with open(os.path.join(ROOT, "docs", "methods", "battery_earns_algorithm.md"), encoding="utf-8") as f:
            self.assertIn("`0 <= s_t <= D / eta`", f.read())


if __name__ == "__main__":
    unittest.main()
