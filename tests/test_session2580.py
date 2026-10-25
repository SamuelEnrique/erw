"""Session 2580: DBEDT's State of Hawaii Data Book 2025, tables 17.07, 17.10 and 17.13 (Hawaii's electricity by island,
Hawaiian Electric on Oahu).

Energy Research Warehouse (ERW). Tests warehouse/connectors/dbedt_hawaii_electricity.py on sheet rows built here (made up
for the test, not DBEDT's): 17.07's sources by island (million kWh to MWh, a negative Others kept), 17.10's two blocks
(customers counted, sales to MWh), 17.13's years (1,000 kWh as MWh, 1,000 kW as MW); an island's sources missing its total,
the islands missing the state, a block's header changed, a year missing and a negative customer count stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2580 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import dbedt_hawaii_electricity as D  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
P = [None] * 12


def t1707(oahu_total=11.0):
    rows = [["Table 17.07-- ELECTRICITY PRODUCTION, BY SOURCE AND BY ISLAND: 2024"] + P,
            ["[Million kWh. Components may not sum to total due to rounding]"] + P,
            ["Island"] + [s[0] for s in D.SOURCES] + P]
    per = {"state_total": [21.0, 15, 0, 2, 1, 1, 1, 0, 2, -1.0], "oahu": [oahu_total, 8, 0, 1, 1, 0, 0, 0, 1, 0],
           "hawaii": [10.0, 7, 0, 1, 0, 1, 1, 0, 1, -1.0]}
    for name, isl in D.ISLANDS:
        rows.append([name] + per.get(isl, [0.0] * 10) + P)
    return rows


def t1710(head="Residential power sold (million kWh)"):
    rows = [["Table 17.10-- ELECTRIC UTILITIES, BY ISLAND: 2025"] + P]
    for lead, h2 in (("residential", head), ("other-use", "Other-use power sold (million kWh)")):
        rows.append(["Island", f"Number of {lead} consumer (as of Dec. 31)", h2] + P)
        for name, isl in D.UTIL_ISLANDS:
            rows.append([name] + ([60, 6.0] if isl == "state_total" else ([60, 6.0] if isl == "oahu" else [0, 0.0])) + P)
    return rows


def t1713(years=(2024, 2025), cust=100):
    h = ["Year"] + [None] * 7
    for j, name, *_ in D.HECO:
        h[j] = name
    rows = [["Table 17.13-- SERVICE PROVIDED BY HAWAIIAN ELECTRIC COMPANY, INC. ON OAHU: 1994 TO 2025"] + P, h + P]
    for y in years:
        rows.append([y, cust, 90, 6500, 6200, 5600, 0.4, 1516] + P)
    return rows + [["[a] Net generation plus purchased power."] + P]


class Parse(unittest.TestCase):
    def test_rows(self):
        a = D.parse_1707(t1707(), BASE)
        b = D.parse_1710(t1710(), BASE)
        c = D.parse_1713(t1713(), BASE)
        r = {(x["entity"], x["variable"], x["ts_utc"][:4]): (x["value"], x["unit"]) for x in a + b + c}
        self.assertEqual(r[("dbedt:hi:oahu:petroleum", "generation", "2024")], (8000.0, "MWh"))
        self.assertEqual(r[("dbedt:hi:hawaii:others", "generation", "2024")], (-1000.0, "MWh"))
        self.assertEqual(r[("dbedt:hi:oahu", "residential_sales", "2025")], (6000.0, "MWh"))
        self.assertEqual(r[("dbedt:hi:state_total", "other_customers", "2025")], (60.0, "count"))
        self.assertEqual(r[("dbedt:hi:heco_oahu", "generating_capability", "2025")], (1516.0, "MW"))
        self.assertEqual(r[("dbedt:hi:heco_oahu", "net_input", "2024")], (6500.0, "MWh"))
        self.assertEqual(len(a), 8 * 10)
        self.assertEqual(len(b), 7 * 4)
        self.assertEqual(len(c), 2 * 5)

    def test_stops(self):
        for f in (lambda: D.parse_1707(t1707(oahu_total=12.0), BASE),
                  lambda: D.parse_1710(t1710(head="Residential power used (million kWh)"), BASE),
                  lambda: D.parse_1713(t1713(years=(2023, 2025)), BASE),
                  lambda: D.parse_1713(t1713(cust=-1), BASE)):
            with self.assertRaises(RuntimeError):
                f()

    def test_islands_against_state(self):
        rows = t1707()
        rows[3][1] = 25.0
        rows[3][2] = 19.0
        with self.assertRaises(RuntimeError):
            D.parse_1707(rows, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(D.NAME), "power")
        self.assertIn(D.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {D.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
