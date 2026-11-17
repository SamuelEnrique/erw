"""Ruling alternative 3 of /learn/bill (session 7715, finished by session 7900, 17 November 2026, branch wip/alt-bill-3;
not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-bill-2026-11-17.md, line 3): weight the
wholesale price by the days of each month a meter-read span covers? On this branch the calculator takes two optional
read days and prices the wholesale bar by the span's months, each weighted by its days inside the span
(site/lib/bill.ts spanPrice, monthPrices); with no read days the bar reads one calendar month, as on main. Pinned with
the page's own library on the rows committed beside the replication (replication/bill/source_rows.csv, the live set of
16 November 2026), for the impact file's example span, 16 September to 15 October 2026 (15 days of each month):
PG&E's NP15 USD 44.85 to 47.48 per MWh (+5.9 percent; 600 kWh's wholesale USD 26.91 to 28.49); the Texas hub 39.50 to
41.06 (+4.0 percent; 23.70 to 24.64); SP15 38.52 to 38.50 (-0.04 percent).

    python -m unittest tests.test_alt_bill_3 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NP, SP, TX = "caiso:TH_NP15_GEN-APND", "caiso:TH_SP15_GEN-APND", "ercot:HB_HUBAVG"


class TheMeterReadSpan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-bill-3-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_main_reads_september_2026(self):
        for e, price in ((NP, 44.85), (SP, 38.52), (TX, 39.50)):
            m = self.f[e]["main"]
            self.assertEqual((m["month"], round(m["price"], 2), m["partial"]), ("2026-09", price, False))

    def test_the_span_weights_each_month_by_its_days(self):
        for e, main, span, pct in ((NP, 44.85, 47.48, 5.9), (TX, 39.50, 41.06, 4.0), (SP, 38.52, 38.50, -0.0)):
            s = self.f[e]["span"]
            self.assertEqual([(p["month"], p["days"]) for p in s["parts"]], [("2026-09", 15), ("2026-10", 15)])
            self.assertEqual(round(s["price"], 2), span)
            self.assertEqual(round((s["price"] / self.f[e]["main"]["price"] - 1) * 100, 1), pct)

    def test_the_wholesale_of_600_kwh(self):
        usd = lambda e, k: round(600 * self.f[e][k]["price"] / 1000, 2)
        self.assertEqual((usd(NP, "main"), usd(NP, "span")), (26.91, 28.49))
        self.assertEqual((usd(TX, "main"), usd(TX, "span")), (23.70, 24.64))
        self.assertEqual((usd(SP, "main"), usd(SP, "span")), (23.11, 23.10))

    def test_a_span_inside_one_month_is_that_month(self):
        for e in (NP, SP, TX):
            self.assertAlmostEqual(self.f[e]["one_month"]["price"], self.f[e]["main"]["price"], places=9)

    def test_a_month_not_held_or_days_out_of_order_leave_the_span_unpriced(self):
        for e in (NP, SP, TX):
            self.assertIsNone(self.f[e]["not_held"])
            self.assertIsNone(self.f[e]["out_of_order"])

    def test_the_calculator_draws_the_read_days_and_names_the_span(self):
        with open(os.path.join(SITE, "app", "learn", "bill", "BillCalc.tsx"), encoding="utf-8") as fh:
            calc = fh.read()
        self.assertIn('data-read-from="1"', calc)
        self.assertIn('data-read-to="1"', calc)
        self.assertIn("the read from ${readFrom} to ${readTo}", calc)
        self.assertIn("The span is not priced", calc)


if __name__ == "__main__":
    unittest.main()
