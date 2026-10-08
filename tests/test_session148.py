"""Session 148: ERCOT's reserve prices by day and by month, so that no question reads a year of hourly rows.

Energy Research Warehouse (ERW). The builder of ercot_as_prices_daily and ercot_as_prices_monthly
(warehouse/derived/ercot_as_prices_rollup.py) on hours made here: the mean, the lowest and the highest of the hours
held; the two clock-change days; a day and a month with missing hours, which carry their count and are never filled; a
product that begins in the middle of a month; the rows a later run keeps. A trial that records nothing. The two tables
computed again from the hourly table with plain Python, on a machine that holds it. Where the tables are registered.

The hourly table is not in git. It is looked for in ERW_TABLES when that is set (another copy's warehouse/output),
else in this copy's warehouse/output; the tests that need it are skipped where it is not.

    python -m unittest tests.test_session148 -v
"""

import csv
import datetime as dt
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from decimal import ROUND_HALF_UP, Decimal
from unittest import mock
from zoneinfo import ZoneInfo

import pandas as pd
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import ercot_as_prices_rollup as rb  # noqa: E402

TZ = "America/Chicago"
STAMP = "2026-10-07T00:00:00Z"


def tables_dir():
    """Where the warehouse's tables are on this machine: ERW_TABLES, else this copy's warehouse/output."""
    return os.environ.get("ERW_TABLES") or os.path.join(ROOT, "warehouse", "output")


def hourly_path():
    return os.path.join(tables_dir(), "ercot_as_prices.csv")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def hours(start, end, price, product="REGUP"):
    """The hours of one product over local [start, end): price is a number or a function of the local time."""
    idx = pd.date_range(pd.Timestamp(start, tz=TZ).tz_convert("UTC"), pd.Timestamp(end, tz=TZ).tz_convert("UTC"), freq="h", inclusive="left")
    v = [float(price(t)) for t in idx.tz_convert(TZ)] if callable(price) else [float(price)] * len(idx)
    return pd.DataFrame({"entity": "ercot:" + product, "variable": "mcpc_dam", "ts_utc": idx.strftime("%Y-%m-%dT%H:%M:%SZ"), "value": v,
                         "unit": "USD/MW-hour", "freq": "PT1H", "geo": "US-TX", "market": "ercot_dam", "node": product,
                         "source": "ercot:NP4-181-ER", "source_url": "https://www.ercot.com/", "retrieved_at": STAMP, "vintage": ""},
                        columns=rb.COLS)


def table_of(df, table, stamp=STAMP):
    """The rows the builder writes for these hours: {(entity, variable without its prefix, period): value}."""
    s = rb.summarize(rb.check_input(df), rb.TABLES[table][1])
    rows = rb.rows_of(s, table, stamp)
    cut = 10 if table == rb.DAILY else 7
    return rows, {(r.entity, r.variable[len("mcpc_dam_"):], r.ts_utc[:cut]): float(r.value) for r in rows.itertuples()}


class TheDay(unittest.TestCase):
    def test_five_rows_a_product_and_day_the_mean_the_lowest_and_the_highest_of_its_hours(self):
        rows, t = table_of(hours("2024-06-05", "2024-06-07", lambda x: x.hour), rb.DAILY)
        self.assertEqual(len(rows), 10)                                                     # two days, five rows each
        for day in ("2024-06-05", "2024-06-06"):
            self.assertEqual((t[("ercot:REGUP", "mean", day)], t[("ercot:REGUP", "min", day)], t[("ercot:REGUP", "max", day)]), (11.5, 0.0, 23.0))
            self.assertEqual((t[("ercot:REGUP", "hours", day)], t[("ercot:REGUP", "hours_in_day", day)]), (24.0, 24.0))
        self.assertEqual(set(rows["freq"]), {"P1D"})
        self.assertEqual(set(rows.loc[rows["variable"].str.contains("hours"), "unit"]), {"count"})
        self.assertEqual(set(rows.loc[~rows["variable"].str.contains("hours"), "unit"]), {"USD/MW-hour"})
        self.assertEqual(set(rows["ts_utc"].str[10:]), {"T00:00:00Z"})                      # the local day as its date
        self.assertEqual((set(rows["market"]), set(rows["node"]), set(rows["geo"]), set(rows["source"])), ({"ercot_dam"}, {"REGUP"}, {"US-TX"}, {rb.SOURCE}))

    def test_the_two_clock_change_days_hold_23_and_25_hours_and_are_whole(self):
        _, t = table_of(pd.concat([hours("2025-03-08", "2025-03-11", 4), hours("2025-11-01", "2025-11-04", 4)]), rb.DAILY)
        want = {"2025-03-08": 24, "2025-03-09": 23, "2025-03-10": 24, "2025-11-01": 24, "2025-11-02": 25, "2025-11-03": 24}
        for day, n in want.items():
            self.assertEqual((t[("ercot:REGUP", "hours", day)], t[("ercot:REGUP", "hours_in_day", day)]), (float(n), float(n)), day)

    def test_a_day_with_missing_hours_is_written_with_its_count_and_is_not_filled(self):
        df = hours("2024-06-05", "2024-06-06", lambda x: 100.0 if x.hour == 17 else 10.0)
        short = df[~df["ts_utc"].isin(["2024-06-05T22:00:00Z", "2024-06-05T23:00:00Z", "2024-06-06T00:00:00Z"])]   # 17:00 to 19:00 local
        _, whole = table_of(df, rb.DAILY)
        _, t = table_of(short, rb.DAILY)
        k = ("ercot:REGUP", "2024-06-05")
        self.assertEqual((t[(k[0], "hours", k[1])], t[(k[0], "hours_in_day", k[1])]), (21.0, 24.0))     # it carries its count
        self.assertEqual(t[(k[0], "mean", k[1])], 10.0)                                     # of the 21 hours held: nothing stands in for the three
        self.assertEqual(t[(k[0], "max", k[1])], 10.0)                                      # the hour at 100 is not held, and not guessed
        self.assertEqual(whole[(k[0], "mean", k[1])], 13.75)
        self.assertEqual(whole[(k[0], "max", k[1])], 100.0)

    def test_the_mean_is_rounded_to_four_decimals_half_up_and_the_extremes_are_as_published(self):
        # 23 hours at 0.1 and one at 0.05: the mean is 0.0979166..., written 0.0979
        _, t = table_of(hours("2024-06-05", "2024-06-06", lambda x: 0.05 if x.hour == 3 else 0.1), rb.DAILY)
        self.assertEqual(t[("ercot:REGUP", "mean", "2024-06-05")], 0.0979)
        self.assertEqual((t[("ercot:REGUP", "min", "2024-06-05")], t[("ercot:REGUP", "max", "2024-06-05")]), (0.05, 0.1))
        self.assertEqual(rb.num(0.00005), "0.0001")                                         # half up, not half to even
        self.assertEqual(rb.num(2.00015), "2.0002")


