"""Session 7002 (chain 301): the policy monitor's data faults, rows 7, 12, 13, 18 and 25 of
docs/reviews/policy-faults-2026-11-11.md.

Energy Research Warehouse (ERW). On rows and texts written here (MADE UP: no such documents): a deadline's hour with a
time zone and no "Time" (row 7); a printed text read before the fields existed, whose fields came from the summary
alone, asked again and its fields read from it, and one whose fields came from its text never asked again (row 7); two
actions of one docket with their own RINs as two records (row 13); the plain read's document and the scoring
document in the monitor's file (rows 12 and 18); a year a read writes beside words its text does not write it with
(row 25). No network, no data lock.

    python -m unittest tests.test_session7002_policy -v
"""

import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for part in ("connectors", "policy", "derived", "chat"):
    sys.path.insert(0, os.path.join(ROOT, "warehouse", part))
import fields as F  # noqa: E402
import monitor_site as MS  # noqa: E402
import policy_sources as ps  # noqa: E402
import reads as R  # noqa: E402
import records as REC  # noqa: E402

DOC = ("<html><body><pre>\n[Federal Register Volume 91, Number 1 (Friday, January 2, 2026)]\n[Notices]\n"
       "[FR Doc No: 2026-00001]\n\n\n-----------------------------------------------------------------------\n\n"
       "DEPARTMENT OF ENERGY\n\nFederal Energy Regulatory Commission\n\n[Docket No. CP26-1-000]\n\n\n"
       "Made Up LNG LLC; Notice of Schedule for the Preparation of an Environmental Assessment\n\n"
       "    Schedule for Environmental Review\n\n"
       "Issuance of EA--November 6, 2026\n"
       "90-day Federal Authorization Decision Deadline--February 4, 2027\n</pre></body></html>")


def fr_row(n, day="2026-01-02"):
    """MADE UP: a Register row as the connector builds it."""
    return {"event_id": f"federalregister:{n}", "event_date": day, "fr_document_number": n, "agency": "FERC",
            "action_type": "notice", "status": "Notice.", "docket": "CP26-1-000", "parties": "FERC",
            "title": "Made Up LNG LLC; Notice of Schedule for the Preparation of an Environmental Assessment",
            "abstract": "", "_text_url": f"https://www.federalregister.gov/documents/full_text/text/2026/01/02/{n}.txt"}


def quiet(*a, **k):
    return None


class Row7Dates(unittest.TestCase):
    def test_a_time_zone_without_time(self):
        self.assertEqual(F.dates("comments are due by 5:00 p.m. Eastern on November 16, 2026."),
                         [("comments_due", "2026-11-16", "comments are due by 5:00 p.m. Eastern on November 16, 2026.")])
        self.assertEqual(F.dates("Protests are due by 4 p.m. Central Prevailing on December 1, 2026.")[0][:2],
                         ("intervention_due", "2026-12-01"))


class Row7TextsAskedAgain(unittest.TestCase):
    def test_a_text_whose_fields_came_from_the_summary_is_asked_again(self):
        calls = []
        with tempfile.TemporaryDirectory() as d:
            r = fr_row("2026-00001")
            held = {r["event_id"]: {"text_status": "read", "fields_from": "record and summary", "first_paragraph": "",
                                    "place_words": "", "title_register": "", "text_read_at": "2026-10-01T00:00:00Z",
                                    "title": r["title"]}}
            ps.read_texts([r], held, d, quiet, fetch=lambda u: calls.append(u) or (200, DOC.encode(), ""), sleep=quiet)
        self.assertEqual(len(calls), 1)
        self.assertIn("text", r["fields_from"])
        self.assertIn("review_due=2026-11-06", r["dates"])
        self.assertIn("decision_due=2027-02-04", r["dates"])

    def test_a_text_whose_fields_came_from_it_is_not_asked_again(self):
        calls = []
        with tempfile.TemporaryDirectory() as d:
            r = fr_row("2026-00001")
            held = {r["event_id"]: {"text_status": "read", "fields_from": "record and text", "dates": "review_due=2026-11-06",
                                    "first_paragraph": "", "place_words": "", "title_register": "", "title": r["title"],
                                    "text_read_at": "2026-10-01T00:00:00Z"}}
            ps.read_texts([r], held, d, quiet, fetch=lambda u: calls.append(u) or (200, DOC.encode(), ""), sleep=quiet)
        self.assertEqual(calls, [])
        self.assertEqual(r["dates"], "review_due=2026-11-06")

    def test_one_left_by_the_ceiling_keeps_what_it_held(self):
        with tempfile.TemporaryDirectory() as d:
            r = fr_row("2026-00001")
            held = {r["event_id"]: {"text_status": "read", "fields_from": "record and summary", "first_paragraph": "p",
                                    "place_words": "", "title_register": "", "text_read_at": "2026-10-01T00:00:00Z",
                                    "title": r["title"]}}
            n = ps.read_texts([r], held, d, quiet, max_requests=0, fetch=lambda u: (200, DOC.encode(), ""), sleep=quiet)
        self.assertEqual(n["left"], 1)
        self.assertEqual((r["text_status"], r["first_paragraph"]), ("read", "p"))


