"""Session 3057 (chain 166): one record an action (warehouse/policy/records.py), graded on 30 stored rows whose
records were written from their own words (tests/fixtures/policy/records_3057.json), and the rules of the record.

    .venv/Scripts/python.exe -m pytest -q tests/test_policy_records.py
"""

import itertools
import json
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "policy"))
import fields as F  # noqa: E402
import records as R  # noqa: E402


def fixture():
    with open(os.path.join(ROOT, "tests", "fixtures", "policy", "records_3057.json"), encoding="utf-8") as f:
        items = json.load(f)["items"]
    for x in items:
        x["body"] = F.body(x["agency"], None, x["docket"], x["title"])
    return items


class Graded(unittest.TestCase):
    def test_every_pair_of_the_thirty_is_together_or_apart_as_the_answers_say(self):
        items = fixture()
        got = R.group(items)
        want = {x["event_id"]: x["record"] for x in items}
        together = joined = apart = 0
        for a, b in itertools.combinations(want, 2):
            w, g = want[a] == want[b], got[a] == got[b]
            together += w and g
            joined += g and not w
            apart += w and not g
        print(f"\npolicy records on 30 stored rows: {together} of 20 pairs together, {joined} wrongly joined, {apart} wrongly apart")
        self.assertEqual((together, joined, apart), (20, 0, 0))


class Rules(unittest.TestCase):
    def test_a_proceeding_id_and_what_is_not_one(self):
        self.assertEqual(R.proceeding_ids("CP25-539-001;CP25-539-000"), ["ferc:CP25-539"])
        self.assertEqual(R.proceeding_ids("Project No. 15249-002"), ["project:15249-002"])
        self.assertEqual(R.proceeding_ids("Docket Nos. 50-616 and 50-617;NRC-2026-0265", "NRC"), ["nrc:NRC-2026-0265"])
        self.assertEqual(R.proceeding_ids("Docket No. 50-261", "NRC"), [], "a plant's license docket spans unrelated matters")
        self.assertEqual(R.proceeding_ids("A2407-014-004-065516;#O2509-014-004-125222", "BLM"), [], "a billing code")
        self.assertEqual(R.proceeding_ids("WV-124-FOR;OSM-2016-0012;S1D1S SS08011000 SX064A000 232S1801", "OSMRE"),
                         ["docket:OSM-2016-0012", "osmre:WV-124-FOR"])
        self.assertEqual(R.proceeding_ids("Docket No. 15-190-LNG", "DOE"), ["doe:15-190-LNG"])
        self.assertEqual(R.proceeding_ids("EPA-HQ-OW-2009-0819;FRL-8794.3-01-OW;2040-AG48", "EPA"),
                         ["docket:EPA-HQ-OW-2009-0819", "rin:2040-AG48"])

    def rows(self):
        base = {"agency": "NRC", "action_type": "notice", "status": "Notice; receipt.", "source_url": "u", "significance": "6",
                "sector": "nuclear", "news_story_ids": "", "news_story_urls": "", "related_urls": "", "abstract": "", "first_paragraph": ""}
        title = "SMR, LLC; Pioneer Units 1 and 2; Phased Construction Permit Application-Limited Work Authorization"
        out = [dict(base, event_id=f"federalregister:x{i}", event_date=d, title=title, docket="NRC-2026-0265", source_url=f"u{i}")
               for i, d in enumerate(["2026-10-01", "2026-10-08", "2026-10-15", "2026-10-22"])]
        out.append(dict(base, event_id="federalregister:y", event_date="2026-08-28", title="SMR, LLC; Pioneer Units 1 and 2; Exemption",
                        status="Notice; issuance.", docket="NRC-2026-0265", news_story_ids="news:1", news_story_urls="n1"))
        out.append(dict(base, event_id="federalregister:z", event_date="2026-09-01", title="Another plant; Exemption",
                        status="Notice; issuance.", docket="Docket No. 50-261"))
        return pd.DataFrame(out)

    def test_a_repeated_notice_is_one_step_of_the_history_with_every_date(self):
        r = R.records(self.rows())
        self.assertEqual(len(r), 2)
        p = r[r["event_id"] == "nrc:NRC-2026-0265"].iloc[0]
        self.assertEqual(p["n_documents"], "5")
        self.assertEqual(p["history"].split(" | ")[0], "2026-08-28 order issued federalregister:y")
        self.assertTrue(p["history"].split(" | ")[1].startswith("2026-10-01,2026-10-08,2026-10-15,2026-10-22 application filed "))
        self.assertEqual((p["first_date"], p["last_date"], p["status"]), ("2026-08-28", "2026-10-22", "filed"))
        self.assertEqual(p["source_urls"], "u;u0;u1;u2;u3")
        self.assertEqual(p["news_story_urls"], "n1", "every source of every document")
        self.assertEqual(list(r.columns), R.COLS)

    def test_a_document_without_a_proceeding_id_joins_only_a_repeat_of_its_title(self):
        rows = [{"event_id": "a", "event_date": "2026-01-01", "agency": "DOE", "title": "Same Title", "docket": ""},
                {"event_id": "b", "event_date": "2026-01-20", "agency": "DOE", "title": "Same title.", "docket": ""},
                {"event_id": "c", "event_date": "2026-06-01", "agency": "DOE", "title": "Same Title", "docket": ""},
                {"event_id": "d", "event_date": "2026-01-02", "agency": "EPA", "title": "Same Title", "docket": ""}]
        g = R.group(rows)
        self.assertEqual(g["a"], g["b"])
        self.assertNotEqual(g["a"], g["c"], "more than 45 days later: another record")
        self.assertNotEqual(g["a"], g["d"], "another body")

    def test_the_next_step_is_any_document_s_first_step_after_the_newest(self):
        df = pd.DataFrame([
            {"event_id": "a", "event_date": "2026-09-01", "agency": "FERC", "action_type": "notice", "title": "Acme; Notice of Application",
             "status": "", "docket": "CP26-1-000", "source_url": "s1", "significance": "4", "sector": "gas", "abstract": "",
             "first_paragraph": "The deadline for filing protests, motions to intervene, and comments is 5:00 p.m. Eastern Time on December 8, 2026."},
            {"event_id": "b", "event_date": "2026-10-01", "agency": "FERC", "action_type": "notice", "title": "Acme; Notice of Scoping Period",
             "status": "", "docket": "CP26-1-000", "source_url": "s2", "significance": "5", "sector": "gas", "abstract": "", "first_paragraph": ""}])
        r = R.records(df).iloc[0]
        self.assertEqual((r["event_id"], r["next_step"], r["next_step_date"]), ("ferc:CP26-1", "comments due", "2026-12-08"))
        self.assertEqual((r["significance"], r["status"]), ("5", "open"))


if __name__ == "__main__":
    unittest.main()
