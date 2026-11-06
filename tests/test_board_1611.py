"""Session 1611 (chain 165): the day's extremes.

Held here, on the real rows of ERCOT's Houston load zone (tests/fixtures/board_1601/): a power row carries its latest
complete local day's highest and lowest hour, each with the hour it began in the grid's local time, the real-time hour
the mean of its four 15-minute prices; the power group draws them in a column of their own; a held grid's row loses
them with its other figures; the check of the page expects them. No network, no model. Nothing here sets the
environment at import.
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


class TheExtremes(unittest.TestCase):
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

    def expected(self, market):
        t = pd.read_csv(os.path.join(FIX, "ercot_zone_prices_history.csv"), comment="#")
        t = t[(t["entity"] == "ercot:LZ_HOUSTON") & (t["market"] == market)].copy()
        t["hour"] = pd.to_datetime(t["ts_utc"], utc=True).dt.floor("h")
        h = t.groupby("hour")["value"].agg(["mean", "size"])
        h = h[h["size"] == (4 if market.endswith("rtm") else 1)]["mean"]
        local = h.index.tz_convert("America/Chicago")
        day = h[[d.date().isoformat() == "2026-10-13" for d in local]]
        return day

    def test_real_time_high_and_low_with_their_hours(self):
        e = self.rows["ercot-lz-houston-rt"]["ext"]
        day = self.expected("ercot_rtm")
        hi, lo = day.idxmax(), day.idxmin()
        self.assertEqual((e["t"], e["tz"], e["hours"]), ("2026-10-13", "America/Chicago", 24))
        self.assertEqual((e["hi"]["v"], e["hi"]["utc"], e["hi"]["local"]), (round(float(day[hi]), 4), hi.strftime("%Y-%m-%dT%H:%M:%SZ"), hi.tz_convert("America/Chicago").strftime("%H:%M")))
        self.assertEqual((e["lo"]["v"], e["lo"]["local"]), (round(float(day[lo]), 4), lo.tz_convert("America/Chicago").strftime("%H:%M")))

    def test_day_ahead_too_and_none_without_a_day(self):
        e = self.rows["ercot-lz-houston-da"]["ext"]
        day = self.expected("ercot_dam")
        self.assertEqual(e["hi"]["v"], round(float(day.max()), 4))
        self.assertNotIn("ext", self.rows["ercot-lz-aen-rt"])         # no real-time hours held: no extremes
        self.assertNotIn("ext", self.rows["ercot-lz-houston-rt-battery"])   # the column is the power group's only

    def test_the_group_and_the_check(self):
        power = next(g for g in self.bp.GROUPS if g["id"] == "power")
        self.assertTrue(power.get("extremes"))
        self.assertEqual([g["id"] for g in self.bp.GROUPS if g.get("extremes")], ["power"])
        with open(os.path.join(SITE, "scripts", "check-board.mjs"), encoding="utf-8") as f:
            self.assertIn("want(`${r.id}|ext|hi`, b.fmt(r.ext.hi.v, r.unit))", f.read())
        with open(os.path.join(SITE, "components", "board", "BoardView.tsx"), encoding="utf-8") as f:
            v = f.read()
        self.assertIn("<ExtCell row={row} built={file.built} />", v)
        self.assertIn("data-n={`${row.id}|ext|hi`}", v)

    def test_a_held_row_loses_them(self):
        exe = shutil.which("node")
        if not exe or not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("node or the site's packages are not here")
        script = ("const b = await import('./lib/board.ts');"
                  "const ext = { t: '2026-10-13', tz: 'America/New_York', hi: { v: 90, utc: '2026-10-13T22:00:00Z', local: '18:00' }, lo: { v: 20, utc: '2026-10-13T08:00:00Z', local: '04:00' }, hours: 24 };"
                  "const file = { built: '2026-10-14T00:00:00Z', rows: [{ id: 'nyiso-n-y-c-rt', group: 'power', status: 'ok', tags: { grid: 'NYISO' }, last: { t: '2026-10-13', v: 50 }, ext }], week: [], spikes: [] };"
                  "const held = b.holdRows(file, ['NYISO']).rows[0];"
                  "process.stdout.write(JSON.stringify({ status: held.status, ext: held.ext ?? null, words: b.extremeWords({ ext, unit: 'USD/MWh' }) }));")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        got = json.loads(r.stdout)
        self.assertEqual((got["status"], got["ext"]), ("license", None))
        self.assertIn("the highest began at 18:00, the lowest at 04:00 (local time, America/New_York)", got["words"])


if __name__ == "__main__":
    unittest.main()
