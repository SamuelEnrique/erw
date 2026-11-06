"""Session 1612 (chain 165): the week and the month in one row.

Held here, on the real rows of ERCOT's Houston load zone (tests/fixtures/board_1601/, 10 to 13 October 2026): a power
row's extremes carry the last 7 and 30 days' complete local days, their peak hour with its day and local time, and the
count of hours above 100, 250 and 1,000 USD/MWh; the fixture holds four complete days, so both windows count those four
and say so; the page draws them under the day's high and low and the check expects each number. No network, no model.
Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
SITE = os.path.join(ROOT, "site")
FIX = os.path.join(ROOT, "tests", "fixtures", "board_1601")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


class TheWindows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bp = cls.bp = builder()
        saved, absent, intervals = bp.ip.OUT_DIR, list(bp.ABSENT), dict(bp.INTERVALS)
        bp.ip.OUT_DIR = FIX
        try:
            b = bp.Board()
            store = bp.hourly_store(lambda s: None, tables=["ercot_zone_prices_history"])
            bp.build_power(b, store, bp.pb.nerc_holidays(range(2025, 2028)), lambda s: None)
        finally:
            bp.ip.OUT_DIR, bp.ABSENT[:] = saved, absent
            bp.INTERVALS.clear(); bp.INTERVALS.update(intervals)
        cls.rows = {r["id"]: r for r in b.rows}

    def hours(self):
        t = pd.read_csv(os.path.join(FIX, "ercot_zone_prices_history.csv"), comment="#")
        t = t[(t["entity"] == "ercot:LZ_HOUSTON") & (t["market"] == "ercot_rtm")].copy()
        t["hour"] = pd.to_datetime(t["ts_utc"], utc=True).dt.floor("h")
        h = t.groupby("hour")["value"].agg(["mean", "size"])
        h = h[h["size"] == 4]["mean"]
        local = pd.Series([d.date().isoformat() for d in h.index.tz_convert("America/Chicago")], index=h.index)
        full = [d for d, n in local.value_counts().items() if n == 24]
        return h[local.isin(full)], sorted(full)

    def test_the_week_and_the_month_of_the_real_hours(self):
        h, days = self.hours()
        e = self.rows["ercot-lz-houston-rt"]["ext"]
        self.assertEqual(days, ["2026-10-10", "2026-10-11", "2026-10-12", "2026-10-13"])
        for k in ("w", "m"):
            x = e[k]
            self.assertEqual((x["days"], x["first"], x["hours"]), (4, "2026-10-10", 96), k)
            self.assertEqual(x["peak"]["v"], round(float(h.max()), 4))
            self.assertEqual(x["peak"]["day"], h.idxmax().tz_convert("America/Chicago").date().isoformat())
            self.assertEqual(x["above"], {str(n): int((h > n).sum()) for n in (100, 250, 1000)})

    def test_the_page_and_the_check(self):
        with open(os.path.join(SITE, "components", "board", "BoardView.tsx"), encoding="utf-8") as f:
            v = f.read()
        self.assertIn("data-n={`${row.id}|ext|${k}|peak`}", v)
        self.assertIn("data-n={`${row.id}|ext|${k}|${n}`}", v)
        with open(os.path.join(SITE, "scripts", "check-board.mjs"), encoding="utf-8") as f:
            self.assertIn("want(`${r.id}|ext|${k}|${n}`, String(x.above[n]))", f.read())
        self.assertEqual(self.bp.THRESHOLDS, (100, 250, 1000))

    def test_the_hover_words(self):
        exe = shutil.which("node")
        if not exe or not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("node or the site's packages are not here")
        e = self.rows["ercot-lz-houston-rt"]["ext"]
        script = ("const b = await import('./lib/board.ts');"
                  f"const ext = {json.dumps(e)};"
                  "process.stdout.write(JSON.stringify([b.windowWords({ ext, unit: 'USD/MWh' }, 'w'), b.windowWords({ ext: null, unit: 'USD/MWh' }, 'w')]));")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        words, none = json.loads(r.stdout)
        self.assertTrue(words.startswith("4 complete days, 10 Oct 2026 to 13 Oct 2026, 96 hours: the peak hour began at "), words)
        self.assertIn("hours above 100 USD/MWh: ", words)
        self.assertIn("1,000 USD/MWh: ", words)
        self.assertIsNone(none)


if __name__ == "__main__":
    unittest.main()
