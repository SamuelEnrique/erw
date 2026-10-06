"""Session 127: the price board, version 4 (/board/v4, in review).

Energy Research Warehouse (ERW). EIA's NYMEX futures connector (warehouse/connectors/eia_futures.py) and the board's
builder (warehouse/derived/price_board_v4.py), on real samples saved under tests/fixtures/session127/: twelve rows of
EIA's own answer for natural gas futures contract 1, and fifteen months of the daily series the board reads (Henry Hub,
WTI, Gulf Coast gasoline and diesel, ERCOT's hub average day-ahead and real time) as the warehouse held them on
5 October 2026. Where a test removes or moves a real value it says so: it tests the arithmetic and writes nothing.
"""
import datetime as dt
import json
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import eia_futures as ef  # noqa: E402
import price_board_v4 as b4  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session127")
SITE = os.path.join(ROOT, "site")
COPY = os.path.join(SITE, "data", "board_v4.json")
D = dt.date


def series(entity, variable):
    x = pd.read_csv(os.path.join(FIX, "daily_series_sample.csv"), comment="#")
    x = x[(x["entity"] == entity) & (x["variable"] == variable)]
    return {dt.date.fromisoformat(t[:10]): float(v) for t, v in zip(x["ts_utc"], x["value"])}


class Futures(unittest.TestCase):
    def rows(self):
        with open(os.path.join(FIX, "eia_ng_futures_RNGC1_sample.json"), encoding="utf-8") as f:
            rows = json.load(f)["response"]["data"]
        for r in rows:
            r["_url"], r["_retrieved"] = "https://api.eia.gov/v2/natural-gas/pri/fut/data/", "2026-10-05T23:50:00Z"
        return rows

    def test_eias_rows_become_the_tables_rows_unchanged(self):
        t, empty = ef.shape("eia:RNGC1", self.rows())
        self.assertEqual((len(t), empty), (12, 0))
        self.assertEqual(set(t["unit"]), {"USD/MMBtu"})
        self.assertEqual(set(t["node"]), {"1"})
        self.assertEqual(set(t["source"]), {"eia:nymex_futures_natural_gas"})
        self.assertEqual((t["ts_utc"].iloc[0], float(t["value"].iloc[0])), ("2019-01-01T00:00:00Z", 2.94))      # EIA's first row of 2019
        self.assertEqual(t["ts_utc"].iloc[-1], "2024-04-05T00:00:00Z")                                          # the day EIA stopped

    def test_a_date_with_no_value_is_left_out_and_counted(self):
        rows = self.rows()
        rows[3]["value"] = None                                        # one real value removed, for the arithmetic
        t, empty = ef.shape("eia:RNGC1", rows)
        self.assertEqual((len(t), empty), (11, 1))

    def test_a_value_that_is_not_a_number_or_a_unit_that_is_not_eias_stops_it(self):
        rows = self.rows()
        rows[2]["value"] = "W"
        with self.assertRaises(RuntimeError):
            ef.shape("eia:RNGC1", rows)
        rows = self.rows()
        rows[2]["units"] = "$/GAL"
        with self.assertRaises(RuntimeError):
            ef.shape("eia:RNGC1", rows)

    def test_sixteen_contracts_and_the_ceiling(self):
        self.assertEqual(len(ef.SERIES), 16)
        self.assertEqual(sorted({v[4] for v in ef.SERIES.values()}), [1, 2, 3, 4])
        self.assertEqual(ef.CEILING, 600_000)
        self.assertEqual(ef.START, "2019-01-01")


