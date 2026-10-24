"""Session 1315 (chain 096): one list of Ask's stored runs (warehouse/chat/eval/runs.json), read by history.py,
replay.py and refusals.py.

Held here: every JSON file of the folder is a run, a run's grades, or named under left_out with why, and every file the
list names is there; the three scripts take their runs from it (replay's runs are the list's replayed ones, refusals'
limit of 8 the list's); and their three documents are what the list gives, unchanged by the move (each --check).
No network, no model. Nothing here sets the environment at import.
"""
import glob
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


def runs():
    with open(os.path.join(EVAL, "runs.json"), encoding="utf-8") as f:
        return json.load(f)


class TheList(unittest.TestCase):
    def test_every_file_is_named_once(self):
        doc = runs()
        named = [e["file"] for e in doc["runs"]] + [e["grades"] for e in doc["runs"] if e["grades"]] + list(doc["left_out"])
        self.assertEqual(len(named), len(set(named)))
        here = sorted(os.path.basename(p) for p in glob.glob(os.path.join(EVAL, "*.json")))
        self.assertEqual(sorted(named), here)
        for e in doc["runs"]:
            self.assertIn(e["history"]["kind"], ("answers", "regrade", "held", "right"), e["file"])
            self.assertIn(e["limit"], (8, 12, None), e["file"])

    def test_the_scripts_read_it(self):
        if EVAL not in sys.path:
            sys.path.insert(0, EVAL)
        import refusals as F  # noqa: E402
        import replay as R  # noqa: E402
        doc = runs()
        self.assertEqual([r[0] for r in R.RUNS], [e["file"] for e in doc["runs"] if e["replay"]])
        self.assertEqual(F.EIGHT, {"session 267", "session 302", "session 320"})
        for name in ("history.py", "replay.py", "refusals.py"):
            with open(os.path.join(EVAL, name), encoding="utf-8") as f:
                self.assertIn("runs.json", f.read(), name)

    def test_the_documents_are_unchanged(self):
        for name in ("history.py", "replay.py", "refusals.py"):
            r = subprocess.run([sys.executable, os.path.join(EVAL, name), "--check"], capture_output=True, text=True, timeout=300)
            self.assertEqual(r.returncode, 0, name + r.stdout[-1000:] + r.stderr[-1000:])


if __name__ == "__main__":
    unittest.main()
