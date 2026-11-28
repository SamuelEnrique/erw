"""Audit of /equities, finding 4 (session 11403, docs/reviews/equities-model-audit-2026-11-28.md): "Capital spending"
is the first concept of a list that a filing holds, and some filings hold a concept that is not their capital spending.

1. Six companies' newest capital spending is filed as exactly 0 (Big Sky Industrial, VAALCO, EON Resources, Prairie
   Operating, Hadron Energy, Spruce Power). VAALCO's line, PaymentsToAcquireOilAndGasProperty, read 102,996,000 for
   2024 and 0 for each 2026 period; an oil producer drilling through 2026 does not spend nothing.
2. Payments add up within a year: a year to date cannot be less than the year to date of the quarter before (same
   start). In the files it is, by more than 1 percent, for VAALCO (9 months of 2025: 3,034,000 against 58,527,000 for
   its first 3 months) and Prairie (12 months of 2025 under its 9 months), among others counted here: a concept that
   changed between filings.
3. The lines mix definitions across companies: debt is LongTermDebt (with the current portion) for 130 companies,
   LongTermDebtNoncurrent (without it) for 67, and with capital or finance leases for 26; net income is the parent's
   share (NetIncomeLoss) for 212 and with noncontrolling interests (ProfitLoss) for 27.

The test shows it on main's files (it passes on main). Which concept is read, and whether a 0 is drawn, moves figures:
for Samuel's ruling, and a data request (each filing's own capital spending line)."""
import collections
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
D = os.path.join(ROOT, "site", "data", "equities")
ZERO = {"BSIN", "EGY", "EONR", "PROP", "HDRN", "SPRU"}


def load(rel):
    with open(os.path.join(D, rel), encoding="utf-8") as f:
        return json.load(f)


class CapitalSpending(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cos = [c for c in load("index.json")["companies"] if c["fundamentals_status"] == "shown"]
        cls.ser = {c["ticker"]: load(c["file"]) for c in cls.cos}

    def rows(self, tk):
        s = self.ser[tk]
        return [dict(zip(s["quarterly_columns"], r)) for r in s["quarterly"]]

    def test_six_zeros(self):
        zero = {c["ticker"] for c in self.cos if c["newest_filed"]["capex"] and c["newest_filed"]["capex"]["v"] == 0}
        self.assertEqual(zero, ZERO)
        egy = {(r["period_end"], r["months"]): r["capex"] for r in self.rows("EGY") if r["capex"] is not None}
        self.assertEqual(egy[("2024-12-31", 12)], 102996000)
        self.assertEqual(egy[("2026-09-30", 9)], 0)

    def test_a_year_to_date_that_falls(self):
        falls = set()
        for tk in self.ser:
            best = {}
            for r in self.rows(tk):
                if r["capex"] is None or r["months"] is None or r["period_start"] is None:
                    continue
                k = (r["period_start"], r["months"])
                if k not in best or (r["filed"], r["accession"]) > (best[k]["filed"], best[k]["accession"]):
                    best[k] = r
            by_start = collections.defaultdict(list)
            for (start, m), r in best.items():
                by_start[start].append((m, r["capex"]))
            for start, xs in by_start.items():
                xs.sort()
                if any(b < a * 0.99 for (_, a), (_, b) in zip(xs, xs[1:]) if a > 0):
                    falls.add(tk)
        self.assertIn("EGY", falls)
        self.assertIn("PROP", falls)
        self.assertGreaterEqual(len(falls), 5)
        print(f"\ncompanies whose capital spending falls within a year: {len(falls)}: {sorted(falls)}")

    def test_mixed_definitions(self):
        debt = collections.Counter(self.ser[c["ticker"]]["concepts"].get("debt") for c in self.cos)
        self.assertEqual(debt["us-gaap:LongTermDebt"], 130)
        self.assertEqual(debt["us-gaap:LongTermDebtNoncurrent"], 67)
        self.assertEqual(debt["us-gaap:LongTermDebtAndCapitalLeaseObligations"], 26)
        ni = collections.Counter(self.ser[c["ticker"]]["concepts"].get("net_income") for c in self.cos)
        self.assertEqual(ni["us-gaap:NetIncomeLoss"], 212)
        self.assertEqual(ni["us-gaap:ProfitLoss"], 27)


if __name__ == "__main__":
    unittest.main()
