"""Session 1613 (chain 165): the comparison, against a year before and the twelve-month mean.

Held here: a row carries its trailing twelve-month mean (the values held in the 365 days ending on its latest) and the
latest less it, when as many values are held as the one-year range needs, and none otherwise; the comparison with the
same date a year before is the year's move, its date on hover; the page draws a "12-month avg" column, blank on a stale
row, a held grid's row loses it, and the check expects both numbers. The series are made in memory: they test the
rule, they are no one's prices. No network, no model. Nothing here sets the environment at import.
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
SITE = os.path.join(ROOT, "site")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


class TheTwelveMonthMean(unittest.TestCase):
    def test_the_mean_of_the_365_days_and_the_latest_less_it(self):
        bp = builder()
        end = dt.date(2026, 10, 30)
        s = {end - dt.timedelta(days=i): float(i % 10) for i in range(400)}
        a = bp.stats(s, "D")["avg365"]
        window = [s[end - dt.timedelta(days=i)] for i in range(365)]
        self.assertEqual((a["n"], a["v"]), (365, round(sum(window) / 365, 4)))
        self.assertEqual(a["ch"], round(s[end] - sum(window) / 365, 4))
        y = bp.stats(s, "D")["moves"]["y"]
        self.assertEqual(y["t"], "2025-10-30")             # the same date a year before: the year's move

    def test_none_when_the_year_is_thin(self):
        bp = builder()
        end = dt.date(2026, 10, 30)
        self.assertNotIn("avg365", bp.stats({end - dt.timedelta(days=i): 1.0 for i in range(100)}, "D"))
        m = {dt.date(2026 - (i // 12), 12 - (i % 12), 1): 2.0 for i in range(24)}
        self.assertEqual(bp.stats(m, "M")["avg365"]["n"], 12)

    def test_the_page_and_the_check(self):
        with open(os.path.join(SITE, "components", "board", "BoardView.tsx"), encoding="utf-8") as f:
            v = f.read()
        self.assertIn(">12-month avg</th>", v)
        self.assertIn("<Avg365Cell row={row} built={file.built} />", v)
        self.assertIn("data-n={`${row.id}|vs365`}", v)
        with open(os.path.join(SITE, "scripts", "check-board.mjs"), encoding="utf-8") as f:
            self.assertIn("want(`${r.id}|vs365`, b.signed(r.avg365.ch, r.unit))", f.read())

    def test_a_held_row_loses_it(self):
        exe = shutil.which("node")
        if not exe or not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("node or the site's packages are not here")
        script = ("const b = await import('./lib/board.ts');"
                  "const file = { built: '2026-10-14T00:00:00Z', rows: [{ id: 'isone-h-internal-hub-da', group: 'power', status: 'ok', tags: { grid: 'ISO-NE' }, last: { t: '2026-10-13', v: 50 }, avg365: { v: 40, n: 365, ch: 10 } }], week: [], spikes: [] };"
                  "process.stdout.write(JSON.stringify(b.holdRows(file, ['ISO-NE']).rows[0].avg365 ?? null));")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIsNone(json.loads(r.stdout))


if __name__ == "__main__":
    unittest.main()
