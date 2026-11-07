"""Session 3056 (chain 166): the precise fields of a policy action (warehouse/policy/fields.py), graded against 30
stored actions whose answers were written from their own texts (tests/fixtures/policy/actions_3056.json), and the
rules that hold whatever the text: nothing is kept that the text does not state.

    .venv/Scripts/python.exe -m pytest -q tests/test_policy_fields.py
"""

import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "policy"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import policy_fields as F  # noqa: E402  session 3233: its own name, beside the deals tracker's fields

FIX = os.path.join(ROOT, "tests", "fixtures", "policy")


def items():
    with open(os.path.join(FIX, "actions_3056.json"), encoding="utf-8") as f:
        doc = json.load(f)
    for it in doc["items"]:
        with open(os.path.join(FIX, it["text_file"]), encoding="utf-8") as f:
            yield it, f.read()


def derive(it, text):
    return F.derive(it["row"], text, it["record"] or None)


class Graded(unittest.TestCase):
    """Each field against the answers; the counts are printed, and each must be 29 of 30 or better."""

    def test_the_fields_agree_with_the_answers(self):
        n, ok, misses = 0, {k: 0 for k in ("body", "instrument", "status", "dates", "next_step", "figure")}, []
        for it, text in items():
            n += 1
            g, a = derive(it, text), it["answer"]
            got_dates = {x for x in g["dates"].split("; ") if x}
            want_dates = {f"{x['kind']}={x['date']}" for x in a["dates"]}
            ahead = sorted(x["date"] for x in a["dates"] if x["date"] >= it["row"]["event_date"])
            fig = (float(g["figure_value"]), g["figure_unit"]) if g["figure_value"] else None
            want_fig = (float(a["figure"]["value"]), a["figure"]["unit"]) if a["figure"] else None
            res = {"body": g["body"] == a["body"], "instrument": g["instrument"] == a["instrument"],
                   "status": g["action_status"] == a["status"], "dates": got_dates == want_dates,
                   "next_step": g["next_step_date"] == (ahead[0] if ahead else ""), "figure": fig == want_fig}
            for k, v in res.items():
                ok[k] += v
                if not v:
                    misses.append(f"r{it['r']} {k}")
        print("\npolicy fields on 30 stored actions: " + ", ".join(f"{k} {v} of {n}" for k, v in ok.items()))
        self.assertEqual(n, 30)
        for k, v in ok.items():
            self.assertGreaterEqual(v, 29, f"{k}: {v} of {n}; misses: {misses}")


class NothingInvented(unittest.TestCase):
    """What the module keeps stands in the text it was given."""

    def test_every_date_stands_in_its_evidence_or_in_the_record(self):
        for it, text in items():
            g = derive(it, text)
            pairs = [x for x in g["dates"].split("; ") if x]
            ev = g["dates_evidence"].split(" | ") if pairs else []
            self.assertEqual(len(pairs), len(ev), it["row"]["event_id"])
            for p, e in zip(pairs, ev):
                kind, d = p.split("=")
                self.assertIn(kind, F.KINDS)
                if e.startswith("the Federal Register's record:"):
                    self.assertIn(d, e)
                    continue
                y, m, day = d.split("-")
                month = F.MONTHS.split("|")[int(m) - 1]
                self.assertRegex(e, rf"{month}\s+{int(day)},\s+{y}", f"{it['row']['event_id']}: {p} not in its words")

    def test_every_figure_stands_in_its_sentence(self):
        for it, text in items():
            g = derive(it, text)
            if not g["figure_value"]:
                self.assertEqual(g["figure_unit"] + g["figure_evidence"], "")
                continue
            self.assertIn(g["figure_unit"], F.FIGURE_UNITS)
            digits = re.sub(r"\D", "", g["figure_evidence"])
            lead = str(g["figure_value"]).split(".")[0][:2]
            self.assertIn(lead, digits, it["row"]["event_id"])

    def test_no_text_gives_no_date_and_no_figure(self):
        row = {"agency": "FERC", "action_type": "notice", "title": "Acme Pipeline, LLC; Notice of Application",
               "status": "", "docket": "Docket No. CP26-1-000", "event_date": "2026-11-01"}
        g = F.derive(row, "", None)
        self.assertEqual((g["dates"], g["next_step_date"], g["figure_value"]), ("", "", ""))
        self.assertEqual((g["instrument"], g["action_status"], g["fields_from"]), ("application", "filed", "title"))

    def test_the_vocabularies_hold(self):
        for it, text in items():
            g = derive(it, text)
            self.assertIn(g["instrument"], F.INSTRUMENTS)
            self.assertIn(g["action_status"], F.STATUSES)


