"""Session 10212 (storage audit, finding 5, for the owner): the build-out's year ends leave out batteries retired before 2025.

warehouse/derived/storage_buildout.py rebuilds every month from the one EIA-860M inventory held, with the retired table
eia860m_retired_generators, which keeps only the inventory year and the year before. The warehouse also holds
eia860m_retired_generators_all (every retired generator EIA lists, warehouse/connectors/eia860m_retired_all.py; August
2026: 50 battery units, 524.3 MW, 42 of them and 185.8 MW retired before 2025). Read with it, a battery retired before
2025 would count in each year end it operated. Measured for the United States against the September 2026 inventory
(docs/reviews/storage-model-audit-2026-11-26/measures.json, "buildout_year_ends_with_retired"): 2015 250.2 MW becomes
362.9 (+45.0 percent), 2016 461.4 becomes 587.0 (+27.2), 2017 579.0 becomes 693.2 (+19.7), 2018 799.4 becomes 910.9
(+13.9), 2019 1,004.0 becomes 1,115.4 (+11.1), 2020 1,589.0 becomes 1,695.0 (+6.7), 2021 +1.9, 2022 +0.4, 2023 +0.2,
2024 and every month from 2025 unchanged.

These tests show it on main (they pass there). Reading the full list would move the bars a reader sees, so it is not
made: for Samuel's ruling, default "left as it is".
"""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class RetiredBeforeTheWindow(unittest.TestCase):
    def test_the_builder_reads_the_window_only(self):
        b = read("warehouse", "derived", "storage_buildout.py")
        self.assertIn('"retired": "eia860m_retired_generators"}', b)
        self.assertNotIn("eia860m_retired_generators_all", b)
        self.assertIn("a unit retired before\n  the retired table's window (the vintage year and the year before) is absent from every month.", b)

    def test_the_full_list_is_held_and_public(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "connectors", "eia860m_retired_all.py")))
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
            rows = [r for r in csv.reader(f) if r and r[0] == "eia860m_retired_generators_all"]
        self.assertEqual(len(rows), 1)
        self.assertIn("public", rows[0])


if __name__ == "__main__":
    unittest.main()
