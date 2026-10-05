"""Session 114: ERCOT's hub prices by day, and Ask ERCOT's past prices; the deals page's AI tag.

Energy Research Warehouse (ERW). The builder of ercot_hub_prices_daily (warehouse/derived/ercot_hub_prices_daily.py)
on intervals made here: the complete-day rule on the two clock-change days, the peak rule on a weekday, a weekend day
and a holiday, the hours below zero and above 200, the rows a machine without the history carries. The table as built,
computed again from the interval tables without the builder's code. That Ask ERCOT is told to read it, that the site's
database is told to hold it out of a visitor's counts, and that /deals reads the AI tag whatever its case.

    python -m unittest tests.test_session114 -v
"""

import json
import os
import re
import subprocess
import sys
import unittest

import numpy as np
import pandas as pd
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import ercot_hub_prices_daily as hd  # noqa: E402
import price_board as pb  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
TABLE = os.path.join(OUT, "ercot_hub_prices_daily.csv")
HISTORY = os.path.join(OUT, "ercot_all_hub_prices_history.csv")
TZ = "America/Chicago"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def intervals(start, end, market, price, node="HB_TEST"):
    """Intervals of one hub over local [start, end): price is a number or a function of the local time."""
    freq = hd.FREQ[market]
    idx = pd.date_range(pd.Timestamp(start, tz=TZ).tz_convert("UTC"), pd.Timestamp(end, tz=TZ).tz_convert("UTC"),
                        freq={"PT1H": "h", "PT15M": "15min"}[freq], inclusive="left")
    v = [float(price(t)) for t in idx.tz_convert(TZ)] if callable(price) else [float(price)] * len(idx)
    return pd.DataFrame({"entity": "ercot:" + node, "variable": "spp_" + market[-3:], "ts_utc": idx.strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "value": v, "unit": "USD/MWh", "freq": freq, "geo": "US-TX", "market": market, "node": node, "ts": idx})


def table_of(df):
    s = hd.summarize(df, pb.nerc_holidays(range(2014, 2030)))
    rows = hd.rows_of(s, "2026-10-05T00:00:00Z")
    return s, {(r.variable, r.ts_utc[:10]): float(r.value) for r in rows.itertuples()}