class Rules(unittest.TestCase):
    def test_a_docket_has_one_form(self):
        self.assertEqual(F.docket_ids("Docket Nos. 050-616 and 050-617;NRC-2026-0265"), "50-616;50-617;NRC-2026-0265")
        self.assertEqual(F.docket_ids("Docket Nos. 50-616 and 50-617"), "50-616;50-617")
        self.assertEqual(F.docket_ids("Project Nos. 2722-023 & 15373-000"), "2722-023;15373-000")
        self.assertEqual(F.docket_ids("Docket No. CP26-34-000;Docket No. CP26-35-000"), "CP26-34-000;CP26-35-000")

    def test_the_body_is_the_bureau_not_its_department(self):
        self.assertEqual(F.body("Interior", {"agencies": ["Interior Department", "Ocean Energy Management Bureau"]}), "BOEM")
        self.assertEqual(F.body("Interior", None, "SATS No. WY-055-FOR"), "OSMRE")
        self.assertEqual(F.body("FERC", {"agencies": ["Energy Department", "Federal Energy Regulatory Commission"]}), "FERC")
        self.assertEqual(F.body("DOE", {"agencies": ["Energy Department"]}), "DOE")
        self.assertEqual(F.body("PUCT", None, "", "Governor Abbott Announces Grant Funding"), "Texas Governor")

    def test_the_next_step_is_the_first_on_or_after_the_document(self):
        steps = [("effective", "2026-12-28", "a"), ("comments_due", "2026-11-13", "b"), ("comments_due", "2026-10-01", "c")]
        self.assertEqual(F.next_step(steps, "2026-10-14"), ("comments due", "2026-11-13", "b"))
        self.assertEqual(F.next_step(steps, "2027-01-01"), ("", "", ""))

    def test_a_deadline_hour_and_a_page_mark_do_not_hide_the_date(self):
        t = ("please submit your comments so that the Commission receives them in Washington, DC on or before 5:00 p.m. "
             "Eastern Time on\n[[Page 63535]]\nNovember 2, 2026. Comments may be submitted in written form.")
        self.assertEqual(F.dates(t)[0][:2], ("comments_due", "2026-11-02"))

    def test_the_dates_of_session_3125(self):
        # a water quality certification's deadline (r50 of the audit's sample, its words)
        t = ("Date of Receipt of the Certification Request: August 27, 2026 Reasonable Period of Time to Act on the "
             "Certification Request: One year, August 27, 2027 If Maine DEP fails or refuses to act")
        self.assertEqual([x[:2] for x in F.dates(t)], [("decision_due", "2027-08-27")])
        # a release's forums, abbreviated months, in a list after "When:" (r38)
        t = ("Forums provide customers with an opportunity to communicate. When: Tue., Oct. 13, 2026 at 1 p.m. (Virtual) "
             "Tue., Oct. 27, 2026 at 2 p.m. and 6 p.m. (In-Person) What: The CPUC will hold forums.")
        self.assertEqual([x[:2] for x in F.dates(t)], [("meeting", "2026-10-13"), ("meeting", "2026-10-27")])
        # sessions under their own headings, and a comment period extended "to" a date (r78)
        t = ("On July 24, 2026, Commission staff extended the comment period to September 18, 2026.\n\n"
             "Evening Scoping Session\n\n    Date: Tuesday, September 15, 2026.\n    Time: 6:00 p.m.\n\n"
             "Daytime Scoping Session\n\n    Date: Wednesday, September 16, 2026.\n")
        self.assertEqual([x[:2] for x in F.dates(t)], [("comments_due", "2026-09-18"), ("meeting", "2026-09-15"), ("meeting", "2026-09-16")])
        # a date under "Date:" with no session, meeting, hearing or forum above it is no step
        self.assertEqual(F.dates("Receipt\n\n    Date: Tuesday, September 15, 2026.\n"), [])

    def test_the_figures_of_the_third_sample(self):
        # session 3154: a range, a rate and a change "from ... to" are no single total; "$96 Million to 67 ..." is one
        self.assertEqual(F.figure("Steam Electric ELG", "SUMMARY: The rule is estimated to reduce costs by $446 to $1,090 million "
                                  "dollars annually. DATES: soon.", "proposed_rule"), (None, "", ""))
        self.assertEqual(F.figure("Proposed Reinstatement of Lease", "SUMMARY: The lessee agrees to new lease terms for rental of $20 per acre. "
                                  "DATES: soon.", "notice"), (None, "", ""))
        self.assertEqual(F.figure("U.S. Department of Energy Awards $96 Million to 67 Early Career Scientists", "", "press_release")[:2],
                         (96000000, "USD"))

    def test_the_figures_of_the_fresh_audit(self):
        # session 3142: a FERC notice's capacity past its first 1,800 characters (r72 stood at 2,188)
        t = ("[Docket No. CP26-1-000] Take notice that Acme filed an application. " + "z " * 1000 +
             "The pipeline expansion will add approximately 1,900 million cubic feet per day of incremental firm transportation capacity.")
        self.assertEqual(F.figure("Acme; Notice of Application", t, "notice")[:2], (1900, "MMcf/d"))

    def test_the_figures_of_session_3126(self):
        # a total in a sentence of its own, past the opening paragraph (r31 of the audit's sample, its words)
        t = ("Take notice that the following application has been filed. " + "x " * 900 +
             "(b) five 596-kilowatt (kW) horizontal Kaplan turbine-generator units (Units 1 to 5), for a total installed capacity of 2,980 kW; (2) a section.")
        self.assertEqual(F.figure("Acme Hydro; Notice of Scoping Period", t, "notice")[:2], (2980, "kW"), "the total, not the first unit's 596")
        # "$100 million," keeps its scale (r29)
        self.assertEqual(F.figure("A Fellowship", "Fellows will train. Total planned funding is up to $100 million, with $20 million in Fiscal Year 2027.", "press_release")[:2],
                         (100000000, "USD"))
        # a figure of context, in no sentence of the action's own total, is never taken (the coal orders' 17 gigawatts)
        t = "Secretary Wright issued an emergency order. " + "y " * 500 + "Since 2021 the region has lost 17 gigawatts of dispatchable power."
        self.assertEqual(F.figure("Keeping a Plant Online", t, "press_release"), (None, "", ""))

    def test_a_past_date_that_is_no_step_is_left(self):
        t = ("If you submitted comments on this project to the Commission before the opening of this docket on "
             "September 9, 2026, you will need to file those comments in Docket No. CP26-578-000.")
        self.assertEqual(F.dates(t), [])

    def test_the_dates_of_the_fresh_audit(self):
        # session 3141: the fresh audit's class 1, each by its document's words
        cases = [
            ("Notice is hereby given that answers in response to the motions for abeyance are due by 5:00 p.m. Eastern Time on August 7, 2026.",
             [("comments_due", "2026-08-07")]),
            ("Schedule for Environmental Review Issuance of EA--August 21, 2026 90-day Federal Authorization Decision Deadline \\2\\--November 19, 2026",
             [("review_due", "2026-08-21"), ("decision_due", "2026-11-19")]),
            ("Under section 307(b)(1) of the CAA, petitions for judicial review of these actions must be filed in the D.C. Circuit by October 5, 2026.",
             [("review_petition_due", "2026-10-05")]),
            ("r. Final amendments to the application must be filed with the Commission on or before 5:00 Eastern Time on July 15, 2026.",
             [("filing_due", "2026-07-15")]),
            ("Any individual or entity interested in submitting study requests, commenting on the PAD or SD1, and any agency requesting "
             "cooperating status must do so on or before 5:00 p.m. Eastern Time on August 7, 2026.", [("comments_due", "2026-08-07")]),
            ("The IAB will also hold an online preparatory meeting among company representatives at 2 p.m., Paris time, on June 10, 2026.",
             [("meeting", "2026-06-10")]),
            ("The final rule extended the reporting deadline for reporting year 2025 from March 31, 2026, to October 30, 2026.",
             [("filing_due", "2026-10-30")]),
            # a date being replaced is no step; its replacement is
            ("On page 5, in the first column, correct ``This RG is effective on June 4, 2026'' to read, ``This RG is effective on August 18, 2026.''",
             [("effective", "2026-08-18")]),
        ]
        for text, want in cases:
            self.assertEqual([x[:2] for x in F.dates(text)], want, text[:60])

    def test_the_dates_of_the_third_sample(self):
        # session 3152: the third sample's class 1, each by its document's words
        cases = [
            ("Compliance date: Compliance filings required by this final rule are due on September 1, 2026.", [("filing_due", "2026-09-01")]),
            ("Final rules and guidance to conclude the revision process must be issued no later than November 23, 2026.", [("decision_due", "2026-11-23")]),
            ("Objections and requests for hearings must be received on or before July 13, 2026.", [("intervention_due", "2026-07-13")]),
            ("This document announces that the public hearing scheduled for Wednesday, May 27, 2026, Thursday, May 28, 2026, will be telephonic.",
             [("meeting", "2026-05-27"), ("meeting", "2026-05-28")]),
            ("DATES: The due date to pay additional royalties based on the major portion prices is July 31, 2026.", [("filing_due", "2026-07-31")]),
            ("Public hearing: EPA will hold an online (i.e., virtual) public hearing on May 28, 2026.", [("meeting", "2026-05-28")]),
            ("If anyone contacts us requesting a public hearing on or before April 27, 2026, we will hold one.", [("intervention_due", "2026-04-27")]),
            # a date a party asks for is no step; a filing deadline on a step's date is that step
            ("In the Request, Texas LNG asks DOE to extend the deadline to February 10, 2032.", []),
            ("Comments are due by 5:00 p.m. Eastern Time on November 2, 2026. Because the 60-day filing deadline falls on a Saturday, "
             "the filing deadline is extended until 5:00 p.m. Eastern Time on November 2, 2026.", [("comments_due", "2026-11-02")]),
        ]
        for text, want in cases:
            self.assertEqual([x[:2] for x in F.dates(text)], want, text[:60])

    def test_the_instruments_of_the_fresh_audit(self):
        # session 3140: the nine rows of the fresh audit's class 5, by their titles and the Register's action lines
        cases = [
            ("notice", "Proposed Reissuance of NPDES General Permit for Oil and Gas Exploration Facilities in Federal Waters of Cook Inlet (AKG51000)",
             "Notice of proposed reissuance of NPDES General Permit and request for public comment.", ("approval", "proposed")),
            ("notice", "Duke Energy Carolinas, LLC; Belews Creek; Notice of Hearing", "Early site permit application; notice of uncontested hearing.", ("meeting", "scheduled")),
            ("press_release", "People who Power the Process: Electric General Rate Case Program and Project Supervisor", "", ("announcement", "announced")),
            ("notice", "Rockies Express Pipeline LLC, Cheyenne Connector, LLC, East Cheyenne Gas Storage, LLC; Notice of Revised Schedule for "
             "Environmental Review of the Critical Energy Reliability Link Project", "", ("environmental_review", "scheduled")),
            ("notice", "Clean Air Act Operating Permit Program; Order on Petition for Objection to State Operating Permit for the Humboldt Redwood Company, LLC",
             "Notice of final order on petition.", ("order", "issued")),
            ("notice", "Reliability Technical Conference; Notice of Reliability Technical Conference", "", ("meeting", "scheduled")),
            ("press_release", "NRC Schedules Open House to Discuss Donald C. Cook Power Plant Performance", "", ("meeting", "scheduled")),
            ("notice", "Algonquin Gas Transmission, LLC; Notice of Scoping Period Requesting Comments on Environmental Issues for the Planned Algonquin "
             "Reliable Affordable Resilient Enhancement Project, and Notice of Public Scoping Sessions", "", ("environmental_review", "open")),
            ("notice", "International Energy Agency Meetings", "Notice of meetings.", ("meeting", "scheduled")),
            # and the NRC's "order imposing procedures" stays an application's notice
            ("notice", "Applications for Amendments to Facility Operating Licenses Involving Proposed No Significant Hazards Consideration Determination",
             "License amendment request; notice of opportunity to comment, request a hearing, and petition for leave to intervene; order imposing procedures.",
             ("application", "filed")),
        ]
        for action_type, title, line, want in cases:
            row = {"agency": "X", "action_type": action_type, "title": title, "status": line, "docket": "", "event_date": "2026-07-01"}
            g = F.derive(row, "", None)
            self.assertEqual((g["instrument"], g["action_status"]), want, title)

    def test_the_instruments_of_the_third_sample(self):
        # session 3153: the third sample's class 5 and class 2 rows, by their titles and action lines
        cases = [
            ("press_release", "NRC to Brief Public on Annual Nuclear Plant Safety Across Four States", "", ("meeting", "scheduled")),
            ("notice", "FERC Form 580, Interrogatories on Fuel and Energy Purchase Practices; Notice of Request for Partial Waiver", "", ("notice", "issued")),
            ("press_release", "NRC Extends St. Lucie Nuclear Plant Operations Into the 2060s", "", ("order", "issued")),
            ("notice", "Proposed Reinstatement of BLM New Mexico Terminated Oil and Gas Lease: NMNM105294482", "Notice of lease reinstatement.", ("notice", "proposed")),
            ("press_release", "NRC Expands Wyoming's Authority Over Key Nuclear Materials as Rare Earth Development Grows", "", ("approval", "final")),
            ("press_release", "NRC to Discuss Wolf Creek Nuclear Power Plant Performance", "", ("meeting", "scheduled")),
            ("notice", "Boott Hydropower, LLC; Notice of Revised Procedural Schedule for Processing of Relicense Application", "", ("notice", "scheduled")),
            # an application tendered with its procedural schedule stays an application
            ("notice", "ALLETE, Inc.; Notice of Application Tendered for Filing With the Commission and Establishing Procedural Schedule for Relicensing", "",
             ("application", "filed")),
        ]
        for action_type, title, line, want in cases:
            row = {"agency": "X", "action_type": action_type, "title": title, "status": line, "docket": "", "event_date": "2026-05-01"}
            g = F.derive(row, "", None)
            self.assertEqual((g["instrument"], g["action_status"]), want, title)

    def test_out_of_scope_is_marked_by_a_written_list(self):
        # session 3129: the audit's four (r3, r9, r26, r29), by their titles
        for t, why in [("Notice of 229 Boundary for the SLAC National Accelerator Laboratory", "a laboratory's security boundary"),
                       ("Cross-Media Electronic Reporting: Announcement of Determination To Approve Authorized Program Revisions", "electronic reporting rules"),
                       ("Senior Executive Service Performance Review Board", "an agency's personnel board"),
                       ("Energy Department Launches Genesis Mission Graduate Fellowship to Advance American Scientific Leadership", "a fellowship or scholarship"),
                       # session 3142: the fresh audit's r28
                       ("Notice of Inventory Completion: U.S. Department of Energy, Idaho Operations Office, Idaho Falls, ID",
                        "an inventory under the Native American Graves Protection and Repatriation Act"),
                       # session 3154: the third sample's r32 and r79
                       ("Oxirane, 2-phenyl-, polymer With oxirane, mono(hydrogen 2-sulfobutanedioate), octyl ether, sodium salt (1:2) in Pesticide "
                        "Formulations; Exemption From the Requirement for a Tolerance", "a pesticide's tolerance"),
                       ("Patrick Rhode Sworn in as Commissioner of the PUCT", "an official sworn in")]:
            self.assertEqual(F.scope(t), f"out of scope: {why}")
        # and no other action of the fixture (its r26 is the personnel board above)
        for it, text in items():
            want = "out of scope: an agency's personnel board" if it["r"] == 26 else ""
            self.assertEqual(derive(it, text)["scope"], want, it["row"]["title"])

    def test_the_connector_keeps_its_columns_and_adds_these_beside(self):
        import policy_sources as ps
        for c in ("agency", "action_type", "title", "significance", "why", "source_url", "event_date", "status"):
            self.assertIn(c, ps.COLS, "a column the Digest or the page reads keeps its name")
        for c in F.FIELD_COLS:
            self.assertIn(c, ps.COLS)
        self.assertEqual(ps.COLS.index("retrieved_at"), len(ps.COLS) - 1)

    def test_the_scorer_names_the_sector_the_action_applies_to(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("policy_score_3056", os.path.join(ROOT, "warehouse", "policy", "score.py"))
        PS = importlib.util.module_from_spec(spec)   # not the news scorer, which is also named score
        spec.loader.exec_module(PS)
        self.assertIn("choose policy only when the summary and the title name no part of it", PS.POLICY_NOTE)
        self.assertIn("When the summary is empty, say what the title says and no more", PS.POLICY_NOTE)

    def test_the_table_of_session_157_gains_the_new_columns_and_no_value_changes(self):
        import csv
        import tempfile
        import iso_prices as ip
        import policy_sources as ps
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "policy_actions.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("# MADE UP: a table of session 157's shape\n")
                w = csv.writer(f, lineterminator="\n")
                w.writerow(ps.COLS_S157)
                w.writerow(["madeup:1"] + ["x"] * (len(ps.COLS_S157) - 1))
            keep = ip.OUT_DIR
            try:
                ip.OUT_DIR = d
                self.assertTrue(ps.widen_held(lambda *a: None))
                self.assertFalse(ps.widen_held(lambda *a: None), "a table already wide is left")
            finally:
                ip.OUT_DIR = keep
            with open(path, encoding="utf-8") as f:
                f.readline()
                rows = list(csv.DictReader(f))
        self.assertEqual(list(rows[0]), ps.COLS)
        self.assertTrue(all(rows[0][c] == "x" for c in ps.COLS_S157[1:]))
        self.assertTrue(all(rows[0][c] == "" for c in F.FIELD_COLS))


if __name__ == "__main__":
    unittest.main()
