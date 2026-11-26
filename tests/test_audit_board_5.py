"""Audit of the price board, finding 5 (session 10206, docs/reviews/board-model-audit-2026-11-26.md): "Battery spread" is
the day's highest hour less its lowest (warehouse/derived/board_page.py, FORMULAS["battery"]), in either order, one
hour each way, before losses: the trader's top-bottom convention, not what a battery earns. The row's formula and the
note said neither.

1. From the page's own hourly file (site/public/board/h), ERCOT Hub average, day-ahead, the 365 complete local days to
   the file's last: on some days the lowest hour comes after the highest, so charging first gives a smaller spread, and
   an 85 percent round trip smaller still. Passes on main.
2. The fix on this branch, words only: the note's spreads table says it, with the measured sizes. Fails on main. The
   row's own formula is the builder's words (a file window E may touch tonight): the ready text is in the audit."""
import collections
import datetime as dt
import json
import os
import unittest
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def complete_days(path):
    with open(path, encoding="utf-8") as f:
        h = json.load(f)
    tz = ZoneInfo(h["tz"])
    by = collections.defaultdict(list)
    for i, v in enumerate(h["da"]):
        loc = dt.datetime.fromtimestamp((h["t0"] + i) * 3600, tz=dt.timezone.utc).astimezone(tz)
        by[loc.date()].append(v)
    out = {}
    for d, vs in by.items():
        a = dt.datetime(d.year, d.month, d.day, tzinfo=tz)
        n = d + dt.timedelta(days=1)
        b = dt.datetime(n.year, n.month, n.day, tzinfo=tz)
        hours = round((b.astimezone(dt.timezone.utc) - a.astimezone(dt.timezone.utc)).total_seconds() / 3600)   # 23 or 25 on the daylight saving days
        if len(vs) == hours and all(v is not None for v in vs):
            out[d] = vs
    return out


class BatterySpreadIsTopBottom(unittest.TestCase):
    def test_order_and_losses_make_it_smaller(self):
        days = complete_days(os.path.join(ROOT, "site", "public", "board", "h", "ercot-hb-hubavg.json"))
        keep = sorted(days)[-365:]
        board = ordered = eff = 0.0
        late = 0
        for d in keep:
            p = days[d]
            board += max(p) - min(p)
            best, best85, low = 0.0, 0.0, p[0]
            for v in p[1:]:
                best, best85, low = max(best, v - low), max(best85, v - low / 0.85), min(low, v)
            ordered += best
            eff += best85
            late += p.index(min(p)) > p.index(max(p))
        self.assertGreater(late, 0)
        self.assertLess(ordered, board)
        self.assertLess(eff, ordered)
        if keep[-1] == dt.date(2026, 11, 20):          # the file measured: 55.22, 50.89, 47.52 a day; 57 days late
            self.assertAlmostEqual(board / 365, 55.22, delta=0.005)
            self.assertAlmostEqual(ordered / 365, 50.89, delta=0.005)
            self.assertEqual(late, 57)

    def test_the_note_says_top_bottom_not_what_a_battery_earns(self):
        with open(os.path.join(ROOT, "docs", "methods", "price_board.md"), encoding="utf-8") as f:
            self.assertIn("In either order, one hour each way, before losses: the trader's top-bottom spread, not what a battery earns", f.read())


if __name__ == "__main__":
    unittest.main()
