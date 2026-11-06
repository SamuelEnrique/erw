"""Session 1614 (chain 165): the downloads of the board as shown.

Held here: the rows' CSV carries the board as the page shows it (the year to date, the twelve-month mean and the
latest less it, the day's high and low hour and their local times), the row's interval and its status words, with
"hold" still last; a held row carries none of the figures and its status words; the Python and Stata readers read that
CSV at the address they are given, the Stata one in the owner's form (no line continuation, one empty line between the
commands outside a loop and none inside, every figure column destrung with force); the footer links both. No network,
no model. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def node(script):
    exe = shutil.which("node")
    if not exe or not os.path.isdir(os.path.join(SITE, "node_modules")):
        raise unittest.SkipTest("node or the site's packages are not here")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                       capture_output=True, text=True, timeout=300, encoding="utf-8")
    if r.returncode != 0 and "Unknown file extension" in r.stderr:
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


class TheDownloads(unittest.TestCase):
    def test_the_csv_as_shown(self):
        got = node("const b = await import('./lib/board.ts');"
                   "const ok = { id: 'ercot-lz-houston-rt', group: 'power', label: 'ERCOT Houston load zone', at: 'real time', code: 'LZ_HOUSTON', unit: 'USD/MWh', freq: 'D', tags: {}, status: 'ok', source: 0,"
                   " basis: 'A daily mean.', last: { t: '2026-10-13', v: 35.78 }, moves: { d: { t: '2026-10-12', v: 30, ch: 5.78, pct: 1 }, ytd: { t: '2025-12-31', v: 30, ch: 5.78, pct: 1 } },"
                   " avg365: { v: 40, n: 365, ch: -4.22 }, ext: { t: '2026-10-13', tz: 'America/Chicago', hi: { v: 90, utc: 'x', local: '18:00' }, lo: { v: 12, utc: 'y', local: '04:00' }, hours: 24 } };"
                   "const grey = { id: 'rin-price', group: 'carbon', label: 'RINs', at: 'daily', code: '', unit: 'USD/RIN', freq: '', tags: {}, status: 'licensed', note: 'x' };"
                   "const text = b.rowsCsv({ built: '2026-10-14T00:00:00Z', sources: ['ERCOT'], heat_rate: 7, coal_heat_rate: 10.5, gas_back_days: 4, slack_days: 6, groups: [], rows: [ok, grey], week: [], spikes: [], held: [] });"
                   "const body = text.split('\\n').filter((l) => l && !l.startsWith('#'));"
                   "process.stdout.write(JSON.stringify({ head: body[0].split(','), ok: body[1], grey: body[2], cols: b.ROWS_HEAD }));")
        cols = got["cols"]
        self.assertEqual(cols[-1], "hold")
        for c in ("ytd_move", "avg_12m", "vs_12m", "day_high", "day_high_local", "day_low", "day_low_local", "basis", "status_words"):
            self.assertIn(c, cols)
        self.assertLess(cols.index("day_low_local"), cols.index("source"))
        ok = got["ok"].split(",")
        self.assertEqual([ok[cols.index(c)] for c in ("ytd_move", "avg_12m", "vs_12m", "day_high", "day_high_local", "day_low", "day_low_local", "basis", "status_words")],
                         ["5.78", "40", "-4.22", "90", "18:00", "12", "04:00", "A daily mean.", ""])
        grey = got["grey"].split(",")
        self.assertEqual(grey[cols.index("status_words")], "licensed source needed")
        self.assertTrue(all(grey[i] == "" for i in range(cols.index("latest"), cols.index("source"))))
        self.assertFalse(any(ch.isdigit() for ch in ",".join(grey[cols.index("latest"):])))

    def test_the_readers(self):
        got = node("const b = await import('./lib/board.ts');"
                   "process.stdout.write(JSON.stringify({ py: b.rowsReader('py', 'https://example.org/board/rows'), do: b.rowsReader('do', 'https://example.org/board/rows'), cols: b.ROWS_HEAD }));")
        self.assertIn('URL = "https://example.org/board/rows"', got["py"])
        self.assertIn("status_words", got["py"])
        do = got["do"].split("\n")
        self.assertIn('copy "https://example.org/board/rows" `raw\'', do)
        self.assertFalse([l for l in do if l.rstrip().endswith("///")])
        inside = do[do.index("while r(eof) == 0 {") + 1:do.index("}")]
        self.assertTrue(inside and all(l.strip() for l in inside))                       # no empty line inside the loop
        outside = [i for i, l in enumerate(do) if l and not l.startswith("*") and not l.startswith("    ") and l not in ("}",)]
        for i in outside[:-1]:
            if do[i].startswith("while"):
                continue
            self.assertEqual(do[i + 1], "", do[i])                                     # one empty line after each command
        figures = [c for c in got["cols"][got["cols"].index("latest"):got["cols"].index("source")] if not c.endswith("_local")]
        for c in figures:
            self.assertIn(f"destring {c}, replace force", do)

    def test_the_routes_and_the_footer(self):
        for kind, ext in (("python", "py"), ("stata", "do")):
            with open(os.path.join(SITE, "app", "board", "rows", kind, "route.ts"), encoding="utf-8") as f:
                src = f.read()
            self.assertIn(f'rowsReader("{ext}", url)', src)
            self.assertIn('new URL("/board/rows", req.url)', src)
        with open(os.path.join(SITE, "app", "board", "page.tsx"), encoding="utf-8") as f:
            page = f.read()
        self.assertIn('<SiteLink href="/board/rows/python">Python</SiteLink>', page)
        self.assertIn('<SiteLink href="/board/rows/stata">Stata</SiteLink>', page)


if __name__ == "__main__":
    unittest.main()
