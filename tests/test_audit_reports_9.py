"""Session 10232, the report library audit (docs/reviews/reports-model-audit-2026-11-26.md), finding 9. Shows the
finding; not for landing (a fix changes what the charts and figures show: Samuel's ruling, default left as it is).

Three things a reader sees that the rows do not say:
- the AI gigawatts draft's imports chart draws a net exporter at zero (Math.max(0, ...)) and labels the bar "0.0":
  PJM, -3.00 percent in the table beside it, and SPP, -1.11, both read "0.0", and both bars take the "best" green;
- the shape-premium draft's ERCOT chart places its bars by order, not by date, so the four months that are not complete
  (on the copy of 4 October 2026: 2018-07, 2018-11, 2025-12, 2026-10) leave no gap, and the year labels drift;
- tonnes of CO2 and megawatts are shown to the hundredth (1,250,885.79 tonnes, 408,002.06 MW), a precision the
  measures do not have.

The data test reads the tables from ERW_AUDIT_OUTPUT (or warehouse/output) and is skipped where they are not held.
"""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AI = os.path.join(ROOT, "site", "app", "reports", "draft", "ai-gigawatts", "page.tsx")
SP = os.path.join(ROOT, "site", "app", "reports", "draft", "shape-premium", "page.tsx")
OUT = os.environ.get("ERW_AUDIT_OUTPUT") or os.path.join(ROOT, "warehouse", "output")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


class WhatTheChartsDraw(unittest.TestCase):
    def test_exporters_are_drawn_at_zero(self):
        s = read(AI)
        self.assertIn("v: Math.max(0, r.imp!.v)", s)
        self.assertIn('unit="percent of demand imported, net (exporters at 0)" best="low"', s)
        self.assertIn('fill={it.v === bestV ? "var(--color-down)" : "var(--color-accent)"}', s)

    def test_the_month_bars_are_placed_by_order(self):
        s = read(SP)
        self.assertIn("const bw = (W - L - R) / ms.length;", s)
        self.assertIn("<rect x={L + i * bw + 0.5}", s)

    def test_tonnes_are_shown_to_the_hundredth(self):
        s = read(AI)
        self.assertIn("const N = ({ x }: { x?: V }) => (x ? <Num check={x.k} raw={x.v}>{shown(x.v)}</Num>", s)
        self.assertIn("<N x={ci0.co2} /> tonnes of CO2", s)

    @unittest.skipUnless(os.path.exists(os.path.join(OUT, "ai_power_regions.csv")), "ai_power_regions not held here")
    def test_two_shown_regions_are_net_exporters(self):
        neg = []
        with open(os.path.join(OUT, "ai_power_regions.csv"), encoding="utf-8") as f:
            for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
                if r["variable"] == "net_import_share_pct" and float(r["value"]) < 0 and r["entity"] in ("iso:pjm", "iso:spp"):
                    neg.append(r["entity"])
        self.assertEqual(sorted(neg), ["iso:pjm", "iso:spp"])

    @unittest.skipUnless(os.path.exists(os.path.join(OUT, "cost_of_power_monthly.csv")), "cost_of_power_monthly not held here")
    def test_ercot_has_months_that_are_not_complete(self):
        m = {}
        with open(os.path.join(OUT, "cost_of_power_monthly.csv"), encoding="utf-8") as f:
            for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
                if r["entity"] == "ercot:HB_HUBAVG":
                    m.setdefault(r["ts_utc"][:10], {})[r["variable"]] = float(r["value"])
        gaps = [ts for ts, v in m.items() if "rt_shape_premium" in v and v.get("rt_hours") != v.get("hours_in_month")]
        self.assertGreaterEqual(len(gaps), 2)


if __name__ == "__main__":
    unittest.main()
