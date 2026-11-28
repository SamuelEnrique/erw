"""wip/ready-reports-whole-month (session 11406, chain 770, part C): the other choice of the reports audit of
26 November, finding 2 (docs/reviews/reports-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main /reports/draft/shape-premium ranks its hubs on the newest month every open hub holds with any day-ahead hours,
and draws its hour profiles on the profile table's newest month, whole or not (on the copy of 4 October 2026: October
2026, 48 of 744 hours, CAISO -0.38, ERCOT 0.21, SPP 0.49 USD/MWh). On this branch both take the latest month whole at
every open hub (September 2026 on that copy: 0.81, 1.05, 3.44; ERCOT's dearest-to-cheapest hour 1.96 becomes 3.25).
The data test mirrors the page's rule on cost_of_power_monthly where a copy is held (ERW_AUDIT_OUTPUT, this worktree's
warehouse/output, or the main copy's, read only) and prints before and after. The audit's test
(tests/test_audit_reports_2.py on wip/audit-reports-2) is carried, turned round."""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "site", "app", "reports", "draft", "shape-premium", "page.tsx")
OPEN = ("caiso:TH_SP15_GEN-APND", "ercot:HB_HUBAVG", "spp:SPPNORTH_HUB")


def out_dir():
    for d in (os.environ.get("ERW_AUDIT_OUTPUT"), os.path.join(ROOT, "warehouse", "output"), os.path.join(ROOT, "..", "erw", "warehouse", "output")):
        if d and os.path.exists(os.path.join(d, "cost_of_power_monthly.csv")):
            return d
    return None


def src():
    with open(PAGE, encoding="utf-8") as f:
        return f.read()


class TheWholeMonth(unittest.TestCase):
    def test_the_page_asks_for_a_whole_month(self):
        s = src()
        self.assertIn('&& all.some((r) => r.entity === h.e && r.variable === "da_hours" && r.ts_utc.slice(0, 10) === ts', s)
        self.assertIn('x.variable === "hours_in_month" && x.ts_utc.slice(0, 10) === ts && x.value === r.value', s)
        self.assertIn("const pm = [...pmAll].reverse().find(wholeAt) ?? pmAll.at(-1)!;", s)
        self.assertNotIn("const pm = [...new Set(prof.map((r) => r.ts_utc.slice(0, 10)))].sort().at(-1)!;", s)

    def test_before_and_after_on_a_held_copy(self):
        d = out_dir()
        if not d:
            self.skipTest("cost_of_power_monthly is not held here")
        m = {}
        with open(os.path.join(d, "cost_of_power_monthly.csv"), encoding="utf-8") as f:
            for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
                if r["entity"] in OPEN:
                    m.setdefault((r["entity"], r["ts_utc"][:10]), {})[r["variable"]] = float(r["value"])
        months = sorted({ts for (e, ts), v in m.items() if "da_shape_premium" in v}, reverse=True)
        before = next(ts for ts in months if all("da_shape_premium" in m.get((e, ts), {}) for e in OPEN))
        after = next(ts for ts in months if all("da_shape_premium" in m.get((e, ts), {}) and m[(e, ts)].get("da_hours") == m[(e, ts)].get("hours_in_month") for e in OPEN))
        fmt = lambda ts: ", ".join(f"{e.split(':')[0]} {m[(e, ts)]['da_shape_premium']:.2f}" for e in OPEN)  # noqa: E731
        print(f"before {before} ({fmt(before)}); after {after} ({fmt(after)})")
        self.assertTrue(all(m[(e, after)]["da_hours"] == m[(e, after)]["hours_in_month"] for e in OPEN))
        if before == "2026-10-01" and after == "2026-09-01":   # the copy of 4 October 2026
            self.assertEqual([round(m[(e, after)]["da_shape_premium"], 2) for e in OPEN], [0.81, 1.05, 3.44])


if __name__ == "__main__":
    unittest.main()
