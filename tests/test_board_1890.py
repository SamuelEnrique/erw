"""Session 1890: the trader path walked 13 November 2026 (session 1885), fault 4, step 13.

The fault: "the top block's tile for a stale series prints its moves. The tile reads 'ERCOT Hub average day-ahead
40.64 USD/MWh, 6 Nov 2026 (stale), Day +13.65, Week +0.72', while the same series' row in the table below writes
'stale' in each move cell" (session 1608's rule: MoveCell in components/board/BoardView.tsx, shownMove in lib/board.ts).

The fix: a stale tile blanks its moves the way the row does: the word "stale", its title "Not shown: the series is
stale (...)" with closeAge's words, no up or down color and no arrow (dir 0), and no "top|<id>|<k>" number mark. A fresh
tile reads its move through shownMove, the row's function. scripts/check-board.mjs compares the tile's moves with
shownMove too, so a stale tile with a number in it is a failure there.

No network, no model, no browser. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def top_twelve():
    s = src("site", "components", "board", "BoardView.tsx")
    return s[s.index("function TopTwelve("):s.index("function Headline(")]


def node_ok():
    return shutil.which("node") and os.path.isdir(os.path.join(SITE, "node_modules", "typescript"))


class TheStaleTileBlanksItsMoves(unittest.TestCase):
    def test_a_stale_tile_writes_stale_with_the_age_as_its_title(self):
        t = top_twelve()
        self.assertIn("const age = closeAge(r, file.built);", t)
        self.assertIn("if (r.moves?.[k] && age?.stale) {", t)
        branch = t[t.index("if (r.moves?.[k] && age?.stale) {"):]
        branch = branch[:branch.index("}\n") + 1]
        self.assertIn("dir: 0", branch)
        self.assertIn("title: `Not shown: the series is stale (${age.words}).`", branch)
        self.assertIn(">stale</span>", branch)
        self.assertNotIn("data-n=", branch)
        self.assertNotIn("signed(", branch)

    def test_the_row_writes_the_same_title(self):
        s = src("site", "components", "board", "BoardView.tsx")
        cell = s[s.index("function MoveCell("):]
        cell = cell[:cell.index("const m = shownMove(row, k, built);")]
        self.assertIn("title={`Not shown: the series is stale (${closeAge(row, built)!.words}).`}>stale</span>", cell)

    def test_a_fresh_tile_reads_its_move_through_shown_move(self):
        t = top_twelve()
        self.assertIn("const m = shownMove(r, k, file.built);", t)
        self.assertNotIn("const m = r.moves?.[k];", t)
        # the stale branch comes before any number is written
        self.assertLess(t.index("age?.stale"), t.index("data-n={`top|${r.id}|${k}`}"))

    def test_check_board_compares_the_tiles_moves_with_shown_move(self):
        c = src("site", "scripts", "check-board.mjs")
        line = c[c.index('for (const k of ["d", "w"]) {'):]
        line = line[:line.index("\n")]
        self.assertIn("const mv = b.shownMove(r, k, file.built);", line)
        self.assertIn("top|${r.id}|${k}", line)
        self.assertNotIn("const mv = r.moves[k];", c)


@unittest.skipUnless(node_ok(), "node or the site's packages are not here")
class TheLibraryAgrees(unittest.TestCase):
    def test_a_stale_series_has_no_shown_move_and_a_fresh_one_has_its_move(self):
        script = ("const b = await import('./lib/board.ts');"
                  "const mv = { t: '2026-11-05', v: 26.99, ch: 13.65, pct: 50.6 };"
                  "const row = (id, t) => ({ id, group: 'power', label: id, at: 'day-ahead', code: id, unit: 'USD/MWh', freq: 'D', tags: {},"
                  " status: 'ok', source: 0, last: { t, v: 40.64 }, moves: { d: mv, w: { ...mv, ch: 0.72 } } });"
                  "const built = '2026-11-13T00:30:00Z';"
                  "const old = row('old', '2026-11-06'), fresh = row('fresh', '2026-11-13');"
                  "process.stdout.write(JSON.stringify({ stale: b.closeAge(old, built).stale, words: b.closeAge(old, built).words,"
                  " oldD: b.shownMove(old, 'd', built), oldW: b.shownMove(old, 'w', built),"
                  " freshStale: b.closeAge(fresh, built).stale, freshD: b.shownMove(fresh, 'd', built) }));")
        r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        got = json.loads(r.stdout)
        self.assertTrue(got["stale"])
        self.assertIn("Stale", got["words"])
        self.assertIsNone(got["oldD"])
        self.assertIsNone(got["oldW"])
        self.assertFalse(got["freshStale"])
        self.assertEqual(got["freshD"]["ch"], 13.65)


if __name__ == "__main__":
    unittest.main()
