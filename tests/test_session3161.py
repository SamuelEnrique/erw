"""Session 3161 (chain 181): every derived table's own source names the ERW as "Energy Research Warehouse (ERW), derived".

Chain 177's session 3109 found that the package test `test_derived_tables_flag_license_and_inputs` failed on the data
machine's full warehouse for four old derived tables (eia930_demand_weather, eia_annual_crosscheck_ba, grid_stress_days,
iso_queue_statistics): their builders registered the publisher "Energy Research Warehouse (ERW)" without ", derived".
The GitHub runner holds none of the four, so no scheduled step showed it. Session 2884 fixed the same fault for
ercot_wind_solar_hsl_monthly. This test reads the repository's records only: no request, no table.
"""
import csv
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DERIVED = "Energy Research Warehouse (ERW), derived"
FOUR = {"erw:demand_weather": "warehouse/derived/demand_weather.py",
        "erw:eia_annual_crosscheck_ba": "warehouse/derived/eia_annual_crosscheck.py",
        "erw:grid_stress_days": "warehouse/derived/stress_days.py",
        "erw:iso_queue_statistics": "warehouse/derived/queue_statistics.py"}


def rows(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


class TestDerivedPublisher(unittest.TestCase):
    def test_every_derived_tables_own_source_names_the_derived_publisher(self):
        derived = {r["table"] for r in rows("warehouse", "metadata", "coverage.csv") if r["derived"] == "yes"}
        bad = []
        for r in rows("warehouse", "metadata", "sources.csv"):
            if not r["source"].startswith("erw:"):
                continue
            tables = set(re.split(r"[;\s]+", r["tables"].strip())) - {""}
            if tables & derived and not r["publisher"].startswith(DERIVED):
                bad.append((r["source"], r["publisher"]))
        self.assertEqual(bad, [])

    def test_the_four_builders_register_it(self):
        src = {r["source"]: r for r in rows("warehouse", "metadata", "sources.csv")}
        for sid, path in FOUR.items():
            self.assertEqual(src[sid]["publisher"], DERIVED, sid)
            with open(os.path.join(ROOT, path), encoding="utf-8") as f:
                text = f.read()
            self.assertIn(f'publisher="{DERIVED}"', text, path)
            self.assertNotIn('publisher="Energy Research Warehouse (ERW)",', text, path)

    def test_the_sites_citations_follow(self):
        import json
        with open(os.path.join(ROOT, "site", "data", "table_citations.json"), encoding="utf-8") as f:
            cites = json.load(f)
        for t in ("eia930_demand_weather", "eia_annual_crosscheck_ba", "grid_stress_days", "iso_queue_statistics"):
            if t in cites:
                self.assertTrue(cites[t].startswith(DERIVED + ". "), t)


if __name__ == "__main__":
    unittest.main()
