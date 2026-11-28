"""Session 11407 (chain 770, part C): the states audit's finding 7 readied for Samuel's ruling, the nation without Puerto Rico.

Carried over from session 10223's tests/test_audit_states_9.py (branch wip/audit-states-9), which showed that the United
States' plants part took EIA-860M whole, so the nation's capacity held Puerto Rico's 6,474.3 MW while its generation and
sales, EIA's national totals, leave Puerto Rico out. On this branch build_plants (warehouse/derived/states_page.py)
keeps only the fifty states' and the District's rows for "US", in the operating, planned and retired tables. On
EIA-860M of 2026-09 the capacity 1,423,491.7 MW becomes 1,417,017.4 (-0.45 percent); on the page files of 28 November
2026 (EIA-860M of 2026-10) 1,428,117.4 becomes 1,421,643.1. The page files are the data machine's: site file rebuilt at
landing by the desk. docs/reviews/states-model-audit-2026-11-26.md, finding 7.
"""
import importlib.util
import json
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "states")


def load_builder():
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
    spec = importlib.util.spec_from_file_location("states_page_ready_no_pr", os.path.join(ROOT, "warehouse", "derived", "states_page.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def gen(rows, extra):
    base = {"name": "x", "county": "c", "operator": "o", "balancing_authority": "B", "technology_group": "solar", "net_summer_mw": 1.0,
            "lat": 0.0, "lon": 0.0, "vintage": "2026-09", "energy_capacity_mwh": 0.0}
    return pd.DataFrame([{**base, **extra, "plant_id": p, "state": s, "nameplate_mw": mw} for p, s, mw in rows])


class MadeUpPlants(unittest.TestCase):
    def test_the_nation_leaves_puerto_rico_out(self):
        m = load_builder()
        op = gen([("1", "TX", 100.0), ("2", "PR", 40.0), ("3", "DC", 5.0)], {"planned_retirement_date": ""})
        planned = gen([("4", "TX", 10.0), ("5", "PR", 7.0)], {"planned_operation_date": "2027-01", "status": "under_construction"})
        retired = gen([("6", "PR", 3.0)], {"retirement_date": "2026-03"})
        us = m.build_plants(op, planned, retired, "US")
        self.assertEqual(us["capacity_total_mw"], 105.0)
        self.assertEqual(us["plants"], 2)
        self.assertEqual(us["coming_by_year"]["2027"]["solar"]["nameplate_mw"], 10.0)
        self.assertEqual(us["retired_by_year"], {})
        tx = m.build_plants(op, planned, retired, "TX")
        self.assertEqual(tx["capacity_total_mw"], 100.0)            # a state's part does not change


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "index.json")), "the states' page files are not on this machine")
class ThePageFiles(unittest.TestCase):
    def test_puerto_rico_is_the_gap_until_the_rebuild(self):
        with open(os.path.join(DIR, "index.json"), encoding="utf-8") as f:
            cap = {r["state"]: r["capacity_mw"] for r in json.load(f)["states"]}
        rest = cap["US"] - sum(v for k, v in cap.items() if k != "US")
        # a file built before this branch holds Puerto Rico's 6,474.3 MW in the nation; one the builder now writes holds none
        self.assertTrue(abs(rest - 6474.3) <= 0.5 or abs(rest) <= 0.5, rest)


class TheWords(unittest.TestCase):
    def test_the_builder_the_decision_and_the_note(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "states_page.py"), encoding="utf-8") as f:
            b = f.read()
        self.assertIn('op, planned, retired = (x[x["state"].isin(list(STATES))] for x in (op, planned, retired))', b)
        with open(os.path.join(ROOT, "site", "app", "states", "Decisions.tsx"), encoding="utf-8") as f:
            dec = f.read()
        self.assertIn("without Puerto Rico's 6,474 MW, as its generation and sales", dec)
        self.assertNotIn("EIA-860M's whole", dec)
        with open(os.path.join(ROOT, "docs", "methods", "states_page.md"), encoding="utf-8") as f:
            note = f.read()
        self.assertIn("the nation's capacity 1,423,491.7 MW became 1,417,017.4 on EIA-860M of 2026-09", note)
        for t in (b, dec, note):
            self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()
