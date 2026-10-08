"""Session 141: the large-load statements, from ten entities to forty. The rule on rows made for the test (no number
without its sentence, for megawatt rows and for wait rows; a third party's copy not taken; a row collected twice taken
once; every verified statement taken, with no cap; an undated web page filed on the day it was read and said so); the
stage vocabulary (the original words always kept beside the class; a funnel placed, placed in part, or not); the
table internal and absent from the repository; the summary in place. No request and no model call."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import large_load_statements as ll  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def row(**over):
    r = {"entity": "Oncor Electric Delivery", "entity_type": "utility", "parent_company": "Sempra", "document_title": "An answer in a rate case", "document_type": "rate case testimony",
         "document_date": "2025-08-25", "document_url": "https://example.org/answer.pdf", "page_or_slide": "64", "mw": "5846", "quantity_as_written": "5,846 MW",
         "stage_as_worded": "advanced to the construction stage", "load_type_as_worded": "large load", "place_as_worded": "its service territory", "time_horizon_as_worded": "",
         "wait_or_lead_time_as_worded": "", "sentence": "105 projects have advanced to the construction stage, totaling 5,846 MW.", "local_file": "x", "retrieved_at": "2026-10-07T09:20:00Z",
         "verified": "yes", "notes": "", "collected_in": "pass H", "page": "64", "row_kind": "mw", "stage_class_proposed": "5 under construction or energized",
         "stage_class_reason": "the document says the projects advanced to the construction stage", "terms_url": ""}
    r.update(over)
    return r


class Rule(unittest.TestCase):
    def test_forty_entities_and_the_pilots_ten_among_them(self):
        self.assertEqual(len(ll.FORTY_141), 40)   # session 151: GROUPS holds eighty now, the forty of this session first
        self.assertEqual(list(ll.GROUPS)[:40], ll.FORTY_141)
        self.assertTrue(set(ll.PILOT_TEN) <= set(ll.FORTY_141))
        self.assertNotIn("MISO", " ".join(ll.GROUPS))   # MISO's own site is not requested while its terms are under review
        self.assertIn("MISO is not among them", ll.ENTITIES_141)
        # PPL's and FirstEnergy's submissions that PJM posts are theirs now, not PJM's
        self.assertEqual(ll.group_of("PPL Electric Utilities (submission to PJM)"), "PPL")
        self.assertEqual(ll.group_of("FirstEnergy (submission to PJM)"), "FirstEnergy")
        self.assertEqual(ll.group_of("PJM Interconnection"), "PJM Interconnection")
        self.assertEqual(ll.group_of("Appalachian Power (AEP)"), "American Electric Power")
        self.assertEqual(ll.group_of("California Energy Commission (the data center forecast California ISO relies on)"), "California ISO")
        self.assertIsNone(ll.group_of("A utility nobody chose"))

    def test_no_number_without_its_sentence_for_megawatts_and_for_waits(self):
        wait = row(row_kind="wait", mw="", quantity_as_written="825 days", sentence="The average interconnection time was 825 days.", stage_class_proposed="none")
        words = row(row_kind="wait", mw="", quantity_as_written="several years", sentence="It could take several years after an agreement is reached.")
        broken = row(row_kind="wait", mw="", quantity_as_written="multiyear", sentence="The need is driven by the multi-year transmission buildout.")
        self.assertTrue(ll.figure_in_sentence(wait) and ll.figure_in_sentence(words) and ll.figure_in_sentence(broken))
        self.assertFalse(ll.figure_in_sentence(row(row_kind="wait", quantity_as_written="687 days", sentence="The average was 825 days.")))
        self.assertFalse(ll.figure_in_sentence(row(quantity_as_written="six gigawatts", sentence="It holds six gigawatts.")))   # a megawatt figure in words: kept beside the table
        said = []
        good, failed = ll.checked([row(), wait, row(sentence=""), row(verified="no"), row(document_date="summer 2026"), row(document_date="", page="12")], said.append)
        # session 151: a PDF that prints no date is filed on the day it was read, as an undated web page was here (until then it was not taken)
        self.assertEqual((len(good), failed), (3, 3))
        self.assertEqual(ll.to_row(dict(row(document_date="", page="12"), entity_group="Oncor Electric Delivery"), "x")["event_date_basis"], "undated document: the day it was read")

    def test_every_verified_statement_is_taken_once_and_a_third_partys_copy_is_not(self):
        rows = [row(mw=str(1000 * k), quantity_as_written=f"{k} gigawatts", sentence=f"It is {k} gigawatts.", stage_as_worded=f"stage {k}") for k in range(1, 9)]
        again = row(mw="3000", quantity_as_written="3 gigawatts", sentence="It is 3 gigawatts.", stage_as_worded="stage 3", collected_in="pass Z")
        staff = row(notes="CAUTION: the commission staff's testimony, not the company's", quantity_as_written="99 gigawatts", sentence="It is 99 gigawatts.")
        hosted = row(document_url="https://ceae.ku.edu/deck.pdf", quantity_as_written="2 gigawatts", sentence="Hosted elsewhere: 2 gigawatts.")
        other = row(entity="A utility nobody chose", quantity_as_written="9 gigawatts", sentence="Nine: 9 gigawatts.")
        taken, left = ll.choose(rows + [again, staff, hosted, other])
        self.assertEqual(len(taken), 8)   # no cap: all eight, and the row collected twice once
        self.assertEqual([r["collected_in"] for r in taken if r["quantity_as_written"] == "3 gigawatts"], ["pass Z"])   # the later pass's copy
        why = sorted(r["why_not_taken"] for r in left)
        self.assertEqual(len(left), 4)
        self.assertTrue(any("CAUTION" in w for w in why) and any("third party's host" in w for w in why) and any("not one of the entities" in w for w in why)
                        and any("collected again" in w for w in why))
        self.assertEqual(len(taken) + len(left), len(rows) + 4)   # nothing collected is lost

    def test_a_row_of_the_table(self):
        out = ll.to_row(dict(row(), entity_group="Oncor Electric Delivery"), "2026-10-07T10:00:00Z")
        self.assertEqual(list(out), ll.COLS)
        self.assertEqual((out["page"], out["row_kind"], out["stage_class"], out["event_date_basis"]), ("64", "mw", "5 under construction or energized", "document"))
        self.assertEqual(out["status"], "advanced to the construction stage")   # the document's own words stay
        self.assertIn("the document says the projects advanced", out["stage_class_basis"])
        wait = ll.to_row(dict(row(row_kind="wait", mw="", quantity_as_written="825 days", sentence="The average was 825 days.", stage_class_proposed="none"), entity_group="Oncor Electric Delivery"), "x")
        self.assertEqual((wait["mw"], wait["row_kind"], wait["stage_class"]), ("", "wait", "none"))
        # a web page that prints no date: filed on the day it was read, and said so
        page = ll.to_row(dict(row(document_date="", page="", retrieved_at="2026-10-07T09:30:00Z"), entity_group="PacifiCorp"), "x")
        self.assertEqual((page["event_date"], page["document_date_as_stated"], page["event_date_basis"]), ("2026-10-07", "", "undated page: the day it was read"))
        year = ll.to_row(dict(row(document_date="2025"), entity_group="AES"), "x")
        self.assertEqual((year["event_date"], year["document_date_as_stated"]), ("2025-01-01", "2025"))
        # a pilot row carries no class of its own: placed by its entity's stage words where a later pass placed them, else "not classed"
        pilot = dict(row(stage_class_proposed="", stage_class_reason="", stage_as_worded="Electric Service Agreement (ESA)"), entity_group="Dominion Energy Virginia")
        self.assertEqual(ll.to_row(pilot, "x", {("Dominion Energy Virginia", "electric service agreement (esa)"): "4 signed service agreement"})["stage_class"], "4 signed service agreement")
        self.assertEqual(ll.to_row(pilot, "x", {})["stage_class"], "not classed")


class Vocabulary(unittest.TestCase):
    STAGES = [
        dict(entity="Dominion Energy Virginia", stage_as_worded="DP Request", definition_as_worded="", stage_class_proposed="1 request or inquiry", stage_class_reason="a request", funnel_order="1", collected_in="pass H"),
        dict(entity="Dominion Energy Virginia", stage_as_worded="Engineering Letter of Authorization (ELOA)", definition_as_worded="An ELOA authorizes engineering.", stage_class_proposed="2 study or engineering", stage_class_reason="engineering", funnel_order="2", collected_in="pass H"),
        dict(entity="Dominion Energy Virginia", stage_as_worded="Electric Service Agreement (ESA)", definition_as_worded="", stage_class_proposed="4 signed service agreement", stage_class_reason="an agreement", funnel_order="3", collected_in="pass H"),
        dict(entity="FirstEnergy", stage_as_worded="Load Studies", definition_as_worded="", stage_class_proposed="2 study or engineering", stage_class_reason="studies", funnel_order="1", collected_in="pass D"),
        dict(entity="FirstEnergy", stage_as_worded="Pipeline", definition_as_worded="", stage_class_proposed="none", stage_class_reason="not defined", funnel_order="2", collected_in="pass D"),
        dict(entity="Xcel Energy", stage_as_worded="Electric Services Agreement", definition_as_worded="", stage_class_proposed="4 signed service agreement", stage_class_reason="", funnel_order="1", collected_in="pass E"),
        dict(entity="Xcel Energy", stage_as_worded="Feasibility Study", definition_as_worded="", stage_class_proposed="2 study or engineering", stage_class_reason="", funnel_order="2", collected_in="pass E"),
    ]

    def test_the_original_words_stay_beside_the_class(self):
        v = ll.stage_vocabulary(self.STAGES)
        self.assertEqual(len(v), 7)
        for r in v:
            self.assertTrue(r["stage_as_worded"] and (r["stage_class"] in ll.STAGES or r["stage_class"] == ll.NOT_A_STAGE))
        eloa = next(r for r in v if r["stage_as_worded"].startswith("Engineering Letter"))
        self.assertEqual((eloa["stage_class"], eloa["stage_class_basis"]), ("2 study or engineering", "the document defines the stage"))
        self.assertEqual(next(r for r in v if r["stage_as_worded"] == "DP Request")["stage_class_basis"], "the stage's own words")
        self.assertEqual(len(ll.STAGES), 5)
        self.assertEqual([k[0] for k in ll.STAGES], ["1", "2", "3", "4", "5"])

    def test_which_funnels_can_be_placed(self):
        f = ll.funnels(ll.stage_vocabulary(self.STAGES))
        self.assertEqual(f["Dominion Energy Virginia"]["verdict"], "placed")           # three stages in order, every word on a stage
        self.assertEqual(f["FirstEnergy"]["verdict"], "one stage only")                # one word on a stage, one on none
        self.assertEqual(f["Xcel Energy"]["verdict"], "not placed")                    # its own order runs against the stages' order
        self.assertTrue(f["Xcel Energy"]["against_order"])
        self.assertEqual(f["Salt River Project"]["verdict"], "not placed")             # no stage words held
        self.assertEqual(len(f), len(ll.GROUPS))   # forty here, eighty since session 151

    def test_a_class_is_one_of_five_or_none(self):
        self.assertEqual(ll.class_of("4 signed service agreement"), "4 signed service agreement")
        self.assertEqual(ll.class_of("none: a forecast"), "none")
        self.assertEqual(ll.class_of(""), "")


class Held(unittest.TestCase):
    def test_the_table_is_internal_and_nothing_of_it_is_published(self):
        text = src("warehouse", "connectors", "large_load_statements.py")
        self.assertIn("License: internal", text)
        self.assertIn("DO NOT SUM across rows or entities", text)
        self.assertNotIn("urlopen", text)
        self.assertNotIn("requests.get", text)
        self.assertNotIn("anthropic", text.lower())
        live = src("warehouse", "supabase", "live_set.yaml")
        self.assertIn("- large_load_statements", live.split("catalogue_hold:", 1)[1])
        self.assertNotIn("large_load_statements", live.split("catalogue_hold:", 1)[0])
        tracked = os.popen(f'git -C "{ROOT}" ls-files warehouse/output warehouse/raw').read()
        self.assertNotIn("large_load_statements", tracked)   # neither the table nor the passes' files are in the repository
        self.assertFalse(os.path.exists(os.path.join(ROOT, "site", "data", "large_load_statements.json")))

    def test_the_summary_for_the_letter_is_in_place(self):
        doc = src("docs", "accelerator", "large_load_forty.md")
        self.assertNotIn(chr(0x2014), doc)
        for words in ("no number without its sentence", "nothing summed across entities", "434", "38", "five stages", "825 days", "687 days", "not a person's review",
                      "Estimates from the rates measured here, not measurements"):
            self.assertIn(words, doc)
        self.assertLessEqual(len(doc.splitlines()), 90)   # one page
        self.assertNotIn(chr(0x2014), src("warehouse", "connectors", "large_load_statements.py"))


if __name__ == "__main__":
    unittest.main()