class TheMonth(unittest.TestCase):
    def test_a_months_mean_is_of_its_hours_not_of_its_daily_means(self):
        # March 2025: 10 on the day the clocks go forward (23 hours), 0 on every other day
        df = hours("2025-03-01", "2025-04-01", lambda x: 10.0 if x.day == 9 else 0.0)
        rows, t = table_of(df, rb.MONTHLY)
        self.assertEqual(len(rows), 5)
        self.assertEqual((t[("ercot:REGUP", "hours", "2025-03")], t[("ercot:REGUP", "hours_in_month", "2025-03")]), (743.0, 743.0))
        self.assertEqual(t[("ercot:REGUP", "mean", "2025-03")], round(230 / 743, 4))        # 0.3096, of the 743 hours
        self.assertNotEqual(t[("ercot:REGUP", "mean", "2025-03")], round(10 / 31, 4))       # 0.3226, the mean of the daily means
        self.assertEqual(set(rows["freq"]), {"P1M"})
        self.assertEqual(set(rows["ts_utc"]), {"2025-03-01T00:00:00Z"})                     # the month as its first local day

    def test_november_has_an_hour_more_and_a_month_is_cut_at_local_midnight(self):
        _, t = table_of(hours("2025-10-31", "2025-12-02", 1), rb.MONTHLY)
        self.assertEqual(t[("ercot:REGUP", "hours_in_month", "2025-11")], 721.0)
        self.assertEqual(t[("ercot:REGUP", "hours", "2025-11")], 721.0)
        self.assertEqual((t[("ercot:REGUP", "hours", "2025-10")], t[("ercot:REGUP", "hours_in_month", "2025-10")]), (24.0, 744.0))
        self.assertEqual((t[("ercot:REGUP", "hours", "2025-12")], t[("ercot:REGUP", "hours_in_month", "2025-12")]), (24.0, 744.0))

    def test_a_product_has_no_row_before_its_first_hour_and_its_first_month_is_short_with_its_count(self):
        # as ECRS, which begins on 10 June 2023; another product is held from the start of May
        df = pd.concat([hours("2023-05-01", "2023-07-01", 5, "RRS"), hours("2023-06-10", "2023-07-01", lambda x: 50.0 if x.day == 20 else 2.0, "ECRS")])
        _, d = table_of(df, rb.DAILY)
        _, m = table_of(df, rb.MONTHLY)
        self.assertNotIn(("ercot:ECRS", "mean", "2023-06-09"), d)                           # absence, never a zero
        self.assertNotIn(("ercot:ECRS", "hours", "2023-06-09"), d)
        self.assertIn(("ercot:ECRS", "mean", "2023-06-10"), d)
        self.assertIn(("ercot:RRS", "mean", "2023-06-09"), d)
        self.assertNotIn(("ercot:ECRS", "mean", "2023-05"), m)
        self.assertEqual((m[("ercot:ECRS", "hours", "2023-06")], m[("ercot:ECRS", "hours_in_month", "2023-06")]), (504.0, 720.0))
        self.assertEqual(m[("ercot:ECRS", "mean", "2023-06")], round((24 * 50 + 480 * 2) / 504, 4))   # of the 504 hours held, not of 720
        self.assertEqual((m[("ercot:RRS", "hours", "2023-06")], m[("ercot:RRS", "hours_in_month", "2023-06")]), (720.0, 720.0))