class TheDay(unittest.TestCase):
    def test_a_day_is_whole_on_both_clock_change_days_and_left_out_when_an_interval_is_missing(self):
        df = pd.concat([intervals("2023-03-11", "2023-03-14", "ercot_dam", 30), intervals("2023-11-04", "2023-11-07", "ercot_rtm", 30)])
        s, t = table_of(df)
        n = {(r.market, str(r.day.date())): (r.n, r.expected) for r in s.itertuples()}
        self.assertEqual(n[("ercot_dam", "2023-03-12")], (23, 23))
        self.assertEqual(n[("ercot_dam", "2023-03-13")], (24, 24))
        self.assertEqual(n[("ercot_rtm", "2023-11-05")], (100, 100))
        self.assertEqual(n[("ercot_rtm", "2023-11-06")], (96, 96))
        short = df[~((df["market"] == "ercot_dam") & (df["ts_utc"] == "2023-03-13T15:00:00Z"))]
        s2, t2 = table_of(short)
        self.assertNotIn(("da_mean", "2023-03-13"), t2)  # 23 of 24 hours: not written, not filled
        self.assertIn(("da_mean", "2023-03-12"), t2)
        self.assertEqual(sum(1 for k in t if k[1] == "2023-03-13"), 7)
        self.assertEqual(sum(1 for k in t2 if k[1] == "2023-03-13"), 0)

    def test_peak_is_the_weekday_block_and_a_weekend_day_or_a_holiday_has_no_peak_row(self):
        # Monday 3 July 2023, Tuesday 4 July (a NERC holiday), Saturday 8 July: the price is the local hour
        df = pd.concat([intervals("2023-07-03", "2023-07-05", "ercot_dam", lambda t: t.hour),
                        intervals("2023-07-08", "2023-07-09", "ercot_dam", lambda t: t.hour)])
        _, t = table_of(df)
        self.assertEqual(t[("da_peak_mean", "2023-07-03")], np.mean(range(6, 22)))       # hours ending 7 to 22
        self.assertEqual(t[("da_offpeak_mean", "2023-07-03")], np.mean(list(range(0, 6)) + [22, 23]))
        self.assertEqual(t[("da_mean", "2023-07-03")], 11.5)
        for day in ("2023-07-04", "2023-07-08"):
            self.assertNotIn(("da_peak_mean", day), t)
            self.assertEqual(t[("da_offpeak_mean", day)], t[("da_mean", day)])
        self.assertEqual((t[("da_min", "2023-07-03")], t[("da_max", "2023-07-03")]), (0.0, 23.0))

    def test_hours_below_zero_and_above_200_count_a_quarter_for_an_interval_and_are_strict(self):
        def price(t):
            if t.hour == 3:
                return -5.0 if t.minute < 30 else 0.0      # two intervals below zero; zero is not below zero
            if t.hour == 17:
                return 200.0 if t.minute == 0 else 250.0   # three intervals above 200; 200 is not above 200
            return 40.0
        _, t = table_of(intervals("2024-06-05", "2024-06-06", "ercot_rtm", price))
        self.assertEqual(t[("rt_hours_below_zero", "2024-06-05")], 0.5)
        self.assertEqual(t[("rt_hours_above_200", "2024-06-05")], 0.75)
        _, d = table_of(intervals("2024-06-05", "2024-06-06", "ercot_dam", lambda t: -1.0 if t.hour < 4 else 500.0 if t.hour == 18 else 20.0))
        self.assertEqual((d[("da_hours_below_zero", "2024-06-05")], d[("da_hours_above_200", "2024-06-05")]), (4.0, 1.0))

    def test_days_the_inputs_do_not_hold_are_carried_and_an_unchanged_row_keeps_its_stamp(self):
        old_in = intervals("2024-06-03", "2024-06-06", "ercot_dam", 25)
        s = hd.summarize(old_in, set())
        old = hd.rows_of(s, "2026-01-01T00:00:00Z")
        new_in = pd.concat([intervals("2024-06-05", "2024-06-06", "ercot_dam", 25), intervals("2024-06-06", "2024-06-07", "ercot_dam", 99)])
        s2 = hd.summarize(new_in, set())
        new = hd.rows_of(s2, "2026-10-05T00:00:00Z")
        seen = pd.MultiIndex.from_arrays([s2["entity"], s2["market"], [pb.day_ts(x.date()) for x in s2["day"]]])
        out, carried = hd.merge_previous(new, old, seen, lambda m: None)
        by = {(r.variable, r.ts_utc[:10]): r for r in out.itertuples()}
        self.assertEqual(carried, 14)                                                  # 3 and 4 June, seven rows each
        self.assertEqual(by[("da_mean", "2024-06-03")].retrieved_at, "2026-01-01T00:00:00Z")
        self.assertEqual(by[("da_mean", "2024-06-05")].retrieved_at, "2026-01-01T00:00:00Z")   # unchanged: its stamp kept
        self.assertEqual(by[("da_mean", "2024-06-06")].retrieved_at, "2026-10-05T00:00:00Z")   # new
        self.assertFalse(out.duplicated(["entity", "variable", "ts_utc"]).any())

    def test_a_statistic_is_a_row_and_the_table_has_no_extra_column(self):
        self.assertEqual(hd.COLS, hd.ip.SERIES_COLS)   # the site's database keeps only these of a series table
        self.assertIn('(["extra"] if shape != "series"', src("warehouse", "supabase", "load.py"))
        self.assertEqual([n for n, _, _ in hd.STATS], ["mean", "peak_mean", "offpeak_mean", "min", "max", "hours_below_zero", "hours_above_200"])


