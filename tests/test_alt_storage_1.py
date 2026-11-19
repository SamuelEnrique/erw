"""Ruling alternative 1 of /storage (session 7727, 17 November 2026, branch wip/alt-storage-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-storage-2026-11-17.md, line 1): give the daily
cycle a month's total discharge by grid beside the newest day and the 30-day spark? On this branch the panel gains a
column, each grid's newest calendar month whose every local day is held, summed (site/lib/storagemonth.ts monthTotal); a
month with a day missing is not summed. No figure that stands moves. Pinned with the page's own function on the local
storage_daily_cycle where it is on the machine (warehouse/output, or the folder ERW_TABLES_DIR names): its newest whole
month is September 2026: CAISO 1,335,586 MWh (44,520 a day), ERCOT 787,056 (26,235), SPP 31,766 (1,059); August 2026
1,462,303, 796,960 and 33,939. On the site the month is the newest the live set holds whole (October 2026).

    python -m unittest tests.test_alt_storage_1 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")


class TheRule(unittest.TestCase):
    def test_a_month_missing_a_day_is_not_summed(self):
        js = ("const S = await import('./lib/storagemonth.ts');"
              "const r = (d, v) => ({ entity: 'e', variable: 'mwh_discharged', ts_utc: d + 'T00:00:00Z', value: v });"
              "const feb = Array.from({ length: 28 }, (_, i) => r('2026-02-' + String(i + 1).padStart(2, '0'), 1));"
              "const mar = Array.from({ length: 30 }, (_, i) => r('2026-03-' + String(i + 1).padStart(2, '0'), 2));"
              "process.stdout.write(JSON.stringify(S.monthTotal([...feb, ...mar], 'e')));")
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(p.returncode, 0, p.stderr[-1500:])
        self.assertEqual(json.loads(p.stdout), {"month": "2026-02", "mwh": 28, "days": 28, "perDay": 1})


class TheColumnsOwnRead(unittest.TestCase):
    """Session 8401 (chain 503), browser row 363: every cell of the column read "no whole month". It was summed from the
    panel's read, the last 45 days of the table, in which no calendar month is whole from about the 15th of a month on
    (on 17 November the read starts on 3 October). The column reads the discharge from the first day of the month two
    before (site/lib/storagemonth.ts monthSince); the page drawn whole on made-up rows holds it
    (site/scripts/test-alt-storage-month.mjs)."""

    def test_the_page_drawn_on_17_november(self):
        p = subprocess.run(["node", "--import", "./scripts/battery-awards-page-register.mjs", "scripts/test-alt-storage-month.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600)
        self.assertEqual(p.returncode, 0, p.stdout[-2500:] + p.stderr[-1500:])
        self.assertIn("17 of 17 passed", p.stdout)

    def test_the_source(self):
        with open(os.path.join(SITE, "app", "storage", "page.tsx"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertIn('attempt(() => series("storage_daily_cycle", { variable: "mwh_discharged", since: monthSince() })),', s)
        self.assertIn('attempt(() => series("storage_daily_cycle", { since: daysAgo(45) })),', s, "the panel's own read stands")
        self.assertIn("monthTotal(month.data, b.entity)", s)
        self.assertNotIn("monthTotal(rows, b.entity)", s, "the column is not summed from the panel's 45 days")
        # the month's cell carries no check key, so it is held by the page itself where the row's other cells are held by Num
        self.assertIn("licenseHeldRow(T, b.entity) ?", s)


@unittest.skipUnless(os.path.exists(os.path.join(TABLES, "storage_daily_cycle.csv")), "storage_daily_cycle is not on this machine")
class OnTheLocalTable(unittest.TestCase):
    def test_the_newest_whole_months(self):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-storage-figures.mjs", TABLES], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(p.returncode, 0, p.stderr[-1500:])
        f = json.loads(p.stdout)
        self.assertEqual({e: (f[e]["month"], round(f[e]["mwh"]), round(f[e]["perDay"])) for e in ("caiso:ISO", "eia930:ERCO", "eia930:SWPP")},
                         {"caiso:ISO": ("2026-09", 1335586, 44520), "eia930:ERCO": ("2026-09", 787056, 26235), "eia930:SWPP": ("2026-09", 31766, 1059)})
        self.assertEqual([round(f["august"][e]["mwh"]) for e in ("caiso:ISO", "eia930:ERCO", "eia930:SWPP")], [1462303, 796960, 33939])


if __name__ == "__main__":
    unittest.main()
