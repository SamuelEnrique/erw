"""Session 891: a method note for each table chain 048 wrote or changed, linked from coverage's Method column.

Energy Research Warehouse (ERW). Each note under docs/methods/ names its table on its `Tables:` line, carries the sections
of sessions 674 to 678's form, and has no dash; docs/coverage.md's Method cell links it. No network.

    python -m unittest tests.test_session891 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TABLES = {
    "eia861_energy_efficiency": "eia861_efficiency", "eia861_operational_data": "eia861_operations",
    "eia861_distribution_systems": "eia861_distribution", "eia861_distributed_generation": "eia861_distribution",
    "eia_petroleum_exports_by_destination": "eia_petroleum_exports_by_destination",
    "eia860_generator_owners": "eia860_schedules", "eia860_storage_generators": "eia860_schedules",
    "eia860_solar_generators": "eia860_schedules", "eia860_wind_generators": "eia860_schedules",
    "eia_international_electricity_annual": "eia_international_electricity_annual", "cer_electricity_trade": "cer_electricity_trade",
    "frb_utility_output_monthly": "frb_utility_output_monthly", "uspvdb_solar_facilities": "uspvdb_solar_facilities",
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
