"""Session 11408, readied for the owner's ruling (weekend page part 3.4, battery choice 2; the battery audit of 20
November, finding 2, docs/reviews/battery-model-audit-2026-11-20.md, carried from wip/audit-battery-2): the charge is
carried over midnight within each local month.

1. warehouse/derived/battery_stack.py: blocks_of joins consecutive held days of one month with the same products and
   durations, and splits at a month, a gap or a change of durations; a one-day block solves exactly as solve_day; with
   CARRY False solve_days is solve_day day by day (the program until now).
2. Re-solved on every day of the public dispatch file's last twelve months (November 2025 to October 2026) at 4 hours:
   USD 85.90 per kW, against the file's 80.40 (+6.8 percent; the audit's +6.9 carried December whole), in 13 blocks;
   every day passes check_carried, and the state of charge at each block's later midnights is carried, not reset.
   The table, the public file and the scenario steps are rebuilt at landing by the desk.
3. The decision and the note's section 12 say so, word for word alike."""
import csv
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import battery_stack as bs  # noqa: E402

CSV = os.path.join(ROOT, "site", "public", "battery", "erw_2026_battery_dispatch.csv")


def items():
    out = {}
    with open(CSV, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    ix = {c: i for i, c in enumerate(rows[0])}
    for r in rows[1:]:
        if r[ix["in_last_twelve"]] != "1":
            continue
        e, a = out.setdefault(r[ix["local_day"]], ([], {k: [] for k in ("regup", "regdn", "rrs", "ecrs", "nspin")}))
        e.append(float(r[ix["price_energy_usd_mwh"]]))
        for k in a:
            a[k].append(float(r[ix[f"price_{k}_usd_mw"]]))
    res = []
    for d in sorted(out):
        energy, prices = out[d]
        prods = [p for p in bs.MARKETS["ercot"]["products"] if (p["first"] is None or p["first"] <= d) and prices[p["key"]][0] != -999]
        res.append((d, energy, [prices[p["key"]] for p in prods], tuple((p["up"], bs.required_hours(p, d)[0]) for p in prods)))
    return res


class Carried(unittest.TestCase):
    def test_blocks(self):
        it = items()
        blocks = bs.blocks_of(it)
        self.assertEqual(len(blocks), 13)
        for blk in blocks:
            self.assertEqual(len({d[:7] for d, *_ in blk}), 1)
            self.assertEqual(len({s for *_, s in blk}), 1)
        gap = [it[0], it[2]]
        self.assertEqual(len(bs.blocks_of(gap)), 2)

    def test_one_day_and_the_old_program(self):
        d, e, r, s = items()[40]
        self.assertAlmostEqual(bs.solve_block([(e, r, s)], 4)[0]["total"], bs.solve_day(e, r, s, 4)["total"], places=6)
        try:
            bs.CARRY = False
            old = bs.solve_days(items()[:10], 4)
        finally:
            bs.CARRY = True
        for d, e, r, s in items()[:10]:
            self.assertAlmostEqual(old[d]["total"], bs.solve_day(e, r, s, 4)["total"], places=9)

    def test_the_default_case_re_solved(self):
        it = items()
        sols = bs.solve_days(it, 4)      # raises if any day breaks a limit
        self.assertEqual(len(sols), len(it))
        self.assertAlmostEqual(sum(s["total"] for s in sols.values()) / 1000, 85.90, places=2)
        carried = [s["start"] for s in sols.values() if s["start"] > 1e-6]
        self.assertGreater(len(carried), 100)   # most midnights inside a block hold energy

    def test_the_words(self):
        words = "The battery starts empty at the first held day of a local month and carries its charge over each midnight to the month's end (session 11408)"
        with open(os.path.join(ROOT, "docs", "methods", "battery_earns_algorithm.md"), encoding="utf-8") as f:
            self.assertIn("2. " + words, f.read())
        with open(os.path.join(ROOT, "site", "lib", "decisions.ts"), encoding="utf-8") as f:
            self.assertIn(words, f.read())

    def test_build_market_on_one_month(self):
        """build_market itself, on January 2026 from the public file's prices (the same series as both strategies'):
        every day solved, and the month's sum equal to solve_days on the same days."""
        import pandas as pd
        with open(CSV, encoding="utf-8") as f:
            rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
        ix = {c: i for i, c in enumerate(rows[0])}
        keep = [r for r in rows[1:] if r[ix["local_month"]] == "2026-01"]
        idx = pd.DatetimeIndex([pd.Timestamp(r[ix["hour_utc"]]) for r in keep])
        e = pd.Series([float(r[ix["price_energy_usd_mwh"]]) for r in keep], index=idx)
        res = {k: pd.Series([float(r[ix[f"price_{k}_usd_mw"]]) for r in keep], index=idx) for k in ("regup", "regdn", "rrs", "ecrs", "nspin")}
        days, left = bs.build_market("ercot", {"rtm": e, "dam": e}, res, lambda *_: None)
        got = days[("foresight", 4)]
        self.assertEqual(len(got), 31)
        want = bs.solve_days([x for x in items() if x[0].startswith("2026-01")], 4)
        self.assertAlmostEqual(sum(v["total"] for v in got.values()), sum(s["total"] for s in want.values()), places=6)

    def test_the_builders_import(self):
        import battery_dispatch_export  # noqa: F401
        import battery_scenario_steps  # noqa: F401


if __name__ == "__main__":
    unittest.main()
