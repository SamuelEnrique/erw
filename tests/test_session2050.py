"""Session 2050: DOE's GRIP selections.

Energy Research Warehouse (ERW). Tests warehouse/connectors/doe_grip.py on a page and program pages built here in
energy.gov's form (made up for the test, not DOE's): the projects read from the page's settings, each round's date
read from its program's page, the amounts in dollars, the states split; a column not in the map, an amount not in DOE's
form, a round without its date and a project given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2050 -v
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import doe_grip as G  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def row(applicant="Utility A", project="Line B", fed="$1,000,000", rec="$2,500,000", status="Awarded", rnd="First",
        program="Smart Grid Grants", loc="IL, TX", full="Illinois, Texas"):
    return {"Applicant/Selectee": applicant, "Project": project, "Federal Cost Share": fed, "Recipient Cost Share": rec,
            "Status": status, "Round": rnd, "program": program, "Locations": loc, "StateFull": full, "keywords": ""}


def page(rows):
    return ('<html><script type="application/json" data-drupal-selector="drupal-settings-json">'
            + json.dumps({"datatableRows": rows}) + "</script></html>")


PROGRAM = ("<h3>Second Funding Opportunity</h3><p>On&nbsp;October 18, 2024, the U.S. Department of Energy announced</p>"
           "<h3>First Funding Opportunity</h3><p>On October 18, 2023, the U.S. Department of Energy announced</p>")
DATES = {p: G.round_dates(PROGRAM, "u") for p in G.PROGRAMS}


class Build(unittest.TestCase):
    def test_rows(self):
        t = G.build(G.settings_rows(page([row(), row(applicant="Utility C", rnd="Second", status="Selected")])), DATES, "u", "r")
        a = t.iloc[0]
        self.assertTrue(a.event_id.startswith("doe_grip:first:"))
        self.assertEqual((a.event_date, a.status, a.x_federal_usd, a.x_recipient_usd, a.x_states), ("2023-10-18", "awarded", "1000000", "2500000", "IL;TX"))
        self.assertEqual((t.iloc[1].event_date, t.iloc[1].status), ("2024-10-18", "selected"))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            G.build([dict(row(), Mystery="x")], DATES, "u", "r")
        with self.assertRaises(RuntimeError):
            G.build([row(fed="about a million")], DATES, "u", "r")
        with self.assertRaises(RuntimeError):
            G.build([row(rnd="Third")], DATES, "u", "r")
        with self.assertRaises(RuntimeError):
            G.build([row(), row()], DATES, "u", "r")
        with self.assertRaises(RuntimeError):
            G.settings_rows("<html></html>")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(G.NAME), "power")
        self.assertIn(G.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {G.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
