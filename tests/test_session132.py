"""Session 132: the price board and its markets workbench, one page at /board.

Energy Research Warehouse (ERW). The four connectors the session added (EIA's regional retail fuel, crude streams and
plant fuel costs; the Federal Reserve's Treasury yields on FRED; the IMF's commodity prices; California's LCFS credit
price) and the board's builder (warehouse/derived/board_page.py), on real samples saved under tests/fixtures/session132/
and session127/: rows of each publisher's own answer as received on 6 October 2026, and four operating days of ERCOT's
day-ahead and real-time prices as the warehouse held them. Where a test removes or renames a real value it says so: it
tests the arithmetic and writes nothing.
"""
import datetime as dt
import json
import os
import re
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import board_page as bp  # noqa: E402
import carb_lcfs  # noqa: E402
import eia_board as eb  # noqa: E402
import fred_treasury  # noqa: E402
import imf_pcps  # noqa: E402
import price_board as pb  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session132")
FIX127 = os.path.join(ROOT, "tests", "fixtures", "session127")
SITE = os.path.join(ROOT, "site")
D = dt.date
STAMP = ("https://example.invalid/the-address-without-a-key", "2026-10-06T08:18:00Z")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def eia_rows(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        rows = json.load(f)["response"]["data"]
    for r in rows:
        r["_url"], r["_retrieved"] = STAMP
    return rows


def daily127(entity, variable):
    x = pd.read_csv(os.path.join(FIX127, "daily_series_sample.csv"), comment="#")
    x = x[(x["entity"] == entity) & (x["variable"] == variable)]
    return {D.fromisoformat(t[:10]): float(v) for t, v in zip(x["ts_utc"], x["value"])}


def hourly_sample():
    x = pd.read_csv(os.path.join(FIX, "ercot_hub_prices_sample.csv"), comment="#", dtype=str)
    x["value"] = x["value"].astype(float)
    x["ts"] = pd.to_datetime(x["ts_utc"], utc=True)
    return x


class EiaConnector(unittest.TestCase):
    def test_retail_fuel_rows_are_eia_values_unchanged(self):
        part = eb.TABLES["eia_regional_retail_fuel_prices"]["parts"][0]
        rows = eia_rows("eia_gnd_sample.json")
        out, empty = eb.shape_series(part, rows, "weekly")
        self.assertEqual((len(out), empty), (len(rows), 0))
        by = {(r["entity"], r["ts_utc"]): r for r in out}
        us = by[("eia:EMM_EPMR_PTE_NUS_DPG", "2026-09-28T00:00:00Z")]
        raw = next(r for r in rows if r["series"] == "EMM_EPMR_PTE_NUS_DPG" and r["period"] == "2026-09-28")
        self.assertEqual(us["value"], float(raw["value"]))
        self.assertEqual((us["unit"], us["freq"], us["geo"], us["node"], us["variable"]), ("USD/gal", "P1W", "US", "U.S.", "retail_price"))
        self.assertEqual(by[("eia:EMM_EPMR_PTE_SCA_DPG", "2026-09-28T00:00:00Z")]["geo"], "US-CA")      # a state
        self.assertEqual(by[("eia:EMM_EPMR_PTE_R10_DPG", "2026-09-28T00:00:00Z")]["geo"], "")           # a PADD is no state
        self.assertEqual(part["source"], "eia:petroleum/pri/gnd:regional")       # the older table's registry row is left alone

    def test_a_crude_stream_eia_lists_with_no_value_is_not_written(self):
        part = eb.TABLES["eia_crude_stream_prices"]["parts"][0]
        rows = eia_rows("eia_dfp2_sample.json")
        blank = [r for r in rows if r["value"] is None]
        self.assertGreater(len(blank), 0)                         # the two California streams
        out, empty = eb.shape_series(part, rows, "monthly")
        self.assertEqual(empty, len(blank))
        self.assertEqual(len(out), len(rows) - len(blank))
        self.assertTrue(all(r["ts_utc"].endswith("-01T00:00:00Z") and r["freq"] == "P1M" and r["unit"] == "USD/bbl" for r in out))
        names = {r["node"] for r in out}
        self.assertIn("West Texas Intermediate", names)
        self.assertIn("Mars Blend", names)
        self.assertFalse(any("Dollars per Barrel" in n or "First Purchase Price" in n for n in names))

    def test_an_unexpected_unit_stops_the_pull(self):
        part = eb.TABLES["eia_crude_stream_prices"]["parts"][0]
        rows = eia_rows("eia_dfp2_sample.json")
        rows[0] = dict(rows[0], units="$/GAL")                    # a real row with its unit changed, to see the pull refuse it
        with self.assertRaises(RuntimeError):
            eb.shape_series(part, rows, "monthly")

    def test_plant_fuel_costs_zero_is_no_delivery_and_a_negative_cost_is_kept(self):
        part = eb.TABLES["eia_power_plant_fuel_costs"]["parts"][0]
        rows = eia_rows("eia_epod_cost_sample.json")
        out, empty = eb.shape_epod(part, rows, "monthly")
        by = {(r["entity"], r["variable"], r["ts_utc"][:7]): r for r in out}
        us = next(r for r in rows if r["location"] == "US" and r["fueltypeid"] == "COW" and r["period"] == "2026-05")
        self.assertEqual(by[("eia:plant_fuel_cost:US:COW", "cost_per_mmbtu", "2026-05")]["value"], float(us["cost-per-btu"]))
        self.assertEqual(by[("eia:plant_fuel_cost:US:COW", "cost_per_short_ton", "2026-05")]["unit"], "USD/short_ton")
        self.assertEqual(by[("eia:plant_fuel_cost:US:NG", "cost_per_mcf", "2026-05")]["unit"], "USD/Mcf")
        zero = [r for r in rows if r["location"] == "CA" and r["fueltypeid"] == "COW"]
        self.assertTrue(zero and all(float(r["cost"] or 0) == 0 for r in zero))      # EIA's own rows: California's coal costs 0
        self.assertFalse(any(k[0] == "eia:plant_fuel_cost:CA:COW" for k in by))      # so no row is written for it
        nm = by[("eia:plant_fuel_cost:NM:NG", "cost_per_mmbtu", "2026-04")]
        self.assertLess(nm["value"], 0)                                              # a negative cost is EIA's value, kept
        self.assertGreater(empty, 0)
        self.assertTrue(all(r["value"] != 0 for r in out))

    def test_the_ceiling_stops_a_run(self):
        b = eb.Budget()
        self.assertEqual(b.n, eb.EXPLORED)
        b.add(1000)
        with self.assertRaises(RuntimeError):
            b.add(eb.CEILING)
        self.assertEqual(eb.CEILING, 1_500_000)


class OtherConnectors(unittest.TestCase):
    def test_a_market_holiday_in_freds_file_is_not_a_value(self):
        text = src("tests", "fixtures", "session132", "fred_DGS10_sample.csv")
        blanks = [ln for ln in text.splitlines()[1:] if ln.split(",")[1] in ("", ".")]
        self.assertGreaterEqual(len(blanks), 2)                   # Christmas Day and New Year's Day
        t, empty = fred_treasury.parse("DGS10", text, *STAMP)
        self.assertEqual(empty, len(blanks))
        self.assertEqual(len(t), len(text.splitlines()) - 1 - len(blanks))
        self.assertNotIn("2024-12-25T00:00:00Z", set(t["ts_utc"]))
        first = text.splitlines()[1].split(",")
        self.assertEqual(float(t.loc[t["ts_utc"] == first[0] + "T00:00:00Z", "value"].iloc[0]), float(first[1]))
        self.assertEqual(set(t["unit"]), {"pct"})

    def test_imf_rows_by_indicator_and_month(self):
        with open(os.path.join(FIX, "imf_pcps_2026_sample.json"), encoding="utf-8") as f:
            body = json.load(f)
        t, empty = imf_pcps.parse(body, *STAMP)
        self.assertEqual(empty, 0)
        self.assertEqual(set(t["entity"]), {f"imf:PCPS:{c}" for c in imf_pcps.SERIES})
        self.assertEqual(len(t), 40)                               # five commodities, January to August 2026
        ds = body["data"]["dataSets"][0]["series"]
        ind = [v["id"] for v in body["data"]["structures"][0]["dimensions"]["series"][1]["values"]]
        key = next(k for k in ds if ind[int(k.split(":")[1])] == "PURAN")
        want = float(ds[key]["observations"]["7"][0])
        got = t[(t["entity"] == "imf:PCPS:PURAN") & (t["ts_utc"] == "2026-08-01T00:00:00Z")]
        self.assertEqual(float(got["value"].iloc[0]), want)
        self.assertEqual(got["unit"].iloc[0], "USD/lb")
        self.assertEqual(set(t.loc[t["entity"] != "imf:PCPS:PURAN", "unit"]), {"USD/t"})

    def test_carbs_weekly_sheet_as_listed_with_its_one_tuesday(self):
        with open(os.path.join(FIX, "carb_lcfs_weekly_sample.xlsx"), "rb") as f:
            content = f.read()
        # the sample skips from January 2019 to August 2021 to August 2026: the connector refuses a sheet that is not one
        # row a week, so the three stretches are read one at a time
        df = pd.read_excel(os.path.join(FIX, "carb_lcfs_weekly_sample.xlsx"))
        self.assertIn(pd.Timestamp("2021-09-07"), set(pd.to_datetime(df.iloc[:, 0])))      # CARB's own Tuesday
        with self.assertRaises(RuntimeError):
            carb_lcfs.parse(content, *STAMP)
        import io
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(content))
        ws = wb.active
        for row in list(ws.iter_rows(min_row=2)):
            if row[0].value.year != 2026:
                ws.delete_rows(row[0].row)                         # keep the 2026 stretch only: real rows, none changed
        buf = io.BytesIO()
        wb.save(buf)
        t, empty, weeks = carb_lcfs.parse(buf.getvalue(), *STAMP)
        self.assertEqual(weeks, len(df[pd.to_datetime(df.iloc[:, 0]).dt.year == 2026]))
        last = df.iloc[-1]
        got = t[(t["variable"] == "credit_price_weekly_avg") & (t["ts_utc"] == pd.Timestamp(last.iloc[0]).strftime("%Y-%m-%dT00:00:00Z"))]
        self.assertEqual(float(got["value"].iloc[0]), float(last.iloc[1]))
        self.assertEqual(set(t["unit"]), {"USD/tCO2", "tCO2"})
        self.assertEqual(carb_lcfs.workbook_url('<a href="/sites/default/files/2026-09/Weekly%20LCFS%20Credit%20Activity.xlsx">x</a>'),
                         "https://ww2.arb.ca.gov/sites/default/files/2026-09/Weekly%20LCFS%20Credit%20Activity.xlsx")


