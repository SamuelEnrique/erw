"""Audit of /equities, finding 1 (session 11403, docs/reviews/equities-model-audit-2026-11-28.md): three utilities
listed by a preferred share carry their parent's consolidated figures as their own.

Consumers Energy (CMS-PB), Southern California Edison (SCE-PG) and Pacific Gas and Electric (PCG-PE) file one 10-Q
with their parents (CMS Energy, Edison International, PG&E Corp). For the quarter to 30 September 2026 each
subsidiary's series file holds, from the parent's accession, the parent's revenue, net income, capital spending, debt
and share count, to the dollar and to the share. A subsidiary whose common stock its parent holds cannot have the
parent's public share count, so these figures are the parent's. The table of every company on /equities prints them
as the subsidiary's newest period (Consumers Energy: revenue USD 2,183 million, which is CMS Energy's).

The test shows the fault on main's files (it passes on main). The fix moves figures (the subsidiaries' newest
periods), so it is not made: for Samuel's ruling, and a data request for the data machine (which file of the SEC the
joined filing was read from, and the subsidiary's own figures in that filing)."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
D = os.path.join(ROOT, "site", "data", "equities")
PAIRS = [("CMS", "CMS-PB"), ("EIX", "SCE-PG"), ("PCG", "PCG-PE")]
COLS = ("revenue", "net_income", "capex", "debt", "shares_outstanding")


def series(tk):
    with open(os.path.join(D, "series", f"{tk}.json"), encoding="utf-8") as f:
        s = json.load(f)
    return {(r[1], r[2]): dict(zip(s["quarterly_columns"], r)) for r in s["quarterly"]}


def listed(tk):
    with open(os.path.join(D, "index.json"), encoding="utf-8") as f:
        return next(c for c in json.load(f)["companies"] if c["ticker"] == tk)


class SubsidiaryCarriesParent(unittest.TestCase):
    def test_same_filing_same_figures(self):
        for parent, child in PAIRS:
            p, c = series(parent), series(child)
            k = ("2026-09-30", 3)
            self.assertIn(k, p, parent)
            self.assertIn(k, c, child)
            self.assertEqual(p[k]["accession"], c[k]["accession"], f"{child}: one joint filing")
            for col in ("revenue", "net_income", "debt", "shares_outstanding"):
                self.assertIsNotNone(c[k][col], f"{child} {col}")
                self.assertEqual(p[k][col], c[k][col], f"{child} {col} is {parent}'s")

    def test_the_list_prints_the_parents_figures(self):
        for parent, child in PAIRS:
            a, b = listed(parent)["newest_filed"], listed(child)["newest_filed"]
            self.assertEqual(a["period_end"], b["period_end"])
            self.assertEqual(a["revenue"], b["revenue"], f"{child}: the list's revenue is {parent}'s")
            self.assertEqual(a["shares_outstanding"], b["shares_outstanding"], f"{child}: the list's share count is {parent}'s")

    def test_sce_own_count_before(self):
        # Southern California Edison's own filings gave its own count (434,888,104 shares through 2012); the 2026 rows
        # give Edison International's
        s = series("SCE-PG")
        own = [r["shares_outstanding"] for (e, m), r in s.items() if e.startswith("2012") and r["shares_outstanding"]]
        self.assertTrue(own and set(own) == {434888104})
        self.assertEqual(s[("2026-09-30", 3)]["shares_outstanding"], series("EIX")[("2026-09-30", 3)]["shares_outstanding"])


if __name__ == "__main__":
    unittest.main()
