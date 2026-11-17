"""Session 7052 (chain 370, the data machine): done-line request 109.

energy_projects carries a queue position's proposed in-service date (`proposed_date`, from the queue table's
proposed_in_service_date, where the grid operator's report states one), and the map's file carries it beside the queue
date (`more.queue.proposed`, a date as `d` writes one, 0 where none).
"""

import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheProposedDate(unittest.TestCase):
    def test_the_builder_carries_the_column(self):
        s = src("warehouse", "derived", "energy_projects.py")
        self.assertIn('"source_table", "proposed_date"]', s)
        self.assertIn('d["proposed_in_service_date"]', s)

    def test_the_live_set_is_not_asked_for_it(self):
        # a new live column needs a migration (a person's step); the live set's select stays as it was
        self.assertNotIn("proposed_date", src("warehouse", "supabase", "live_set.yaml"))

    def test_the_map_file_holds_one_per_queue_position(self):
        d = json.loads(src("site", "data", "map.json"))
        q = next(k for k in d["kinds"] if k["slug"] == "queue")
        p = d["more"]["queue"]["proposed"]
        self.assertEqual(len(p), q["rows"])
        self.assertTrue(all(x == 0 or 19000101 <= x <= 21001231 for x in p))
        self.assertGreater(sum(1 for x in p if x), q["rows"] // 2)


if __name__ == "__main__":
    unittest.main()
