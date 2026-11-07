"""Session 2263 (chain 159): a facility's status from its own words, and a pause that is not a cancellation.

The second read (session 2249) found 3 of 60 sampled facilities with a status fault: two stated and left empty
("Chip firm will support first 222MW data center, due to be delivered next year"; "Microsoft's biggest India data
center on track to go live in mid-2026") and one cancelled for "Crusoe ... Pauses Wyoming Site" (the prompt's
cancelled is "paused indefinitely"). warehouse/datacenters/facility_fields.py reads an empty status from the
facility's words (status_from_words: its evidence, or the cluster's words when the cluster gives one facility) and
refuses a cancelled whose words say only paused (paused_only). On the replayed 2249 answers: 3 to 0, no other
facility of either fixture changing status.
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "datacenters"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "datacenters", "eval"))
import facility_fields as ff  # noqa: E402
import dc_fixture  # noqa: E402


class TheWords(unittest.TestCase):
    def test_each_status(self):
        for text, want in (("Microsoft's biggest India data center on track to go live in mid-2026", "under_construction"),
                           ("first 222MW data center, due to be delivered next year", "under_construction"),
                           ("Colt DCS and RMZ start work on third facility", "under_construction"),
                           ("county approves rezoning for data center", "permitted"),
                           ("developer filed plans with the county", "applied"),
                           ("Meta unveils Louisiana data center", "announced"),
                           ("the campus came online in March", "operating"),
                           ("Microsoft scraps data center project", "cancelled"),
                           ("JERA teams up with Dell, building data centre near Tokyo", ""),
                           ("Crusoe Pushed Aside at Wyoming AI Project After Google Concerns", "")):
            self.assertEqual(ff.status_from_words(text)[0], want, text)

    def test_paused(self):
        self.assertTrue(ff.paused_only("Pauses Wyoming Site"))
        self.assertFalse(ff.paused_only("paused indefinitely"))
        self.assertFalse(ff.paused_only("cancelled"))


class TheSample(unittest.TestCase):
    def test_status_faults_three_to_none(self):
        rows, log = dc_fixture.replay("2249")
        fills = [l for l in log.splitlines() if "status" in l and "from the words" in l]
        self.assertEqual(len(fills), 2)
        self.assertTrue(any("'on track to go live'" in l for l in fills))
        self.assertTrue(any("'due to be delivered'" in l for l in fills))
        self.assertIn("'Pauses Wyoming Site' says paused, not kept", log)
        with open(os.path.join(ROOT, "tests", "fixtures", "datacenters", "stories_2249.json"), encoding="utf-8") as f:
            fx = {s["event_id"]: s.get("fixture") for s in json.load(f)}
        got = {}
        for r in rows.to_dict("records"):
            for sid in str(r["story_ids"]).split(";"):
                if fx.get(sid) in ("F018", "F039", "F041"):
                    got[fx[sid]] = r["project_status"]
        self.assertEqual(got, {"F018": "under_construction", "F039": "", "F041": "under_construction"})


if __name__ == "__main__":
    unittest.main()