class Figures(unittest.TestCase):
    def test_henry_hub_as_held(self):
        hh = daily127("eia:henry_hub", "spot_price")
        s = bp.stats(hh, "D")
        self.assertEqual(s["last"], {"t": "2026-09-29", "v": 3.18})
        self.assertEqual(s["moves"]["w"]["ch"], 0.28)
        for k in ("d", "w", "m", "y"):
            m = s["moves"][k]
            self.assertAlmostEqual(m["ch"], 3.18 - hh[D.fromisoformat(m["t"])], places=4)      # a move is the last value less a day actually held
        self.assertEqual(s["spark"]["v"][-1], 3.18)
        self.assertLessEqual(len(s["spark"]["v"]), bp.SPARK_POINTS)
        self.assertEqual(s["avg7"]["n"], len([d for d in hh if D(2026, 9, 22) < d <= D(2026, 9, 29)]))

    def test_a_move_whose_earlier_day_is_missing_is_not_made(self):
        hh = daily127("eia:henry_hub", "spot_price")
        last = max(hh)
        cut = {d: v for d, v in hh.items() if not (last - dt.timedelta(days=7 + bp.SLACK) <= d <= last - dt.timedelta(days=7))}     # real values, a week of them removed
        self.assertIsNone(bp.stats(cut, "D")["moves"]["w"])
        self.assertIsNotNone(bp.stats(cut, "D")["moves"]["y"])

    def test_weekly_and_monthly_series_have_no_daily_move(self):
        monthly = {D(2025 + (m - 1) // 12, (m - 1) % 12 + 1, 1): float(m) for m in range(1, 21)}
        s = bp.stats(monthly, "M")
        self.assertIsNone(s["moves"]["d"])
        self.assertIsNone(s["moves"]["w"])
        self.assertEqual(s["moves"]["m"]["ch"], 1.0)               # against the month before
        self.assertEqual(s["moves"]["y"]["ch"], 12.0)              # against the same month a year before
        self.assertNotIn("avg7", s)
        weekly = {D(2026, 1, 5) + dt.timedelta(days=7 * i): float(i) for i in range(30)}
        s = bp.stats(weekly, "W")
        self.assertIsNone(s["moves"]["d"])
        self.assertEqual(s["moves"]["w"]["ch"], 1.0)
        self.assertEqual(s["range"]["n"], 30)                      # a range needs 26 weekly values
        self.assertIsNone(bp.stats({k: v for k, v in list(weekly.items())[:20]}, "W")["range"])

    def test_spreads_by_their_formulas(self):
        hh, wti = daily127("eia:henry_hub", "spot_price"), daily127("eia:wti_cushing", "spot_price")
        gas, dsl = daily127("eia:EER_EPMRU_PF4_RGC_DPG", "spot_price"), daily127("eia:EER_EPD2DXL0_PF4_RGC_DPG", "spot_price")
        da, rt = daily127("ercot:HB_HUBAVG", "da_mean"), daily127("ercot:HB_HUBAVG", "rt_mean")
        d = D(2026, 9, 29)
        self.assertAlmostEqual(bp.crack(gas, dsl, wti)[d], (2 * gas[d] + dsl[d]) * 42 / 3 - wti[d], places=9)
        self.assertAlmostEqual(bp.spark(da, hh)[d], da[d] - 7.0 * hh[d], places=9)
        self.assertAlmostEqual(bp.implied_heat_rate(da, hh)[d], da[d] / hh[d], places=9)
        sunday = D(2026, 9, 27)                                    # no gas trading day: the newest one up to four days before
        self.assertNotIn(sunday, hh)
        self.assertAlmostEqual(bp.spark(da, hh)[sunday], da[sunday] - 7.0 * hh[D(2026, 9, 25)], places=9)
        self.assertNotIn(max(da), bp.spark(da, hh))                # the newest power day is past EIA's newest gas day by more than four
        self.assertAlmostEqual(bp.minus(da, rt)[d], da[d] - rt[d], places=9)

    def test_the_dark_spread_is_monthly_and_needs_every_day_of_the_month(self):
        da = daily127("ercot:HB_HUBAVG", "da_mean")
        mm = bp.month_means(da)
        aug = [v for d, v in da.items() if (d.year, d.month) == (2026, 8)]
        self.assertEqual(len(aug), 31)
        self.assertAlmostEqual(mm[D(2026, 8, 1)], sum(aug) / 31, places=9)
        self.assertNotIn(D(2026, 10, 1), mm)                       # October has only begun
        short = {d: v for d, v in da.items() if d != D(2026, 8, 15)}       # a real month with one day removed
        self.assertNotIn(D(2026, 8, 1), bp.month_means(short))
        coal = {D(2026, 8, 1): 2.5}
        self.assertAlmostEqual(bp.dark(da, coal)[D(2026, 8, 1)], sum(aug) / 31 - bp.COAL_HEAT_RATE * 2.5, places=9)
        self.assertEqual(set(bp.dark(da, coal)), {D(2026, 8, 1)})  # no coal cost, no dark spread


class Power(unittest.TestCase):
    def test_an_hour_of_real_time_is_the_mean_of_its_four_intervals(self):
        x = hourly_sample()
        h = bp.to_hourly(x)
        hub = h.loc[("ercot:HB_HUBAVG", "rt")]
        self.assertEqual(len(hub), 96)                             # four operating days
        hour = pd.Timestamp("2026-09-30T20:00:00Z")
        four = x[(x["entity"] == "ercot:HB_HUBAVG") & (x["market"] == "ercot_rtm") & (x["ts"] >= hour) & (x["ts"] < hour + pd.Timedelta(hours=1))]
        self.assertEqual(len(four), 4)
        self.assertAlmostEqual(hub[hour], four["value"].mean(), places=9)
        self.assertEqual(len(h.loc[("ercot:HB_HUBAVG", "da")]), 96)

    def test_an_hour_short_of_an_interval_is_not_an_hour_and_its_day_is_not_a_day(self):
        x = hourly_sample()
        gone = x[(x["entity"] == "ercot:HB_HUBAVG") & (x["market"] == "ercot_rtm") & (x["ts_utc"] == "2026-09-30T20:15:00Z")].index
        self.assertEqual(len(gone), 1)
        h = bp.to_hourly(x.drop(gone))                             # the real rows, one interval removed
        hub = h.loc[("ercot:HB_HUBAVG", "rt")]
        self.assertEqual(len(hub), 95)
        self.assertNotIn(pd.Timestamp("2026-09-30T20:00:00Z"), hub.index)
        holidays = pb.nerc_holidays(range(2025, 2028))
        d = bp.daily_of(hub, "America/Chicago", "ercot", holidays)
        self.assertEqual(sorted(d.index), [D(2026, 9, 28), D(2026, 9, 29), D(2026, 10, 1)])        # 30 September is short of an hour
        full = bp.daily_of(bp.to_hourly(x).loc[("ercot:HB_HUBAVG", "rt")], "America/Chicago", "ercot", holidays)
        self.assertEqual(len(full), 4)

    def test_daily_figures_and_the_battery_spread(self):
        x = hourly_sample()
        h = bp.to_hourly(x).loc[("ercot:HB_HUBAVG", "da")]
        d = bp.daily_of(h, "America/Chicago", "ercot", pb.nerc_holidays(range(2025, 2028)))
        day = D(2026, 9, 30)
        hours = h[(h.index >= pd.Timestamp("2026-09-30T05:00:00Z")) & (h.index < pd.Timestamp("2026-10-01T05:00:00Z"))]
        self.assertEqual(len(hours), 24)
        self.assertAlmostEqual(d.loc[day, "mean"], hours.mean(), places=9)
        self.assertAlmostEqual(d.loc[day, "max"] - d.loc[day, "min"], hours.max() - hours.min(), places=9)      # the battery spread
        peak = hours[6:22]                                         # hours ending 7 to 22, a Wednesday
        self.assertAlmostEqual(d.loc[day, "peak"], peak.mean(), places=9)
        self.assertAlmostEqual(d.loc[day, "offpeak"], pd.concat([hours[:6], hours[22:]]).mean(), places=9)

    def test_miso_is_dropped_unread(self):
        x = hourly_sample()
        x = x.assign(entity=x["entity"].str.replace("ercot:HB_WEST", "miso:INDIANA.HUB"))        # real ERCOT rows under MISO's name, to see them dropped
        h = bp.to_hourly(x)
        self.assertEqual(set(h.index.get_level_values(0)), {"ercot:HB_HUBAVG"})
        self.assertNotIn("miso", bp.ISO)
        self.assertNotIn("pjm", bp.ISO)

    def test_the_hourly_file_marks_gaps_and_peak_hours(self):
        x = hourly_sample()
        gone = x[(x["entity"] == "ercot:HB_HUBAVG") & (x["market"] == "ercot_rtm") & (x["ts_utc"] == "2026-09-30T20:15:00Z")].index
        h = bp.to_hourly(x.drop(gone))
        f = bp.hourly_file("ercot-hb-hubavg", "America/Chicago", "ercot", h.loc[("ercot:HB_HUBAVG", "da")], h.loc[("ercot:HB_HUBAVG", "rt")], pb.nerc_holidays(range(2025, 2028)))
        self.assertEqual((f["n"], len(f["da"]), len(f["rt"]), len(f["pk"])), (96, 96, 96, 96))
        i = int(pd.Timestamp("2026-09-30T20:00:00Z").timestamp() // 3600) - f["t0"]
        self.assertIsNone(f["rt"][i])                              # the hour not held is a gap, never a filled value
        self.assertIsNotNone(f["da"][i])
        self.assertEqual(f["pk"].count("1"), 4 * 16)               # four weekdays, sixteen on-peak hours each


class TheBoard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(SITE, "data", "board.json"), encoding="utf-8") as f:
            cls.board = json.load(f)
        cls.rows = {r["id"]: r for r in cls.board["rows"]}

    def test_every_price_row_holds_its_figures(self):
        ok = [r for r in self.board["rows"] if r["status"] == "ok"]
        self.assertGreater(len(ok), 700)
        for r in ok:
            self.assertIn("last", r, r["id"])
            self.assertEqual(set(r["moves"]), {"d", "w", "m", "y"}, r["id"])
            self.assertIn("spark", r, r["id"])
            self.assertLessEqual(len(r["spark"]["v"]), 30, r["id"])
            self.assertIn(r["freq"], ("D", "W", "M"), r["id"])
            self.assertTrue(os.path.exists(os.path.join(SITE, "public", "board", "s", r["id"] + ".json")), r["id"])
            if r["freq"] != "D":
                self.assertIsNone(r["moves"]["d"], r["id"])        # monthly series are shown monthly

    def test_wti_brent_and_the_gap_are_three_rows_and_the_gap_is_their_difference(self):
        wti, brent, gap = self.rows["eia-wti-cushing-spot"], self.rows["eia-brent-spot"], self.rows["erw-brent-minus-wti"]
        self.assertEqual(wti["last"]["t"], brent["last"]["t"])
        self.assertAlmostEqual(gap["last"]["v"], brent["last"]["v"] - wti["last"]["v"], places=4)
        for r in (wti, brent, gap):
            self.assertEqual(r["group"], "crude")
            self.assertIsNotNone(r["moves"]["y"])

    def test_miso_and_pjm_rows_are_listed_and_blank(self):
        miso = [r for r in self.board["rows"] if r["id"].startswith("miso-")]
        pjm = [r for r in self.board["rows"] if r["id"].startswith("pjm-")]
        self.assertEqual((len(miso), len(pjm)), (18, 12))          # eight hubs and five hubs in two markets, one ancillary row and one spread row each
        for r in miso + pjm + [self.rows["miso-spark"], self.rows["pjm-spark"]]:
            self.assertEqual(r["status"], "paused" if "miso" in r["id"] else "licensed", r["id"])
            for k in ("last", "moves", "spark", "range"):
                self.assertNotIn(k, r, r["id"])
        self.assertFalse(any("miso" in f or "pjm" in f for f in os.listdir(os.path.join(SITE, "public", "board", "s"))))
        self.assertFalse(any("miso" in f or "pjm" in f for f in os.listdir(os.path.join(SITE, "public", "board", "h"))))
        self.assertFalse(any(w["grid"] in ("MISO", "PJM") for w in self.board["week"]))
        self.assertFalse(any(s["grid"] in ("MISO", "PJM") for s in self.board["spikes"]))

    def test_greyed_rows_name_the_source_that_would_supply_them(self):
        names = " | ".join(r["label"] for r in self.board["rows"] if r["status"] == "licensed")
        for want in ("Waha", "SoCal Citygate", "Algonquin", "Chicago", "TTF", "JKM", "PJM", "Capacity prices", "Uranium, daily", "Lithium, daily", "Renewable energy credits",
                     "European carbon", "Energy equities", "futures", "Coal spot price"):
            self.assertIn(want, names)
        for r in self.board["rows"]:
            if r["status"] != "ok":
                self.assertTrue(r.get("note"), r["id"])
        curve = [r for r in self.board["rows"] if r.get("curve")]
        self.assertEqual({r["id"] for r in curve}, {"eia-henry-hub-spot", "eia-wti-cushing-spot", "eia-eer-epmru-pf4-y35ny-dpg-spot", "eia-eer-epd2f-pf4-y35ny-dpg-spot"})
        self.assertTrue(all(r["curve"]["status"] == "licensed" and "5 April 2024" in r["curve"]["note"] for r in curve))

    def test_every_spread_carries_its_formula_with_its_stated_heat_rate_or_yield(self):
        f = {r["id"]: r.get("formula", "") for r in self.board["rows"]}
        self.assertIn("7 MMBtu/MWh", f["ercot-hb-hubavg-spark"])
        self.assertIn("Indicative", f["ercot-hb-hubavg-spark"])
        self.assertIn("10.5 MMBtu/MWh", f["ercot-hb-hubavg-dark"])
        self.assertIn("2 x Gulf Coast conventional gasoline + 1 x", f["erw-crack-321-gulf-coast"])
        self.assertIn("highest hourly price - its lowest", f["ercot-hb-hubavg-da-battery"])
        self.assertTrue(f["ercot-hb-hubavg-da-minus-rt"] and f["erw-brent-minus-wti"])
        for g in ("spark", "da_rt", "battery", "oilspreads"):
            self.assertTrue(all(r.get("formula") for r in self.board["rows"] if r["group"] == g and r["status"] == "ok"), g)
        battery = self.rows["ercot-hb-hubavg-da-battery"]
        self.assertIn("avg30", battery)                            # the battery spread with its 30-day average

    def test_the_week_the_markets_page_showed(self):
        week = {w["hub"]: w for w in self.board["week"]}
        self.assertIn("ercot-hb-hubavg", week)
        self.assertTrue({"da_mean_usd", "da_onpeak_mean_usd", "da_offpeak_mean_usd"} <= set(week["ercot-hb-hubavg"]["means"]))
        self.assertTrue(self.board["spikes"])
        self.assertEqual(self.board["spikes"], sorted(self.board["spikes"], key=lambda s: (-s["v"], s["t"])))

    def test_ancillary_services_for_the_four_grids_held(self):
        grids = {r["tags"]["grid"] for r in self.board["rows"] if r["group"] == "as" and r["status"] == "ok"}
        self.assertEqual(grids, {"ERCOT", "CAISO", "NYISO", "SPP"})
        self.assertEqual(self.rows["ercot-regup-mcpc-dam"]["label"], "ERCOT Regulation up")
        self.assertIn("REGUP", self.rows["ercot-regup-mcpc-dam"]["code"])     # the code on hover, the words on the face


class ThePage(unittest.TestCase):
    def test_one_tool_one_page_one_address(self):
        cfg = src("site", "next.config.ts")
        for old in ("/markets", "/board/v3", "/board/v4"):
            self.assertIn(f'{{ source: "{old}", destination: "/board", permanent: true }}', cfg)
        self.assertRegex(src("site", "lib", "release.ts"), r'"/board":\s*"review"')
        self.assertTrue(os.path.exists(os.path.join(SITE, "app", "board", "page.tsx")))
        for gone in (("board", "v3"), ("board", "v4"), ("markets",)):
            self.assertFalse(os.path.exists(os.path.join(SITE, "app", *gone)), gone)
        for kept in ("board-original", "board-v3", "board-v4", "markets"):
            self.assertTrue(os.path.exists(os.path.join(SITE, "app", "_retired", kept, "page.tsx")), kept)       # nothing was deleted
        self.assertNotIn('href: "/markets"', src("site", "lib", "pages.ts"))
        self.assertNotIn("/board/v", src("site", "lib", "audience.ts"))

    def test_the_page_face_carries_no_method(self):
        face = src("site", "components", "board", "BoardView.tsx") + src("site", "components", "board", "Workbench.tsx") + src("site", "app", "board", "page.tsx")
        shown = re.sub(r"(?m)^\s*//.*$", "", face)                 # the code's own comments are not on the page
        for word in ("methodology", "limitation", "disputed", "What is on this board", "<Fold", "SourceLine"):
            self.assertNotIn(word, shown, word)
        self.assertIn('"/data/methods/price_board"', shown)
        self.assertIn('href="/explorer/ercot-peak-premium"', shown)
        lib = src("site", "lib", "board.ts")
        for words in ("paused while terms are reviewed", "licensed source needed", "not held yet", "working on it"):
            self.assertIn(words, lib)

    def test_the_method_note_holds_what_the_page_does_not(self):
        note = src("docs", "methods", "price_board.md")
        for words in ("Session 132", "5 April 2024", "S&P Global", "International Monetary Fund", "www.ca.gov/use", "7.0 MMBtu/MWh", "10.5 MMBtu/MWh", "paused", "eia_power_plant_fuel_costs"):
            self.assertIn(words, note, words)

    def test_the_refresh_is_scheduled_once_a_day_through_the_guard(self):
        # 6 October 2026: the owner had it scheduled (the chain prompt of that day). Until then this test asserted
        # that nothing called the script; it now asserts the one call, under health.py, and the guard on the builder
        sh = src("warehouse", "refresh_board.sh")
        for step in ('--step "eia_board"', '--step "fred_treasury"', '--step "imf_pcps"', '--step "carb_lcfs"', '--step "board_page"'):
            self.assertIn("health.py run " + step, sh)
        self.assertIn('--step "board_page" -- "$PY" warehouse/derived/page_keep.py board', sh)
        for wf in os.listdir(os.path.join(ROOT, ".github", "workflows")):
            self.assertNotIn("refresh_board.sh", src(".github", "workflows", wf), wf)
        daily = src("warehouse", "run_daily.sh")
        call = 'health.py run --step "board" -- bash warehouse/refresh_board.sh'
        self.assertEqual(daily.count(call), 1)
        self.assertLess(daily.index("run_other price_board "), daily.index(call))
        self.assertLess(daily.index("run_other trader_view "), daily.index(call))
        self.assertIn("site/data/board.json site/public/board", src(".github", "workflows", "daily-prices.yml"))

    def test_the_new_tables_are_held_out_of_the_live_set(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
        import load
        for t in ("eia_regional_retail_fuel_prices", "eia_crude_stream_prices", "eia_power_plant_fuel_costs", "fred_treasury_yields", "imf_commodity_prices", "carb_lcfs_credit_prices"):
            self.assertIn(t, load.LIVE["catalogue_hold"])
        for s in ("eia:petroleum/pri/gnd:regional", "fred:h15_treasury_yields", "imf:pcps", "carb:lcfs_weekly_credit_price"):
            self.assertIn(s, load.LIVE["sources_hold"])
        reg = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), dtype=str, keep_default_na=False)
        self.assertIn("eia:petroleum/pri/gnd", set(reg["source"]))                 # the older tables' rows are as they were

    def test_no_em_dash_in_what_the_session_wrote(self):
        for p in (("warehouse", "connectors", "eia_board.py"), ("warehouse", "connectors", "fred_treasury.py"), ("warehouse", "connectors", "imf_pcps.py"),
                  ("warehouse", "connectors", "carb_lcfs.py"), ("warehouse", "derived", "board_page.py"), ("warehouse", "refresh_board.sh"),
                  ("site", "app", "board", "page.tsx"), ("site", "lib", "board.ts"), ("site", "components", "board", "BoardView.tsx"),
                  ("site", "components", "board", "Workbench.tsx"), ("site", "scripts", "check-board.mjs"), ("site", "scripts", "test-board.mjs"),
                  ("site", "scripts", "shot.mjs"), ("docs", "methods", "price_board.md"), ("tests", "test_session132.py")):
            text = src(*p)
            self.assertNotIn(chr(0x2014), text, p)
            self.assertNotIn(chr(0x2013), text, p)


if __name__ == "__main__":
    unittest.main()
