"""Ruling alternative 4 of /learn/bill (session 7715, finished by session 7900, 17 November 2026, branch wip/alt-bill-4;
not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-bill-2026-11-17.md, line 4): count the energy
lost on the wires (about 5 percent) in the wholesale share, and set the Texas homes against their own load zone? On
this branch the losses half is built: the wholesale dollars are the metered kWh times 1.05 at the price point
(site/lib/bill.ts LOSS_FACTOR, wholesaleUsdOf), on the five cards and in the calculator. The load-zone half is not
built: ERCOT's zone prices are not in cost_of_power_monthly (data request row 209) nor on this machine. Pinned with the
page's own library on the rows committed beside the replication (replication/bill/source_rows.csv, the live set of
16 November 2026), at September 2026's prices: every wholesale figure +5 percent; the share PG&E 11.7 to 12.3 percent,
SCE 10.3 to 10.8, SDG&E 6.9 to 7.3, Oncor and CenterPoint 24.9 to 26.1. No bill total moves.

    python -m unittest tests.test_alt_bill_4 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")

# key: (total, main USD, other choice USD, main share, other choice share)
WANT = {
    "CA": (229.63, 26.91, 28.25, 11.7, 12.3),
    "SCE": (224.76, 23.11, 24.27, 10.3, 10.8),
    "SDGE": (332.91, 23.11, 24.27, 6.9, 7.3),
    "TX": (95.27, 23.70, 24.89, 24.9, 26.1),
    "TXC": (95.28, 23.70, 24.89, 24.9, 26.1),
}


class TheWiresLosses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-bill-4-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_factor(self):
        self.assertEqual(self.f["loss_factor"], 1.05)

    def test_the_five_cards(self):
        for key, want in WANT.items():
            b = self.f["bills"][key]
            self.assertEqual(b["month"], "2026-09")
            self.assertEqual(b["kwh"], 600)
            got = (round(b["total"], 2), round(b["main_usd"], 2), round(b["alt_usd"], 2), round(b["main_share"], 1), round(b["alt_share"], 1))
            self.assertEqual(got, want, key)

    def test_every_wholesale_figure_is_five_percent_higher(self):
        for b in self.f["bills"].values():
            self.assertAlmostEqual(b["alt_usd"] / b["main_usd"], 1.05, places=9)

    def test_the_page_and_the_calculator_use_the_one_function_and_say_so(self):
        for name, words in (("page.tsx", "percent lost on the wires."),("BillCalc.tsx", "the site&apos;s default counts the metered kWh only")):
            with open(os.path.join(SITE, "app", "learn", "bill", name), encoding="utf-8") as fh:
                text = fh.read()
            self.assertIn("wholesaleUsdOf(", text)
            self.assertIn(words, text)
            self.assertNotIn("kwh * w.price) / 1000", text)
            self.assertNotIn("kwh * w.row.value) / 1000", text)


if __name__ == "__main__":
    unittest.main()
