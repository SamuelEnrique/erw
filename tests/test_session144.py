"""Session 144: the curtailment page's numbers (shares, where free energy is, what it is worth).

No request is made and nothing is written under warehouse/output or site/data. Every figure is read from saved real
samples under tests/fixtures/session144, cut from the warehouse's own tables on 7 October 2026:
    caiso/   CAISO's curtailment and output by day and Today's Outlook solar and wind by hour, December 2025 and
             March 2026; the monthly table's rows of December 2025 as the warehouse held them
    spp/     SPP's curtailment by day and EIA-930's hourly wind and solar for SWPP, December 2025; and EIA's hours of
             30 August to 2 September 2018, where its zero-wind hours end
    prices/  CAISO SP15 day-ahead and real-time prices of the week from 13 September 2026 (ten hours below zero), the
             same hours in two tables; and CAISO's curtailment of that week

    python -m unittest tests.test_session144
"""

import os
import shutil
import sys
import tempfile
import unittest
from decimal import Decimal

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import iso_prices as ip  # noqa: E402
import price_compare as pc  # noqa: E402
import curtailment_profile as cp  # noqa: E402
import curtailment_shares as cs  # noqa: E402
import curtailment_worth as cw  # noqa: E402
import free_energy as fe  # noqa: E402

FX = os.path.join(ROOT, "tests", "fixtures", "session144")
PRICE_TABLES = ["iso_hub_prices_history", "iso_dam_hub_prices", "iso_rtm_hub_prices"]
SP15 = "caiso:TH_SP15_GEN-APND"
WEEK = (pd.Timestamp("2026-09-13", tz="UTC"), pd.Timestamp("2026-09-20", tz="UTC"), 168)


def quiet(_):
    pass


def table(sub, name, cols=None):
    p = os.path.join(FX, sub, name + ".csv")
    return pd.read_csv(p, skiprows=ip.header_rows(p), usecols=cols)


def prices():
    return pc.read_prices(os.path.join(FX, "prices"), "2026-09-01", quiet, tables=PRICE_TABLES)


class MonthlySums(unittest.TestCase):
    """The monthly sums equal the daily sums."""

    def test_month_is_the_exact_sum_of_its_days(self):
        monthly = table("caiso", "iso_curtailment_monthly")
        daily = pd.concat([table("caiso", "caiso_curtailment_daily"), table("spp", "spp_curtailment_daily")])
        daily = daily[daily["ts_utc"].str[:7] == "2025-12"]
        checked = 0
        for _, r in monthly.iterrows():
            d = daily[(daily["entity"] == r["entity"]) & (daily["variable"] == r["variable"])]
            self.assertEqual(d["ts_utc"].nunique(), 31, (r["entity"], r["variable"]))
            total = sum((Decimal(str(v)) for v in d["value"]), Decimal(0))
            self.assertAlmostEqual(float(total), r["value"], places=6, msg=(r["entity"], r["variable"]))
            checked += 1
        self.assertEqual(checked, 16)  # eight variables of caiso:ISO and eight of spp:SPP

    def test_share_of_a_whole_month_rests_on_the_monthly_sums(self):
        monthly = table("caiso", "iso_curtailment_monthly")
        cur, outputs = cs.caiso_inputs(os.path.join(FX, "caiso"), quiet)
        r = cs.best_month("2025-12", cs.CAISO_TZ, cur, outputs)
        m = monthly[monthly["entity"] == "caiso:ISO"].set_index("variable")["value"]
        self.assertEqual((r["days_held"], r["hours_held"], r["hours_in_month"]), (31, 744, 744))
        self.assertAlmostEqual(r["curtailed_mwh"], m["curtailed_solar_mwh"] + m["curtailed_wind_mwh"], places=2)
        self.assertAlmostEqual(r["output_mwh"], m["solar_generation_mwh"] + m["wind_generation_mwh"], places=2)
        # the page's figure until now: the same share from the monthly sums
        self.assertAlmostEqual(r["share_pct"], 100 * r["curtailed_mwh"] / (r["curtailed_mwh"] + r["output_mwh"]), places=4)


