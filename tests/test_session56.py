"""Session 56: California levels in the battery game.

Energy Research Warehouse (ERW). No network, no model.
1. Each California day in site/data/battery_levels.json is real rows: its timestamps and prices equal the CAISO SP15
   real-time rows (lmp_rtm_15m_mean) of iso_hub_prices_history, and it holds every interval of its Pacific-time day.
2. Each day is the one its rule picks, recomputed here by hand from the table (complete days only): the lowest mean of
   10:00 to 15:00 Pacific, and the largest rise from the 12:00 to 15:00 mean to the 18:00 to 21:00 mean; and the
   numbers in each day's line are that rule's numbers.
3. No California day shares its date with an ERCOT level (the game keys levels by date), and the five ERCOT days are
   unchanged.
4. The page and the game: the levels grouped by grid, the rule shown, the debrief naming the grid and linking
   /grid/caiso, the time zone per level.

    python -m unittest tests.test_session56 -v
"""

import json
import os
import re
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LEVELS = os.path.join(ROOT, "site", "data", "battery_levels.json")
TABLE = os.path.join(ROOT, "warehouse", "output", "iso_hub_prices_history.csv")
TZ = "America/Los_Angeles"


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def levels():
    with open(LEVELS, encoding="utf-8") as f:
        return json.load(f)["levels"]


