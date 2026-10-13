"""Session 231: the findings pipeline proven end to end, and the one dead link it found.

A draft approved at /internal/findings and chosen for the Roundup has no committed card file: its card is in its row of
public.scanner_drafts. roundup_pick now reads it from there, only while its state is approved, and writes the Roundup's
lines without the words "not reviewed" and without a link to a card page that does not exist. No network: the review
list is a function handed in.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import roundup_pick  # noqa: E402

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "session181", "drafts.json")


def draft():
    with open(FIXTURE, encoding="utf-8") as f:
        return json.load(f)[0]


class Answer:
    def __init__(self, rows, status=200):
        self.status_code, self._rows = status, rows

    def json(self):
        return self._rows


class WithKeys(unittest.TestCase):
    def setUp(self):
        import lock
        self.lock, self.saved = lock, lock.env
        lock.env = lambda name: {"SUPABASE_URL": "https://example.invalid", "SUPABASE_SERVICE_KEY": "k"}.get(name, "")

    def tearDown(self):
        self.lock.env = self.saved


class TheApprovedDraft(WithKeys):
    def test_only_an_approved_draft_is_asked_for(self):
        d, seen = draft(), {}

        def get(url, params=None, headers=None, timeout=None):
            seen.update(url=url, params=params)
            return Answer([{"id": d["id"], "card": d["card"]}])
        card = roundup_pick.approved_draft(d["id"], log=lambda m: None, get=get)
        self.assertEqual(card["card_id"], d["id"])
        self.assertTrue(seen["url"].endswith("/rest/v1/scanner_drafts"))
        self.assertEqual(seen["params"]["state"], "eq.approved")
        self.assertEqual(seen["params"]["id"], f"eq.{d['id']}")

    def test_a_draft_not_approved_is_no_card(self):
        d = draft()
        self.assertIsNone(roundup_pick.approved_draft(d["id"], log=lambda m: None, get=lambda *a, **k: Answer([])))
        self.assertIsNone(roundup_pick.approved_draft(d["id"], log=lambda m: None, get=lambda *a, **k: Answer([], 500)))

    def test_a_row_holding_another_cards_id_is_no_card(self):
        d = draft()
        other = dict(d["card"], card_id="scan-record-000000000000")
        self.assertIsNone(roundup_pick.approved_draft(d["id"], log=lambda m: None, get=lambda *a, **k: Answer([{"id": d["id"], "card": other}])))


class TheChoice(unittest.TestCase):
    def setUp(self):
        self.saved = roundup_pick.approved_draft

    def tearDown(self):
        roundup_pick.approved_draft = self.saved

    def test_a_draft_without_a_file_is_read_from_the_review_list(self):
        d, asked = draft(), []
        roundup_pick.approved_draft = lambda cid, log=print, get=None: asked.append(cid) or d["card"]
        self.assertEqual(roundup_pick.load_card(d["id"], log=lambda m: None)["card_id"], d["id"])
        self.assertEqual(asked, [d["id"]])

    def test_a_finding_without_a_file_never_asks_the_review_list(self):
        asked = []
        roundup_pick.approved_draft = lambda cid, log=print, get=None: asked.append(cid)
        self.assertIsNone(roundup_pick.load_card("no_such_finding", log=lambda m: None))
        self.assertEqual(asked, [])

    def test_a_committed_finding_is_read_from_its_file_as_before(self):
        self.assertEqual(roundup_pick.load_card("queue_divorce")["card_id"], "queue_divorce")

    def test_the_drafts_lines_say_it_was_approved_and_link_no_missing_page(self):
        d = draft()
        L = roundup_pick.lines(d["card"], "2026-W42")
        text = "\n".join(L)
        self.assertIn("chosen for this Roundup", L[0])
        self.assertNotIn("not reviewed", text)
        self.assertIn("approved by a person at the review list", text)
        self.assertNotIn("/analysis/card/", text)
        self.assertIn(d["card"]["source_line"], text)
        for c in d["card"]["callouts"]:
            self.assertIn(c["after"]["text"], text)
        self.assertNotIn(chr(0x2014), text)


def load_worker():
    """The findings worker by its path, under its own module name (tests/test_session170.py says why)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("findings_worker_231", os.path.join(ROOT, "warehouse", "analysis", "findings", "worker.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheWorkersCode(unittest.TestCase):
    """The worker started on 11 October ran the scanner of 10 October for two days: it loads again what changed."""

    def test_unchanged_code_is_not_loaded_again(self):
        w = load_worker()
        calls = []
        self.assertFalse(w.fresh_code(stamp=lambda: w._LOADED["stamp"], again=lambda: calls.append(1), say=lambda m: None))
        self.assertEqual(calls, [])

    def test_changed_code_is_loaded_again_once_and_said(self):
        w = load_worker()
        calls, said = [], []
        later = w._LOADED["stamp"] + 60
        self.assertTrue(w.fresh_code(stamp=lambda: later, again=lambda: calls.append(1), say=said.append))
        self.assertFalse(w.fresh_code(stamp=lambda: later, again=lambda: calls.append(1), say=said.append))
        self.assertEqual(calls, [1])
        self.assertEqual(len(said), 1)
        self.assertIn("loaded again", said[0])

    def test_the_stamp_is_the_newest_python_file_of_the_folder(self):
        import tempfile
        w = load_worker()
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(w.code_stamp(d), 0.0)
            for name, t in (("a.py", 1000), ("b.py", 3000), ("c.txt", 9000)):
                p = os.path.join(d, name)
                open(p, "w").close()
                os.utime(p, (t, t))
            self.assertEqual(w.code_stamp(d), 3000)

    def test_every_request_asks_first(self):
        with open(os.path.join(ROOT, "warehouse", "analysis", "findings", "worker.py"), encoding="utf-8") as f:
            text = f.read()
        body = text[text.index("def run_one("):text.index("def turn(")]
        self.assertIn("fresh_code()", body)
        self.assertLess(body.index("fresh_code()"), body.index("run_scanner(q, row, params, in_dir)"))
        self.assertLess(body.index("fresh_code()"), body.index("run_finding.run("))


if __name__ == "__main__":
    unittest.main()