class Shares(unittest.TestCase):
    def setUp(self):
        self.cur, self.outputs = cs.caiso_inputs(os.path.join(FX, "caiso"), quiet)

    def test_a_share_never_exceeds_100_percent(self):
        for c, o in [(0, 5), (1, 1), (5e6, 1e-3), (163505.3, 7764160.3)]:
            s = cs.share_pct(c, o)
            self.assertTrue(0 <= s <= 100, (c, o, s))
        for c, o in [(None, 5), (5, None), (-1, 5), (5, -1), (0, 0), (float("nan"), 5)]:
            self.assertIsNone(cs.share_pct(c, o), (c, o))
        for month in ("2025-12", "2026-03"):
            for basis, by_day in self.outputs:
                r = cs.month_share(month, cs.CAISO_TZ, self.cur, by_day)
                if "share_pct" in r:
                    self.assertTrue(0 < r["share_pct"] < 100, (month, basis, r))

    def test_no_share_from_an_output_of_nothing(self):
        days = cs.month_days("2025-12")
        r = cs.month_share("2025-12", cs.CAISO_TZ, self.cur, {d: 0.0 for d in days})
        self.assertNotIn("share_pct", r)
        self.assertIn("no share", r["missing"])

    def test_december_2025_two_sources_of_caisos_agree(self):
        by = dict(self.outputs)
        a = cs.month_share("2025-12", cs.CAISO_TZ, self.cur, by["caiso_curtailment_daily"])
        b = cs.month_share("2025-12", cs.CAISO_TZ, self.cur, by["caiso_fuel_supply"])
        self.assertEqual((a["days_held"], b["days_held"]), (31, 31))
        self.assertLess(abs(a["output_mwh"] / b["output_mwh"] - 1), 0.01)   # the workbook and Today's Outlook, within 1 percent
        self.assertLess(abs(a["share_pct"] - b["share_pct"]), 0.01)
        # a tie in hours goes to the first source in the order of preference, whole: never two in one month
        self.assertEqual(cs.best_month("2025-12", cs.CAISO_TZ, self.cur, self.outputs)["basis"], "caiso_curtailment_daily")

    def test_march_2026_was_not_computable_and_now_is(self):
        by = dict(self.outputs)
        # the daily table's output of 2026 is the Daily Renewable Report's, not the workbook's: not used as a denominator
        self.assertEqual([d for d in by["caiso_curtailment_daily"] if d.startswith("2026")], [])
        daily = table("caiso", "caiso_curtailment_daily")
        report = daily[(daily["variable"] == "solar_generation_mwh") & (daily["ts_utc"].str[:7] == "2026-03")]
        self.assertEqual(len(report), 27)  # why the page read "not computable": 27 of the month's 31 days
        r = cs.best_month("2026-03", cs.CAISO_TZ, self.cur, self.outputs)
        self.assertEqual((r["basis"], r["days_held"], r["days_in_month"], r["hours_held"], r["hours_in_month"]), ("caiso_fuel_supply", 30, 31, 720, 743))
        self.assertAlmostEqual(r["share_pct"], 9.3054, places=3)
        # the numerator is cut to the same days as the denominator: 30 days of curtailment, not the month's 31
        held = [d for d in cs.month_days("2026-03") if d in by["caiso_fuel_supply"]]
        self.assertAlmostEqual(r["curtailed_mwh"], sum(self.cur[d] for d in held), places=2)
        self.assertLess(r["curtailed_mwh"], sum(self.cur[d] for d in cs.month_days("2026-03")))

    def test_a_month_under_95_percent_of_its_hours_writes_no_share(self):
        by = dict(dict(self.outputs)["caiso_fuel_supply"])
        for d in ("2026-03-10", "2026-03-11"):   # with the day CAISO's file lacks, 28 of 31 days: 672 of 743 hours, 90.4 percent
            by.pop(d)
        r = cs.month_share("2026-03", cs.CAISO_TZ, self.cur, by)
        self.assertNotIn("share_pct", r)
        self.assertNotIn("curtailed_mwh", r)
        self.assertEqual((r["days_held"], r["hours_held"], r["hours_in_month"]), (28, 672, 743))
        self.assertIn("under 95%", r["missing"])
        self.assertEqual(cs.rows({"caiso": {"2026-03": r}}), [])   # and no row of the table

    def test_a_day_short_of_an_hour_is_not_a_day(self):
        f = table("caiso", "caiso_fuel_supply")
        w = f.pivot_table(index="ts_utc", columns="variable", values="value").dropna()
        w.index = pd.to_datetime(w.index, utc=True)
        s = w.sum(axis=1).sort_index()
        whole = cs.whole_days(s, cs.CAISO_TZ)
        self.assertIn("2025-12-15", whole)
        short = cs.whole_days(s.drop(pd.Timestamp("2025-12-15T20:00:00Z")), cs.CAISO_TZ)
        self.assertNotIn("2025-12-15", short)
        self.assertEqual(len(short), len(whole) - 1)
        self.assertEqual(cs.day_hours("2026-03-08", cs.CAISO_TZ), 23)   # the clock change: a day of 23 hours
        self.assertEqual(cs.day_hours("2025-11-02", cs.CAISO_TZ), 25)
        # the one day of March 2026 the Today's Outlook table does not hold is that day, so the month rests on 30 days
        self.assertEqual([d for d in cs.month_days("2026-03") if d not in whole], ["2026-03-08"])

    def test_spp_share_on_eia_hours_of_the_same_days(self):
        d = table("spp", "spp_curtailment_daily")
        cur = cs.daily_sum(d[d["entity"] == "spp:SPP"], ["curtailed_solar_mwh", "curtailed_wind_mwh"])
        e = table("spp", "swpp_wind_solar_hours")
        e.index = pd.to_datetime(e["ts_utc"], utc=True)
        out = cs.whole_days(cs.wind_solar(e["wind"], e["solar"]), cs.SPP_TZ)
        r = cs.month_share("2025-12", cs.SPP_TZ, cur, out)
        self.assertEqual((r["days_held"], r["hours_held"], r["hours_in_month"]), (31, 744, 744))
        self.assertAlmostEqual(r["output_mwh"], float((e["wind"] + e["solar"]).sum()), places=1)
        self.assertAlmostEqual(r["share_pct"], 9.1506, places=3)
        self.assertLess(r["share_pct"], 100)
        # one hour of EIA's blank: its day is out, and the numerator with it
        e2 = e.copy()
        e2.loc[pd.Timestamp("2025-12-20T18:00:00Z"), "wind"] = float("nan")
        r2 = cs.month_share("2025-12", cs.SPP_TZ, cur, cs.whole_days(cs.wind_solar(e2["wind"], e2["solar"]), cs.SPP_TZ))
        self.assertEqual((r2["days_held"], r2["hours_held"]), (30, 720))
        self.assertAlmostEqual(r["curtailed_mwh"] - r2["curtailed_mwh"], cur["2025-12-20"], places=2)

    def test_eias_zero_wind_hours_are_not_held(self):
        e = table("spp", "swpp_wind_solar_hours_2018")
        e.index = pd.to_datetime(e["ts_utc"], utc=True)
        self.assertEqual(int((e["wind"] == 0).sum()), 24)
        days = cs.whole_days(cs.wind_solar(e["wind"], e["solar"]), cs.SPP_TZ)
        self.assertEqual(sorted(days), ["2018-08-31", "2018-09-01", "2018-09-02"])   # 30 August, all zero wind, is not a day

    def test_rows_of_the_table(self):
        r = cs.best_month("2025-12", cs.CAISO_TZ, self.cur, self.outputs)
        rows = cs.rows({"caiso": {"2025-12": r}})
        self.assertEqual([x["variable"] for x in rows], list(cs.VARS))
        self.assertEqual({x["entity"] for x in rows}, {"caiso:ISO"})
        self.assertEqual({x["unit"] for x in rows}, {"pct", "MWh", "count"})
        self.assertTrue(all(x["ts_utc"] == "2025-12-01T00:00:00Z" and x["freq"] == "P1M" for x in rows))


