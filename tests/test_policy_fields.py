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
import fields as F  # noqa: E402

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

    def test_a_past_date_that_is_no_step_is_left(self):
        t = ("If you submitted comments on this project to the Commission before the opening of this docket on "
             "September 9, 2026, you will need to file those comments in Docket No. CP26-578-000.")
        self.assertEqual(F.dates(t), [])

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
