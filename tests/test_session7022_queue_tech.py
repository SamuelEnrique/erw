"""Session 7022 (chain 301, the data machine, 16 November 2026): done-line request 41.

iso_queue_statistics gains the same figures by technology group (storage, solar, solar with storage, wind, gas, other,
and not stated where a queue gives no technology) beside the rows for all, from each queue's fuel_technology. The
groups' entities, <iso>:tech_<group>:queue_<year>, are outside the pages' reads of <iso>:queue_* (a PostgREST like, in
which "_" is any one character) and the replication's exact match, so the rows for all and every page figure stand.
The words below are the six queues' own, as pulled on 5 November 2026.
"""

import importlib.util
import os
import re
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def builder():
    path = os.path.join(ROOT, "warehouse", "derived", "queue_statistics.py")
    spec = importlib.util.spec_from_file_location("queue_statistics_7022", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


CASES = {
    # ERCOT: "<fuel> - <technology>"
    "Other - Battery Energy Storage": "storage", "Solar - Photovoltaic Solar": "solar", "Wind - Wind Turbine": "wind",
    "Gas - Combustion (gas) Turbine, but not part of a Combined-Cycle": "gas", "Gas - Steam Turbine other than Combined-Cycle": "gas",
    "Other - Other": "other", "Nuclear - Steam Turbine other than Combined-Cycle": "other", "Hydrogen - Other": "other",
    # CAISO: parts joined by "+"
    "Photovoltaic": "solar", "Storage": "storage", "Photovoltaic + Storage": "solar_storage", "Storage + Photovoltaic": "solar_storage",
    "Storage + Storage": "storage", "Storage + Solar Thermal": "solar_storage", "Wind Turbine + Storage": "other", "Storage + Other": "other",
    "Steam Turbine": "other", "Combined Cycle": "gas", "Combined Cycle + Combined Cycle": "gas", "Combustion Turbine + Storage": "other",
    # NYISO
    "Energy Storage": "storage", "Pumped Storage": "storage", "Flywheel": "storage", "Dual Fuel": "gas", "Natural Gas": "gas",
    "AC Transmission": "other", "Methane": "other",
    # MISO
    "Battery Storage": "storage", "Hybrid": "other", "Gas": "gas", "Compressed Air Storage": "storage",
    # SPP: "<family> - <parts joined by />"
    "Battery/Storage": "storage", "Hybrid - Solar/Storage": "solar_storage", "Hybrid - Solar/Battery": "solar_storage",
    "Hybrid - Thermal/Storage": "other", "Hybrid - Solar": "solar", "Thermal - CT": "gas", "Thermal - Coal": "other",
    "Thermal": "other", "Thermal - NG/CT": "gas", "Thermal - CT/ST": "other", "Hybrid - Wind/Storage": "other", "WIND": "wind",
    # ISO-NE: EIA's fuel codes, one word each
    "SUN": "solar", "BAT": "storage", "WND": "wind", "NG": "gas", "SUN BAT": "solar_storage", "DFO NG": "gas", "JF KER NG": "gas",
    "WAT BAT": "other", "KER BAT": "other", "SUN WAT": "other", "NG WDS": "other", "NG SUN BAT": "other", "DFO": "other",
    # no words
    "": "not_stated", None: "not_stated",
}


class TheGroups(unittest.TestCase):
    def setUp(self):
        self.m = builder()

    def test_each_queues_words(self):
        for words, group in CASES.items():
            self.assertEqual(self.m.technology_group(words), group, words)

    def test_the_groups_named(self):
        self.assertEqual(self.m.TECH_GROUPS, ["storage", "solar", "solar_storage", "wind", "gas", "other", "not_stated"])


class TheRows(unittest.TestCase):
    """One queue year of six positions, built here, through the builder's own stats(), as main() writes them."""

    def test_the_groups_add_to_the_rows_for_all(self):
        m = builder()
        q = pd.DataFrame({
            "fuel_technology": ["Storage", "Photovoltaic", "Photovoltaic + Storage", "Storage", "Hydro", ""],
            "status": ["active", "withdrawn", "completed", "withdrawn", "active", "active"],
            "capacity_mw": ["100", "50", "80.5", "", "10", "5"],
            "queue_date": ["2024-02-01"] * 6, "actual_in_service_date": ["", "", "2025-03-01", "", "", ""],
        })
        q["tech"] = q["fuel_technology"].map(m.technology_group)
        whole = m.stats(q, "caiso")
        groups = {g: m.stats(q[q["tech"] == g], "caiso") for g in m.TECH_GROUPS if (q["tech"] == g).any()}
        self.assertEqual(sorted(groups), ["not_stated", "other", "solar", "solar_storage", "storage"])
        for v in ("positions_entered", "positions_withdrawn", "positions_operating", "positions_waiting"):
            self.assertEqual(sum(g[v][0] for g in groups.values()), whole[v][0], v)
        self.assertEqual(groups["storage"]["positions_entered"][0], 2.0)
        self.assertEqual(groups["storage"]["mw_entered"][0], 100.0)       # a position with no MW is counted, not summed
        self.assertEqual(groups["storage"]["withdrawal_rate"][0], 0.5)

    def test_the_entities_stay_outside_the_pages_reads(self):
        like = re.compile(r"^ercot:queue.")        # the PostgREST like ercot:queue_* ("_" is any one character)
        exact = re.compile(r"[a-z]+:queue_(\d{4})")
        e = "ercot:tech_storage:queue_2024"
        self.assertIsNone(like.match(e))
        self.assertIsNone(exact.fullmatch(e))
        self.assertTrue(like.match("ercot:queue_2024") and exact.fullmatch("ercot:queue_2024"))


if __name__ == "__main__":
    unittest.main()
