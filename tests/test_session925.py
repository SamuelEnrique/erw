"""Session 925: the NRC's power reactor units, operating and in decommissioning.

Energy Research Warehouse (ERW). Tests warehouse/connectors/nrc_reactors.py on a list and datasets built here in the
NRC's form (figures made up for the test, not the NRC's): the docket read from the list's name cell, the state from the
location, the dataset's columns joined by docket and left empty for a unit it does not hold, a retired unit from the
decommissioning dataset, a date cell with words kept as given; a list row without a docket stopping the run; the sector
rule and the holds. No network.

    python -m unittest tests.test_session925 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import nrc_reactors as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

LIST = ("<table><tr>" + "".join(f"<th>{c}</th>" for c in N.LIST_COLS) + "</tr>"
        "<tr><td>Test Plant 1 05000999</td><td>DPR-1</td><td>PWR</td><td>6 miles W of Town, AR</td><td>Owner Inc.</td><td>4</td></tr>"
        "<tr><td>New Plant 2 05200026</td><td>NPF-2</td><td>PWR</td><td>near City, GA</td><td>Other Co.</td><td>2</td></tr></table>")


def op_frame():
    r = {k: "" for k in N.OP_FIELDS}
    r.update({"Docket Number": "5000999", "Year of Update": "2022", "Capacity MWe": "850", "Plant Name, Unit Number": "Test Plant, Unit 1",
              "Operating License Issued": "1974-05-21 00:00:00", "Renewed Operating License Issued": "Application Withdrawn",
              "Licensed MWt": "2568"})
    return pd.DataFrame([r])


def decom_frame():
    r = {k: "" for k in N.DECOM_FIELDS}
    r.update({"Docket Number": "05000155", "Year of Update": "2022", "Unit": "Old Rock Point", "Location": "Charlevoix, MI",
              "Reactor Type": "BWR", "MWt": "240", "Shut Down": "1997-08-29 00:00:00"})
    return pd.DataFrame([r])


class Reactors(unittest.TestCase):
    def test_join(self):
        listed = N.list_rows(LIST)
        op = N.dataset(op_frame(), N.OP_FIELDS, ["Docket Number", "Year of Update", "Capacity MWe"])
        decom = N.dataset(decom_frame(), N.DECOM_FIELDS, ["Docket Number", "Year of Update", "Location", "Reactor Type"])
        t = N.build(listed, op, decom, {"list": "u", "decom": "d"}, {"list": "r", "decom": "r"}, {"list": "", "decom": ""}).set_index("entity_id")
        a = t.loc["nrc_reactor:05000999"]
        self.assertEqual((a["name"], a.geo, a.capacity_mw, a.status, a.x_operating_license, a.x_renewed_license, a.x_dataset_year),
                         ("Test Plant 1", "US-AR", 850.0, "operating", "1974-05-21", "Application Withdrawn", "2022"))
        b = t.loc["nrc_reactor:05200026"]
        self.assertEqual((b.capacity_mw, b.x_dataset_year, b.geo), ("", "", "US-GA"))
        c = t.loc["nrc_reactor:05000155"]
        self.assertEqual((c.status, c.status_date, c.geo, c.x_licensed_mwt), ("retired", "1997-08-29", "US-MI", "240"))

    def test_list_row_without_docket_stops(self):
        with self.assertRaises(RuntimeError):
            N.list_rows(LIST.replace("05000999", "0599"))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "nrc_power_reactors"
        self.assertEqual(B.sector_of(name), "power;uranium")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
