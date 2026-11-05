"""Session 930: ORNL's U.S. hydropower relicensing and license surrender data.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ornl_hydro_relicensing.py on sheets built here in the
workbook's form (figures made up for the test, not ORNL's): the event date from the issuance, else the application, else
the notice; the EHA plant as entity_ids; the new capacity for a relicense and the old for a surrender; a docket given twice
kept with -2; a heading not in the map and a row without a date stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session930 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ornl_hydro_relicensing as O  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

RELIC = ["FERC_docket", "EHA_PtID", "Project_name", "Project_licensee", "Licensee_type", "Waterway", "Project_type", "Latitude", "Longitude", "State",
         "NOI_date", "Application_date", "Proc_type", "FcIssue", "FcExpire", "Mode_new", "Status", "Settlement", "Construction", "T_G_investment",
         "Capacity_new_MW"]
SURR = ["FERC_docket", "EHA_PtID", "Project_name", "Project_licensee", "Licensee_type", "Waterway", "Project_type", "Latitude", "Longitude", "State",
        "NOI_date", "Application_date", "FcIssue", "Status", "Dam_removal", "Capacity_old_MW", "Reason_category"]


def frame(cols, rows):
    return pd.DataFrame([{c: r.get(c) for c in cols} for r in rows], dtype=str)


class Records(unittest.TestCase):
    def test_dates_ids_and_capacity(self):
        rel = frame(RELIC, [{"FERC_docket": "P-176", "EHA_PtID": "hc1019_p01", "Project_licensee": "City", "FcIssue": "2012-09-25 00:00:00",
                             "Application_date": "2010-01-13 00:00:00", "Status": "Issued Relicense", "Capacity_new_MW": "1.5"},
                            {"FERC_docket": "P-200", "NOI_date": "2024-01-31 00:00:00", "Status": "Submitted NOI to Relicense"}])
        sur = frame(SURR, [{"FERC_docket": "P-6055", "Application_date": "2023-01-03 00:00:00", "Status": "Pending Surrender", "Capacity_old_MW": "0.105",
                            "Dam_removal": "Yes"},
                           {"FERC_docket": "P-6055", "Application_date": "2024-01-03 00:00:00", "Status": "Pending Surrender"}])
        t = O.events({"Relicenses": rel, "Surrenders": sur}, "u", "r").set_index("event_id")
        a = t.loc["ornl_relicense:P-176:relicense"]
        self.assertEqual((a.event_date, a.x_date_kind, a.entity_ids, a.mw, a.event_type), ("2012-09-25", "ferc_issued", "ornl_eha:hc1019_p01", 1.5, "hydro_relicense"))
        self.assertEqual(t.loc["ornl_relicense:P-200:relicense", "x_date_kind"], "notice_of_intent")
        s = t.loc["ornl_relicense:P-6055:surrender"]
        self.assertEqual((s.mw, s.x_dam_removal, s.event_type), (0.105, "Yes", "hydro_license_surrender"))
        self.assertIn("ornl_relicense:P-6055:surrender-2", t.index)

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            O.events({"Relicenses": frame(RELIC + ["Extra"], [{"FERC_docket": "P-1", "FcIssue": "2020-01-01"}]), "Surrenders": frame(SURR, [])}, "u", "r")
        with self.assertRaises(RuntimeError):
            O.events({"Relicenses": frame(RELIC, [{"FERC_docket": "P-1"}]), "Surrenders": frame(SURR, [])}, "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "ornl_hydropower_relicensing"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
