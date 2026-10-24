"""Session 2072: EPA's GHGRP, every facility's total reported emissions.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ghgrp_facilities.py on a workbook built here in the
summary's form (made up for the test, not EPA's): the six segments read, the years' columns from 2015, a blank no row,
a pipeline listed a row a state kept apart by its state's code, a row naming no state keeping the facility's id; a
column of years not in EPA's form, a state name not in the map and a facility twice in a year stopping the run; the unit
tCO2e in the validator, the sector rule and the holds. No network.

    python -m unittest tests.test_session2072 -v
"""

import io
import os
import sys
import unittest

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import ghgrp_facilities as G  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

YEARS = [2023, 2014]


def workbook(pipe_rows=None, direct_year_label="Total reported direct emissions"):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for seg in G.SEGMENTS:
        ws = wb.create_sheet(seg)
        ws.append(["Summary data"]); ws.append(["note"]); ws.append(["units"])
        if seg in ("Transmission Pipelines", "LDC - Direct Emissions"):
            ws.append(["Facility Id", "FRS Id", "Facility Name", "State where Emissions Occur", "Reported State",
                       "Primary NAICS Code", "Latest Reported Industry Type (subparts)"] + [f"{y} Total reported direct emissions from X" for y in YEARS])
            for r in (pipe_rows or [["7", "", "Pipe Co", "Connecticut", "TX", "486210", "W-TRANS", 100.5, 9]] if seg == "Transmission Pipelines" else []):
                ws.append(r)
        else:
            label = direct_year_label if seg == "Direct Point Emitters" else "Total reported emissions from Y"
            ws.append(["Facility Id", "FRS Id", "Facility Name", "State", "Primary NAICS Code", "Latest Reported Industry Type (subparts)",
                       "Latest Reported Industry Type (sectors)"] + [f"{y} {label}" for y in YEARS])
            if seg == "Direct Point Emitters":
                ws.append(["1", "110", "Plant A", "TX", "221112", "C,D", "Power Plants", 5000.25, 1])
                ws.append(["2", "111", "Plant B", "OH", "324110", "C,Y", "Refineries", None, 2])
    out = io.BytesIO(); wb.save(out)
    return out.getvalue()


class Build(unittest.TestCase):
    def test_rows(self):
        rows = [["7", "", "Pipe Co", "Connecticut", "TX", "486210", "W-TRANS", 100.5, 9],
                ["7", "", "Pipe Co", "New York", "TX", "486210", "W-TRANS", 50.0, 9],
                ["8", "", "Gas Co", "None", "OH", "486210", "W-TRANS", 10.0, 9]]
        t = G.build(workbook(rows), 2015, "u", "r", "v").set_index(["entity", "variable", "ts_utc"])
        self.assertEqual(t.loc[("ghgrp:1", "emissions_direct", "2023-01-01T00:00:00Z"), "value"], 5000.25)
        self.assertNotIn(("ghgrp:1", "emissions_direct", "2014-01-01T00:00:00Z"), t.index)
        self.assertNotIn(("ghgrp:2", "emissions_direct", "2023-01-01T00:00:00Z"), t.index)
        a = t.loc[("ghgrp:7:CT", "emissions_transmission_pipelines", "2023-01-01T00:00:00Z")]
        self.assertEqual((a.value, a.geo, a.unit, a.x_emission_state), (100.5, "US-CT", "tCO2e", "CT"))
        self.assertIn(("ghgrp:7:NY", "emissions_transmission_pipelines", "2023-01-01T00:00:00Z"), t.index)
        b = t.loc[("ghgrp:8", "emissions_transmission_pipelines", "2023-01-01T00:00:00Z")]
        self.assertEqual((b.geo, b.x_emission_state), ("US-OH", ""))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            G.build(workbook(direct_year_label="Emissions"), 2015, "u", "r", "v")
        with self.assertRaises(RuntimeError):
            G.build(workbook([["7", "", "Pipe Co", "Atlantis", "TX", "486210", "W-TRANS", 1, 1]]), 2015, "u", "r", "v")
        with self.assertRaises(RuntimeError):
            G.build(workbook([["7", "", "P", "Connecticut", "TX", "1", "W", 1, 1], ["7", "", "P", "CT", "TX", "1", "W", 2, 1]]), 2015, "u", "r", "v")


class Registered(unittest.TestCase):
    def test_unit_sector_and_holds(self):
        self.assertIn("tCO2e", V.UNITS)
        self.assertEqual(B.sector_of(G.NAME), "carbon;power;oil;gas")
        self.assertIn(G.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {G.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            self.assertIn("61. **Session 2072: tCO2e.**", f.read())


if __name__ == "__main__":
    unittest.main()
