"""Session 1135 (chain 076): CARB's allowance auctions, a quarterly row.

Held here, on the table's real rows (tests/fixtures/session1135/, copied from this machine's carb_auction_allowance_prices):
the builder draws the current and the advance auction's settlement prices as two quarterly rows of the carbon group, the
current one under the id of the grey row it replaces (so page_keep.py keeps no stale twin); a quarterly row has a move
over a year only, and a one-year range once four values are held; the page writes a quarter's date as its month, says
"quarterly", draws no daily, weekly or monthly move for it, marks it stale past 135 days, and the workbench charts it
on the months' axis. No network, no model. Nothing here sets the environment at import.
"""
import csv
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
SITE = os.path.join(ROOT, "site")
FIX = os.path.join(ROOT, "tests", "fixtures", "session1135")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


class TheQuarterlyRows(unittest.TestCase):
    def test_two_rows_from_the_real_rows(self):
        bp = builder()
        saved, absent = bp.ip.OUT_DIR, list(bp.ABSENT)
        bp.ip.OUT_DIR = FIX
        try:
            b = bp.Board()
            s, _ = bp.table_daily("carb_auction_allowance_prices")
            for key, entity in (("cca|auction", "carb:current_auction"), ("cca|advance", "carb:advance_auction")):
                b.add("carbon", key, "California carbon allowance", "USD/t CO2e", "Q", s.get((entity, "settlement_price"), {}))
        finally:
            bp.ip.OUT_DIR, bp.ABSENT[:] = saved, absent
        rows = {r["id"]: r for r in b.rows}
        self.assertEqual(sorted(rows), ["cca-advance", "cca-auction"])
        with open(os.path.join(FIX, "carb_auction_allowance_prices.csv"), encoding="utf-8") as f:
            raw = [r for r in csv.DictReader(line for line in f if not line.startswith("#"))]
        newest = max(r["ts_utc"] for r in raw if r["entity"] == "carb:current_auction")
        want = next(float(r["value"]) for r in raw if r["entity"] == "carb:current_auction" and r["ts_utc"] == newest)
        cur = rows["cca-auction"]
        self.assertEqual((cur["status"], cur["freq"], cur["last"]["t"], cur["last"]["v"]), ("ok", "Q", newest[:10], want))
        self.assertIsNone(cur["moves"]["d"]); self.assertIsNone(cur["moves"]["w"]); self.assertIsNone(cur["moves"]["m"])
        self.assertIsNotNone(cur["moves"]["y"])
        self.assertIsNotNone(cur["range"])
        self.assertNotIn("avg7", cur)

    def test_the_builder_draws_them_in_the_carbon_group(self):
        with open(os.path.join(DERIVED, "board_page.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('("cca|auction", "carb:current_auction", "current auction, settlement price, quarterly")', src)
        self.assertIn('RANGE_MIN = {"D": 180, "W": 26, "M": 9, "Q": 4}', src)

    def test_the_page_and_the_workbench(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        script = ("const b = await import('./lib/board.ts');"
                  "const r = { id: 'x', group: 'carbon', freq: 'Q', last: { t: '2026-08-01', v: 41.76 } };"
                  "process.stdout.write(JSON.stringify({ words: b.FREQ_WORDS.Q, date: b.dateWords('2026-08-01', 'Q'), short: b.shortDate('2026-08-01', 'Q'),"
                  " moves: ['d','w','m','y'].map((k) => b.noMove('Q', k)), chart: b.chartFreq('Q'), fresh: b.closeAge(r, '2026-10-23T00:00:00Z').stale,"
                  " old: b.closeAge(r, '2026-12-15T00:00:00Z').stale, limit: b.STALE_DAYS.Q }));")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        import json
        got = json.loads(r.stdout)
        self.assertEqual(got, {"words": "quarterly", "date": "Aug 2026", "short": "Aug 2026", "moves": [True, True, True, False], "chart": "M",
                               "fresh": False, "old": True, "limit": 135})


if __name__ == "__main__":
    unittest.main()
