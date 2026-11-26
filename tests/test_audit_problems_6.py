"""Session 10229 (the problems audit, finding 7; a figure, not for landing). The California default bills of /learn/bill
are winter bills (Samuel's ruling of 14 October 2026: every California default in the season of 1 October 2026), and
their wholesale energy is valued at the latest complete month, September 2026, which is PG&E's summer (June 1 through
September 30, E-TOU-C). The same is "Prices and your bill" question 3. This test shows the size of that mismatch from the
live rows kept in replication/bill/source_rows.csv and site/data/bill_rules.json; it passes on main and changes nothing.
For Samuel's ruling, default "left as it is": at the mean of the winter months held (October 2025 to May 2026) the share
is 8.08 percent, not 11.72; the September price against PG&E's summer bill gives 10.26.
"""
import csv
import json
import os
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ROWS = os.path.join(ROOT, "replication", "bill", "source_rows.csv")
RULES = os.path.join(ROOT, "site", "data", "bill_rules.json")
ENT = "caiso:TH_NP15_GEN-APND"


def bill(ca, season):
    d = ca["defaults"]
    kwh, ps, days = d["kwh"], d["peak_share"], d["days"]
    base = min(kwh, ca["baseline_quantities"]["code_B"][d["territory"]][0 if season == "summer" else 1] * days)
    s = ca["seasons"][season]
    return kwh * (ps * s["peak"] + (1 - ps) * s["offpeak"]) + base * ca["baseline_credit"]["rate"] + days * ca["base_services"]["tiers"][d["income_tier"]]


class AWinterBillAtASummerPrice(unittest.TestCase):
    def setUp(self):
        self.ca = json.load(open(RULES, encoding="utf-8"))["bills"]["CA"]
        self.lw = {}
        with open(ROWS, encoding="utf-8") as f:
            for r in csv.DictReader(line for line in f if not line.startswith("#")):
                if r["entity"] == ENT and r["variable"] == "rt_load_weighted":
                    self.lw[r["ts_utc"][:7]] = float(r["value"])

    def test_the_default_is_winter_and_the_month_is_summer(self):
        self.assertEqual(self.ca["defaults"]["season"], "winter")
        self.assertIn("June 1 through September 30", self.ca["seasons"]["summer"]["label"])
        self.assertIn("2026-09", self.lw)

    def test_the_size(self):
        win, summer = bill(self.ca, "winter"), bill(self.ca, "summer")
        self.assertEqual((round(win, 2), round(summer, 2)), (229.63, 262.33))
        sep = 600 * self.lw["2026-09"] / 1000
        self.assertEqual(round(sep, 2), 26.91)
        self.assertEqual(round(sep / win * 100, 2), 11.72)          # the page's share
        self.assertEqual(round(sep / summer * 100, 2), 10.26)       # September's price against the summer bill
        months = [m for m in self.lw if "2025-10" <= m <= "2026-05"]
        self.assertEqual(len(months), 8)
        winter = 600 * sum(self.lw[m] for m in months) / len(months) / 1000
        self.assertEqual(round(winter, 2), 18.54)
        self.assertEqual(round(winter / win * 100, 2), 8.08)        # the winter months' mean against the winter bill


if __name__ == "__main__":
    unittest.main()
