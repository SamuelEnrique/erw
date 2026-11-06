"""Session 1631 (chain 167): the rows' CSV carries the week's and the month's cells too (audit row 39).

Held here: a power row's week and month (its peak hour and its hours above 100, 250 and 1,000 USD/MWh) are columns of the
rows' CSV between "latest" and "source", so a held row's are empty as its other figures, and the Stata reader destrings
them; a row without them leaves them empty. No network, no model. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


class TheWeekAndMonthColumns(unittest.TestCase):
    def test_the_columns(self):
        exe = shutil.which("node")
        if not exe or not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("node or the site's packages are not here")
        script = ("const b = await import('./lib/board.ts');"
                  "const pk = (v) => ({ v, utc: 'x', local: '18:00', day: '2026-10-10' });"
                  "const ext = { t: '2026-10-13', tz: 'America/Chicago', hi: pk(90), lo: pk(12), hours: 24,"
                  " w: { days: 7, first: '2026-10-07', hours: 168, peak: pk(120.5), above: { '100': 3, '250': 0, '1000': 0 } },"
                  " m: { days: 30, first: '2026-09-14', hours: 720, peak: pk(310), above: { '100': 9, '250': 2, '1000': 0 } } };"
                  "const ok = { id: 'a', group: 'power', label: 'A', at: '', code: '', unit: 'USD/MWh', freq: 'D', tags: {}, status: 'ok', last: { t: '2026-10-13', v: 35 }, ext };"
                  "const fuel = { id: 'b', group: 'gas', label: 'B', at: '', code: '', unit: 'USD/MMBtu', freq: 'D', tags: {}, status: 'ok', last: { t: '2026-10-13', v: 3 } };"
                  "const text = b.rowsCsv({ built: '2026-10-14T00:00:00Z', sources: [], heat_rate: 7, coal_heat_rate: 10.5, gas_back_days: 4, slack_days: 6, groups: [], rows: [ok, fuel], week: [], spikes: [], held: [] });"
                  "const body = text.split('\\n').filter((l) => l && !l.startsWith('#'));"
                  "process.stdout.write(JSON.stringify({ cols: b.ROWS_HEAD, ok: body[1].split(','), fuel: body[2].split(','), stata: b.rowsReader('do', 'https://example.org/board/rows') }));")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        got = json.loads(r.stdout)
        cols = got["cols"]
        names = ["week_peak", "week_hours_over_100", "week_hours_over_250", "week_hours_over_1000",
                 "month_peak", "month_hours_over_100", "month_hours_over_250", "month_hours_over_1000"]
        self.assertTrue(cols.index("latest") < cols.index("week_peak") and cols.index("month_hours_over_1000") < cols.index("source"))
        self.assertEqual([got["ok"][cols.index(c)] for c in names], ["120.5", "3", "0", "0", "310", "9", "2", "0"])
        self.assertEqual([got["fuel"][cols.index(c)] for c in names], [""] * 8)
        for c in names:
            self.assertIn(f"destring {c}, replace force", got["stata"])
        self.assertEqual(cols[-1], "hold")


if __name__ == "__main__":
    unittest.main()
