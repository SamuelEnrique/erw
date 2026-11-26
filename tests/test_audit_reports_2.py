"""Session 10232, the report library audit (docs/reviews/reports-model-audit-2026-11-26.md), finding 2. Shows the
finding; not for landing (a fix moves figures: Samuel's ruling, default left as it is).

/reports/draft/shape-premium ranks its hubs ("Six ISOs, <month>") on the newest month every open hub holds with any
day-ahead hours, complete or not, and draws its hour-of-day profiles ("Where in the day") on the profile table's newest
month, complete or not. On the warehouse's copy of 4 October 2026 that month is October 2026 with 48 of 744 hours (two
days): CAISO -0.38, ERCOT 0.21, SPP 0.49 USD/MWh. The latest month complete at all three (September 2026) reads 0.81,
1.05 and 3.44; ERCOT's dearest-to-cheapest ratio reads 1.96 on the two days and 3.25 on September.

The data test reads cost_of_power_monthly from ERW_AUDIT_OUTPUT (or warehouse/output) and is skipped where the table is
not held, as on GitHub's runner.
"""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "site", "app", "reports", "draft", "shape-premium", "page.tsx")
OUT = os.environ.get("ERW_AUDIT_OUTPUT") or os.path.join(ROOT, "warehouse", "output")
OPEN = ("caiso:TH_SP15_GEN-APND", "ercot:HB_HUBAVG", "spp:SPPNORTH_HUB")


def src():
    with open(PAGE, encoding="utf-8") as f:
        return f.read()


class TheNewestMonthIsTakenWhateverItsHours(unittest.TestCase):
    def test_the_ranked_month_asks_only_for_a_row(self):
        s = src()
        line = [ln for ln in s.splitlines() if "OPEN.every((h) => all.some((r) => r.entity === h.e && r.variable === \"da_shape_premium\"" in ln]
        self.assertEqual(len(line), 1)
        self.assertNotIn("hours_in_month", line[0])
        self.assertNotIn("da_hours", line[0])

    def test_the_profile_month_is_the_newest_held(self):
        self.assertIn("const pm = [...new Set(prof.map((r) => r.ts_utc.slice(0, 10)))].sort().at(-1)!;", src())

    @unittest.skipUnless(os.path.exists(os.path.join(OUT, "cost_of_power_monthly.csv")), "cost_of_power_monthly not held here")
    def test_on_the_held_copy_the_ranked_month_is_partial(self):
        m = {}
        with open(os.path.join(OUT, "cost_of_power_monthly.csv"), encoding="utf-8") as f:
            for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
                m.setdefault((r["entity"], r["ts_utc"][:10]), {})[r["variable"]] = float(r["value"])
        months = sorted({ts for (e, ts), v in m.items() if "da_shape_premium" in v}, reverse=True)
        latest = next(ts for ts in months if all("da_shape_premium" in m.get((e, ts), {}) for e in OPEN))
        partial = [e for e in OPEN if m[(e, latest)]["da_hours"] < m[(e, latest)]["hours_in_month"]]
        # the page's own rule lands on a month some hub holds only in part (on the copy of 4 October 2026: 48 of 744 hours)
        if not partial:
            self.skipTest(f"the held copy's newest month {latest} is complete at every open hub")
        self.assertTrue(partial)


if __name__ == "__main__":
    unittest.main()
