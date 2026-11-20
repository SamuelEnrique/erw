"""Audit of "What a battery earns", finding 6 (session 9840, docs/reviews/battery-model-audit-2026-11-20.md): the page
calls each figure an upper bound (decision 3, the year chart's sentence, the strategy's hover). Two of the model's own
rules hold the figure below what a battery that foresaw the prices could earn under every other rule of the model.

1. December 2025, the page's own prices (the public dispatch file): the model's days, each from empty, against the same
   program with the charge carried across midnight (tests/audit_battery_lp.py, checked equal to solve_day day by day).
   Session 9840 measured 7,893.88 against 7,076.31 USD per MW, +11.6 percent.
2. A day of flat hourly means with moving quarters: the hourly program earns nothing from energy, the quarter-priced one
   does (finding 3). Over the last twelve months both rules together give USD 88.81 per kW against 81.40.
These two pass on main: they show the fault.
3. The fix on this branch: no page text and no decision calls the figures an upper bound. This fails on main."""
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


def month_hours(month):
    out = {}
    with open(CSV, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    ix = {c: i for i, c in enumerate(rows[0])}
    for r in rows[1:]:
        if r[ix["local_month"]] != month:
            continue
        d = r[ix["local_day"]]
        prods = [p for p in bs.MARKETS["ercot"]["products"] if p["first"] is None or p["first"] <= d]
        out.setdefault(d, []).append(dict(day=d, p=[float(r[ix["price_energy_usd_mwh"]])], a=[float(r[ix[f"price_{p['key']}_usd_mw"]]) for p in prods],
                                          spec=tuple((p["up"], bs.required_hours(p, d)[0]) for p in prods), keys=[p["key"] for p in prods]))
    return out


class NotAnUpperBound(unittest.TestCase):
    def test_a_foreseeing_battery_earns_more_than_the_figure(self):
        days = month_hours("2025-12")
        self.assertEqual(len(days), 31)
        model = 0.0
        for d, hrs in sorted(days.items()):
            spec = hrs[0]["spec"]
            v = bs.solve_day([h["p"][0] for h in hrs], [[h["a"][k] for h in hrs] for k in range(len(spec))], spec, 4)["total"]
            self.assertAlmostEqual(solve_block(hrs, 4)["total"], v, places=4)
            model += v
        carried = solve_block([h for d in sorted(days) for h in days[d]], 4)["total"]
        self.assertGreater(carried, model * 1.05, f"carried {carried:.2f} against the model's {model:.2f} USD per MW")

    def test_quarters_inside_flat_hours(self):
        spec = ((True, 0.5),)
        hrs = [dict(day="2026-01-01", p=[20.0, 20.0, 60.0, 60.0], a=[0.0], spec=spec, keys=["regup"]) for _ in range(24)]
        hourly = solve_block([dict(h, p=[40.0]) for h in hrs], 4, q=1)
        quarter = solve_block(hrs, 4, q=4)
        self.assertGreater(quarter["total"], hourly["total"] + 20.0)

    def test_no_text_calls_the_figures_an_upper_bound(self):
        def read(*p):
            with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
                return f.read()
        self.assertNotIn("so each figure is an upper bound", read("site", "lib", "decisions.ts"))
        self.assertNotIn("so each figure is an upper bound", read("docs", "methods", "battery_earns_algorithm.md"))
        page = read("site", "app", "cost-of-power", "battery", "page.tsx")
        self.assertNotIn("This is an upper bound:", page)
        self.assertNotIn("An upper bound, not a forecast.", page)
        self.assertNotIn("an upper bound, not a forecast", read("site", "app", "cost-of-power", "battery", "BatteryForm.tsx"))


if __name__ == "__main__":
    unittest.main()
