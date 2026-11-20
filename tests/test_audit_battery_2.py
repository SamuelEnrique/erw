"""Audit of "What a battery earns", finding 2 (session 9840, docs/reviews/battery-model-audit-2026-11-20.md): each local
day starts empty and what is left at midnight is lost. The note (section 5) bounds what this costs by the first hour's
upward reserves, USD 1.29 per kW over the last twelve months. The test measures the whole cost on the page's own prices.

1. The restatement (tests/audit_battery_lp.py) is the model's own program: with each day from empty it equals
   battery_stack.solve_day on every day of the last twelve months.
2. The same program with the state of charge carried across midnight inside each calendar month (one cycle a local day,
   86 percent, the day's required durations, hourly: every other rule the model's) earns USD 86.63 per kW against the
   page's 81.40: four times the note's bound.
It passes on the code as it is: it shows the fault. Nothing is written."""
import csv
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import battery_stack as bs  # noqa: E402
from audit_battery_lp import solve_block  # noqa: E402

CSV = os.path.join(ROOT, "site", "public", "battery", "erw_2026_battery_dispatch.csv")
KEYS = ("regup", "regdn", "rrs", "ecrs", "nspin")


def hours_by_day():
    """{local day: [hour dicts]} for the file's last twelve months, in the restatement's form, and the first-hour bound."""
    out, bound = {}, 0.0
    with open(CSV, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    ix = {c: i for i, c in enumerate(rows[0])}
    for r in rows[1:]:
        if r[ix["in_last_twelve"]] != "1":
            continue
        d = r[ix["local_day"]]
        prods = [p for p in bs.MARKETS["ercot"]["products"] if p["first"] is None or p["first"] <= d]
        spec = tuple((p["up"], bs.required_hours(p, d)[0]) for p in prods)
        a = [float(r[ix[f"price_{p['key']}_usd_mw"]]) for p in prods]
        out.setdefault(d, []).append(dict(day=d, p=[float(r[ix["price_energy_usd_mwh"]])], a=a, spec=spec,
                                          keys=[p["key"] for p in prods]))
        if r[ix["hour_of_day"]] == "0":
            bound += max(x for p, x in zip(prods, a) if p["up"])
    return out, bound / 1000


class MidnightReset(unittest.TestCase):
    def test_reset_costs_four_times_the_notes_bound(self):
        days, bound = hours_by_day()
        self.assertEqual(len(days), 365)
        self.assertAlmostEqual(bound, 1.29, places=2)                 # the note's section 5 figure
        daily = 0.0
        for d, hrs in sorted(days.items()):
            spec = hrs[0]["spec"]
            model = bs.solve_day([h["p"][0] for h in hrs], [[h["a"][k] for h in hrs] for k in range(len(spec))], spec, 4)["total"]
            mine = solve_block(hrs, 4)["total"]
            self.assertAlmostEqual(mine, model, places=4)             # the restatement is the model's program
            daily += model
        self.assertAlmostEqual(daily / 1000, 81.4022, places=3)       # the page's headline
        carried = 0.0
        for m in sorted({d[:7] for d in days}):
            carried += solve_block([h for d in sorted(days) if d[:7] == m for h in days[d]], 4)["total"]
        gain = (carried - daily) / 1000
        # session 9840 measured 86.6324 - 81.4022 = 5.23 per kW, 6.4 percent
        self.assertGreater(gain, 4 * bound, f"carrying the charge across midnight adds {gain:.2f} per kW; the note bounds it at {bound:.2f}")


if __name__ == "__main__":
    unittest.main()
