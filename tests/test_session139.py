"""Session 139: the pilot table of large-load statements and the Stanford materials. The table's rule on rows made
for the test (no number without its sentence, a CAUTION row not taken, at most five an entity, newest and largest
first, a new stage before a repeated one, a range kept as a range); the documents the owner asked for, in place, with
no em dash; nothing of the table in the repository or in the live set. No request and no model call."""
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
    r = {"entity": "Oncor Electric Delivery", "entity_type": "utility", "parent_company": "Sempra", "document_title": "A release", "document_type": "earnings release",
         "document_date": "2026-08-06", "document_url": "https://example.org/release.html", "page_or_slide": "1", "mw": "44000", "quantity_as_written": "44 gigawatts",
         "stage_as_worded": "expected to be eligible", "load_type_as_worded": "large load", "place_as_worded": "its service territory", "time_horizon_as_worded": "",
         "wait_or_lead_time_as_worded": "", "sentence": "About 44 gigawatts is expected to be eligible.", "local_file": "x", "retrieved_at": "2026-10-07T01:40:00Z",
         "verified": "yes", "notes": "", "collected_in": "pass B"}
    r.update(over)
    return r


class Rule(unittest.TestCase):
    def test_no_number_without_its_sentence(self):
        said = []
        good, failed = ll.checked([row(), row(sentence=""), row(quantity_as_written="45 gigawatts"), row(verified="no"), row(document_url="release.html"),
                                   row(document_date="summer 2026")], said.append)
        self.assertEqual((len(good), failed), (1, 5))
        self.assertTrue(any("the figure as written is not in the sentence" in s for s in said))
        self.assertTrue(ll.figure_in_sentence(row(quantity_as_written="17,861 MW", sentence="It holds 17,861 MW of signed load.")))
        self.assertFalse(ll.figure_in_sentence(row(quantity_as_written="five gigawatts", sentence="It holds five gigawatts.")))   # digits only: kept beside the table

    def test_at_most_five_an_entity_newest_largest_and_a_new_stage_first(self):
        rows = [row(mw=str(1000 * k), quantity_as_written=f"{k} gigawatts", sentence=f"It is {k} gigawatts.", stage_as_worded="queue" if k < 5 else f"stage {k}",
                    document_date="2026-08-06" if k > 2 else "2026-05-01") for k in range(1, 9)]
        rows.append(row(entity="Some other utility", sentence="Not one of the ten: 9 gigawatts.", quantity_as_written="9 gigawatts"))
        rows.append(row(notes="CAUTION: a third party's copy", mw="99000", quantity_as_written="99 gigawatts", sentence="It is 99 gigawatts."))
        # session 141 takes every verified statement (PER_GROUP is None); the pilot's five an entity is the rule with per_group=5
        self.assertIsNone(ll.PER_GROUP)
        taken, left = ll.choose(rows, per_group=5)
        self.assertEqual(len(taken), 5)
        self.assertEqual([r["mw"] for r in taken], ["8000", "7000", "6000", "5000", "4000"])   # the newest document, its largest figure first
        self.assertEqual({r["entity_group"] for r in taken}, {"Oncor Electric Delivery"})
        why = {r["mw"]: r["why_not_taken"] for r in left}
        self.assertIn("CAUTION", why["99000"])
        self.assertIn("not one of the entities", why["44000"])
        self.assertEqual(len(taken) + len(left), len(rows))   # nothing collected is lost
        # a stage not yet held comes before one that repeats, even when it is smaller
        two = [row(mw=str(m), quantity_as_written=f"{m} MW", sentence=f"It is {m} MW.", stage_as_worded=s) for m, s in
               ((900, "queue"), (800, "queue"), (700, "queue"), (600, "queue"), (500, "queue"), (100, "signed"))]
        self.assertIn("100", [r["mw"] for r in ll.choose(two, per_group=5)[0]])

    def test_a_row_of_the_table(self):
        r = row(entity_group="Entergy", mw="7000-12000", quantity_as_written="7 to 12 GW", document_date="2026-05", sentence="A pipeline of 7 to 12 GW.")
        out = ll.to_row(r, "2026-10-07T02:00:00Z")
        self.assertEqual((out["mw"], out["mw_low"], out["mw_high"]), ("", 7000.0, 12000.0))   # a range stays a range
        self.assertEqual((out["event_date"], out["document_date_as_stated"]), ("2026-05-01", "2026-05"))
        self.assertEqual((out["event_type"], out["source"], out["status"]), ("large_load_statement", "erw:large_load_pilot", "expected to be eligible"))
        self.assertTrue(out["event_id"].startswith("llstmt:") and len(out["event_id"]) == 23)
        self.assertEqual(out["event_id"], ll.to_row(dict(r), "2026-10-08T00:00:00Z")["event_id"])   # a stable id
        self.assertEqual(list(out), ll.COLS)
        self.assertEqual(len(ll.GROUPS), 40)   # session 141: from ten entities to forty
        self.assertTrue(set(ll.PILOT_TEN) <= set(ll.GROUPS))


