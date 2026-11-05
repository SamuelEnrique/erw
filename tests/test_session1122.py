"""Session 1122 (chain 075): Ask reads the board. Held here: the tool board_rank, in both languages, ranks every public
hub's newest value of one of the board's measures (price_board_latest, price_board_spreads) as asked; on the rows
recorded from the live set (tests/fixtures/session1122/board_reads.json) the site's tool gives the five keys of
warehouse/chat/eval/questions_s1122.yaml, which expected_s1122.py computed from the same rows without the tools; the
spec the site reads carries the tool. No network, no model. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
CHAT = os.path.join(ROOT, "warehouse", "chat")


def chat_tools():
    if CHAT not in sys.path:
        sys.path.insert(0, CHAT)
    import tools  # noqa: E402
    return tools


class BoardRank(unittest.TestCase):
    def test_the_python_tool_ranks_querys_rows(self):
        t = chat_tools()
        saved_q, saved_p = t.query, t.provenance
        got = {}

        def fake_query(table, aggregation, **kw):
            got.update(table=table, aggregation=aggregation, **kw)
            return {"units": ["USD/MWh"], "result": [{"entity": "a:x", "value": 3.0, "at": "2026-10-22T00:00:00Z"}, {"entity": "b:y", "value": -7.0, "at": "2026-10-23T00:00:00Z"},
                                                     {"entity": "c:z", "value": 5.0, "at": "2026-10-23T00:00:00Z"}]}
        t.query, t.provenance = fake_query, (lambda name: {"source_report": "erw:price_board"})
        try:
            hi = t.board_rank("spark_spread_7")
            mv = t.board_rank("da_day_change_pct", order="largest_move")
            lo = t.board_rank("rt_latest_day_mean", order="lowest")
        finally:
            t.query, t.provenance = saved_q, saved_p
        self.assertEqual([r["entity"] for r in hi["ranked"]], ["c:z", "a:x", "b:y"])
        self.assertEqual(hi["table"], "price_board_spreads")
        self.assertEqual([r["entity"] for r in mv["ranked"]], ["b:y", "c:z", "a:x"])
        self.assertEqual([r["entity"] for r in lo["ranked"]], ["b:y", "a:x", "c:z"])
        self.assertEqual((got["aggregation"], got["group_by"]), ("latest", "entity"))
        with self.assertRaises(t.ToolError):
            t.board_rank("nonsense")

    def test_the_spec_carries_the_tool(self):
        with open(os.path.join(SITE, "lib", "chat", "spec.json"), encoding="utf-8") as f:
            spec = json.load(f)
        self.assertIn("board_rank", [x["name"] for x in spec["tools"]])
        self.assertIn("board_rank", chat_tools().FUNCTIONS)

    def test_the_five_questions(self):
        with open(os.path.join(CHAT, "eval", "expected_s1122.json"), encoding="utf-8") as f:
            keys = json.load(f)["questions"]
        self.assertEqual([k["id"] for k in keys], ["k01", "k02", "k03", "k04", "k05"])
        self.assertTrue(all(not k["entity"].startswith(("isone:", "nyiso:", "miso:")) for k in keys))
        with open(os.path.join(CHAT, "eval", "questions_s1122.yaml"), encoding="utf-8") as f:
            self.assertEqual(f.read().count("- id: k0"), 5)

    def test_the_site_tool_on_the_recorded_rows(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/test-ask-1122.mjs"], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("3 of 3 passed", r.stdout)


if __name__ == "__main__":
    unittest.main()