class Row13Records(unittest.TestCase):
    def test_two_rins_in_one_docket_are_two_records(self):
        rows = [dict(event_id="fr:19071", event_date="2026-09-17", agency="EPA", body="EPA", title="Partial Repeal",
                     docket="EPA-HQ-OAR-2025-0124;FRL-12674-02-OAR;2060-AW55"),
                dict(event_id="fr:19072", event_date="2026-09-17", agency="EPA", body="EPA", title="Rescission",
                     docket="EPA-HQ-OAR-2025-0124;FRL-12674.1-01-OAR;2060-AX00"),
                dict(event_id="fr:20000", event_date="2026-10-01", agency="EPA", body="EPA", title="Correction",
                     docket="EPA-HQ-OAR-2025-0124")]
        g = REC.group(rows)
        self.assertNotEqual(g["fr:19071"], g["fr:19072"])
        self.assertEqual(len(set(g.values())), 2)
        self.assertIn(g["fr:20000"], (g["fr:19071"], g["fr:19072"]))

    def test_one_rin_or_none_keeps_one_record(self):
        rows = [dict(event_id="a", event_date="2026-01-01", agency="EPA", body="EPA", title="P", docket="EPA-HQ-OAR-2024-0001;2060-AA00"),
                dict(event_id="b", event_date="2026-02-01", agency="EPA", body="EPA", title="F", docket="EPA-HQ-OAR-2024-0001")]
        g = REC.group(rows)
        self.assertEqual(g["a"], g["b"])


def actions():
    base = {"event_type": "filing", "parties": "", "entity_ids": "", "mw": "", "price": "", "currency": "",
            "source": "federalregister:api", "abstract": "", "rin": "", "fr_document_number": "", "sector_tags": "",
            "related_urls": "", "news_story_ids": "", "news_story_urls": "", "sector": "gas", "first_paragraph": "",
            "agency": "FERC", "action_type": "notice", "status": "", "docket": "Docket No. CP26-1-000", "states": "TX"}
    return pd.DataFrame([
        dict(base, event_id="federalregister:1", event_date="2026-09-01", significance="7", why="a new LNG export",
             title="Acme LNG, LLC; Notice of Application", source_url="https://example.gov/1"),
        dict(base, event_id="federalregister:2", event_date="2026-10-01", significance="5", why="a schedule",
             title="Acme LNG, LLC; Notice of Schedule for the Preparation of an Environmental Assessment",
             source_url="https://example.gov/2"),
    ])


class Rows12And18Monitor(unittest.TestCase):
    def test_the_plain_read_and_the_significance_name_their_documents(self):
        reads = pd.DataFrame([{"action_event_id": "federalregister:1", "affected_isos": "", "plain_read": "Acme asked FERC."}])
        doc = MS.build(actions(), reads, {}, today="2026-11-16")
        r = doc["rows"][0]
        self.assertEqual(r["plain_doc"], {"event_id": "federalregister:1", "date": "2026-09-01", "newest": False})
        self.assertEqual(r["significance"], 7)
        self.assertEqual(r["significance_doc"], {"event_id": "federalregister:1", "date": "2026-09-01", "why": "a new LNG export"})


class Row25Years(unittest.TestCase):
    TEXT = "Interior affirms the two lease sales. The notices of sale published in 2023 were challenged in lawsuits filed in 2023."

    def test_a_year_beside_other_words_fails(self):
        self.assertEqual(R.years_beside_their_words("two offshore lease sales held in 2023", self.TEXT), ["held in 2023"])

    def test_a_year_beside_its_own_words_passes(self):
        self.assertEqual(R.years_beside_their_words("notices of sale were published in 2023; lawsuits filed in 2023", self.TEXT), [])

    def test_check_field_says_so(self):
        val = {"spans": ["Interior affirms the two lease sales"], "text": "Interior stands by two lease sales held in 2023."}
        self.assertTrue(R.check_field("plain_read", val, self.TEXT)[0].startswith("a year beside words"))


if __name__ == "__main__":
    unittest.main()