class Held(unittest.TestCase):
    def test_the_table_is_internal_and_not_in_the_repository_or_the_live_set(self):
        text = src("warehouse", "connectors", "large_load_statements.py")
        self.assertIn("License: internal", text)
        self.assertNotIn("urlopen", text)
        self.assertNotIn("anthropic", text.lower())
        live = src("warehouse", "supabase", "live_set.yaml")
        hold = live.split("catalogue_hold:", 1)[1]
        self.assertIn("- large_load_statements", hold)
        self.assertIn("- texas_delivery_charges", hold)
        self.assertIn("- erw:large_load_pilot", live.split("sources_hold:", 1)[1])
        self.assertNotIn("large_load_statements", live.split("catalogue_hold:", 1)[0])   # not among the tables loaded
        ignored = src(".gitignore")
        self.assertIn("warehouse/raw/", ignored)
        self.assertFalse(os.path.exists(os.path.join(ROOT, "docs", "accelerator", "large_load_statements.csv")))
        self.assertIn('(r"^large_load_statements$", "power")', src("warehouse", "metadata", "build_coverage.py"))


class Documents(unittest.TestCase):
    FILES = [("docs", "accelerator", "call_requirements.md"), ("docs", "accelerator", "evidence_pack.md"), ("docs", "accelerator", "large_load_pilot.md"),
             ("docs", "accelerator", "letter_facts.md"), ("docs", "accelerator", "redivis_release_checklist.md"), ("docs", "paper", "outline.md"),
             ("docs", "paper", "related_projects_notes.md")]

    def test_every_document_asked_for_is_there_with_no_em_dash(self):
        for f in self.FILES + [("warehouse", "connectors", "large_load_statements.py"), ("tests", "test_session139.py")]:
            text = src(*f)
            self.assertGreater(len(text), 2000, "/".join(f))
            self.assertNotIn(chr(0x2014), text, "/".join(f))

    def test_the_documents_say_what_the_evidence_supports(self):
        pilot, letter, call = src("docs", "accelerator", "large_load_pilot.md"), src("docs", "accelerator", "letter_facts.md"), src("docs", "accelerator", "call_requirements.md")
        self.assertIn("is false for New York and the Pacific Northwest", pilot)          # the strict claim is not written as true
        self.assertIn('Do not write "no public dataset exists"', letter)
        self.assertIn("No number without its sentence", pilot)
        self.assertIn("Nothing was summed", pilot)
        self.assertIn("The full RFP document of the current call was not read", call)   # what was not found is said
        self.assertIn("Its full text was not read", letter)
        self.assertIn("what a PJM data license would add", letter)
        outline = src("docs", "paper", "outline.md")
        for name in ("PUDL", "gridstatus", "Open Grid Emissions", "LBNL Queued Up", "Open Power System Data", "Item Response Warehouse"):
            self.assertIn(name, outline)
        self.assertEqual(outline.count("### 5."), 3)   # three empirical demonstrations
        checklist = src("docs", "accelerator", "redivis_release_checklist.md")
        self.assertIn("WAITS ON THE OWNER", checklist)
        self.assertIn("DONE", checklist)


if __name__ == "__main__":
    unittest.main()
