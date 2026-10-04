"""Session 104: the price board, version 3 (/board/v3, in review).

The board's arithmetic (site/lib/board3.ts) on days made for the test and on the warehouse's own table; MISO shown as
paused and PJM as licensed, in words; the page in review; the older board as it was. No network.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


STDIN = "JSON.parse(await new Promise((done) => { let s = ''; process.stdin.on('data', (d) => { s += d; }); process.stdin.on('end', () => done(s)); }))"


def node(js, stdin=None):
    """Run a few lines of JavaScript in the site's folder; `stdin` is given to them as text (a long table does not fit
    on a Windows command line)."""
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120, input=stdin)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def rows(entity, variable, days, unit="USD/MWh"):
    return [{"entity": entity, "variable": variable, "ts_utc": f"{d}T00:00:00Z", "value": v, "unit": unit} for d, v in days]


class TheArithmetic(unittest.TestCase):
    def line(self, days):
        return node("const b = await import('./lib/board3.ts');"
                    f"console.log(JSON.stringify(b.lineOf('e', 'Grid', 'Hub', {json.dumps(rows('e', 'da_daily_mean', days))})));")

    def test_last_day_and_week(self):
        days = [(f"2026-09-{d:02d}", 20.0 + d) for d in range(20, 31)] + [("2026-10-01", 40.0), ("2026-10-02", 37.5)]
        l = self.line(days)
        self.assertEqual(l["last"], {"t": "2026-10-02", "v": 37.5})
        self.assertEqual((l["day"]["from"]["t"], l["day"]["change"]), ("2026-10-01", -2.5))
        self.assertAlmostEqual(l["day"]["pct"], -6.25)
        self.assertEqual((l["week"]["from"]["t"], l["week"]["from"]["v"]), ("2026-09-25", 45.0))   # seven days before the last
        self.assertEqual(l["week"]["change"], -7.5)
        self.assertEqual(len(l["history"]), 13)
        self.assertEqual(l["history"][0]["t"], "2026-09-20")

    def test_a_move_whose_earlier_day_is_not_held_is_null(self):
        l = self.line([("2026-10-02", 30.0)])
        self.assertIsNone(l["day"])
        self.assertIsNone(l["week"])
        l = self.line([("2026-09-01", 10.0), ("2026-10-01", 30.0), ("2026-10-02", 33.0)])      # the only older day is a month back
        self.assertEqual(l["day"]["change"], 3.0)
        self.assertIsNone(l["week"], "a day a month earlier is not a week's move")
        l = self.line([])
        self.assertEqual((l["last"], l["history"]), (None, []))

    def test_a_fuel_skips_the_weekend(self):
        # EIA publishes no Saturday or Sunday: the day's move is against Friday, the week's against the Monday before
        days = [("2026-09-21", 3.00), ("2026-09-22", 3.05), ("2026-09-23", 3.10), ("2026-09-24", 3.08), ("2026-09-25", 3.12), ("2026-09-28", 3.20), ("2026-09-29", 3.26)]
        l = self.line(days)
        self.assertEqual(l["day"]["from"]["t"], "2026-09-28")
        self.assertEqual(l["week"]["from"]["t"], "2026-09-22")
        self.assertAlmostEqual(l["week"]["change"], 0.21)

    def test_thirty_days_of_history_at_most(self):
        days = [(str(d.date()), 1.0) for d in pd.date_range("2026-08-01", periods=50)]
        self.assertEqual(len(self.line(days)["history"]), 30)

    def test_the_summary_sentence(self):
        power = rows("ercot:HB_HUBAVG", "da_daily_mean", [("2026-10-03", 30.0), ("2026-10-04", 28.5)]) + rows("caiso:TH_SP15_GEN-APND", "da_daily_mean", [("2026-10-04", 41.25)]) \
            + rows("nyiso:N.Y.C.", "da_daily_mean", [("2026-10-03", 99.0)])
        fuel = rows("eia:henry_hub", "spot_price", [("2026-09-29", 3.26)], "USD/MMBtu") + rows("eia:wti_cushing", "spot_price", [("2026-09-29", 70.1)], "USD/bbl")
        out = node("const b = await import('./lib/board3.ts');"
                   f"const p = b.powerLines({json.dumps(power)}, 'da'); const f = b.fuelLines({json.dumps(fuel)});"
                   "console.log(JSON.stringify({ s: b.summary(p, f, 'da'), none: b.summary(b.powerLines([], 'da'), f, 'da'), grids: p.map((x) => x.label), withheld: b.WITHHELD.map(b.withheldWords) }));")
        # no day is held by all three grids here: 3 October and 4 October are each held by two, and the newer is taken
        self.assertEqual(out["s"], "Day-ahead power for 4 October 2026 averaged from USD 28.50 per MWh in ERCOT to USD 41.25 in CAISO, across the 2 grids with that day held; "
                                   "Henry Hub gas was USD 3.26 per MMBtu on 29 September 2026 and WTI crude USD 70.10 a barrel.")
        ahead = rows("ercot:HB_HUBAVG", "da_daily_mean", [("2026-10-03", 30.0), ("2026-10-04", 28.5)]) + rows("caiso:TH_SP15_GEN-APND", "da_daily_mean", [("2026-10-03", 44.0), ("2026-10-04", 41.25)])             + rows("nyiso:N.Y.C.", "da_daily_mean", [("2026-10-03", 99.0), ("2026-10-04", 60.0), ("2026-10-05", 61.0)])
        s2 = node("const b = await import('./lib/board3.ts');"
                  f"const p = b.powerLines({json.dumps(ahead)}, 'da'); console.log(JSON.stringify({{ day: b.commonDay(p), s: b.summary(p, [], 'da') }}));")
        self.assertEqual(s2["day"], "2026-10-04")           # New York holds a day more; the grids are compared on the day all three hold
        self.assertEqual(s2["s"], "Day-ahead power for 4 October 2026 averaged from USD 28.50 per MWh in ERCOT to USD 60.00 in NYISO, across the 3 grids with that day held.")
        self.assertIsNone(out["none"])                       # no power price read: no sentence, the page says so
        self.assertEqual(out["grids"], ["ERCOT", "CAISO", "NYISO", "SPP", "ISO-NE"])     # MISO and PJM are not among the priced
        self.assertTrue(out["withheld"][0].startswith("Paused since 4 October 2026: MISO's terms forbid automated access"))
        self.assertTrue(out["withheld"][1].startswith("Licensed: PJM's prices are published under a license"))


class OnTheWarehousesTable(unittest.TestCase):
    @unittest.skipUnless(os.path.exists(os.path.join(OUT, "price_board_latest.csv")), "price_board_latest is not on this machine")
    def test_the_board_gives_the_tables_own_figures(self):
        path = os.path.join(OUT, "price_board_latest.csv")
        t = pd.read_csv(path, skiprows=ip.header_rows(path))
        d = t[t["variable"] == "da_daily_mean"]
        got = node(f"const b = await import('./lib/board3.ts'); const rows = {STDIN};"
                   "console.log(JSON.stringify(b.powerLines(rows, 'da')));", stdin=d[["entity", "variable", "ts_utc", "value", "unit"]].to_json(orient="records"))
        self.assertEqual(len(got), 5)
        for l in got:
            mine = d[d["entity"] == l["key"]].sort_values("ts_utc")
            self.assertEqual(l["last"]["v"], float(mine["value"].iloc[-1]), l["key"])
            self.assertEqual(l["last"]["t"], mine["ts_utc"].iloc[-1][:10])
            self.assertAlmostEqual(l["day"]["change"], float(mine["value"].iloc[-1] - mine["value"].iloc[-2]), places=6)
            # the table's own day change is the same number (price_board.py computes it too)
            own = t[(t["entity"] == l["key"]) & (t["variable"] == "da_day_change")]["value"]
            if len(own):
                self.assertAlmostEqual(l["day"]["change"], float(own.iloc[0]), places=3, msg=l["key"])
        self.assertNotIn("miso:INDIANA.HUB", [l["key"] for l in got])


class ThePage(unittest.TestCase):
    def test_in_review_in_the_battery_pages_layout_and_the_old_board_untouched(self):
        page = src("site", "app", "board", "v3", "page.tsx")
        for piece in ("ToolPage", "ToolHeader", "InputPanel", "HeadlineRow", "ToolSection", "ToolTable", "Fold", "SourceLine"):
            self.assertIn(f"<{piece}", page)
        for title in ('title="Power, by grid"', 'title="Natural gas"', 'title="Oil"'):
            self.assertIn(title, page)
        self.assertIn("data-board-summary", page)
        self.assertIn("data-board-withheld={w.iso}", page)
        self.assertIn("so no number is shown", page)                # a failed read shows no number
        self.assertRegex(src("site", "lib", "release.ts"), r'"/board/v3":\s*"review"')
        self.assertRegex(src("site", "lib", "release.ts"), r'"/board":\s*"review"')
        old = src("site", "app", "board", "page.tsx")
        self.assertNotIn("board3", old)
        r = subprocess.run(["git", "log", "--format=%s", "-1", "--", "site/app/board/page.tsx"], cwd=ROOT, capture_output=True, text=True)
        self.assertNotIn("Session 104", r.stdout)                    # the last commit to touch the old board is not this session's

    def test_no_em_dash(self):
        for rel in ("site/lib/board3.ts", "site/app/board/v3/page.tsx", "tests/test_session104.py"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
