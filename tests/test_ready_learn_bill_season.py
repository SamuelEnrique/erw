"""Session 11407 (chain 770, part C): the owner's other choice on the problems audit's finding 7 (session 10229,
docs/reviews/problems-model-audit-2026-11-26.md; the audit's test was tests/test_audit_problems_6.py on
wip/audit-problems-6), readied, not landed until Samuel rules.

The California default bills of /learn/bill are winter bills (Samuel's ruling of 14 October 2026), and on origin/main
their wholesale energy is valued at the latest complete month, September 2026, the last month of PG&E's summer; so is
"Prices and your bill" question 3. On this branch a bill whose tariff has seasons (wholesale_season_months in
site/data/bill_rules.json: PG&E and SCE; SDG&E's change of season was not read as a date) is set against the plain
mean of the load-weighted real-time price over its own season's months among the twelve months that end with the
latest complete month (lib/bill.ts, wholesaleFor; the calculator takes the season the reader picks). On the live rows
kept in replication/bill/source_rows.csv: PG&E's share 11.72 percent becomes 8.08 (26.91 USD to 18.54), SCE's 10.28
becomes 6.53. The page figures kept in replication/bill/ and replication/problem_sets/ were drawn with the site's own
code on this branch (site/scripts/bill-figures.mjs; problem-sets-figures.mjs replay, question B3 carried over)."""
import csv
import json
import os
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ROWS = os.path.join(ROOT, "replication", "bill", "source_rows.csv")
RULES = os.path.join(ROOT, "site", "data", "bill_rules.json")
NP15, SP15 = "caiso:TH_NP15_GEN-APND", "caiso:TH_SP15_GEN-APND"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def bill(ca, season):
    d = ca["defaults"]
    kwh, ps, days = d["kwh"], d["peak_share"], d["days"]
    base = min(kwh, ca["baseline_quantities"]["code_B"][d["territory"]][0 if season == "summer" else 1] * days)
    s = ca["seasons"][season]
    return kwh * (ps * s["peak"] + (1 - ps) * s["offpeak"]) + base * ca["baseline_credit"]["rate"] + days * ca["base_services"]["tiers"][d["income_tier"]]