class TheBuild(unittest.TestCase):
    def test_what_the_builder_refuses(self):
        good = hours("2024-06-05", "2024-06-06", 3)
        rb.check_input(good)
        for change, words in (({"freq": "PT15M"}, "freq"), ({"unit": "USD/MWh"}, "unit"), ({"variable": "spp_dam"}, "variable")):
            with self.assertRaisesRegex(RuntimeError, words + ".*nothing is written"):
                rb.check_input(good.assign(**change))
        empty = good.copy()
        empty.loc[3, "value"] = float("nan")
        with self.assertRaisesRegex(RuntimeError, "no price"):
            rb.check_input(empty)
        with self.assertRaisesRegex(RuntimeError, "duplicate"):
            rb.check_input(pd.concat([good, good.iloc[:1]], ignore_index=True))
        off = good.copy()
        off.loc[0, "ts_utc"] = "2024-06-05T05:30:00Z"
        with self.assertRaisesRegex(RuntimeError, "on the hour"):
            rb.check_input(off)
        with self.assertRaisesRegex(RuntimeError, "no row"):
            rb.check_input(good.iloc[:0])

    def test_an_unchanged_row_keeps_its_stamp_and_a_period_the_input_does_not_hold_is_carried(self):
        _, period, _ = rb.TABLES[rb.DAILY]
        old, _ = table_of(hours("2024-06-03", "2024-06-06", 25), rb.DAILY, "2026-01-01T00:00:00Z")
        new_in = pd.concat([hours("2024-06-05", "2024-06-06", 25), hours("2024-06-06", "2024-06-07", 99)])
        s = rb.summarize(rb.check_input(new_in), period)
        new = rb.rows_of(s, rb.DAILY, "2026-10-07T00:00:00Z")
        seen = pd.MultiIndex.from_arrays([s["entity"], [rb.pb.day_ts(x.date()) for x in s["start"]]])
        out, carried = rb.merge_previous(new, old.assign(value=old["value"].astype(float)), seen, lambda m: None)
        by = {(r.variable, r.ts_utc[:10]): r for r in out.itertuples()}
        self.assertEqual(carried, 10)                                                       # 3 and 4 June, five rows each
        self.assertEqual(by[("mcpc_dam_mean", "2024-06-03")].retrieved_at, "2026-01-01T00:00:00Z")
        self.assertEqual(by[("mcpc_dam_mean", "2024-06-05")].retrieved_at, "2026-01-01T00:00:00Z")   # unchanged: its stamp kept
        self.assertEqual(by[("mcpc_dam_mean", "2024-06-06")].retrieved_at, "2026-10-07T00:00:00Z")   # new
        self.assertFalse(out.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertEqual(len(out), 20)

    def test_a_statistic_is_a_row_and_the_tables_have_no_extra_column(self):
        self.assertEqual(rb.COLS, rb.ip.SERIES_COLS)       # the site's database keeps only these of a series table
        self.assertIn('(["extra"] if shape != "series"', src("warehouse", "supabase", "load.py"))
        self.assertEqual([n for n, _, _ in rb.STATS], ["mean", "min", "max", "hours"])
        self.assertEqual(rb.TABLES, {"ercot_as_prices_daily": ("P1D", "day", "hours_in_day"), "ercot_as_prices_monthly": ("P1M", "month", "hours_in_month")})
        self.assertEqual((rb.SOURCE, rb.UNIT, rb.TZ), ("erw:ercot_as_prices_rollup", "USD/MW-hour", "America/Chicago"))

    def test_the_builder_makes_no_request(self):
        code = src("warehouse", "derived", "ercot_as_prices_rollup.py")
        for word in ("requests", "urllib", "http.client", "gridstatus"):
            self.assertNotIn(word, code)


class TheTrial(unittest.TestCase):
    """The whole builder, from a file of hours made here in a temporary folder to two tables in another."""

    def run_trial(self, df):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        in_dir, out_dir = os.path.join(tmp.name, "in"), os.path.join(tmp.name, "out")
        os.makedirs(in_dir)
        if df is not None:
            with open(os.path.join(in_dir, "ercot_as_prices.csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# hours made by tests/test_session148.py: not data\n")
                df.to_csv(f, index=False, lineterminator="\n")
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(rb.ip, "update_sources") as sources, mock.patch.object(rb.ip, "write_status") as status, \
                redirect_stdout(out), redirect_stderr(err):
            code = rb.main(["--in-dir", in_dir, "--out-dir", out_dir])
        return code, in_dir, out_dir, sources, status, out.getvalue() + err.getvalue()

    def test_a_trial_writes_two_tables_that_pass_the_validator_and_records_nothing(self):
        df = pd.concat([hours("2025-10-30", "2025-11-04", lambda x: x.hour / 4, "REGUP"), hours("2025-11-01", "2025-11-04", 7, "ECRS")])
        df = df[df["ts_utc"] != "2025-11-03T18:00:00Z"]                                     # one hour of each product is not held
        code, in_dir, out_dir, sources, status, said = self.run_trial(df)
        self.assertEqual(code, 0, said)
        sources.assert_not_called()                                                         # no registry row
        status.assert_not_called()                                                          # no run status
        self.assertEqual(sorted(os.listdir(in_dir)), ["ercot_as_prices.csv"])               # nothing is written beside the input
        made = sorted(os.listdir(out_dir))
        self.assertEqual([f for f in made if f.endswith(".csv")], ["ercot_as_prices_daily.csv", "ercot_as_prices_monthly.csv"])
        self.assertEqual(len([f for f in made if f.endswith(".log")]), 1)                   # the trial's log stays with the trial
        self.assertIn("ercot_as_prices_daily.csv: rows=40", said)                           # 5 + 3 product-days, five rows each
        self.assertIn("ercot_as_prices_monthly.csv: rows=15", said)
        with open(os.path.join(out_dir, [f for f in made if f.endswith(".log")][0]), encoding="utf-8") as f:
            log = f.read()
        self.assertIn("short day: ercot_as_prices_daily ercot:ECRS 2025-11-03 holds 23 of 24 hours", log)
        self.assertIn("short day: ercot_as_prices_daily ercot:REGUP 2025-11-03 holds 23 of 24 hours", log)
        self.assertIn("short month: ercot_as_prices_monthly ercot:REGUP 2025-10 holds 48 of 744 hours", log)
        for name, n_short, n in (("ercot_as_prices_daily", 2, 8), ("ercot_as_prices_monthly", 3, 3)):
            path = os.path.join(out_dir, name + ".csv")
            with open(path, encoding="utf-8") as f:
                head = [line for line in f if line.startswith("#")]
            self.assertTrue(any("Never filled" in line and f"{n_short} of the {n} product-" in line for line in head), head)
            self.assertTrue(any(line.startswith("# Derived from: ercot_as_prices") for line in head))
            self.assertFalse(any(tmp_word in "".join(head) for tmp_word in (in_dir, out_dir)))   # no path of this machine in a header
            r = subprocess.run([sys.executable, os.path.join(ROOT, "warehouse", "validate", "erw_validate.py"), path], capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stdout[-800:] + r.stderr[-800:])
        # the same hours again: every row is unchanged and keeps the first run's stamp
        first = pd.read_csv(os.path.join(out_dir, "ercot_as_prices_daily.csv"), comment="#", dtype=str, keep_default_na=False)
        with mock.patch.object(rb.ip, "utc_iso", return_value="2031-01-01T00:00:00Z"), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(rb.main(["--in-dir", in_dir, "--out-dir", out_dir]), 0)
        second = pd.read_csv(os.path.join(out_dir, "ercot_as_prices_daily.csv"), comment="#", dtype=str, keep_default_na=False)
        self.assertTrue(first.equals(second))
        self.assertNotIn("2031-01-01T00:00:00Z", set(second["retrieved_at"]))

    def test_without_the_hourly_table_or_with_one_it_cannot_trust_nothing_is_written(self):
        code, _, out_dir, _, _, said = self.run_trial(None)
        self.assertEqual(code, 1)
        self.assertIn("ercot_as_prices_rollup FAILED", said)
        self.assertEqual([f for f in os.listdir(out_dir) if f.endswith(".csv")], [])
        code, _, out_dir, _, _, said = self.run_trial(hours("2024-06-05", "2024-06-06", 3).assign(unit="USD/MWh"))
        self.assertEqual(code, 1)
        self.assertEqual([f for f in os.listdir(out_dir) if f.endswith(".csv")], [])


@unittest.skipUnless(os.path.exists(hourly_path()), "ercot_as_prices is not on this machine (ERW_TABLES names another copy's warehouse/output)")
class TheTablesFromTheHourlyRows(unittest.TestCase):
    """The two tables built in memory from the hourly table this machine holds, and days and months of them computed
    again from the hourly rows with the csv module and plain Python, without the builder's code or pandas."""

    DAYS = [("ercot:REGUP", "2024-07-15"), ("ercot:RRS", "2025-03-09"), ("ercot:NSPIN", "2025-11-02"), ("ercot:REGDN", "2021-02-15"), ("ercot:ECRS", "2023-06-10")]
    MONTHS = [("ercot:ECRS", "2025-06"), ("ercot:ECRS", "2023-06"), ("ercot:RRS", "2021-02"), ("ercot:REGUP", "2018-01")]

    @classmethod
    def setUpClass(cls):
        df = rb.check_input(rb.ip.read_series(hourly_path(), rb.COLS))
        cls.tables, cls.wide = {}, {}
        for table, (_, period, _) in rb.TABLES.items():
            rows = rb.rows_of(rb.summarize(df, period), table, STAMP)
            cls.tables[table] = rows
            cls.wide[table] = rows.assign(v=rows["value"].astype(float), stat=rows["variable"].str[len("mcpc_dam_"):]).pivot(index=["entity", "ts_utc"], columns="stat", values="v")
        tz, utc = ZoneInfo(TZ), dt.timezone.utc
        cls.by_day, cls.by_month = {k: [] for k in cls.DAYS}, {k: [] for k in cls.MONTHS}
        with open(hourly_path(), encoding="utf-8", newline="") as f:
            for r in csv.DictReader(line for line in f if not line.startswith("#")):
                t = dt.datetime.strptime(r["ts_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=utc).astimezone(tz)
                if (r["entity"], t.strftime("%Y-%m-%d")) in cls.by_day:
                    cls.by_day[(r["entity"], t.strftime("%Y-%m-%d"))].append(Decimal(r["value"]))
                if (r["entity"], t.strftime("%Y-%m")) in cls.by_month:
                    cls.by_month[(r["entity"], t.strftime("%Y-%m"))].append(Decimal(r["value"]))

    def same(self, got, vals, hours_in, in_period):
        self.assertGreater(len(vals), 0)
        dec = lambda x: Decimal(repr(float(x)))  # noqa: E731  (the number as the table writes it)
        self.assertEqual(dec(got["mean"]), (sum(vals) / len(vals)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
        self.assertEqual((dec(got["min"]), dec(got["max"])), (min(vals), max(vals)))
        self.assertEqual((int(got["hours"]), int(got[in_period])), (len(vals), hours_in))

    def test_days_computed_again_from_the_hourly_rows(self):
        tz, utc = ZoneInfo(TZ), dt.timezone.utc
        for (entity, day), vals in self.by_day.items():
            a = dt.datetime.strptime(day, "%Y-%m-%d")
            # two times on one zone subtract as wall clocks in Python: both go to UTC first, so a clock change counts
            span = (a + dt.timedelta(days=1)).replace(tzinfo=tz).astimezone(utc) - a.replace(tzinfo=tz).astimezone(utc)
            with self.subTest(entity=entity, day=day):
                self.same(self.wide[rb.DAILY].loc[(entity, day + "T00:00:00Z")], vals, round(span.total_seconds() / 3600), "hours_in_day")
        self.assertEqual(len(self.by_day[("ercot:RRS", "2025-03-09")]), 23)
        self.assertEqual(len(self.by_day[("ercot:NSPIN", "2025-11-02")]), 25)

    def test_months_computed_again_from_the_hourly_rows(self):
        tz, utc = ZoneInfo(TZ), dt.timezone.utc
        for (entity, month), vals in self.by_month.items():
            a = dt.datetime.strptime(month + "-01", "%Y-%m-%d")
            b = (a.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
            span = b.replace(tzinfo=tz).astimezone(utc) - a.replace(tzinfo=tz).astimezone(utc)
            with self.subTest(entity=entity, month=month):
                self.same(self.wide[rb.MONTHLY].loc[(entity, month + "-01T00:00:00Z")], vals, round(span.total_seconds() / 3600), "hours_in_month")
        self.assertEqual(len(self.by_month[("ercot:ECRS", "2023-06")]), 504)                # the product began on 10 June 2023

    def test_what_every_day_and_month_must_satisfy(self):
        for table, in_period in ((rb.DAILY, "hours_in_day"), (rb.MONTHLY, "hours_in_month")):
            rows, w = self.tables[table], self.wide[table]
            self.assertFalse(rows.duplicated(["entity", "variable", "ts_utc"]).any())
            self.assertEqual(len(rows), 5 * len(w))                                         # five rows a product and period, none missing
            self.assertFalse(w.isna().any().any())
            self.assertTrue(((w["min"] <= w["mean"] + 1e-4) & (w["mean"] <= w["max"] + 1e-4)).all())
            self.assertTrue(((w["hours"] >= 1) & (w["hours"] <= w[in_period])).all())
            self.assertEqual(sorted(rows["entity"].unique()), ["ercot:ECRS", "ercot:NSPIN", "ercot:REGDN", "ercot:REGUP", "ercot:RRS"])
        d = self.wide[rb.DAILY]
        self.assertTrue(d["hours_in_day"].isin([23, 24, 25]).all())
        self.assertEqual(d.reset_index().groupby("entity")["ts_utc"].min()["ercot:ECRS"], "2023-06-10T00:00:00Z")   # no row before it began

    def test_no_day_is_missing_between_a_products_first_and_last_and_a_month_is_the_sum_of_its_days(self):
        d = self.wide[rb.DAILY].reset_index()
        for entity, g in d.groupby("entity"):
            days = pd.to_datetime(g["ts_utc"].str[:10])
            self.assertEqual(len(days), (days.max() - days.min()).days + 1, entity)
        d["month"] = d["ts_utc"].str[:7] + "-01T00:00:00Z"
        by = d.groupby(["entity", "month"]).agg(hours=("hours", "sum"), vmin=("min", "min"), vmax=("max", "max"), in_month=("hours_in_day", "sum"))
        by.index.names = ["entity", "ts_utc"]
        m = self.wide[rb.MONTHLY]
        self.assertEqual(len(by), len(m))
        j = m.join(by, rsuffix="_days")
        self.assertTrue((j["hours"] == j["hours_days"]).all())
        self.assertTrue((j["min"] == j["vmin"]).all() and (j["max"] == j["vmax"]).all())
        whole = j[j["hours"] == j["hours_in_month"]]
        self.assertTrue((whole["hours_in_month"] == whole["in_month"]).all())               # a whole month's hours are its days' hours
        self.assertGreater(len(whole), 0.95 * len(j))


class Stores(unittest.TestCase):
    NAMES = ("ercot_as_prices_daily", "ercot_as_prices_monthly")

    def test_loaded_whole_and_held_out_of_a_visitors_counts(self):
        cfg = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        for name in self.NAMES:
            self.assertTrue(any(re.match(p, name) for p in cfg["full"]), name)
            self.assertFalse(any(re.match(p, name) for p in cfg["recent"]["tables"]), name)   # whole, not 35 days
            self.assertIn(name, cfg["review_hold"])
            self.assertNotIn(name, cfg["catalogue_hold"])
            self.assertNotIn(name, cfg["select"])
        self.assertIn(rb.SOURCE, cfg["sources_hold"])
        self.assertEqual(len(cfg["review_hold"]), len(set(cfg["review_hold"])))
        self.assertEqual(len(cfg["sources_hold"]), len(set(cfg["sources_hold"])))

    def test_the_hourly_table_the_battery_page_reads_is_registered_as_it_was(self):
        cfg = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        self.assertIn("^ercot_as_prices$", cfg["full"])                                      # anchored: the rollup's names do not ride on it
        self.assertNotIn("ercot_as_prices", cfg["review_hold"])
        self.assertNotIn("ercot_as_prices", cfg["catalogue_hold"])
        self.assertFalse(any(re.match(p, "ercot_as_prices") for p in cfg["recent"]["tables"]))
        redivis = yaml.safe_load(src("warehouse", "redivis", "config.yaml"))
        self.assertFalse(any(re.match(p, "ercot_as_prices") for p in redivis["restore_before_run"]))

    def test_the_registry_row_is_the_one_the_builder_writes(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), encoding="utf-8", newline="") as f:
            registry = {r["source"]: r for r in csv.DictReader(f)}
        row = registry[rb.SOURCE]
        self.assertEqual(row["tables"], ";".join(sorted(self.NAMES)))
        self.assertEqual((row["license"], row["report_url"]), ("public", rb.METHOD_URL))
        self.assertIn("docs/methods/ercot_as_prices_rollup.md", row["report"])
        self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "methods", "ercot_as_prices_rollup.md")))

    def test_restored_on_the_runner_and_rebuilt_by_the_daily_run_right_after_the_hourly_table(self):
        cfg = yaml.safe_load(src("warehouse", "redivis", "config.yaml"))
        for name in self.NAMES:
            self.assertTrue(any(re.match(p, name) for p in cfg["restore_before_run"]), name)
        sh = src("warehouse", "run_daily.sh")
        hourly = 'run_other ercot_as_prices "$PYTHON" warehouse/health.py run --strict --step "ercot_as_prices" -- "$PYTHON" warehouse/connectors/ercot_as_prices.py\n'
        line = 'run_other ercot_as_prices_rollup "$PYTHON" warehouse/health.py run --strict --step "ercot_as_prices_rollup" -- "$PYTHON" warehouse/derived/ercot_as_prices_rollup.py\n'
        self.assertEqual(sh.count(line), 1)
        self.assertLess(sh.index(hourly), sh.index(line))
        between = sh[sh.index(hourly) + len(hourly):sh.index(line)]
        self.assertFalse([x for x in between.split("\n") if x.strip() and not x.startswith("#")], between)   # no step between the two
        self.assertLess(sh.index(line), sh.index('echo "== validator"'))

    def test_coverage_gives_both_tables_a_sector(self):
        cov = src("warehouse", "metadata", "build_coverage.py")
        self.assertIn('(r"^ercot_as_prices_(daily|monthly)$", "power")', cov)


class TheNote(unittest.TestCase):
    def test_the_method_says_what_a_reader_does_with_a_short_period(self):
        note = src("docs", "methods", "ercot_as_prices_rollup.md")
        for words in ("## Never filled, and what to do with a short day or month", "mcpc_dam_hours_in_day", "mcpc_dam_hours_in_month", "America/Chicago",
                      "Do not scale it up", "absence, never a", "## Checked by hand", "review_hold", "No migration is needed"):
            self.assertIn(words, note, words)
        self.assertIn("44. **Session 148", src("docs", "datastandard.md"))
        self.assertIn("docs/methods/ercot_as_prices_rollup.md", src("docs", "methods", "capacity_and_ancillary.md"))

    def test_no_em_dash_in_what_the_session_wrote_for_the_rollup(self):
        dash = chr(0x2014)
        for parts in (("warehouse", "derived", "ercot_as_prices_rollup.py"), ("docs", "methods", "ercot_as_prices_rollup.md"), ("docs", "methods", "capacity_and_ancillary.md"),
                      ("docs", "datastandard.md"), ("tests", "test_session148.py"), ("warehouse", "supabase", "live_set.yaml"), ("warehouse", "redivis", "config.yaml"),
                      ("warehouse", "run_daily.sh"), ("warehouse", "metadata", "build_coverage.py")):
            self.assertNotIn(dash, src(*parts), parts)


# ---------------------------------------------------------------------------------------------------------------------
# The site's side of the session: Ask ERCOT reads the two tables, the pages of one large read are asked for together,
# and two switches, off unless the server sets them. No model call and no request: the sources are read here, and the
# session's own tests run in node on recorded reads (site/scripts/test-ask-speed.mjs, extended).


class AskReadsTheRollup(unittest.TestCase):
    def test_the_two_tables_are_offered_beside_the_exported_spec_which_is_untouched(self):
        r = src("site", "lib", "chat", "rollup.ts")
        for words in ('daily: "ercot_as_prices_daily", monthly: "ercot_as_prices_monthly"', "export const MAX_HOURLY_DAYS = 35;", 'return env !== "off";',
                      "Never scale a short period", "a longer one is refused by the tool"):
            self.assertIn(words, r, words)
        e = src("site", "lib", "chat", "ercot.ts")
        self.assertIn("return offered ? { ...profile, system: spec.system + rollupGuide() + addendum(base.slug, base.iso) } : profile;", e)
        self.assertIn("const scope: Scope = !offered ? scope143 :", e)                 # switched off, the scope is session 143's
        self.assertIn("rollup: { hourly: ROLLUP.hourly, tables: ROLLUP_TABLES }", e)
        spec = json.loads(src("site", "lib", "chat", "spec_ercot.json"))
        self.assertNotIn("ercot_as_prices_daily", json.dumps(spec))                      # the Python export is as it was
        self.assertIn("ercot_as_prices", spec["tables"])                                 # and the hourly table is still offered

    def test_the_query_tool_refuses_a_long_hourly_read_only_under_the_profile_and_only_once_the_tables_are_held(self):
        t = src("site", "lib", "chat", "tools.ts")
        self.assertIn("if (scope?.rollup && a.table === scope.rollup.hourly && (await allHeld(scope.rollup.tables))) {", t)
        self.assertIn('return names.every((n) => rows.some((r) => r.table_name === n && (r.in_live_set === "yes" || r.in_live_set === "review")));', t)
        # the refusal comes before the rows are read, and the number of rows one query may read is as it was
        # (session 156: the rows are read by the query's own reader, which asks for a series by its entity first; the read
        # of the rows is still the statement after the refusal, and still of at most MAX_ROWS and one row more)
        self.assertLess(t.index("const why = hourlyRefusal("), t.index("let raw = nothingHeld ? [] : await read(bounds);"))
        self.assertIn("const read = async (bounds: string[], more: Record<string, string> = {}, max = MAX_ROWS + 1): Promise<Json[]> => {", t)
        self.assertIn("const MAX_ROWS = 60_000;", t)

    def test_nothing_the_battery_page_reads_was_changed(self):
        # the live battery page reads battery_stack_monthly and battery_stack_stress_daily; the hourly reserve table is the
        # model's input, and the two new tables are read by Ask ERCOT only
        page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        self.assertEqual(page.count("ercot_as_prices"), 1)                               # the hourly table, named once in its source line, as before
        self.assertNotIn("ercot_as_prices_daily", page)
        self.assertNotIn("ercot_as_prices_monthly", page)
        self.assertNotIn("ercot_as_prices_daily", src("site", "lib", "batterystack.ts"))
        stack = src("warehouse", "derived", "battery_stack.py")
        self.assertNotIn("ercot_as_prices_daily", stack)
        self.assertNotIn("ercot_as_prices_monthly", stack)
        self.assertNotIn("ercot_as_prices_rollup", stack)
        for path in (("site", "lib", "release.ts"),):
            self.assertIn('"/ask/ercot": "review"', src(*path))


class PagesReadTogether(unittest.TestCase):
    def test_the_reader_keeps_the_first_page_alone_the_order_and_the_failure(self):
        s = src("site", "lib", "supabase.ts")
        for words in ("export async function restPaged<T>(", "const first = await page(0);", "if (first.length < PAGE) return rows;",
                      "for (const p of asked) p.catch(() => {});", "const batch = await p;", "if (batch.length < PAGE) return rows;",
                      "return restPaged<T>(table, query, revalidate, max, PAGES_TOGETHER);", "if (building) return 1;"):
            self.assertIn(words, s, words)
        # one page's request, its two retries of a cancelled statement and its error are the lines they were
        for words in ('if (attempt < WAITS.length && res.status === 500 && body.includes("57014")) {', "throw new DataError(`Supabase ${table}: HTTP ${res ? res.status : \"none\"} ${body}`);",
                      "throw new DataError(`Supabase ${table}: request failed (${(e as Error).message})`);", "const BUILD_READS = 2;",
                      "const WAITS = BUILDING ? [1000, 3000, 5000, 8000, 12000] : [1000, 3000];", "const PAGE = 1000;"):
            self.assertIn(words, s, words)
        # required and attempt are as they were
        self.assertIn("if (e instanceof NotConfigured || standIn()) return { ok: false, reason };", s)
        self.assertIn("throw e instanceof DataError ? e : new DataError(reason);", s)

    def test_the_comparison_reads_what_the_three_live_pages_read(self):
        c = src("site", "scripts", "compare-paged-reads.mjs")
        # the battery page's two reads are written in the script as the page writes them
        page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        self.assertIn('return rest<Row>("series", { select: "variable,ts_utc,value", table_name: `eq.${TABLE}`, entity: `eq.${entity}`,', page)
        self.assertIn('return rest<StressRow>("series", { select: "variable,ts_utc,value,event", table_name: `eq.${STRESS_TABLE}`, entity: `eq.${entity}`,', page)
        self.assertEqual(page.count("variable: `like.${x.strat}_${x.dur}h_*`, order: \"variable,ts_utc\" }, HOURLY);"), 2)
        self.assertEqual(page.count("rest<"), 2)                                         # and it makes no other
        self.assertIn('query: { select: "variable,ts_utc,value", table_name: `eq.${stack.TABLE}`, entity: `eq.${g.entity}`, variable: `like.${strat}_${dur}h_*`, order: "variable,ts_utc" }', c)
        self.assertIn('query: { select: "variable,ts_utc,value,event", table_name: `eq.${stack.STRESS_TABLE}`, entity: `eq.${g.entity}`, variable: `like.${strat}_${dur}h_*`, order: "variable,ts_utc" }', c)
        # the storage page's four reads and the network page's are made by the pages' own functions
        storage = src("site", "app", "storage", "page.tsx")
        for words in ("attempt(storageUnits),", 'attempt(() => series("storage_daily_cycle", { since: daysAgo(45) })),',
                      'attempt(() => series("eia930_all_storage", { variable: "net_generation_battery_mw", since: since30 })),',
                      'attempt(() => series("caiso_battery_storage", { variable: "batteries_mw", since: since30 })),', "const since30 = daysAgo(31);"):
            self.assertIn(words, storage, words)
        self.assertEqual(storage.count("attempt("), 4)
        for words in ("data.storageUnits()", 'data.series("storage_daily_cycle", { since: data.daysAgo(45) })', "await net.liveExtras({ hours: committed.hours });",
                      "for (const ba of Object.values(net.ISO_BA)) await net.supplyRows(ba);", "sb.restPaged(r.table, r.query, 0, MAX, 1)", "sb.restPaged(r.table, r.query, 0, MAX, together)"):
            self.assertIn(words, c, words)
        self.assertIn("liveExtras(snap)", src("site", "app", "network", "page.tsx"))
        self.assertIn("supplyRows(ba)", src("site", "app", "network", "page.tsx"))
        release = src("site", "lib", "release.ts")
        for path in ("/cost-of-power/battery", "/network", "/storage"):
            self.assertIn(f'"{path}": "live"', release)

    def test_the_recorded_read_is_three_pages_of_real_rows(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "session148", "paged_reads.json"), encoding="utf-8") as f:
            fx = json.load(f)
        self.assertEqual(len(fx["rows"]), 2424)
        self.assertEqual([p["rows"] for p in fx["pages"].values()], [1000, 1000, 424, 0, 0])
        self.assertEqual(fx["query"]["table_name"], "eq.ercot_as_prices")
        self.assertEqual(sorted(fx["rows"][0]), ["t", "v"])
        self.assertTrue(all(a["t"] < b["t"] for a, b in zip(fx["rows"], fx["rows"][1:])))
        self.assertNotIn("supabase.co", json.dumps(fx))                                 # no address of the database, no key
        if os.path.exists(hourly_path()):                                                # where the hourly table is, the recorded rows are its rows
            want = {}
            with open(hourly_path(), encoding="utf-8", newline="") as f:
                for r in csv.DictReader(l for l in f if not l.startswith("#")):
                    if r["entity"] == "ercot:ECRS" and "2025-06-01T05:00:00Z" <= r["ts_utc"] < "2025-09-10T05:00:00Z":
                        want[r["ts_utc"]] = float(r["value"])
            got = {dt.datetime.fromisoformat(r["t"]).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"): r["v"] for r in fx["rows"]}
            self.assertEqual(got, want)


class TheRuleAndTheSwitches(unittest.TestCase):
    def test_the_plan_made_by_rule_is_off_unless_the_server_sets_it(self):
        # Session 156, the owner's ruling of 8 October 2026: the two switches are set. This test held that the rule ran
        # only under ASK_RULE_PLAN=on; it now holds that the loop asks one function, whose default (on) is in
        # site/lib/chat/switches.ts, and that the server can still turn it off. The test's name is session 148's.
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertIn("if (profile?.plan && profile.writing && profile.resume && rulePlanOn()) {", loop)
        self.assertEqual(loop.count("rulePlanOn()"), 1)
        self.assertNotIn("process.env.ASK_RULE_PLAN", loop)
        self.assertLess(loop.index("rulePlanOn()) {"), loop.index("for (;;) {"))
        switches = src("site", "lib", "chat", "switches.ts")
        self.assertIn('return (given(env.ASK_RULE_PLAN) ?? SWITCH_DEFAULTS.ASK_RULE_PLAN) === "on";', switches)   # "off" on the server is off
        plan = src("site", "lib", "chat", "plan.ts")
        for words in ("if (left.some((w) => !FILLER[shape].has(w))) return null;", "if (products.length + hubs.length + fuels.length !== 1) return null;",
                      "if (bad || periods.length > 1) return null;", "if (!opts.rollup || markets.includes(\"rt\") || stat === \"share\") return null;"):
            self.assertIn(words, plan, words)
        self.assertNotIn("import ", plan)                                                # pure: no model, no request, no table read
        self.assertIn("plan: (question, today, _context, history) => (cleanHistory(history).length ? null : rulePlan(question, today, { rollup: held })),", src("site", "lib", "chat", "ercot.ts"))

    def test_the_rule_writes_the_read_only_and_the_answer_passes_the_checks_it_always_passed(self):
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertEqual(loop.count("const s = settle(draft,"), 1)                       # one writing turn and one check, for the model's read and the rule's
        self.assertEqual(loop.count('const w = await call(writer, "absent", asked, "answered");'), 1)
        self.assertIn('const ruled = await fastWrite("rule");', loop)
        self.assertIn("if (outs.every((o) => !o.isError)) {", loop)                      # an error is not written from
        self.assertIn('messages[0] = { role: "user", content: profile.resume(opening, records) };', loop)   # what is not settled is the model's, as before
        self.assertEqual(loop.count('ledger.push(recordCall(model, resp, raw.request_id, profile ? "site_ask_ercot" : "site_ask", opts.questionId));'), 1)
        self.assertEqual(loop.count("client.messages.stream("), 1)
        for words in ("const bad = unverified(draft.answer, sources);", "const uncited = draft.citations.map((c) => c.table).filter((t) => !tablesRead.has(t));"):
            self.assertIn(words, loop, words)

    def test_lower_effort_is_for_the_reading_turn_only_and_off_unless_set(self):
        loop = src("site", "lib", "chat", "ask.ts")
        # session 156: the reader's effort is "low" unless the server says otherwise (site/lib/chat/switches.ts); it is
        # still the reading turn's only, and a value that is not a setting ("off") still leaves that turn as every other
        self.assertIn('const reader = readerEffort(env);\n  if (role === "planner" && READER_EFFORTS.includes(reader)) return reader;', loop)
        self.assertIn("return env.ASK_WRITER_EFFORT || own;", loop)
        self.assertIn('export const READER_EFFORTS = ["low", "medium", "high"];', loop)
        self.assertIn('const w = await call(writer, "absent", asked, "answered");', loop)   # the writing turn is called as the writer: its effort is as it was
        self.assertEqual(json.loads(src("site", "lib", "chat", "spec_ercot.json"))["effort"], "medium")
        self.assertIn('export const PLANNER = "writer";', src("site", "lib", "chat", "ercot.ts"))   # the model is the one it was

    def test_no_ceiling_and_no_page_status_was_changed(self):
        limits = json.loads(src("site", "lib", "chat", "limits.json"))
        self.assertEqual((limits["daily_usd"], limits["monthly_usd"], limits["per_visitor_per_day"]), (3, 30, 15))
        for f in (("site", "lib", "chat", "rollup.ts"), ("site", "lib", "chat", "plan.ts"), ("site", "lib", "supabase.ts"), ("site", "scripts", "compare-paged-reads.mjs")):
            self.assertNotRegex(src(*f), r"ASK_DAILY_USD|ASK_MONTHLY_USD|ASK_PER_VISITOR")
        release = src("site", "lib", "release.ts")
        self.assertIn('"/ask/ercot": "review"', release)
        self.assertEqual(release.count('": "live"'), 3)                                  # three pages open, as before

    def test_the_method_note_says_what_was_added_and_that_two_are_off(self):
        note = src("docs", "methods", "ask_ercot.md")
        for words in ("### The last seconds (session 148", "ercot_as_prices_daily", "is refused before any row is read", "A plan made by rule (off until measured)",
                      "Lower effort on the reading turn (off until measured)", "44 reads, 40,647 rows, none different"):
            self.assertIn(words, note, words)

    def test_no_em_dash_in_what_the_session_wrote_for_the_site(self):
        dash = chr(0x2014)
        for parts in (("site", "lib", "chat", "rollup.ts"), ("site", "lib", "chat", "plan.ts"), ("site", "lib", "chat", "ask.ts"), ("site", "lib", "chat", "ercot.ts"), ("site", "lib", "chat", "tools.ts"),
                      ("site", "lib", "supabase.ts"), ("site", "scripts", "compare-paged-reads.mjs"), ("site", "scripts", "test-ask-speed.mjs"), ("docs", "methods", "ask_ercot.md"),
                      ("tests", "fixtures", "session148", "paged_reads.json"), ("tests", "fixtures", "session148", "rollup_reads.json")):
            self.assertNotIn(dash, src(*parts), parts)


class TheMeasuredRecord(unittest.TestCase):
    """Phase 2: the 100 questions before and after, as warehouse/chat/eval/ercot_speed_results_148.py wrote them."""
    STAGES = ["planning", "fetching", "drawing", "writing", "other"]
    RULED = ["h01", "h02", "h06", "h07", "h12", "h15", "h16", "h18", "h20", "s01", "s03", "s05", "s08", "s11", "s13", "s14"]

    def rows(self):
        text = src("warehouse", "chat", "eval_ercot_speed_results_148.csv")
        self.assertTrue(any("session 148" in l for l in text.split("\n") if l.startswith("#")))
        return list(csv.DictReader(io.StringIO("\n".join(l for l in text.split("\n") if not l.startswith("#")))))

    def test_all_100_questions_were_asked_before_and_after_and_the_stages_sum_to_the_whole(self):
        rows = self.rows()
        self.assertEqual(len(rows), 100)
        self.assertEqual(len({r["id"] for r in rows}), 100)
        for when in ("before", "after"):
            for r in rows:
                self.assertNotEqual(r[f"{when}_total_ms"], "", r["id"])
                self.assertEqual(sum(int(r[f"{when}_{s}_ms"]) for s in self.STAGES), int(r[f"{when}_total_ms"]), r["id"])
                self.assertIn(r[f"{when}_pass"], ("0", "1"))
        # before: session 143's own record for 77 questions, and this session's run of the same tool for the 23 it left
        runs = [r["before_run"] for r in rows]
        self.assertEqual((sum(x in ("after_sample", "after_rest") for x in runs), runs.count("before23")), (77, 23))
        self.assertEqual({r["after_run"] for r in rows}, {"after100"})
        self.assertAlmostEqual(sum(float(r["before_usd"]) for r in rows if r["before_run"] == "before23"), 0.5201, delta=0.002)

    def test_the_pass_counts_and_the_medians_are_the_ones_the_method_note_gives(self):
        import statistics
        rows = self.rows()
        num = [r for r in rows if r["kind"] in ("chart", "sentence")]
        idea = [r for r in rows if r["kind"] == "conceptual"]
        med = lambda part, when: f'{statistics.median(float(r[f"{when}_seconds_words"]) for r in part):.2f}'  # noqa: E731
        self.assertEqual((sum(int(r["before_pass"]) for r in rows), sum(int(r["after_pass"]) for r in rows)), (100, 98))
        self.assertEqual(sorted(r["id"] for r in rows if r["after_pass"] == "0"), ["h14", "h24"])
        self.assertEqual({r["after_why"] for r in rows if r["after_pass"] == "0"}, {"no series"})
        self.assertEqual((med(num, "before"), med(num, "after")), ("6.20", "4.75"))    # the note writes them to one decimal: 6.2 and 4.8
        self.assertEqual((med(idea, "before"), med(idea, "after")), ("2.30", "2.10"))
        under = lambda part, when, t: sum(float(r[f"{when}_seconds_words"]) < t for r in part)  # noqa: E731
        self.assertEqual((under(num, "before", 5), under(num, "after", 5)), (15, 27))
        self.assertEqual((under(idea, "before", 2), under(idea, "after", 2)), (2, 7))
        note = src("docs", "methods", "ask_ercot.md")
        for words in ("| A question about numbers (50; target 5 seconds) | 50, 48 | 6.2, 4.8 | 15, 27 |", "| An idea (25; target 2 seconds) | 25, 25 | 2.3, 2.1 | 2, 7 |",
                      "So the two switches stay off in the code."):
            self.assertIn(words, note, words)

    def test_the_rule_planned_sixteen_and_lost_none_and_every_reading_turn_was_at_the_lower_effort(self):
        rows = self.rows()
        ruled = [r for r in rows if r["after_planned_by"] == "rule"]
        self.assertEqual(sorted(r["id"] for r in ruled), self.RULED)
        self.assertTrue(all(r["after_pass"] == "1" and r["after_model_calls"] == "1" and r["after_efforts"] == "writer:medium" for r in ruled))
        self.assertEqual(sorted({r["after_plan_shape"] for r in ruled}), ["generation", "hub price", "reserve"])
        for r in rows:
            if r["after_planned_by"] != "rule":
                calls = r["after_efforts"].split(";")
                self.assertEqual(calls[0], "planner:low", r["id"])                       # the first call, and only it, at the lower effort
                self.assertTrue(all(c == "writer:medium" for c in calls[1:]), r["id"])
        h12 = next(r for r in rows if r["id"] == "h12")
        self.assertEqual((h12["before_seconds_words"], h12["after_seconds_words"], h12["before_model_calls"], h12["after_model_calls"]), ("43.9", "2.5", "8", "1"))

    def test_the_two_lost_charts_were_asked_again_with_one_change_off_and_the_switches_stayed_off(self):
        rows = {r["id"]: r for r in self.rows()}
        self.assertIn("reask_effort_off: fail", rows["h14"]["asked_again"])
        self.assertIn("reask_rollup_off: fail", rows["h14"]["asked_again"])              # it fails with the tool's guide as session 143 left it too
        self.assertIn("reask_effort_off: fail", rows["h24"]["asked_again"])
        self.assertIn("reask_rollup_off: pass", rows["h24"]["asked_again"])
        self.assertEqual(sum(1 for r in rows.values() if r["asked_again"]), 2)
        # 98 of 100 is not all 100: session 148 turned neither switch on in the code, and its record (the rows above) says
        # so. Session 156: the owner ruled on 8 October 2026 that both are set, so the code's default is now on, in one
        # place, and each can still be turned off on the server. What this test held of the code is held of that place.
        switches = src("site", "lib", "chat", "switches.ts")
        self.assertIn('export const SWITCH_DEFAULTS = { ASK_RULE_PLAN: "on", ASK_READER_EFFORT: "low" } as const;', switches)
        self.assertIn("THE OWNER'S RULING OF 8 OCTOBER 2026", switches)
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertIn("rulePlanOn()", loop)
        self.assertIn("const reader = readerEffort(env);", loop)
        # and session 143's own record is as it was
        old = src("warehouse", "chat", "eval_ercot_speed_results.csv")
        self.assertTrue(any("session 143" in l for l in old.split("\n") if l.startswith("#")))
        self.assertNotIn(chr(0x2014), src("warehouse", "chat", "eval_ercot_speed_results_148.csv") + src("warehouse", "chat", "eval", "ercot_speed_results_148.py"))


class TheNodeTests(unittest.TestCase):
    def test_the_sessions_own_tests_pass_with_no_request_and_no_switch_set(self):
        node = shutil.which("node")
        if not node or not os.path.isdir(os.path.join(ROOT, "site", "node_modules")):
            self.skipTest("node or the site's packages are not here")
        # the switches of the session are taken out of the child's environment only: this process's is not changed
        env = {k: v for k, v in os.environ.items() if k not in ("ASK_RULE_PLAN", "ASK_READER_EFFORT", "ASK_ROLLUP", "ERW_PAGES_TOGETHER", "NEXT_PHASE")}
        r = subprocess.run([node, "--import", "./scripts/alias-register.mjs", "scripts/test-ask-speed.mjs"], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300, env=env)
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-1500:])
        self.assertIn("13 tests pass", r.stdout)                                         # session 143's, as they were
        self.assertIn("21 tests of session 148 pass", r.stdout)


if __name__ == "__main__":
    unittest.main()
