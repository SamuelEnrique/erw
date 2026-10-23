"""Session 877: a method note for each table chain 047 wrote, linked from coverage's Method column.

Energy Research Warehouse (ERW). Each note under docs/methods/ names its table on its `Tables:` line, carries the sections
of sessions 674 to 678's form, and has no dash; docs/coverage.md's Method cell links it. No network.

    python -m unittest tests.test_session877 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TABLES = {
    "eia861_utility_data": "eia861_utility_data", "eia861_demand_response": "eia861_programs", "eia861_dynamic_pricing": "eia861_programs",
    "eia861_advanced_meters": "eia861_meters_netmetering", "eia861_net_metering": "eia861_meters_netmetering",
    "ercot_cdr_units": "ercot_cdr_units", "eia860_plants_annual": "eia860_plants_annual",
    "eia_coal_receipts_annual": "eia_coal_receipts_annual", "eia861_short_form": "eia861_short_form",
}


class EveryTableHasItsNote(unittest.TestCase):
    def test_notes(self):
        for table, note in TABLES.items():
            with open(os.path.join(ROOT, "docs", "methods", note + ".md"), encoding="utf-8") as f:
                text = f.read()
            line = next(ln for ln in text.splitlines() if ln.startswith("Tables: "))
            self.assertIn(f"`{table}`", line, table)
            for s in ("## License", "## What it does not hold"):
                self.assertIn(s, text, f"{note}: {s}")
            self.assertEqual(text.count(chr(0x2014)) + text.count(chr(0x2013)), 0, note)

    def test_coverage_links(self):
        with open(os.path.join(ROOT, "docs", "coverage.md"), encoding="utf-8") as f:
            rows = {ln.split("|")[1].strip().strip("`"): ln for ln in f if ln.startswith("| `")}
        for table, note in TABLES.items():
            cells = re.split(r"(?<!\\)\|", rows[table].rstrip())[1:-1]
            self.assertEqual(cells[-1].strip(), f"[{note}](methods/{note}.md)", table)


if __name__ == "__main__":
    unittest.main()
