"""Audit of the prices pages, finding 5 (session 10218, docs/reviews/prices-model-audit-2026-11-26.md): the Grid map's
price colors (components/grid/MapPrice.tsx, data/regions/prices_map.json) offer "Day-ahead, the newest day", and the
legend gave the two ends of the scale with no date. "The newest day" is the newest whole day the file held when it was
built: the file of 19 November 2026 colors the map by 16 November, and on 26 November the site's own hourly price files
(public/board/h) hold whole days to 20 November for ERCOT's Hub Average and to 25 November for CAISO SP15 and SPP North.
Only each area's hover named the day.

1. What the files hold (passes on main; skipped on another build of the file): the map's day and the newer whole days
   the page's own hourly files hold.
2. The fix on this branch, words only (fails on main): drawn with the site's own component, the legend names the day
   (or the 30 or 365 days to it) and the day the file was built, for every measure. No figure or color moves."""
import collections
import datetime as dt
import json
import os
import subprocess
import unittest
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def newest_whole_day(hid):
    with open(os.path.join(SITE, "public", "board", "h", hid + ".json"), encoding="utf-8") as f:
        hf = json.load(f)
    tz = ZoneInfo(hf["tz"])
    by = collections.Counter()
    for i, v in enumerate(hf["da"]):
        if v is not None:
            by[dt.datetime.fromtimestamp((hf["t0"] + i) * 3600, tz=dt.timezone.utc).astimezone(tz).date()] += 1

    def need(d):
        a = dt.datetime(d.year, d.month, d.day, tzinfo=tz)
        n = d + dt.timedelta(days=1)
        return round((dt.datetime(n.year, n.month, n.day, tzinfo=tz) - a).total_seconds() / 3600)
    return max(d for d, n in by.items() if n == need(d))


class TheLegendNamesTheDay(unittest.TestCase):
    def test_the_maps_day_is_older_than_the_sites_own_hourly_files(self):
        with open(os.path.join(SITE, "data", "regions", "prices_map.json"), encoding="utf-8") as f:
            m = json.load(f)
        if not m["built"].startswith("2026-11-19"):
            self.skipTest(f"measured on the file built 19 November 2026; this one {m['built']}")
        self.assertEqual({m["bas"][b]["day"] for b in ("CISO", "ERCO", "SWPP")}, {"2026-11-16"})
        self.assertGreaterEqual(newest_whole_day("ercot-hb-hubavg"), dt.date(2026, 11, 20))
        self.assertGreaterEqual(newest_whole_day("caiso-th-sp15-gen-apnd"), dt.date(2026, 11, 25))
        self.assertGreaterEqual(newest_whole_day("spp-sppnorth-hub"), dt.date(2026, 11, 25))

    def test_the_legend_names_the_day_and_the_build(self):
        with open(os.path.join(SITE, "data", "regions", "prices_map.json"), encoding="utf-8") as f:
            m = json.load(f)
        out = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/audit-prices-5-draw.mjs"],
                             cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        rows = [json.loads(x) for x in out.stdout.splitlines() if x.startswith("{")]
        self.assertEqual(len(rows), 8)
        day, built = m["bas"]["ERCO"]["day"], m["built"][:10]
        for r in rows:
            k = r["measure"]
            span = f"day-ahead of {day}" if k.startswith("day") else f"the {'30' if '30d' in k else '365'} days to "
            self.assertIn(span, r["legend"], k)
            self.assertIn(f"from the price file built {built}", r["legend"], k)
            self.assertEqual(r["emDashes"], 0)


if __name__ == "__main__":
    unittest.main()