class FreeEnergy(unittest.TestCase):
    def setUp(self):
        self.x = prices()
        self.loc = fe.location_series(self.x)[SP15]

    def test_an_hour_held_in_two_tables_is_counted_once(self):
        raw = sum(len(table("prices", t)) for t in PRICE_TABLES)
        self.assertEqual(raw, 840 + 168 + 672)   # every row of the week is in two tables
        self.assertEqual(len(self.x), 840)       # and is read once
        self.assertEqual(set(self.x["table"]), {"iso_hub_prices_history"})   # the first table of the list wins
        self.assertEqual((len(self.loc["rt"]), len(self.loc["da"])), (168, 168))
        self.assertTrue(self.loc["rt"].index.is_unique)

    def test_a_negative_price_hour_is_counted_once(self):
        h = self.loc["rt"]
        c = fe.counts(h)
        self.assertEqual(c, {"hours_held": 168, "negative": 10, "under5": int((h < 5).sum())})
        negative, under5 = set(h.index[h < 0]), set(h.index[h < fe.THRESHOLD])
        self.assertTrue(negative <= under5)                      # a negative hour is an hour under 5
        self.assertEqual(c["under5"], len(under5))               # and the hours under 5 hold it once
        self.assertEqual(c["under5"] - c["negative"], len(under5 - negative))
        self.assertGreater(c["under5"], c["negative"])           # the week has hours from zero to under 5 too
        twice = pd.concat([h, h])                                # the same hours handed in twice
        self.assertEqual(fe.counts(twice), c)

    def test_an_hour_of_real_time_needs_its_four_quarters(self):
        x = self.x
        drop = x[(x["side"] == "rtm") & (x["ts"] == pd.Timestamp("2026-09-15T20:15:00Z"))].index
        self.assertEqual(len(drop), 1)
        short = fe.location_series(x.drop(drop))[SP15]["rt"]
        self.assertEqual(len(short), 167)
        self.assertNotIn(pd.Timestamp("2026-09-15T20:00:00Z"), short.index)
        q = x[(x["side"] == "rtm") & (x["ts"] >= "2026-09-15T21:00:00Z") & (x["ts"] < "2026-09-15T22:00:00Z")]["value"]
        self.assertAlmostEqual(self.loc["rt"][pd.Timestamp("2026-09-15T21:00:00Z")], q.mean(), places=9)

    def test_a_window_under_95_percent_has_a_reason_and_no_count(self):
        sides = {k: self.loc[k] for k in ("rt", "da")}
        w = fe.window_of(sides, *WEEK)
        self.assertEqual((w["basis"], w["hours_held"], w["negative"]), ("rt", 168, 10))
        month = fe.bounds(["2026-09"], 8)
        m = fe.window_of(sides, *month)
        self.assertNotIn("under5", m)
        self.assertNotIn("negative", m)
        self.assertIn("168 of 720", m["missing"])
        # real time first; day-ahead only when real time does not hold the window
        da_only = fe.window_of({"rt": self.loc["rt"].iloc[:100], "da": self.loc["da"]}, *WEEK)
        self.assertEqual(da_only["basis"], "da")

    def test_the_heatmap_adds_up_to_the_counts(self):
        h = self.loc["rt"]
        heat = fe.heat_of(h, ["2026-08", "2026-09"], 8)
        tot = lambda k: sum(sum(r) for r in heat[k])  # noqa: E731
        self.assertEqual((tot("held"), tot("negative"), tot("under5")), (168, 10, fe.counts(h)["under5"]))
        self.assertEqual(sum(heat["held"][0]), 0)   # August: no hour held, so no count, and held says 0
        self.assertTrue(all(n <= u <= d for rn, ru, rd in zip(heat["negative"], heat["under5"], heat["held"]) for n, u, d in zip(rn, ru, rd)))
        # standard time: 20:00 UTC is 12:00 in California's standard time all year
        one = fe.heat_of(h[h.index == pd.Timestamp("2026-09-15T20:00:00Z")], ["2026-09"], 8)
        self.assertEqual(one["held"][0][12], 1)

    def test_miso_has_no_number(self):
        # the reader's own rule, proved on a name: CAISO's real rows of the fixture, renamed as a MISO hub in a temporary
        # copy, never reach a count. No MISO price is read, here or anywhere in this file.
        tmp = tempfile.mkdtemp()
        try:
            for t in PRICE_TABLES:
                d = table("prices", t)
                d = pd.concat([d, d.assign(entity="miso:INDIANA.HUB")])
                with open(os.path.join(tmp, t + ".csv"), "w", encoding="utf-8", newline="") as f:
                    f.write("# a temporary copy for a test\n")
                    d.to_csv(f, index=False, lineterminator="\n")
            x, blank, _ = fe.read(tmp, "2026-09-01", quiet)
        finally:
            shutil.rmtree(tmp)
        self.assertEqual(set(x["entity"]), {SP15})
        self.assertEqual(blank["miso"], {"name": "MISO", "words": "paused while terms are reviewed", "regions": ["INDIANA.HUB"]})
        self.assertEqual(blank["pjm"], {"name": "PJM", "words": "licensed source needed", "regions": []})
        view = fe.build(x, "2026-09", blank, quiet)
        self.assertNotIn("miso", view["grids"])
        self.assertNotIn("pjm", view["grids"])
        self.assertFalse(any(ch.isdigit() for ch in str(view["blank"])))
        self.assertTrue(all(L["lat"] is None and L["lon"] is None for g in view["grids"].values() for L in g["locations"]))

    def test_gap_and_pair_over_the_same_hours(self):
        rt, da = self.loc["rt"], self.loc["da"]
        # two real series of the same place (real time and day-ahead) stand in for two places: the arithmetic only
        g = fe.gap_of({"A": {"rt": rt}, "B": {"rt": da.iloc[:165]}}, *WEEK)
        self.assertEqual(g["hours_common"], 165)
        idx = rt.index.intersection(da.iloc[:165].index)
        self.assertAlmostEqual(g["gap"], abs(round(float(rt.reindex(idx).mean()), 2) - round(float(da.reindex(idx).mean()), 2)), places=2)
        self.assertIn("missing", fe.gap_of({"A": {"rt": rt}}, *WEEK))
        p = fe.pair_of({"rt": rt}, {"rt": da}, *WEEK)
        self.assertEqual(p["hours_common"], 168)
        self.assertEqual(p["a"]["negative"], 10)
        self.assertIn("missing", fe.pair_of({"rt": rt}, None, *WEEK))


