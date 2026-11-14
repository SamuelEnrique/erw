"""Session 6192 (chain 283): the held-out set, and a read of more than one page that held a row twice.

Energy Research Warehouse (ERW).

The held-out set (questions_heldout.yaml, 35 questions written after the fixes of chains 280 to 282, keyed from the live
set and committed before any asking) was asked once through the site's loop on 14 November 2026. 25 were asked before
the owner's API key reached its own usage limit (the 25th ended in that error; 10 were not asked). Of the 24 answered,
23 were right. The one wrong, h19, was a figure the chat had fetched and the tool had computed wrong:

  SPP's 2,058 withdrawn queue requests summed to 419,388.735 MW in the site's tool, the same on every asking; the rows
  sum to 419,636.335 MW (the key, and the Python tool's figure over the same live set).

The site's query read a table of things in the order of its time column alone. The rows of a queue's snapshot share one
status date, so the order was not whole, a page of 1,000 was cut anywhere among them, and a read of three pages held a
row twice and missed another: the count stayed 2,058 and the sum moved. The read is now in the order of the time and
then of the rows' own ids (entity_id, event_id; entity and variable for a series).

No model, no network.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


def load(name):
    with open(os.path.join(EVAL, name), encoding="utf-8") as f:
        return json.load(f)


class AReadOfMoreThanOnePage(unittest.TestCase):
    def test_the_order_ends_in_the_rows_own_ids_for_every_shape(self):
        ts = open(os.path.join(ROOT, "site", "lib", "chat", "tools.ts"), encoding="utf-8").read()
        self.assertIn('const ids = { series: "entity.asc,variable.asc", entities: "entity_id.asc", events: "event_id.asc" }[shape];', ts)
        self.assertIn('const order = dcol ? (shape === "entities" ? "entity_id.asc" : "event_id.asc") : `${tcol}.asc.nullslast,${ids}`;', ts)
        self.assertNotIn(": `${tcol}.asc.nullslast`;", ts)

    def test_the_stored_answer_was_the_tools_figure_and_not_the_rows(self):
        q = next(x for x in load("eval_s6192_site_heldout_run.json")["questions"] if x["id"] == "h19")
        key = load("keys_heldout.json")["keys"]["h19"]
        self.assertEqual(key["expected"], [419636.335])
        self.assertIn("419,388.74", q["answer"])
        out = q["trace"][0]["out"]
        self.assertEqual((out["rows_matched"], out["result"][0]["value"]), (2058, 419388.735))   # the count right, the sum not
        self.assertEqual(q["trace"][1]["out"]["result"][0]["count"], 2058)

    def test_the_answer_was_a_fetched_number(self):
        """The number check could not have caught it: the figure stood in a tool result. What failed was the read."""
        sys.path.insert(0, EVAL)
        import replay
        q = next(x for x in load("eval_s6192_site_heldout_run.json")["questions"] if x["id"] == "h19")
        self.assertEqual(replay.check(q)["numbers"], [])


class TheHeldOutSet(unittest.TestCase):
    def test_keyed_before_it_was_asked_and_of_every_kind(self):
        import yaml
        with open(os.path.join(EVAL, "questions_heldout.yaml"), encoding="utf-8") as f:
            qs = yaml.safe_load(f)["questions"]
        self.assertEqual(len(qs), 35)
        kinds = {k: sum(1 for q in qs if q["kind"] == k) for k in ("figure", "hold", "pause", "not_live", "outside", "gap", "partial")}
        self.assertEqual(kinds, {"figure": 17, "hold": 4, "pause": 1, "not_live": 3, "outside": 4, "gap": 1, "partial": 5})
        keys = load("keys_heldout.json")
        asked = [q["asked_at_utc"] for q in load("eval_s6192_site_heldout_run.json")["questions"]]
        self.assertLess(keys["computed_at_utc"], min(asked))
        self.assertEqual(len(keys["not_keyed"]), 5)   # left out and named, not replaced after the asking

    def test_the_asking_as_it_ended(self):
        run = load("eval_s6192_site_heldout_run.json")["questions"]
        grades = {g["id"]: g for g in load("eval_s6192_site_heldout_grades.json")["questions"]}
        self.assertEqual(len(run), 25)
        answered = [q for q in run if q["status"] != "error"]
        self.assertEqual(len(answered), 24)
        self.assertEqual(sorted(q["id"] for q in answered if not grades[q["id"]]["ok"]), ["h19"])
        stopped = next(q for q in run if q["status"] == "error")
        self.assertEqual(stopped["id"], "h30")
        self.assertIn("You have reached your specified API usage limits", stopped["error"])
        self.assertIsNone(stopped["answer"])   # an error is a record with no answer, never a guess


if __name__ == "__main__":
    unittest.main()
