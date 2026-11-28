"""wip/ready-reports-exporters (session 11406, chain 770, part C): the other choice of the reports audit of
26 November, finding 9 (docs/reviews/reports-model-audit-2026-11-26.md), the imports chart, readied for Samuel's
ruling, not requested.

On main the AI gigawatts draft's imports chart draws a net exporter at zero (Math.max(0, ...)) and labels it "0.0":
PJM, -3.00 percent in the table beside it, and SPP, -1.11, both "0.0" and both in the "best" green. On this branch the
chart's Bars draw a value below zero left of the axis, the label is the value ("-3.0", "-1.1"), and only the lowest
(PJM) takes the green. Charts with no value below zero draw as before (the axis at the left edge). The two values are
read from ai_power_regions where a copy is held (main copy, read only) and printed."""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AI = os.path.join(ROOT, "site", "app", "reports", "draft", "ai-gigawatts", "page.tsx")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def held(name):
    for d in (os.environ.get("ERW_AUDIT_OUTPUT"), os.path.join(ROOT, "warehouse", "output"), os.path.join(ROOT, "..", "erw", "warehouse", "output")):
        if d and os.path.exists(os.path.join(d, name + ".csv")):
            return os.path.join(d, name + ".csv")
    return None


def geometry(vals, W=640, L=80, R=110):
    """The page's Bars rule, in Python: the axis at zero, each bar from the axis to its value."""
    lo, hi = min([0] + vals), max([0] + vals)
    span = max(hi - lo, 1e-9)
    x = lambda v: L + (v - lo) / span * (W - L - R)  # noqa: E731
    z = x(0)
    return z, [(min(z, x(v)), max(1, abs(x(v) - z))) for v in vals]


class ExportersBelowZero(unittest.TestCase):
    def test_the_chart(self):
        s = read(AI)
        self.assertNotIn("Math.max(0, r.imp!.v)", s)
        self.assertIn('v: r.imp!.v }))} unit="percent of demand imported, net (an exporter below zero)" best="low"', s)
        self.assertIn("const x = (v: number) => L + ((v - lo) / span) * (W - L - R);", s)
        self.assertIn("<rect x={Math.min(z, x(it.v))}", s)

    def test_the_geometry(self):
        z, bars = geometry([20.0, 5.0, -3.0, -1.11])
        self.assertGreater(z, 80)
        self.assertLess(bars[2][0], z)                       # the exporter's bar starts left of the axis
        z0, bars0 = geometry([20.0, 5.0])
        self.assertEqual(z0, 80)                             # with no value below zero, the axis is at the left edge, as before
        self.assertAlmostEqual(bars0[0][1], 450.0)

    def test_the_two_exporters(self):
        p = held("ai_power_regions")
        if not p:
            self.skipTest("ai_power_regions is not held here")
        v = {}
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
                if r["variable"] == "net_import_share_pct" and r["entity"] in ("iso:pjm", "iso:spp"):
                    v[r["entity"]] = float(r["value"])
        print(f"net import share: PJM {v['iso:pjm']:.2f} (drawn '0.0' on main, '{v['iso:pjm']:.1f}' here), SPP {v['iso:spp']:.2f} ('{v['iso:spp']:.1f}')")
        self.assertLess(v["iso:pjm"], 0)
        self.assertLess(v["iso:spp"], 0)


if __name__ == "__main__":
    unittest.main()
