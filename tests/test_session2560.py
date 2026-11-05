"""Session 2560: EEC's Integrated Annual Report 2025, its highlights (Eswatini's energy sold, sent out, generated and imported).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eec_eswatini_electricity.py on a page text built here (made up
for the test, not EEC's): the columns run together, the five figures and the five of the year before each taken in their
labels' order, commas and decimals, the financial year's first day, GWh to MWh, other figures (money, percentages) passed
over; a label missing or twice, labels out of order, a figure missing and the page missing stopping the run; the sector
rule and the holds. No network.

    python -m unittest tests.test_session2560 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eec_eswatini_electricity as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
NL = chr(10)
PAGE = NL.join([
    "OVERVIEW HIGHLIGHTS AND AT-A-GLANCE METRICS",
    "Net Loss Cash Energy Sold System Losses",
    "E80.4 million E28.0 million 1,200 GWh 13.54%",
    "(2024: Profit of E101.1 million). (2024: 1,100 GWh). (2024: 13.16%).",
    "Units Sent Out (Total Supply)",
    "E247.2 million 1,400 GWh",
    "(2024: 1,350 GWh).",
    "Internal Generation",
    "300 GWh E259 million",
    "(2024: 320.5 GWh). drought.",
    "Electricity Imports",
    "950.5 GWh",
    "(2024: 900 GWh).",
    "Local Generation",
    "from Ubombo Sugar Ltd (USL)",
    "60.1 GWh",
    "(2024: 55 GWh)."])


class Parse(unittest.TestCase):
    def test_rows(self):
        t = E.parse_text(PAGE, BASE)
        r = {(x, fy): v for x, fy, v in zip(t.variable, t.x_fiscal_year, t.value)}
        self.assertEqual(r[("sold", "2024/25")], 1200000.0)
        self.assertEqual(r[("sold", "2023/24")], 1100000.0)
        self.assertEqual(r[("internal_generation", "2023/24")], 320500.0)
        self.assertEqual(r[("imports", "2024/25")], 950500.0)
        self.assertEqual(r[("purchases_ubombo_sugar", "2023/24")], 55000.0)
        self.assertEqual(set(t.ts_utc), {"2024-04-01T00:00:00Z", "2023-04-01T00:00:00Z"})
        self.assertEqual(len(t), 10)
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        bad = [PAGE.replace("Electricity Imports", "Imports"),
               PAGE + NL + "Energy Sold",
               PAGE.replace("Internal Generation", "XX").replace("Units Sent Out (Total Supply)", "Internal Generation").replace("XX", "Units Sent Out (Total Supply)"),
               PAGE.replace("60.1 GWh", "60.1"),
               PAGE.replace("HIGHLIGHTS AND AT-A-GLANCE METRICS", "")]
        for text in bad:
            with self.assertRaises(RuntimeError):
                E.parse_text(text, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "power")
        self.assertIn(E.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
