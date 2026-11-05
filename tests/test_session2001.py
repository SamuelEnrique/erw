"""Session 2001: the NRC's advanced reactor applications and pre-applicants.

Energy Research Warehouse (ERW). Tests warehouse/connectors/nrc_new_reactors.py on pages built here in the NRC's form
(made up for the test, not the NRC's): an application's Who, What, When and Where, its power in MWe, its milestones
(the latest done, the next target, the decision), a When given as a month or inside a sentence; the pre-application
table by technology with its microreactor marks and the inactive projects named after it; a missing table or date
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2001 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import nrc_new_reactors as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "retrieved_at": "r", "vintage": "v"}
DASH = chr(0x2014)
ENDASH = chr(0x2013)


def app_page(when="March 31, 2025 (date of application submittal)", milestones=True):
    ms = ("<table><tr><th>Milestones</th><th>Completion Date</th></tr>"
          "<tr><td>Application Tendered</td><td>03/31/2025</td></tr>"
          f"<tr><td>Draft Safety Evaluation {DASH} sections drafted</td><td>February 2026 {ENDASH} A</td></tr>"
          f"<tr><td>Final Safety Evaluation {DASH} issued</td><td>November 2026 {ENDASH} T</td></tr>"
          "<tr><td>Construction Permit Decision</td><td>TBD</td></tr></table>") if milestones else ""
    return (f"<html><head><title>Test Energy, LLC {ENDASH} Test Station Application | Nuclear Regulatory Commission</title></head><body><main>"
            "<table><tr><td></td><td><table>"
            "<tr><td>Who:</td><td>Test Energy, LLC</td></tr>"
            "<tr><td>What:</td><td>Application for a construction permit for an advanced power reactor</td></tr>"
            f"<tr><td>When:</td><td>{when}</td></tr>"
            "<tr><td>Where:</td><td>Calhoun County, Texas</td></tr></table></td></tr></table>"
            "<table><tr><th>Plant Characteristics</th><th>Description</th></tr>"
            "<tr><td>Reactor Type</td><td>HTGR</td></tr><tr><td>Power Level</td><td>4-Module plant with 800 MWth/320 MWe</td></tr></table>"
            f"{ms}</main></body></html>")


PRE = ("<html><body><main><div><table><thead><tr>" + "".join(f"<th>{t}</th>" for t in N.TECHNOLOGIES) + "</tr></thead><tbody>"
       "<tr><td><a href='/x/pre-application-activities/alpha'>Alpha</a></td><td>* <a href='/x/pre-application-activities/beta'>Beta</a></td>"
       "<td></td><td></td><td></td></tr></tbody></table>"
       "<p>Inactive Projects - * <a href='/x/pre-application-activities/beta'>Beta</a>, * <a href='/x/pre-application-activities/gamma'>Gamma</a></p>"
       "</div></main></body></html>")


class Application(unittest.TestCase):
    def test_row(self):
        r = N.application(app_page(), "https://www.nrc.gov/x/test-station", BASE)
        self.assertEqual((r["event_id"], r["event_date"], r["event_type"]), ("nrc_app:test-station", "2025-03-31", "construction_permit_application"))
        self.assertEqual((r["parties"], r["mw"], r["x_state"]), ("Test Energy, LLC", "320", "TX"))
        self.assertEqual(r["x_project"], f"Test Energy, LLC {ENDASH} Test Station Application")
        self.assertEqual((r["status"], r["x_status_date"]), ("Draft Safety Evaluation", "2026-02-01"))
        self.assertEqual(r["x_next_milestone"], "Final Safety Evaluation")
        self.assertEqual((r["x_decision"], r["x_decision_target"]), ("Construction Permit Decision", "TBD"))

    def test_when_written_otherwise(self):
        r = N.application(app_page("Application submitted December 30, 2025; accepted"), "https://www.nrc.gov/x/a", BASE)
        self.assertEqual(r["event_date"], "2025-12-30")
        r = N.application(app_page("April 2025 to present (date of application submittal)", milestones=False), "https://www.nrc.gov/x/b", BASE)
        self.assertEqual(r["event_date"], "2025-04-01")
        self.assertEqual(r["x_when"], "April 2025 to present (date of application submittal)")

    def test_no_date_stops(self):
        with self.assertRaises(RuntimeError):
            N.application(app_page("soon", milestones=False), "https://www.nrc.gov/x/c", BASE)


class Preapplicants(unittest.TestCase):
    def test_rows(self):
        rows = {r["entity_id"]: r for r in N.preapplicants(PRE, BASE, "https://www.nrc.gov/pre")}
        self.assertEqual(rows["nrc_preapp:alpha"]["x_technology"], N.TECHNOLOGIES[0])
        self.assertEqual((rows["nrc_preapp:alpha"]["x_microreactor"], rows["nrc_preapp:alpha"]["x_active"]), ("no", "yes"))
        self.assertEqual((rows["nrc_preapp:beta"]["x_microreactor"], rows["nrc_preapp:beta"]["x_active"]), ("yes", "no"))
        self.assertEqual((rows["nrc_preapp:gamma"]["x_active"], rows["nrc_preapp:gamma"]["x_technology"]), ("no", ""))

    def test_no_table_stops(self):
        with self.assertRaises(RuntimeError):
            N.preapplicants("<html><body><main><p>none</p></main></body></html>", BASE, "u")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        for t in (N.APP_TABLE, N.PRE_TABLE):
            self.assertEqual(B.sector_of(t), "power;uranium")
            self.assertIn(t, R.STORAGE_HELD)
            with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
                self.assertIn(f"  - {t}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
