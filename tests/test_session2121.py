"""Session 2121: EPA's Toxics Release Inventory for the energy industries.

Energy Research Warehouse (ERW). Tests warehouse/connectors/epa_tri_energy.py on a file built here in the TRI basic
file's form (made up for the test, not EPA's): only the energy sectors kept, a form an entity with its document control
number, two forms of one site and chemical kept apart, grams written as g and pounds as lb, zeros kept and blanks
left out; a missing column, a year not the file's, a unit not Pounds or Grams, a value that is not a number and a form
given twice stopping the run; the unit g in the validator and the data standard (Decision 65); the sector rule and the
holds. No network.

    python -m unittest tests.test_session2121 -v
"""

import io
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import epa_tri_energy as T  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

COLS = list(T.KEEP)


def form(**kw):
    r = {c: "" for c in COLS}
    r.update({"1. YEAR": "2023", "2. TRIFD": "46394MCLCX2815I", "36. DOC_CTRL_NUM": "1323222241717", "3. FRS ID": "110000397676",
              "4. FACILITY NAME": "REFINERY X", "7. COUNTY": "LAKE", "8. ST": "IN", "12. LATITUDE": "41.67",
              "13. LONGITUDE": "-87.47", "17. STANDARD PARENT CO NAME": "PARENT Y", "22. INDUSTRY SECTOR CODE": "324",
              "23. INDUSTRY SECTOR": "Petroleum", "30. PRIMARY NAICS": "324110", "37. CHEMICAL": "Benzene",
              "39. TRI CHEMICAL/COMPOUND ID": "0000071432", "40. CAS#": "000071432", "46. CARCINOGEN": "YES",
              "47. PBT": "NO", "48. PFAS": "NO", "49. FORM TYPE": "R", "50. UNIT OF MEASURE": "Pounds",
              "107. TOTAL RELEASES": "18106.000", "65. ON-SITE RELEASE TOTAL": "18000.000", "88. OFF-SITE RELEASE TOTAL": "106.000"})
    r.update(kw)
    return r


def csv_bytes(rows, drop=None):
    t = pd.DataFrame(rows, columns=COLS)
    if drop:
        t = t.drop(columns=[drop])
    return t.to_csv(index=False).encode("utf-8")


class Build(unittest.TestCase):
    def test_rows(self):
        rows = [form(), form(**{"36. DOC_CTRL_NUM": "1323222194324", "107. TOTAL RELEASES": "290.000",
                                "65. ON-SITE RELEASE TOTAL": "290.000", "88. OFF-SITE RELEASE TOTAL": "0.000"}),
                form(**{"2. TRIFD": "PLANTZ", "36. DOC_CTRL_NUM": "9", "22. INDUSTRY SECTOR CODE": "2211",
                        "23. INDUSTRY SECTOR": "Electric Utilities", "37. CHEMICAL": "Dioxin and dioxin-like compounds",
                        "39. TRI CHEMICAL/COMPOUND ID": "N150", "50. UNIT OF MEASURE": "Grams", "88. OFF-SITE RELEASE TOTAL": ""}),
                form(**{"2. TRIFD": "FOODCO", "36. DOC_CTRL_NUM": "8", "22. INDUSTRY SECTOR CODE": "311", "23. INDUSTRY SECTOR": "Food"})]
        t = T.build([(2023, csv_bytes(rows), "u", "r", "")])
        self.assertEqual(set(t.x_sector), {"Petroleum", "Electric Utilities"})
        a = t[(t.entity == "tri:46394MCLCX2815I:0000071432:1323222241717") & (t.variable == "total_releases")].iloc[0]
        self.assertEqual((a.value, a.unit, a.ts_utc, a.geo, a.freq, a.node), (18106.0, "lb", "2023-01-01T00:00:00Z", "US-IN", "P1Y", "REFINERY X"))
        self.assertEqual((a.x_trifd, a.x_frs_id, a.x_chemical_id, a.x_carcinogen), ("46394MCLCX2815I", "110000397676", "0000071432", "YES"))
        b = t[t.entity == "tri:46394MCLCX2815I:0000071432:1323222194324"]
        self.assertEqual(b[b.variable == "off_site_release_total"].iloc[0].value, 0.0)
        d = t[t.entity == "tri:PLANTZ:N150:9"]
        self.assertEqual(set(d.unit), {"g"})
        self.assertEqual(sorted(d.variable), ["on_site_release_total", "total_releases"])
        self.assertEqual(len(t), 3 + 3 + 2)

    def test_stops(self):
        for bad in (csv_bytes([form()], drop="48. PFAS"), csv_bytes([form(**{"1. YEAR": "2022"})]),
                    csv_bytes([form(**{"50. UNIT OF MEASURE": "Kilograms"})]),
                    csv_bytes([form(**{"107. TOTAL RELEASES": "a lot"})]), csv_bytes([form(), form()])):
            with self.assertRaises(RuntimeError):
                T.build([(2023, bad, "u", "r", "")])

    def test_chunks(self):
        rows = [form(**{"36. DOC_CTRL_NUM": str(i)}) for i in range(5)]
        self.assertEqual(len(T.year_rows(csv_bytes(rows), 2023, "u", "r", "", chunksize=2)), 15)


class Registered(unittest.TestCase):
    def test_unit(self):
        self.assertIn("g", V.UNITS)
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("65. **Session 2121: g.**", text)
        self.assertIn("(Decision 65) `g`, a mass in grams", text)

    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(T.NAME), "power;oil;gas;coal")
        self.assertIn(T.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {T.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