class Worth(unittest.TestCase):
    def setUp(self):
        self.t = table("prices", "caiso_curtailment_intervals")
        self.h = cp.hourly_curtailment(self.t).groupby("ts")["mwh"].sum()
        self.p = fe.location_series(prices())[SP15]["rt"]
        idx = pd.date_range(WEEK[0], WEEK[1], freq="h", inclusive="left")
        self.c = self.h.reindex(idx).fillna(0.0)

    def test_value_is_mwh_times_the_hours_price(self):
        r = cw.value_of(self.c, self.p)
        self.assertEqual((r["hours"], r["hours_priced"]), (168, 168))
        self.assertAlmostEqual(r["value_usd"], round(float((self.c * self.p).sum()), 0), places=0)
        self.assertAlmostEqual(r["usd_per_mwh_curtailed"], float((self.c * self.p).sum()) / float(self.c.sum()), places=2)
        self.assertLessEqual(r["share_mwh_negative_pct"], r["share_mwh_under5_pct"])   # the MWh under 5 hold the MWh below zero
        self.assertLessEqual(r["share_mwh_under5_pct"], 100)
        self.assertAlmostEqual(r["share_mwh_negative_pct"], 100 * float(self.c[self.p < 0].sum()) / float(self.c.sum()), places=2)
        self.assertAlmostEqual(r["price_all_hours_mean"], float(self.p.mean()), places=2)
        self.assertAlmostEqual(r["price_curtailed_hours_mean"], float(self.p[self.c > 0].mean()), places=2)

    def test_an_hour_with_no_price_is_left_out_not_priced(self):
        p = self.p.drop(self.p.index[self.c.values.argmax()])   # the hour with the most curtailed
        r = cw.value_of(self.c, p)
        self.assertEqual(r["hours_priced"], 167)
        self.assertAlmostEqual(r["curtailed_mwh"] - r["curtailed_mwh_priced"], float(self.c.max()), places=1)

    def test_the_week_adds_up_to_caisos_days(self):
        days = self.t[self.t["freq"] == "P1D"]
        whole = sorted(cp.covered_days(self.t))
        local = self.h.index.tz_convert("America/Los_Angeles").strftime("%Y-%m-%d")
        for d in whole[1:-1]:   # the Pacific days wholly inside the cut
            day = float(days[days["ts_utc"].str[:10] == d]["value"].sum())
            self.assertAlmostEqual(float(self.h[local == d].sum()), day, places=1, msg=d)

    def test_a_battery_takes_in_one_cycle_a_day_at_most(self):
        iv = pd.DataFrame({"ts": self.h.index, "mwh": self.h.values, "dur": 1.0})
        iv = iv[iv["mwh"] > 0]
        prev = None
        for d in cw.DURATIONS:
            by_day = cw.absorbed(iv, 1.0, d, "America/Los_Angeles")
            self.assertTrue((by_day <= d + 1e-9).all())
            self.assertLessEqual(by_day.sum(), iv["mwh"].sum())
            if prev is not None:
                self.assertGreaterEqual(by_day.sum(), prev)
            prev = by_day.sum()
        # at 1 MW an interval gives its curtailed MWh when that is under 1 MWh, and 1 MWh when over
        one = iv.iloc[[0]]
        self.assertAlmostEqual(float(cw.absorbed(one, 1.0, 8, "America/Los_Angeles").sum()), min(1.0, float(one["mwh"].iloc[0])), places=9)
        # a fleet large enough takes in everything curtailed, and never more
        big = cw.absorbed(iv, 1e6, 8, "America/Los_Angeles")
        self.assertAlmostEqual(float(big.sum()), float(iv["mwh"].sum()), places=6)


if __name__ == "__main__":
    unittest.main()