@unittest.skipUnless(os.path.exists(TABLE), "ercot_hub_prices_daily is not on this machine")
class TheTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        t = pd.read_csv(TABLE, comment="#", dtype=str, keep_default_na=False)
        t["v"] = t["value"].astype(float)
        cls.t = t
        cls.wide = t.pivot(index=["entity", "ts_utc"], columns="variable", values="v")

    def test_shape_keys_and_what_every_day_must_satisfy(self):
        t, w = self.t, self.wide
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertEqual(sorted(t["variable"].unique()), sorted(f"{m}_{s}" for m in ("da", "rt") for s, _, _ in hd.STATS))
        self.assertEqual(set(t.loc[t["variable"].str.contains("hours_"), "unit"]), {"count"})
        self.assertEqual(set(t.loc[~t["variable"].str.contains("hours_"), "unit"]), {"USD/MWh"})
        for m, per_hour in (("da", 1), ("rt", 4)):
            d = w[w[f"{m}_mean"].notna()]
            self.assertTrue(((d[f"{m}_min"] <= d[f"{m}_mean"] + 1e-4) & (d[f"{m}_mean"] <= d[f"{m}_max"] + 1e-4)).all())
            for h in (f"{m}_hours_below_zero", f"{m}_hours_above_200"):
                self.assertTrue(d[h].between(0, 25).all())
                self.assertTrue(np.allclose(d[h] * per_hour, (d[h] * per_hour).round()))   # whole intervals
            days = pd.to_datetime(d.index.get_level_values("ts_utc").str[:10])
            weekend = days.weekday >= 5
            self.assertTrue(d.loc[weekend, f"{m}_peak_mean"].isna().all())               # no peak row, never a zero
            self.assertTrue(np.allclose(d.loc[weekend, f"{m}_offpeak_mean"], d.loc[weekend, f"{m}_mean"]))
            self.assertTrue(d.loc[days.weekday < 5, f"{m}_peak_mean"].notna().mean() > 0.95)   # weekdays but the holidays

    def test_no_day_is_missing_between_the_first_and_the_last(self):
        for (entity, variable), g in self.t[self.t["variable"].isin(["da_mean", "rt_mean"])].groupby(["entity", "variable"]):
            days = pd.to_datetime(g["ts_utc"].str[:10])
            self.assertEqual(len(days), (days.max() - days.min()).days + 1, (entity, variable))

    @unittest.skipUnless(os.path.exists(HISTORY), "the ERCOT interval history is not on this machine")
    def test_days_computed_again_from_the_intervals_without_the_builders_code(self):
        with open(HISTORY, encoding="utf-8") as f:
            skip = sum(1 for line in f if line.startswith("#"))
        h = pd.read_csv(HISTORY, skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype={"value": float})
        local = pd.to_datetime(h["ts_utc"], utc=True).dt.tz_convert(TZ)
        h["day"], h["hour"], h["wd"] = local.dt.strftime("%Y-%m-%d"), local.dt.hour, local.dt.weekday
        cases = [("ercot:HB_HUBAVG", "spp_rtm", "2021-02-15"), ("ercot:HB_WEST", "spp_rtm", "2022-05-08"), ("ercot:HB_NORTH", "spp_dam", "2023-08-17"),
                 ("ercot:HB_HOUSTON", "spp_dam", "2015-01-01"), ("ercot:HB_SOUTH", "spp_rtm", "2019-11-03"), ("ercot:HB_BUSAVG", "spp_dam", "2024-03-10"),
                 ("ercot:HB_WEST", "spp_dam", "2024-04-14"), ("ercot:HB_HUBAVG", "spp_dam", "2026-07-03")]
        holidays = {d.isoformat() for d in pb.nerc_holidays(range(2014, 2028))}
        for entity, variable, day in cases:
            x = h[(h["entity"] == entity) & (h["variable"] == variable) & (h["day"] == day)]
            m, step = ("da", 1.0) if variable == "spp_dam" else ("rt", 0.25)
            self.assertGreater(len(x), 0, (entity, variable, day))
            got = self.wide.loc[(entity, day + "T00:00:00Z")]
            v = x["value"].tolist()
            self.assertAlmostEqual(got[f"{m}_mean"], sum(v) / len(v), places=3)
            self.assertEqual(got[f"{m}_min"], min(v))
            self.assertEqual(got[f"{m}_max"], max(v))
            self.assertEqual(got[f"{m}_hours_below_zero"], step * sum(1 for p in v if p < 0))
            self.assertEqual(got[f"{m}_hours_above_200"], step * sum(1 for p in v if p > 200))
            pk = [p for p, hr, wd in zip(v, x["hour"], x["wd"]) if wd < 5 and 6 <= hr < 22 and day not in holidays]
            if pk:
                self.assertAlmostEqual(got[f"{m}_peak_mean"], sum(pk) / len(pk), places=3)
            else:
                self.assertTrue(np.isnan(got[f"{m}_peak_mean"]))