class AWinterBillAtItsOwnSeasonsPrice(unittest.TestCase):
    def setUp(self):
        self.rules = load(RULES)["bills"]
        self.ca = self.rules["CA"]
        self.lw = {}
        with open(ROWS, encoding="utf-8") as f:
            for r in csv.DictReader(line for line in f if not line.startswith("#")):
                if r["variable"] == "rt_load_weighted":
                    self.lw[(r["entity"], r["ts_utc"][:7])] = float(r["value"])

    def season_mean(self, ent, months, end="2026-09"):
        n = lambda m: int(m[:4]) * 12 + int(m[5:7]) - 1  # noqa: E731
        got = [v for (e, m), v in self.lw.items() if e == ent and n(end) - 12 < n(m) <= n(end) and n(m) % 12 + 1 in months]
        return sum(got) / len(got), len(got)

    def test_the_rules_carry_the_seasons(self):
        self.assertEqual(self.ca["defaults"]["season"], "winter")
        for k in ("CA", "SCE"):
            sm = self.rules[k]["wholesale_season_months"]
            self.assertEqual((sm["summer"], sm["winter"]), ([6, 7, 8, 9], [10, 11, 12, 1, 2, 3, 4, 5]), k)
        self.assertIn("June 1 through September 30", self.ca["seasons"]["summer"]["label"])
        self.assertIn("June 1 and continue until 12:00 a.m. on October 1", self.rules["SCE"]["periods"]["seasons"])
        for k in ("SDGE", "TX", "TXC"):
            self.assertNotIn("wholesale_season_months", self.rules[k], k)

    def test_the_new_figures(self):
        win = bill(self.ca, "winter")
        self.assertEqual(round(win, 2), 229.63)
        price, n = self.season_mean(NP15, self.ca["wholesale_season_months"]["winter"])
        self.assertEqual(n, 8)                                  # October 2025 to May 2026
        self.assertEqual(round(price, 2), 30.91)
        self.assertEqual(round(600 * price / 1000, 2), 18.54)
        self.assertEqual(round(600 * price / 1000 / win * 100, 2), 8.08)     # the share, on this branch
        self.assertEqual(round(600 * self.lw[(NP15, "2026-09")] / 1000 / win * 100, 2), 11.72)  # origin/main's

    def test_the_page_prints_them(self):
        figs = load(os.path.join(ROOT, "replication", "bill", "page_figures.json"))
        page = {f["key"]: f["shown"] for c in figs["cases"] if c["id"] == "page" for f in c["figures"]}
        months = "2025-10 to 2026-05, the mean of the 8 winter months held in the twelve to 2026-09"
        self.assertEqual((page["card|CA|wholesale_usd"], page["card|CA|share_pct"], page["card|CA|price"], page["card|CA|month"]), ("18.54", "8.08", "30.91", months))
        self.assertEqual((page["card|SCE|share_pct"], page["card|SCE|price"], page["card|SCE|month"]), ("6.53", "24.48", months))
        self.assertEqual((page["card|SDGE|price"], page["card|SDGE|month"]), ("38.52", "2026-09"))   # no season read
        self.assertEqual(page["card|TX|month"], "2026-09")
        self.assertEqual((page["opens|bar|price"], page["opens|bar|share_pct"]), ("30.91", "8"))
        summer = {f["key"]: f["shown"] for c in figs["cases"] if c["id"] == "ca_summer_r" for f in c["figures"]}
        self.assertEqual(summer["bar|month"], "2026-06 to 2026-09, the mean of the 4 summer months held in the twelve to 2026-09")
        price, n = self.season_mean(NP15, [6, 7, 8, 9])
        self.assertEqual((summer["bar|price"], n), (f"{price:.2f}", 4))

    def test_the_problem_set_question(self):
        kept = load(os.path.join(ROOT, "replication", "problem_sets", "page_figures.json"))
        b3 = next(q for q in kept["sets"]["prices-and-your-bill"]["questions"] if q["id"] == "b3")
        self.assertEqual(b3["answer"], "18.54 USD of 229.63 USD: 8.08 %.")
        self.assertIn("in the bill's own season: 2025-10 to 2026-05, the mean of the 8 winter months held in the twelve to 2026-09.", b3["q"])
        self.assertTrue(any(s.startswith("The price: the mean of the 8 winter months' load-weighted real-time prices, 42.76 USD/MWh") for s in b3["steps"]))
        b4 = next(q for q in kept["sets"]["prices-and-your-bill"]["questions"] if q["id"] == "b4")
        self.assertEqual(b4["answer"], "23.70 USD of 95.27 USD: 24.88 %.")      # Oncor's tariff has no season

    def test_the_code_and_the_notes(self):
        with open(os.path.join(ROOT, "site", "lib", "bill.ts"), encoding="utf-8") as f:
            self.assertIn("export function wholesaleFor(", f.read())
        with open(os.path.join(ROOT, "site", "scripts", "check-values.mjs"), encoding="utf-8") as f:
            self.assertIn("R[st].wholesale_season_months?.[p[4]]", f.read())
        with open(os.path.join(ROOT, "docs", "methods", "bill.md"), encoding="utf-8") as f:
            note = " ".join(f.read().split())
        self.assertIn("`bill|<bill>|price|<ts>|<season>`", note)
        self.assertIn("at the winter months' mean it is 8.08", note)
        for p in ("site/lib/bill.ts", "site/app/learn/bill/page.tsx", "docs/methods/bill.md", "site/data/bill_rules.json"):
            with open(os.path.join(ROOT, p), encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read(), p)


if __name__ == "__main__":
    unittest.main()
