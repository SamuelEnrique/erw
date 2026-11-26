"""Session 11000 (chain 750, the browser read of 26 November 2026): the Grid tool's "same day last week" lost its
first hours.

Each grid's page (site/components/grid/YourGrid.tsx, RightNow) draws the latest day EIA has published, hour by hour,
beside the same local day a week earlier. The hours came from a read of nine days back from the clock (site/lib/grid.ts).
The latest day is behind the clock by as long as the loads are. On 26 November 2026 at 13:00 UTC it was 24 November:
last week's day began on 17 November at 05:00 to 08:00 UTC, the read began at 17 November 13:00 UTC, and on all seven
grids the first 5 to 8 hours of last week's line read "not held" while the live set held all 24 hours of that day.

The window must reach the lag plus eight days (a local day begins up to a day before its latest hour; the week adds
seven). DEMAND_DAYS in site/lib/data.ts is that window, used by the page's read and by the Now view's.

Energy Research Warehouse (ERW). No network, no build: the source is read and the rule is worked through.

    python -m unittest tests.test_session11000_grid_last_week -v
"""

import datetime as dt
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
H = dt.timedelta(hours=1)


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def demand_days():
    return int(re.search(r"export const DEMAND_DAYS = (\d+);", read("site", "lib", "data.ts")).group(1))


def hours_of_last_week_read(now, latest, offset_hours, window_days):
    """Of the 24 hours of the local day seven days before the latest hour's local day, how many a read that begins
    `window_days` before `now` (floored to the hour, as daysAgo does) can hold. `offset_hours` is the grid's clock
    against UTC (-6 for Central standard time)."""
    since = (now - dt.timedelta(days=window_days)).replace(minute=0, second=0, microsecond=0)
    local = latest + dt.timedelta(hours=offset_hours)
    day_start_utc = dt.datetime(local.year, local.month, local.day) - dt.timedelta(hours=offset_hours) - dt.timedelta(days=7)
    return sum(1 for i in range(24) if day_start_utc + i * H >= since)


class TheWindowReachesLastWeek(unittest.TestCase):
    def test_the_reads_use_the_window(self):
        grid = read("site", "lib", "grid.ts")
        now_view = read("site", "components", "grid", "NowView.tsx")
        self.assertIn('series("eia930_all_demand", { entity: g.entity, variable: "demand_mw", since: daysAgo(DEMAND_DAYS) })', grid)
        self.assertIn('series(DEMAND, { entity, variable: "demand_mw", since: daysAgo(DEMAND_DAYS) })', now_view)
        self.assertIsNone(re.search(r'demand_mw", since: daysAgo\(\d+\)', grid + now_view), "a demand read of the Grid tool counts its days from the clock again")

    def test_the_day_read_on_26_november(self):
        # what the browser saw: 26 November 2026 13:00 UTC, ERCOT's latest hour 24 November 23:00 UTC, Central time
        now, latest = dt.datetime(2026, 11, 26, 13, 2), dt.datetime(2026, 11, 24, 23, 0)
        self.assertEqual(hours_of_last_week_read(now, latest, -6, 9), 17)      # as production drew it: 7 hours cut
        self.assertEqual(hours_of_last_week_read(now, latest, -5, 9), 16)      # PJM, MISO, NYISO, ISO-NE: 8 cut
        self.assertEqual(hours_of_last_week_read(now, latest, -8, 9), 19)      # CAISO: 5 cut
        for offset in (-5, -6, -8):
            self.assertEqual(hours_of_last_week_read(now, latest, offset, demand_days()), 24)

    def test_whole_while_the_loads_are_up_to_a_week_behind(self):
        days = demand_days()
        self.assertGreaterEqual(days, 15)
        now = dt.datetime(2026, 11, 26, 13, 2)
        for lag_hours in range(0, 7 * 24 + 1, 5):
            for offset in (-4, -5, -6, -7, -8):
                latest = (now - dt.timedelta(hours=lag_hours)).replace(minute=0)
                self.assertEqual(hours_of_last_week_read(now, latest, offset, days), 24, (lag_hours, offset))

    def test_nine_days_fail_once_the_loads_are_two_days_behind(self):
        now = dt.datetime(2026, 11, 26, 13, 2)
        self.assertLess(hours_of_last_week_read(now, now - dt.timedelta(hours=48), -6, 9), 24)


if __name__ == "__main__":
    unittest.main()
