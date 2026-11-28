"""Session 11408 (chain 770, part C): the storage build-out, the other choice of the storage audit's finding 5
(docs/reviews/storage-model-audit-2026-11-26.md; its test branch wip/audit-storage-5, carried over here and turned to
the new rule). Not for landing until the owner rules.

The rule on this branch: warehouse/derived/storage_buildout.py reads eia860m_retired_generators_all, where held, and a
battery retired before the retired table's window counts in each month it operated (its MWh not reported: the list has
no energy column). Measured by running the builder on this machine's tables (read only from warehouse/output, written
only into the worktree), the United States' battery MW at each year end, origin/main against here: 2015 250.2 to 362.9,
2016 461.4 to 587.0, 2017 579.0 to 693.2, 2018 799.4 to 910.9, 2019 1,004.0 to 1,115.4, 2020 1,589.0 to 1,695.0, 2021
5,020.8 to 5,116.3, 2022 9,329.8 to 9,368.7, 2023 16,568.3 to 16,601.3; 2024, 2025 and September 2026 unchanged (the
twelve months' net additions of January to March 2025 move, 46 cells). Retired battery units 8 to 50. The table
storage_buildout_monthly is rebuilt and loaded at landing by the desk.

1. earlier_batteries on small frames: a battery of the full list in neither table is added, with no MWh; one already in
   the inventory or the window is not; solar is not.
2. The builder names the full list; the fold and the method note say so."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class RetiredBeforeTheWindow(unittest.TestCase):
    def test_earlier_batteries(self):
        import pandas as pd
        import storage_buildout as sb
        cols = ["entity_id", "prime_mover", "technology_group", "retirement_date", "energy_capacity_mwh", "vintage", "source"]
        op = pd.DataFrame([["eia860:1:1", "BA", "storage", "", "40", "2026-09", "eia:860m"]], columns=cols)
        rt = pd.DataFrame([["eia860:2:1", "BA", "storage", "2025-06-01", "20", "2026-09", "eia:860m"]], columns=cols)
        full = pd.DataFrame([["eia860:2:1", "BA", "storage", "2025-06-01", "2026-08", "eia:860m"],
                             ["eia860:3:1", "BA", "storage", "2019-03-01", "2026-08", "eia:860m"],
                             ["eia860:4:1", "PV", "solar", "2018-01-01", "2026-08", "eia:860m"]],
                            columns=["entity_id", "prime_mover", "technology_group", "retirement_date", "vintage", "source"])
        got = sb.earlier_batteries(full, op, rt)
        self.assertEqual(list(got["entity_id"]), ["eia860:2:1", "eia860:3:1"])
        added = got[got["entity_id"] == "eia860:3:1"].iloc[0]
        self.assertEqual((added["energy_capacity_mwh"], added["vintage"]), ("", "2026-09"))
        self.assertIs(sb.earlier_batteries(None, op, rt), rt)

    def test_the_builder_and_the_words(self):
        b = read("warehouse", "derived", "storage_buildout.py")
        self.assertIn('RETIRED_ALL = "eia860m_retired_generators_all"', b)
        self.assertIn("rows, st = build(op, pl, rt, log, rt_all)", b)
        self.assertIn("Since session 11408 (the storage audit's finding 5, the other choice) a battery retired earlier is read from",
                      read("docs", "methods", "storage_buildout.md"))
        v = " ".join(read("site", "app", "storage", "buildout", "view.tsx").split())
        self.assertIn("is read from EIA&apos;s full list of retired generators and counts in every year it operated", v)
        self.assertNotIn(chr(0x2014), v)


if __name__ == "__main__":
    unittest.main()
