"""Session 7620: the other choice of the ruling on the contracted plant's worst month (branch wip/alt-seller-2, not
landed). On /cost-of-power/seller, "Scenarios A and B", the row "The worst month" of a scenario with an energy contract
took the lowest of every month held since July 2018 (December 2018: USD 750,064 for 200 MW contracted for all its
energy at USD 38 per MWh, coverage 0.46 times). Under the other choice it takes the last three years only: the 36
calendar months ending with the newest month held.

What is held to:
  the scenarios' code filters the held months to the 36 calendar months ending with the newest held month
    (LOWEST_YEARS = 3) before it finds a contracted scenario's worst month, and says the window in the note;
  recomputed from the page's public download (site/public/seller/erw_2026_generator_hourly.csv) through its published
    Python mirror, at the read's case (200 MW, all the energy at USD 38 per MWh): the window is 2023-10 to 2026-09 and
    the worst month December 2025, USD 1,016,595, coverage 0.69 times (+266,531 USD, +35.5 percent on the default's);
    every month held gives the default's December 2018, USD 750,064, 0.46 times;
  the merchant column keeps every month held (its worst month, February 2024, is inside both windows).

No request, no model call. Skips when the download is not on the machine."""
import importlib.util
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUB = os.path.join(ROOT, "site", "public", "seller")
CSV = os.path.join(PUB, "erw_2026_generator_hourly.csv")


def mirror():
    spec = importlib.util.spec_from_file_location("seller_mirror_7620", os.path.join(PUB, "erw_2026_generator_replication.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def prev(ym, k):
    y, mo = int(ym[:4]), int(ym[5:7]) - 1 - k
    y += mo // 12
    return f"{y}-{mo % 12 + 1:02d}"


class TheWorstMonthOfTheLastThreeYears(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(CSV):
            raise unittest.SkipTest("the seller's hourly download is not on this machine")
        cls.M = mirror()
        cls.table = cls.M.numbers(cls.M.read(CSV))["months"]

    def worst(self, mw, price, years):
        M = self.M
        debt = M.stata_round(M.CAPEX_USD_KW * 1000 * M.DEBT_SHARE * M.DEBT_RATE / (1 - (1 + M.DEBT_RATE) ** (-M.DEBT_YEARS)) * mw)
        held = [m for m in self.table if m["held"]]
        newest = max(m["ym"] for m in held)
        since = prev(newest, years * 12 - 1) if years else ""
        out = []
        for m in held:
            if m["ym"] < since:
                continue
            rev = (m["energy_mwh_per_mw"] * price if price is not None else m["revenue_usd_per_mw"]) * mw
            out.append((rev, m["ym"], (rev - M.FOM_USD_KW_YEAR * 1000 * mw / 12) / (debt / 12)))
        out.sort()
        return out[0], since, newest

    def test_the_other_choice_is_december_2025_at_1016595(self):
        (rev, ym, cover), since, newest = self.worst(200, 38.0, 3)
        self.assertEqual((since, newest), ("2023-10", "2026-09"))
        self.assertEqual((ym, round(rev), f"{cover:.2f}"), ("2025-12", 1016595, "0.69"))

    def test_every_month_held_gives_the_default_december_2018(self):
        (rev, ym, cover), _, _ = self.worst(200, 38.0, 0)
        self.assertEqual((ym, round(rev), f"{cover:.2f}"), ("2018-12", 750064, "0.46"))
        self.assertEqual(f"{100 * (1016595 - 750064) / 750064:.1f}", "35.5")

    def test_the_merchant_worst_month_is_in_both_windows(self):
        a, _, _ = self.worst(100, None, 0)
        b, _, _ = self.worst(100, None, 3)
        self.assertEqual(a[1], b[1])

    def test_the_page_takes_the_last_three_years(self):
        with open(os.path.join(ROOT, "site", "app", "cost-of-power", "seller", "SellerScenarios.tsx"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("export const LOWEST_YEARS = 3;", s)
        self.assertIn("(LOWEST_YEARS * 12 - 1), 1)).toISOString().slice(0, 7);", s)
        self.assertIn("f.heldMonths.filter((h) => h.m >= from).map(", s)
        self.assertIn("of the ${withIt.length} months of the last ${LOWEST_YEARS} years", s)
        self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
