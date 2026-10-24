"""Session 2188: the Department of Energy's budget and obligations from USAspending.gov.

Energy Research Warehouse (ERW). Tests warehouse/connectors/usaspending_doe.py on answers built here in USAspending's
form (figures made up for the test, not USAspending's): a fiscal year's totals at its first day, its obligations to date
by period (monthly, and quarterly in an older year), an empty next year passed over, an open year marked partial; award
categories by year; a period given twice, a category not in the map, another agency's record and a figure that does not
read each stopping the run; the sector rule and the hold. No network.

    python -m unittest tests.test_session2188 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import usaspending_doe as U  # noqa: E402
import build_coverage as B  # noqa: E402


def year(fy, periods, br=100.0, ob=80.0, out=70.0):
    return {"fiscal_year": fy, "agency_budgetary_resources": br, "agency_total_obligated": ob, "agency_total_outlayed": out,
            "agency_obligation_by_period": [{"period": p, "obligated": v} for p, v in periods]}


def budget(years, code="089"):
    return {"toptier_code": code, "agency_data_by_year": years}


class Parse(unittest.TestCase):
    def test_budget(self):
        rows = U.parse_budget(budget([
            {"fiscal_year": 2027, "agency_budgetary_resources": None, "agency_total_obligated": None, "agency_total_outlayed": None,
             "agency_obligation_by_period": []},
            year(2026, [(2, 10.0), (3, 20.0)]), year(2019, [(3, 5.0), (6, 9.0)])]), {}, 2026)
        got = {(r["variable"], r["ts_utc"]): r for r in rows}
        self.assertNotIn("2027", {r["x_fiscal_year"] for r in rows})
        self.assertEqual(got[("obligated", "2025-10-01T00:00:00Z")]["value"], 80.0)
        n = got[("obligated_to_date", "2025-11-01T00:00:00Z")]
        self.assertEqual((n["value"], n["freq"], n["x_period"], n["x_partial"]), (10.0, "P1M", "2", "yes"))
        q = got[("obligated_to_date", "2019-03-01T00:00:00Z")]
        self.assertEqual((q["freq"], q["x_partial"]), ("P3M", ""))
        self.assertEqual(got[("budgetary_resources", "2018-10-01T00:00:00Z")]["unit"], "USD")

    def test_awards(self):
        rows = U.parse_awards({"results": [{"category": "grants", "aggregated_amount": 3.5}, {"category": "loans", "aggregated_amount": -1.0}]},
                              2025, {}, 2026)
        self.assertEqual({(r["entity"], r["value"], r["ts_utc"]) for r in rows},
                         {("usaspending:doe:grants", 3.5, "2024-10-01T00:00:00Z"), ("usaspending:doe:loans", -1.0, "2024-10-01T00:00:00Z")})

    def test_stops(self):
        for call, words in [(lambda: U.parse_budget(budget([year(2025, [(2, 1.0), (2, 2.0)])]), {}, 2026), "period given twice"),
                            (lambda: U.parse_budget(budget([year(2025, [])], code="019"), {}, 2026), "not DOE's"),
                            (lambda: U.parse_budget(budget([year(2025, [], br="n/a")]), {}, 2026), "does not read"),
                            (lambda: U.parse_awards({"results": [{"category": "subsidies", "aggregated_amount": 1}]}, 2025, {}, 2026), "categories")]:
            with self.assertRaises(RuntimeError) as c:
                call()
            self.assertIn(words, str(c.exception))

    def test_period_months(self):
        self.assertEqual([U.period_month(2025, p)[:7] for p in (1, 3, 4, 12)], ["2024-10", "2024-12", "2025-01", "2025-09"])


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(U.TABLE), "power;deals")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {U.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
