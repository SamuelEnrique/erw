"""Audit of the prices pages, finding 6 (session 10218, docs/reviews/prices-model-audit-2026-11-26.md): a hub's page
(/prices/<hub>) says "last 30 days" and "Min, mean and max of every interval in the window", but its day-ahead read has
no end: it reaches the newest hour published, which once the next day's day-ahead is out is tomorrow's last hour. Drawn
at 18:00 UTC on 12 November 2026 on this machine's tables, ERCOT's Hub Average day-ahead held 24 hours after the render
time, so the day-ahead minimum, mean and maximum were over a window that ends up to 36 hours after the real time's.

1. Why (passes on main): the day-ahead read is asked with a start and no end (lib/data.ts `series`: ts_utc gte only).
2. The fix on this branch, words only (fails on main): drawn with the page's own function on stand-in rows (every price
   0, made for the test), the note under the table says the day-ahead runs to the newest hour published, up to 36 hours
   after the real time's, and that the From and To columns give each window. No figure moves."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class DayAheadRunsToTheNewestHourPublished(unittest.TestCase):
    def test_the_read_has_a_start_and_no_end(self):
        page = open(os.path.join(SITE, "app", "prices", "[entity]", "page.tsx"), encoding="utf-8").read()
        self.assertIn("attempt(() => series(m.da.table, { entity, variable: m.da.variable, since }))", page)
        data = open(os.path.join(SITE, "lib", "data.ts"), encoding="utf-8").read()
        self.assertIn("if (opts.since) q.ts_utc = `gte.${opts.since}`;", data)
        self.assertNotIn("lte.", data[data.index("export async function series"):data.index("export async function newest")])

    def test_the_page_says_the_two_windows(self):
        out = subprocess.run(["node", "--import", "./scripts/prices-read-register.mjs", "scripts/audit-prices-6-draw.mjs"],
                             cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        r = json.loads([x for x in out.stdout.splitlines() if x.startswith("{")][0])
        t = r["text"]
        self.assertIn("Day-ahead | iso_dam_hub_prices | 84 |", t)             # the stand-in day-ahead runs to 14 November 05:00 UTC
        self.assertIn("| 2026-11-14 05:00 UTC |", t)
        self.assertIn("The day-ahead runs to the newest hour published, which can be tomorrow's, so its window can end with tomorrow's last hour, "
                      "up to 36 hours after the real time's: the From and To columns give each.", t)
        self.assertEqual(r["emDashes"], 0)


if __name__ == "__main__":
    unittest.main()
