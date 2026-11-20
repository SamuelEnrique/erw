"""Audit of "What a generator earns", findings 6 and 7 (session 9841, docs/reviews/generator-model-audit-2026-11-20.md),
both from the page's own public hourly file (site/public/seller/erw_2026_generator_hourly.csv), the default case (ERCOT
solar at the hub average). Each passes on main: it shows the fault. Nothing is written.

6. The merchant plant sells every hour, also below zero (warehouse/derived/merchant_revenue.py, build_iso: revenue =
   output x price over every hour with a value). In the page's last twelve months it sells 117.7 MWh per MW in 189
   negative hours, USD -0.41 per kW; a merchant plant that stops below zero earns 60.26, not 59.85.
7. Output per MW is the fleet's generation over the nameplate installed at the month's start (capacity(), the month's
   first day), so a plant that starts in the month adds its output and not its megawatts. Over the twelve months the
   fleet grew from 28,045 to 32,760 MW; with the month's mid-point nameplate (the mean of this and the next month's start)
   the twelve months earn 59.51, not 59.85, and 184 hours sit above the nameplate (up to 1.075 MWh per MW)."""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV = os.path.join(ROOT, "site", "public", "seller", "erw_2026_generator_hourly.csv")


def hours():
    with open(CSV, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    ix = {c: i for i, c in enumerate(rows[0])}
    out = []
    for r in rows[1:]:
        if r[ix["solar_mwh"]] == "-99999":
            continue
        out.append(dict(month=r[ix["local_month"]], p=float(r[ix["price_usd_mwh"]]), mwh=float(r[ix["solar_mwh"]]),
                        cap=float(r[ix["nameplate_mw"]]), l12=r[ix["in_last_twelve"]] == "1"))
    return out


class GeneratorShape(unittest.TestCase):
    def test_6_sells_below_zero(self):
        h = [x for x in hours() if x["l12"]]
        rev = sum(x["mwh"] / x["cap"] * x["p"] for x in h) / 1000
        neg = [x for x in h if x["p"] < 0]
        loss = sum(x["mwh"] / x["cap"] * x["p"] for x in neg) / 1000
        self.assertAlmostEqual(rev, 59.8523, places=3)                       # the page's headline
        self.assertEqual(sum(1 for x in neg if x["mwh"] > 0), 189)
        self.assertAlmostEqual(loss, -0.4076, places=3)
        self.assertAlmostEqual(rev - loss, 60.2599, places=3)

    def test_7_nameplate_at_the_months_start(self):
        allh = hours()
        cap = {}
        for x in allh:
            cap.setdefault(x["month"], x["cap"])
        months = sorted(cap)
        mid = {m: (cap[m] + cap[months[i + 1]]) / 2 if i + 1 < len(months) else cap[m] for i, m in enumerate(months)}
        h = [x for x in allh if x["l12"]]
        rev = sum(x["mwh"] / x["cap"] * x["p"] for x in h) / 1000
        rev_mid = sum(x["mwh"] / mid[x["month"]] * x["p"] for x in h) / 1000
        self.assertAlmostEqual(rev_mid, 59.5086, places=3)
        self.assertLess(rev_mid, rev - 0.3)
        self.assertEqual(sum(1 for x in h if x["mwh"] / x["cap"] > 1), 184)
        self.assertEqual((round(cap["2025-10"]), round(cap["2026-09"])), (28045, 32760))


if __name__ == "__main__":
    unittest.main()
