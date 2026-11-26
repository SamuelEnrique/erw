"""Session 10210 (curtailment audit, finding 4): the default summary read ten months as a year, and the batteries'
sentence read as if they could not have taken the energy.

/curtailment opens on the newest year the profile holds: 2026, January to October. It said "In 2026, California
curtailed 4,944,663 MWh of solar ... 6.52 percent of its available wind and solar output", and the headline "Over 304 of
304 days, 10 months", beside 2025's twelve months at 4.53 percent. The twelve months to October 2026 give 5.98 percent:
part of the rise is November and December, months of little curtailment, left out. And "In October 2026, 91.54 percent of
that month's curtailment fell in hours in which the batteries were already charging": the code measures the curtailed
MWh in hours of net charging, two totals for the whole system, and the method note says the data does not show what
the batteries could have taken.

Words only (site/app/curtailment/page.tsx): the year is named with its months ("In 2026, January to October,") and the
batteries' sentence says what the hour is. No figure moves.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class SummaryWords(unittest.TestCase):
    def test_the_default_year_is_held_in_part(self):
        prof = json.loads(read("site", "data", "curtailment_profile.json"))
        newest = sorted(prof["years"])[-1]
        self.assertLess(prof["years"][newest]["months"], 12)

    def test_twelve_months_and_the_ten_give_different_shares(self):
        cs = json.loads(read("site", "data", "curtailment", "shares.json"))["grids"]["caiso"]["months"]
        share = lambda ms: 100 * sum(cs[m]["curtailed_mwh"] for m in ms) / sum(cs[m]["curtailed_mwh"] + cs[m]["output_mwh"] for m in ms)
        last12 = sorted(cs)[-12:]
        y = sorted(cs)[-1][:4]
        self.assertGreater(abs(share([m for m in cs if m.startswith(y)]) - share(last12)), 0.3)

    def test_the_page_names_the_months_and_says_what_the_battery_hour_is(self):
        p = read("site", "app", "curtailment", "page.tsx")
        self.assertIn("const spanOf = (period: string): string =>", p)
        self.assertIn("<>In {periodName(period)}{spanOf(period)}, California curtailed", p)
        self.assertIn("{r.months} months{spanOf(period)}", p)
        self.assertNotIn("were already charging", p)
        self.assertIn("hours in which the batteries took in more than they gave back; both are totals for the whole system", p)
        self.assertNotIn(chr(0x2014), p)


if __name__ == "__main__":
    unittest.main()
