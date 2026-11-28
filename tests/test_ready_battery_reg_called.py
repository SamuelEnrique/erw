"""Session 11408, readied for the owner's ruling (weekend page part 3.4, battery choice 1; the battery audit of 20
November, finding 1, docs/reviews/battery-model-audit-2026-11-20.md, carried from wip/audit-battery-1): in ERCOT, 17
percent of a regulation award is called each hour (ERCOT's SCED storage telemetry), moving energy at the hour's price.

1. warehouse/derived/battery_stack.py: spec_of gives ERCOT's regulation a called share of 0.17 and every other product
   (and every other grid) 0; a spec without the share solves exactly as one with a share of 0 (the old program); with
   the share, the state of charge carries the called energy and check_day passes.
2. Re-solved on every day of the public dispatch file's last twelve months (November 2025 to October 2026) at 4 hours:
   USD 74.02 per kW, against the file's 80.40 (-7.9 percent, the audit's figure on this window); every day passes
   check_day. The table and the public file are rebuilt at landing by the desk.
3. The decision and the note's section 12 say so, word for word alike."""
import csv
import os
import sys
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import battery_stack as bs  # noqa: E402

CSV = os.path.join(ROOT, "site", "public", "battery", "erw_2026_battery_dispatch.csv")


def last_twelve():
    days = {}
    with open(CSV, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    ix = {c: i for i, c in enumerate(rows[0])}
    for r in rows[1:]:
        if r[ix["in_last_twelve"]] != "1":
            continue
        e, a = days.setdefault(r[ix["local_day"]], ([], {k: [] for k in ("regup", "regdn", "rrs", "ecrs", "nspin")}))
        e.append(float(r[ix["price_energy_usd_mwh"]]))
        for k in a:
            a[k].append(float(r[ix[f"price_{k}_usd_mw"]]))
    return days


class RegulationCalled(unittest.TestCase):
    def test_spec_of(self):
        prods = bs.MARKETS["ercot"]["products"]
        spec = bs.spec_of("ercot", prods, "2026-06-01")
        called = {p["key"]: s[2] for p, s in zip(prods, spec)}
        self.assertEqual((called["regup"], called["regdn"], called["rrs"], called["ecrs"], called["nspin"]), (0.17, 0.17, 0.0, 0.0, 0.0))
        self.assertTrue(all(s[2] == 0.0 for s in bs.spec_of("caiso", bs.MARKETS["caiso"]["products"], "2026-06-01")))

    def test_a_day_with_and_without_the_call(self):
        days = last_twelve()
        d = sorted(days)[100]
        energy, prices = days[d]
        prods = [p for p in bs.MARKETS["ercot"]["products"] if p["first"] is None or p["first"] <= d]
        old = tuple((p["up"], bs.required_hours(p, d)[0]) for p in prods)
        zero = tuple((u, h, 0.0) for u, h in old)
        new = bs.spec_of("ercot", prods, d)
        pr = [prices[p["key"]] for p in prods]
        a, b, c = (bs.solve_day(energy, pr, s, 4) for s in (old, zero, new))
        self.assertAlmostEqual(a["total"], b["total"], places=9)
        self.assertEqual(bs.check_day(c, new, 4), [])
        self.assertLessEqual(c["total"], a["total"] + 1e-9)
        eta = np.sqrt(bs.RTE)
        reg = [j for j, p in enumerate(prods) if p["key"] in ("regup", "regdn")]
        moved = sum(np.asarray(c["awards"][j]) * (-0.17 / eta if prods[j]["up"] else 0.17 * eta) for j in reg)
        self.assertTrue(np.allclose(c["soc"], np.cumsum(eta * c["charge"] - c["discharge"] / eta + moved)))

    def test_the_default_case_re_solved(self):
        tot, bad = 0.0, 0
        for d, (energy, prices) in last_twelve().items():
            prods = [p for p in bs.MARKETS["ercot"]["products"] if (p["first"] is None or p["first"] <= d) and prices[p["key"]][0] != -999]
            spec = bs.spec_of("ercot", prods, d)
            sol = bs.solve_day(energy, [prices[p["key"]] for p in prods], spec, 4)
            tot += sol["total"]
            bad += bool(bs.check_day(sol, spec, 4))
        self.assertAlmostEqual(tot / 1000, 74.02, places=2)
        self.assertEqual(bad, 0)

    def test_the_words(self):
        words = "in ERCOT 17 percent of a regulation award is called each hour and moves energy at the hour's price"
        with open(os.path.join(ROOT, "docs", "methods", "battery_earns_algorithm.md"), encoding="utf-8") as f:
            self.assertIn("4. The battery is a price taker, awarded up to its full power at the posted price; reserves are paid for being held; " + words, f.read())
        with open(os.path.join(ROOT, "site", "lib", "decisions.ts"), encoding="utf-8") as f:
            self.assertIn(words, f.read())


if __name__ == "__main__":
    unittest.main()
