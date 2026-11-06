"""Session 1632 (chain 167): a held row prints its status words and no digit (audit row 40).

Held here: a held grid's row loses its interval's words (`basis`, whose words carry digits: "24; 23 or 25", "4
15-minute") and the fleet heat rate beside a spark spread (`heat_ref`) with its figures, so its hover and its line of
the rows' CSV carry no digit after its status; the file's checks catch a held row that keeps them. No network, no
model. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


class TheHeldRow(unittest.TestCase):
    def test_no_digit_after_the_hold(self):
        exe = shutil.which("node")
        if not exe or not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("node or the site's packages are not here")
        script = ("const b = await import('./lib/board.ts');"
                  "const row = { id: 'nyiso-n-y-c-spark', group: 'spark', label: 'NYISO New York City', at: 'spark spread, indicative', code: 'N.Y.C.', unit: 'USD/MWh', freq: 'D', tags: { grid: 'NYISO' },"
                  " status: 'ok', source: 0, last: { t: '2026-10-13', v: 20 }, basis: 'A daily mean of the complete local operating day hours (24; 23 or 25 on the daylight saving days), each hour the mean of the hour 4 15-minute prices.',"
                  " heat_ref: { t: '2025-01-01', v: 7.5, table: 'eia_heat_rates_annual' } };"
                  "const file = { built: '2026-10-14T00:00:00Z', sources: ['x'], heat_rate: 7, coal_heat_rate: 10.5, gas_back_days: 4, slack_days: 6, groups: [{ id: 'spark', title: 'S', filters: [] }], rows: [row], week: [], spikes: [] };"
                  "const held = b.holdRows(file, ['NYISO']);"
                  "const line = b.rowsCsv(held).split('\\n').filter((l) => l && !l.startsWith('#'))[1];"
                  "const kept = { ...held, rows: [{ ...held.rows[0], basis: row.basis }] };"
                  "process.stdout.write(JSON.stringify({ r: held.rows[0], line, cols: b.ROWS_HEAD, title: b.nameTitle(held.rows[0], held.sources) ?? null,"
                  " caught: b.boardFileChecks(kept).filter((c) => !c.ok).map((c) => c.what) }));")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        got = json.loads(r.stdout)
        self.assertEqual(got["r"]["status"], "license")
        self.assertNotIn("basis", got["r"])
        self.assertNotIn("heat_ref", got["r"])
        self.assertNotIn("Interval:", got["title"] or "")
        cells = got["line"].split(",")
        self.assertFalse(any(ch.isdigit() for ch in ",".join(cells[got["cols"].index("latest"):got["cols"].index("hold")])))
        self.assertTrue(any(w.startswith("every row with no value") for w in got["caught"]), got["caught"])


if __name__ == "__main__":
    unittest.main()