class Stats(unittest.TestCase):
    def test_henry_hub_as_held_on_5_october_2026(self):
        s = b4.stats(series("eia:henry_hub", "spot_price"))
        self.assertEqual(s["last"], (D(2026, 9, 29), 3.18))
        d, v, ch = s["moves"]["1w"]
        self.assertLessEqual(d, D(2026, 9, 22))
        self.assertGreaterEqual(d, D(2026, 9, 22) - dt.timedelta(days=b4.SLACK))
        self.assertAlmostEqual(ch, 3.18 - v, places=9)
        self.assertAlmostEqual(ch, 0.28, places=2)
        lo, hi, n, pos = s["range"]
        self.assertEqual((lo, hi), (2.54, 30.72))                     # the year's low and high day, as EIA published them
        self.assertGreaterEqual(n, b4.RANGE_MIN)
        self.assertAlmostEqual(pos, (3.18 - 2.54) / (30.72 - 2.54), places=9)

    def test_every_move_is_the_last_value_less_a_day_actually_held(self):
        x = series("ercot:HB_HUBAVG", "da_mean")
        s = b4.stats(x)
        d0, v0 = s["last"]
        for key, back in (("1d", 1), ("1w", 7), ("1m", 30), ("1y", 365)):
            d, v, ch = s["moves"][key]
            self.assertIn(d, x)
            self.assertEqual(v, x[d])
            self.assertAlmostEqual(ch, v0 - v, places=9)
            self.assertLessEqual(d, d0 - dt.timedelta(days=back))

    def test_a_move_whose_earlier_day_is_not_held_is_not_made(self):
        x = series("eia:wti_cushing", "spot_price")
        d0 = max(x)
        for d in list(x):                                             # the days a year back removed, for the arithmetic
            if d0 - dt.timedelta(days=365 + b4.SLACK) <= d <= d0 - dt.timedelta(days=365):
                del x[d]
        s = b4.stats(x)
        self.assertIsNone(s["moves"]["1y"])
        self.assertIsNotNone(s["moves"]["1w"])

    def test_a_range_needs_enough_days_and_an_empty_series_has_no_figures(self):
        x = series("eia:wti_cushing", "spot_price")
        few = {d: v for d, v in x.items() if d > max(x) - dt.timedelta(days=100)}
        self.assertIsNone(b4.stats(few)["range"])
        self.assertIsNone(b4.stats({}))

    def test_a_flat_year_has_a_range_and_no_position(self):
        flat = {D(2026, 1, 1) + dt.timedelta(days=i): 5.0 for i in range(250)}      # made up, for the arithmetic
        lo, hi, n, pos = b4.stats(flat)["range"]
        self.assertEqual((lo, hi, pos), (5.0, 5.0, None))


class Spreads(unittest.TestCase):
    def test_the_spark_spread_takes_the_days_gas_or_the_newest_up_to_four_days_back(self):
        da, gas = series("ercot:HB_HUBAVG", "da_mean"), series("eia:henry_hub", "spot_price")
        sp = b4.spark(da, gas)
        last_gas = max(gas)
        d = last_gas + dt.timedelta(days=b4.GAS_BACK)                  # four days after the newest gas day: still made
        self.assertAlmostEqual(sp[d], da[d] - 7.0 * gas[last_gas], places=9)
        self.assertNotIn(last_gas + dt.timedelta(days=b4.GAS_BACK + 1), sp)   # five days after: not made
        self.assertAlmostEqual(sp[last_gas], da[last_gas] - 7.0 * gas[last_gas], places=9)
        self.assertEqual(b4.HEAT_RATE, 7.0)

    def test_day_ahead_less_real_time_only_where_both_are_held(self):
        da, rt = series("ercot:HB_HUBAVG", "da_mean"), series("ercot:HB_HUBAVG", "rt_mean")
        x = b4.da_minus_rt(da, rt)
        self.assertEqual(set(x), set(da) & set(rt))
        self.assertNotIn(max(da), x)                                   # day-ahead runs a day past real time
        d = max(rt)
        self.assertAlmostEqual(x[d], da[d] - rt[d], places=9)

    def test_the_crack_spread_by_its_formula_on_days_all_three_are_held(self):
        g, d, c = (series(e, "spot_price") for e in b4.CRACK)
        x = b4.crack_321(g, d, c)
        day = D(2026, 9, 29)
        self.assertAlmostEqual(x[day], (2 * g[day] + d[day]) * 42 / 3 - c[day], places=9)
        self.assertAlmostEqual(x[day], 73.632, places=3)
        del c[day]                                                     # the crude of one day removed, for the arithmetic
        self.assertNotIn(day, b4.crack_321(g, d, c))

    def test_miso_is_not_read_and_pjm_is_not_there(self):
        grids = [g[0] for g in b4.GRIDS]
        self.assertEqual(grids, ["ERCOT", "CAISO", "NYISO", "SPP", "ISO-NE"])
        self.assertFalse(any("miso" in g[1] or "pjm" in g[1] for g in b4.GRIDS))


