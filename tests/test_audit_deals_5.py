"""Audit of the energy deal tracker, finding 5 (session 10215, docs/reviews/deals-model-audit-2026-11-26.md): the AI view's
note, grouped by grid, says "A grid named in a story, else the grid that serves most of the state the story names". The
view's rows come from site/lib/deals2.ts toDeal, whose grid is the state's alone (decision 7: the tracker, the comparables
and the AI view read the state; only the table's own column reads a named grid first). On the rows of 12 November 2026 one
deal names a grid (PJM) and no state; it is AI-tagged and sits in "not stated", where the note puts it under PJM.

1. Through the page's library (site/lib/deals2.ts and site/lib/dealsai.ts, run by Node): a tagged deal with a named grid
   and no state is in the "not stated" group; one with a state is under its state's grid. Passes on main.
2. The fix on this branch, words only: the note says the grid is the state's, as decision 7 does. Fails on main."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
D2 = "file:///" + os.path.join(ROOT, "site", "lib", "deals2.ts").replace("\\", "/")
AI = "file:///" + os.path.join(ROOT, "site", "lib", "dealsai.ts").replace("\\", "/")
JS = """
const D = await import(%s);
const A = await import(%s);
const r = (id, extra) => D.toDeal({ event_id: id, event_date: "2026-10-01T00:00:00Z", status: null, mw: null, price: null, currency: null, parties: null,
  source: "s", source_url: "u", extra: { ai_power: "true", ...extra } });
const cells = A.aiCells([r("named", { grid: "PJM" }), r("state", { state: "TX" })], "grid");
console.log(JSON.stringify(cells.map((c) => [c.value, c.deals])));
""" % (json.dumps(D2), json.dumps(AI))


def flat(s):
    return " ".join(s.split())


class TheAiViewsGrid(unittest.TestCase):
    def test_a_named_grid_with_no_state_is_not_read(self):
        out = subprocess.run(["node", "--input-type=module"], input=JS, capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout.strip().splitlines()[-1]), [["ERCOT", 1], ["", 1]])

    def test_the_note_says_the_state_is_read(self):
        with open(os.path.join(ROOT, "site", "app", "deals", "ai", "view.tsx"), encoding="utf-8") as f:
            ai = flat(f.read())
        self.assertNotIn("A grid named in a story, else the grid that serves most of the state", ai)
        self.assertIn("The grid that serves most of the state the story names (a grid a story names without a state is not read here, as in "
                      "the tracker and the comparables: decision 7); ", ai)


if __name__ == "__main__":
    unittest.main()