def need(day):
    a = pd.Timestamp(day).tz_localize(TZ)
    return int(((a + pd.DateOffset(days=1)).normalize() - a).total_seconds() // 900)


class California(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ca = [lv for lv in levels() if lv.get("grid") == "CAISO"]
        cls.sp15 = None
        if os.path.exists(TABLE):
            parts = []
            # the header comments: skip them by count (a "#" inside a URL must not cut a row)
            with open(TABLE, encoding="utf-8") as f:
                n = 0
                for line in f:
                    if not line.startswith("#"):
                        break
                    n += 1
            for ch in pd.read_csv(TABLE, skiprows=n, usecols=["variable", "ts_utc", "value", "market", "node"], chunksize=500_000):
                parts.append(ch[(ch["market"] == "caiso_rtm") & (ch["node"] == "TH_SP15_GEN-APND") & (ch["variable"] == "lmp_rtm_15m_mean")])
            d = pd.concat(parts)
            local = pd.to_datetime(d["ts_utc"], utc=True).dt.tz_convert(TZ)
            cls.sp15 = d.assign(day=local.dt.strftime("%Y-%m-%d"), hour=local.dt.hour).sort_values("ts_utc")

    def test_two_days_whole(self):
        self.assertEqual([lv["slug"] for lv in self.ca], ["caiso-solar-noon", "caiso-duck"])
        for lv in self.ca:
            self.assertEqual((lv["tz"], lv["table"], lv["entity"], lv["variable"], lv["market"]),
                             (TZ, "iso_hub_prices_history", "caiso:TH_SP15_GEN-APND", "lmp_rtm_15m_mean", "caiso_rtm"))
            self.assertEqual(len(lv["price"]), need(lv["date"]), lv["date"])
            self.assertEqual(len(lv["ts_utc"]), need(lv["date"]), lv["date"])
            self.assertEqual(len(set(lv["ts_utc"])), len(lv["ts_utc"]))
            local = pd.to_datetime(lv["ts_utc"], utc=True).tz_convert(TZ)
            self.assertTrue((local.strftime("%Y-%m-%d") == lv["date"]).all(), lv["date"])
            steps = pd.Series(pd.to_datetime(lv["ts_utc"], utc=True)).diff().dropna()
            self.assertTrue((steps == pd.Timedelta(minutes=15)).all(), lv["date"])
            self.assertIn("Pacific", lv["rule"])

    def test_prices_are_the_tables_rows(self):
        if self.sp15 is None:
            self.skipTest("iso_hub_prices_history.csv is not on this machine")
        by = self.sp15.set_index("ts_utc")["value"]
        for lv in self.ca:
            self.assertEqual([float(by[t]) for t in lv["ts_utc"]], lv["price"], lv["date"])
            self.assertEqual(int((self.sp15["day"] == lv["date"]).sum()), need(lv["date"]))  # the table's day is complete, nothing more

    def test_each_rule_picks_its_day(self):
        if self.sp15 is None:
            self.skipTest("iso_hub_prices_history.csv is not on this machine")
        d = self.sp15
        size = d.groupby("day").size()
        full = [x for x in size.index if size[x] == need(x)]
        d = d[d["day"].isin(full)]
        win = lambda a, b: d[(d["hour"] >= a) & (d["hour"] < b)].groupby("day")["value"].mean()  # noqa: E731
        mid, rise = win(10, 15), (win(18, 21) - win(12, 15)).dropna()
        noon, duck = (lv for lv in self.ca)
        self.assertEqual(noon["date"], mid.idxmin())
        self.assertEqual(duck["date"], rise.idxmax())
        self.assertIn(f"{mid.min():,.2f} USD/MWh", noon["why"])
        self.assertIn(f"{rise.max():,.2f} USD/MWh", duck["why"])
        # by hand from the level's own prices, too
        p = pd.Series(noon["price"], index=pd.to_datetime(noon["ts_utc"], utc=True).tz_convert(TZ))
        self.assertAlmostEqual(p[(p.index.hour >= 10) & (p.index.hour < 15)].mean(), mid.min(), places=9)
        q = pd.Series(duck["price"], index=pd.to_datetime(duck["ts_utc"], utc=True).tz_convert(TZ))
        r = q[(q.index.hour >= 18) & (q.index.hour < 21)].mean() - q[(q.index.hour >= 12) & (q.index.hour < 15)].mean()
        self.assertAlmostEqual(r, rise.max(), places=9)
        self.assertEqual(len(full), 393)

    def test_no_date_shared_and_ercot_days_unchanged(self):
        er = [lv for lv in levels() if lv.get("grid", "ERCOT") == "ERCOT"]
        self.assertEqual([lv["date"] for lv in er], ["2021-02-15", "2023-08-10", "2026-04-26", "2026-08-29", "2025-01-05"])
        self.assertFalse({lv["date"] for lv in self.ca} & {lv["date"] for lv in er})
        self.assertTrue(all(lv["tz"] == "America/Chicago" and lv["table"] != "iso_hub_prices_history" for lv in er))

    def test_page_and_game(self):
        game = src("site", "app", "play", "battery", "Game.tsx")
        self.assertIn('(["ERCOT", "CAISO"] as const).filter((gr) => levels.some((l) => l.grid === gr))', game)
        self.assertIn("The rule: {l.rule}", game)
        self.assertIn('href: "/grid/caiso"', game)
        self.assertIn("The grid: {G.name}.", game)
        self.assertIn("<Link href={G.href}>{G.page}</Link>", game)
        self.assertIsNone(re.search(r"clock\(level\.ts_utc", game), "a clock call without the level's time zone")
        self.assertNotIn("(Central time)", game)
        page = src("site", "app", "play", "battery", "page.tsx")
        self.assertIn("the lowest mean price from 10:00 to 15:00 Pacific", page)
        self.assertIn("grid: grid ?? \"ERCOT\", tz: tz ?? TZ", page)
        builder = src("warehouse", "derived", "battery_levels.py")
        self.assertIn("MIDDAY, AFTERNOON, EVENING = (10, 15), (12, 15), (18, 21)", builder)
        self.assertIn("--rebuild-ercot", builder)
        for p in (("site", "app", "play", "battery", "Game.tsx"), ("site", "app", "play", "battery", "page.tsx"), ("warehouse", "derived", "battery_levels.py"),
                  ("site", "data", "battery_levels.json"), ("docs", "methods", "battery_game.md"), ("tests", "test_session56.py")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