class Repository(unittest.TestCase):
    def src(self, *p):
        with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
            return f.read()

    def test_no_em_dash_in_what_the_session_wrote(self):
        for p in (("warehouse", "connectors", "eia_futures.py"), ("warehouse", "derived", "price_board_v4.py"), ("warehouse", "refresh_board_v4.sh"),
                  ("site", "app", "_retired", "board-v4", "page.tsx"), ("site", "lib", "board4.ts"), ("docs", "methods", "price_board_v4.md"), ("tests", "test_session127.py")):
            if os.path.exists(os.path.join(ROOT, *p)):
                text = self.src(*p)
                self.assertNotIn(chr(0x2014), text, p)
                self.assertNotIn(chr(0x2013), text, p)

    def test_the_page_is_in_review_and_the_other_boards_are_untouched(self):
        rel = self.src("site", "lib", "release.ts")
        for line in ('"/board/v4": "review"', '"/board/v3": "review"', '"/board": "review"'):
            self.assertIn(line, rel)
        page = self.src("site", "app", "_retired", "board-v4", "page.tsx")   # session 132: retired, kept unrouted; /board/v4 redirects to /board
        for words in ("@/data/board_v4.json", "data-summary", "Named in the plan, and not on the board", "robots: { index: false", "Formula:", "indicative"):
            self.assertIn(words, page)
        lib = self.src("site", "lib", "board4.ts")
        for name in ("Regional natural gas hubs", "TTF", "JKM", "Uranium", "Carbon allowances", "Lithium", "NYMEX futures"):
            self.assertIn(name, lib)
        self.assertEqual(lib.count("licensed source needed"), 7)
        self.assertIn('import { WITHHELD } from "@/lib/board3"', page)      # PJM licensed and MISO paused, in the words the site already uses

    def test_the_refresh_is_written_and_not_scheduled(self):
        sh = self.src("warehouse", "refresh_board_v4.sh")
        self.assertIn('health.py run --step "price_board_v4"', sh)
        self.assertNotIn("eia_futures.py\n", sh.replace("warehouse/connectors/eia_futures.py is not run here", ""))
        for wf in os.listdir(os.path.join(ROOT, ".github", "workflows")):
            self.assertNotIn("refresh_board_v4", self.src(".github", "workflows", wf), wf)
        self.assertNotIn("price_board_v4", self.src("warehouse", "run_daily.sh"))

    def test_the_tables_are_held_out_of_the_catalogue_and_the_futures_are_internal(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
        import load
        for t in ("price_board_stats", "eia_all_futures_prices"):
            self.assertIn(t, load.LIVE["catalogue_hold"])
        for s in ("erw:price_board_v4", "eia:nymex_futures_petroleum", "eia:nymex_futures_natural_gas"):
            self.assertIn(s, load.LIVE["sources_hold"])
        src = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), dtype=str, keep_default_na=False)
        lic = dict(zip(src["source"], src["license"]))
        if "eia:nymex_futures_petroleum" in lic:
            self.assertEqual((lic["eia:nymex_futures_petroleum"], lic["eia:nymex_futures_natural_gas"], lic["erw:price_board_v4"]), ("internal", "internal", "public"))


@unittest.skipUnless(os.path.exists(COPY), "the site's copy is written by price_board_v4.py --snapshot")
class SiteCopy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(COPY, encoding="utf-8") as f:
            cls.raw = f.read()
        cls.f = json.loads(cls.raw)

    def test_every_line_adds_up(self):
        self.assertNotIn("NaN", self.raw)
        self.assertEqual(len(self.f["lines"]), 33)
        self.assertEqual(sum(1 for ln in self.f["lines"] if ln["formula"]), 11)
        for ln in self.f["lines"]:
            if not ln["last"]:
                continue
            for k, m in (ln["moves"] or {}).items():
                if m:
                    self.assertAlmostEqual(m["change"], ln["last"]["v"] - m["v"], places=3, msg=(ln["key"], k))
                    self.assertLess(m["t"], ln["last"]["t"])
            r = ln["range"]
            if r:
                self.assertLessEqual(r["low"], ln["last"]["v"])
                self.assertGreaterEqual(r["high"], ln["last"]["v"])
                self.assertGreaterEqual(r["days"], self.f["range_min_days"])
                if r["position"] is not None:
                    self.assertTrue(0 <= r["position"] <= 1)

    def test_no_line_of_miso_or_pjm(self):
        self.assertFalse(any("miso" in ln["key"].lower() or "pjm" in ln["key"].lower() for ln in self.f["lines"]))


if __name__ == "__main__":
    unittest.main()
