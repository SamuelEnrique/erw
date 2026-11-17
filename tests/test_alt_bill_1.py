"""Ruling alternative 1 of /learn/bill (session 7715, 17 November 2026, branch wip/alt-bill-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-bill-2026-11-17.md, line 1): count a month
missing a single hour as whole, instead of falling back to the month before? On this branch the wholesale bar reads the
newest month at most one hour short (site/lib/bill.ts wholesaleMonth, MISSING_HOURS_WHOLE; the replication follows).
Nothing moves today (September 2026 is whole for all three price points). Pinned with the page's own library on the rows
committed beside the replication (replication/bill/source_rows.csv, the live set of 16 November 2026), cut at the end of
each month that missed one hour: NP15 as of October 2025 reads October's USD 42.76 per MWh where main fell back to
September's 46.43 (-7.9 percent); as of October 2024 52.58 against 34.30 (+53.3 percent); as of December 2025 36.99
against 46.43 (-20.3 percent); SP15 as of October 2025 29.97 against 36.36 (-17.6 percent).

    python -m unittest tests.test_alt_bill_1 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NP, SP, TX = "caiso:TH_NP15_GEN-APND", "caiso:TH_SP15_GEN-APND", "ercot:HB_HUBAVG"


class TheMonthOneHourShort(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-bill-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def got(self, e, m):
        x = self.f[e][m]
        return x["month"], round(x["price"], 2), x["partial"]

    def test_nothing_moves_today(self):
        for e, price in ((NP, 44.85), (SP, 38.52), (TX, 39.50)):
            self.assertEqual(self.got(e, "today"), ("2026-09", price, False))

    def test_the_months_one_hour_short_are_read(self):
        self.assertEqual(self.got(NP, "2025-10"), ("2025-10", 42.76, False))
        self.assertEqual(self.got(NP, "2024-10"), ("2024-10", 52.58, False))
        self.assertEqual(self.got(NP, "2025-12"), ("2025-12", 36.99, False))
        self.assertEqual(self.got(SP, "2025-10"), ("2025-10", 29.97, False))

    def test_the_rule(self):
        self.assertEqual(self.f["missing"], 1)


if __name__ == "__main__":
    unittest.main()
