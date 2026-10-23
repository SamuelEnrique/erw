"""Session 696: a method note for each table first written before 21 October 2026 that no note named.

Energy Research Warehouse (ERW). Session 674's plan left these tables outside chain 043's notes (it counted 14; 13
remained on 23 October, one having gained a note since). Each now has a note under docs/methods/ whose `Tables:` line
names it, and docs/coverage.md's Method cell links that note. No network.

    python -m unittest tests.test_session696 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TABLES = {
    "eia_crude_first_purchase_prices": "eia_crude_first_purchase_prices", "eia_lng_exports_monthly": "eia_lng_exports_monthly",
    "eia_petroleum_stocks_weekly": "eia_petroleum_stocks_weekly", "eia_petroleum_trade_weekly": "eia_petroleum_trade_weekly",
    "eia_retail_fuel_prices": "eia_retail_fuel_prices", "nyiso_interconnection_queue": "nyiso_interconnection_queue",
    "datacenter_projects_evidence": "datacenter_projects_evidence", "weather_forecast_hourly": "weather_forecast_hourly",
    "news_scores_shadow": "news_scores_shadow", "price_board_carbon": "price_board_carbon",
    "rrc_lease_production_monthly": "rrc_lease_production_monthly", "battery_sourced_ranges": "battery_sourced_ranges",
    "eia930_subba_demand_hourly_2021": "eia930_subba_demand",
}
SECTIONS = ["## License", "## Cross-check", "## What it does not hold"]


class EveryTableHasItsNote(unittest.TestCase):
    def test_the_note_names_the_table(self):
        for table, note in TABLES.items():
            with open(os.path.join(ROOT, "docs", "methods", note + ".md"), encoding="utf-8") as f:
                text = f.read()
            line = next(ln for ln in text.splitlines() if ln.startswith("Tables: "))
            self.assertIn(f"`{table}`", line, table)
            for s in SECTIONS:
                self.assertIn(s, text, f"{note}: {s}")
            self.assertEqual(text.count(chr(0x2014)) + text.count(chr(0x2013)), 0, note)

    def test_coverage_links_it(self):
        with open(os.path.join(ROOT, "docs", "coverage.md"), encoding="utf-8") as f:
            rows = {ln.split("|")[1].strip().strip("`"): ln for ln in f if ln.startswith("| `")}
        for table, note in TABLES.items():
            cells = re.split(r"(?<!\\)\|", rows[table].rstrip())[1:-1]
            self.assertEqual(cells[-1].strip(), f"[{note}](methods/{note}.md)", table)


if __name__ == "__main__":
    unittest.main()
