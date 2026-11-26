"""Audit of the project map, finding 1 (session 10216, docs/reviews/map-model-audit-2026-11-26.md): ERCOT's "Completed"
was worded for one copy of the queue. The list said "Agreement signed, built or not" and the queue tiles' hover said
"Completed" is a signed agreement, built or not: true of gridstatus's word, which the connector kept until session 7022
(landed 16 November 2026). From a pull after that, ERCOT is "completed" only with its day of approval to synchronize.
The page's copy (queue of 2026-11-05) still carries gridstatus's word: 544 of ERCOT's 577 "completed" positions plan to
operate after November 2026. The Queues tab's ERCOT "Operating" follows the queue as pulled. No figure moves.

1. Through the page's file and the connector: the copy's ERCOT words are the ones its vintage predicts, and the
   connector writes ERCOT's milestones. Passes on main.
2. The fix on this branch, words only: the list, the tiles' hover and the Queues tab follow the copy's queue vintage.
   Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class ErcotCompletedFollowsTheCopy(unittest.TestCase):
    def test_the_copys_ercot_words_are_the_ones_its_vintage_predicts(self):
        f = json.loads(src("site", "data", "map.json"))
        q0, n = f["kinds"][2]["start"], f["kinds"][2]["rows"]
        mq = f["more"]["queue"]
        done = [j for j in range(n) if f["grids"][f["g"][q0 + j]]["slug"] == "ercot" and f["statuses"][f["st"][q0 + j]]["slug"] == "q-completed"]
        own = {mq["statuses"][mq["status"][j]] for j in done}
        if f["vintages"]["queue"] < "2026-11-17":
            self.assertEqual(own, {"Completed"}, "a copy before ERCOT's milestones carries gridstatus's word")
            later = sum(1 for j in done if mq["proposed"][j] >= 20261101)
            self.assertGreater(later, len(done) / 2, "most of them still plan to operate: signed agreements, not plants")
        else:
            self.assertNotIn("Completed", own, "a copy from ERCOT's milestones carries ERCOT's own words")
        conn = src("warehouse", "connectors", "iso_queues.py")
        self.assertIn('"ercot": {"Active": "active", "IA Signed": "active", "Approved for Synchronization": "completed"}', conn)

    def test_the_words(self):
        lib = src("site", "lib", "projectmap.ts")
        self.assertIn('export const ERCOT_MILESTONES_FROM = "2026-11-17";', lib)
        self.assertIn('"Agreement signed, built or not (ERCOT; the table says completed)"', lib)
        self.assertIn('"Approved for synchronization (ERCOT; the table says completed)"', lib)
        page = src("site", "app", "map", "ProjectMap.tsx")
        self.assertIn("ercotCompletedIsSigned(f)", page)
        self.assertIn("this copy of the queue predates the connector's reading of ERCOT's own milestones", page)
        self.assertIn("\\\"Completed\\\" is a position ERCOT approved to synchronize", page)
        q = src("site", "app", "map", "QueuesView.tsx")
        self.assertIn("from a pull before 17 November 2026 it counts every position with a signed interconnection agreement, built or not; "
                      "from later pulls, the positions ERCOT approved to synchronize.", q)
        self.assertIn("Session 10216 (the map audit, finding 1)", src("docs", "methods", "map.md"))
        for text in (lib, page, q):
            self.assertNotIn(chr(0x2014), text)


if __name__ == "__main__":
    unittest.main()