class AskErcot(unittest.TestCase):
    def test_the_guide_puts_the_daily_table_first_and_the_rules_say_past_prices(self):
        import ercot
        self.assertEqual(ercot.CARDS[0][0], "ercot_hub_prices_daily")
        self.assertIn("ercot_hub_prices_daily", ercot.SCOPE["tables"])
        self.assertIn("ercot_hub_prices_daily", ercot.SCOPE["filters"])
        self.assertIn("12. Past prices.", ercot.RULES)
        self.assertIn("Name it in the answer as the table you read", ercot.RULES)
        self.assertLess(ercot.RULES.index("11. Context."), ercot.RULES.index("12. Past prices."))
        card = dict(ercot.CARDS)
        self.assertIn("NOT in the site's database", card["ercot_all_hub_prices_history"])
        for v in ("da_mean", "rt_max", "rt_hours_below_zero", "da_hours_above_200", "rt_offpeak_mean"):
            self.assertIn(v, card["ercot_hub_prices_daily"])

    def test_the_sites_spec_is_the_profile_as_it_stands(self):
        import ercot
        spec = json.loads(src("site", "lib", "chat", "spec_ercot.json"))
        self.assertEqual(spec["tables"], ercot.SCOPE["tables"])
        self.assertIn("12. Past prices.", spec["system"])
        self.assertIn("## ercot_hub_prices_daily (public, tier derived", spec["system"])
        self.assertIn("ercot_hub_prices_daily, since 2015", src("site", "lib", "chat", "tools.ts"))

    def test_the_evaluation_has_ten_past_price_questions_checked_against_the_intervals(self):
        spec = yaml.safe_load(src("warehouse", "chat", "eval", "questions_ercot.yaml"))
        qs = spec["questions"]
        self.assertEqual(len(qs), 54)
        past = [q for q in qs if q["note"].startswith("session 114, past prices")]
        self.assertEqual([q["id"] for q in past], [f"e{i}" for i in range(45, 55)])
        for q in past:
            self.assertEqual(q["tables"], ["ercot_hub_prices_daily", "ercot_all_hub_prices_history"])
            self.assertIn("from the intervals of ercot_all_hub_prices_history", q["note"])


class Stores(unittest.TestCase):
    def test_loaded_whole_and_held_out_of_a_visitors_counts(self):
        cfg = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        self.assertTrue(any(re.match(p, "ercot_hub_prices_daily") for p in cfg["full"]))
        self.assertFalse(any(re.match(p, "ercot_hub_prices_daily") for p in cfg["recent"]["tables"]))   # whole, not 35 days
        self.assertIn("ercot_hub_prices_daily", cfg["review_hold"])
        self.assertIn("erw:ercot_hub_prices_daily", cfg["sources_hold"])
        self.assertNotIn("ercot_hub_prices_daily", cfg["catalogue_hold"])

    def test_restored_on_the_runner_and_rebuilt_by_the_daily_run_after_the_prices(self):
        cfg = yaml.safe_load(src("warehouse", "redivis", "config.yaml"))
        self.assertTrue(any(re.match(p, "ercot_hub_prices_daily") for p in cfg["restore_before_run"]))
        sh = src("warehouse", "run_daily.sh")
        line = 'run_other ercot_hub_prices_daily "$PYTHON" warehouse/derived/ercot_hub_prices_daily.py'
        self.assertIn(line, sh)
        self.assertLess(sh.index("consolidate.py build"), sh.index(line))
        self.assertLess(sh.index(line), sh.index('echo "== validator"'))

    def test_the_builder_makes_no_request(self):
        code = src("warehouse", "derived", "ercot_hub_prices_daily.py")
        for word in ("requests", "urllib", "http.client", "gridstatus"):
            self.assertNotIn(word, code)


class DealsPage(unittest.TestCase):
    def test_the_ai_tag_is_read_whatever_its_case(self):
        page = src("site", "app", "deals", "page.tsx")
        self.assertIn('aiPower: String(x.ai_power ?? "").toLowerCase() === "true"', page)
        self.assertNotIn('x.ai_power === "true"', page)

    @unittest.skipUnless(os.path.exists(os.path.join(OUT, "energy_deals.csv")), "energy_deals is not on this machine")
    def test_the_table_writes_the_tag_with_a_capital(self):
        d = pd.read_csv(os.path.join(OUT, "energy_deals.csv"), comment="#", dtype=str, keep_default_na=False)
        self.assertEqual(set(d["ai_power"].str.lower()), {"true", "false"})
        self.assertGreater((d["ai_power"] == "True").sum(), 0)   # the form the page's exact test never matched


if __name__ == "__main__":
    unittest.main()
