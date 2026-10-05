"""Session 120: what Texas's batteries did in real time.

The reducer of ERCOT's 60-Day SCED Disclosure (a day of five-minute runs to resource-hours and their four 15-minute
intervals), the node price connector, and the monthly table that sets real-time output beside the day-ahead awards,
on saved real samples. No network. tests/fixtures/session120/ holds rows of ERCOT's own files, unaltered (the storage
file's offer-curve columns left out), three of ERCOT's own price zips whole, and real rows of two ERW tables.
"""
import datetime as dt
import io
import os
import re
import shutil
import sys
import tempfile
import unittest
import zipfile
from decimal import Decimal

import pandas as pd
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("ERW_LOCK_EXEMPT", "1")
for p in ("warehouse/connectors", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, *p.split("/")))
import ercot_rt_spp as spp  # noqa: E402
import ercot_sced_esr as sced  # noqa: E402
import ercot_storage_realtime as rt  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session120")
AUG5, MAR8, FEB5 = dt.date(2026, 8, 5), dt.date(2026, 3, 8), dt.date(2026, 2, 5)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def raw(day):
    df = pd.read_csv(os.path.join(FIX, f"esr_in_sced_{day}.csv"), skiprows=1, dtype=str, keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    return df[sced.KEEP].copy()


def by_hand(df, resource, hour_utc, column="Telemetered Net Output"):
    """The hour's energy of one resource, recomputed without the reducer's code, in exact decimals: each SCED run of
    the day (the day's clock: every stamp in the file) holds until the next one; a resource's MW at a run times the
    part of that run's interval inside the hour."""
    stamp = lambda s: pd.Timestamp(dt.datetime.strptime(s, "%m/%d/%Y %H:%M:%S")).tz_localize("America/Chicago").tz_convert("UTC")  # noqa: E731
    clock = sorted({stamp(s) for s in df["SCED Time Stamp"]})
    day = clock[0].tz_convert("America/Chicago").normalize()
    end = (day + pd.Timedelta(days=1)).tz_convert("UTC")
    nxt = dict(zip(clock, clock[1:] + [end]))
    h0 = pd.Timestamp(hour_utc)
    h1 = h0 + pd.Timedelta(hours=1)
    total = Decimal(0)
    for _, r in df[df["Resource Name"] == resource].iterrows():
        t = stamp(r["SCED Time Stamp"])
        a, b = max(t, h0), min(nxt[t], h1)
        if b > a and r[column] != "":
            total += Decimal(r[column]) * Decimal(int((b - a).total_seconds())) / Decimal(3600)
    return total


class TheReducer(unittest.TestCase):
    def setUp(self):
        self.df = raw("2026-08-05")
        self.out = sced.reduce_day(self.df, None, AUG5)

    def test_a_day_is_one_row_a_resource_and_hour(self):
        self.assertEqual((len(self.out), self.out["resource"].nunique()), (72, 3))
        self.assertEqual(list(self.out.columns), sced.DAY_COLS)
        self.assertEqual((self.out["hour"].min(), self.out["hour"].max()), ("2026-08-05T05:00:00Z", "2026-08-06T04:00:00Z"))   # the Central day, in UTC
        self.assertFalse(self.out.duplicated(["resource", "hour"]).any())

    def test_an_hours_energy_is_erccots_mw_held_to_the_next_run_recomputed_by_hand(self):
        for resource, hour in (("ADL_ESR1", "2026-08-06T01:00:00Z"), ("ADL_ESR1", "2026-08-05T15:00:00Z"), ("ANCHOR_ESR1", "2026-08-06T00:00:00Z"),
                               ("ABINDUST_ESR1", "2026-08-05T05:00:00Z")):
            got = self.out[(self.out["resource"] == resource) & (self.out["hour"] == hour)].iloc[0]
            self.assertAlmostEqual(got["net_output_mwh"], float(by_hand(self.df, resource, hour)), places=9, msg=f"{resource} {hour}")
            self.assertAlmostEqual(got["base_point_mwh"], float(by_hand(self.df, resource, hour, "Base Point")), places=9)
            self.assertAlmostEqual(got["as_ecrs_mwh"], float(by_hand(self.df, resource, hour, "AS Awards ECRS")), places=9)

    def test_the_evening_of_5_august_at_one_battery(self):
        # a 60 MW resource in the hour from 20:00 Central: 41.12 MWh out, most of it in the first three intervals
        x = self.out[(self.out["resource"] == "ADL_ESR1") & (self.out["hour"] == "2026-08-06T01:00:00Z")].iloc[0]
        self.assertEqual(x["runs"], 13)
        self.assertEqual(round(x["net_output_mwh"], 4), 41.1218)
        self.assertEqual([round(x[q], 4) for q in sced.QUARTERS], [12.2518, 14.9983, 13.7709, 0.1008])
        self.assertEqual((x["hsl_mw"], x["soc_start_mwh"]), (60.0, 42.6))

    def test_the_four_intervals_add_up_and_discharge_less_charge_is_the_net(self):
        o = self.out
        self.assertLess((o[sced.QUARTERS].sum(axis=1) - o["net_output_mwh"]).abs().max(), 1e-9)
        self.assertLess((o["discharge_mwh"] - o["charge_mwh"] - o["net_output_mwh"]).abs().max(), 1e-9)
        self.assertTrue((o["discharge_mwh"] >= 0).all() and (o["charge_mwh"] >= 0).all())
        day = o.groupby("resource")[["discharge_mwh", "charge_mwh"]].sum().round(4)
        self.assertEqual(day.loc["ADL_ESR1"].tolist(), [56.2652, 74.0869])

    def test_a_blank_award_is_no_award(self):
        self.assertTrue((self.df["AS Awards REGUP"] == "").any())            # ERCOT leaves the cell empty
        self.assertFalse(self.out["as_regup_mwh"].isna().any())
        x = self.out[(self.out["resource"] == "ADL_ESR1") & (self.out["hour"] == "2026-08-06T01:00:00Z")].iloc[0]
        self.assertEqual(x["as_regup_mwh"], 0.0)

    def test_the_day_the_clocks_go_forward_is_23_hours_and_not_a_gap(self):
        # the first version read ERCOT's Central stamps as they stood and refused 8 March 2026 for "a gap of 65 minutes"
        o = sced.reduce_day(raw("2026-03-08"), None, MAR8)
        self.assertEqual(o["hour"].nunique(), 23)
        self.assertEqual((o["hour"].min(), o["hour"].max()), ("2026-03-08T06:00:00Z", "2026-03-09T04:00:00Z"))
        self.assertEqual(sorted(o["hour"].unique())[1:3], ["2026-03-08T07:00:00Z", "2026-03-08T08:00:00Z"])   # 01:00 CST, then 03:00 CDT
        self.assertTrue(o["runs"].between(11, 13).all())

    def test_a_resource_that_leaves_the_file_is_not_carried_through_the_day(self):
        # 5 February 2026: CHISMGRD_ESR1 is in ERCOT's file until 00:30 and not after. Held to its own next row, its last
        # five minutes would have been 23 hours, and the first version refused the whole day for "a gap of 1410 minutes"
        df = raw("2026-02-05")
        self.assertEqual(int((df["Resource Name"] == "CHISMGRD_ESR1").sum()), 7)
        o = sced.reduce_day(df, None, FEB5)
        self.assertEqual(o.groupby("resource").size().to_dict(), {"ADL_ESR1": 24, "CHISMGRD_ESR1": 1})
        x = o[o["resource"] == "CHISMGRD_ESR1"].iloc[0]
        self.assertEqual((x["hour"], x["runs"]), ("2026-02-05T06:00:00Z", 7))

    def test_an_hour_with_no_run_has_no_row_and_nothing_is_filled(self):
        df = self.df
        t = pd.to_datetime(df["SCED Time Stamp"], format="%m/%d/%Y %H:%M:%S")
        cut = df[~((df["Resource Name"] == "ANCHOR_ESR1") & (t.dt.hour == 14))]
        o = sced.reduce_day(cut, None, AUG5)
        self.assertEqual(o.groupby("resource").size().to_dict(), {"ABINDUST_ESR1": 24, "ADL_ESR1": 24, "ANCHOR_ESR1": 23})
        self.assertNotIn("2026-08-05T19:00:00Z", set(o[o["resource"] == "ANCHOR_ESR1"]["hour"]))
        other = o[o["resource"] == "ADL_ESR1"].reset_index(drop=True)
        base = self.out[self.out["resource"] == "ADL_ESR1"].reset_index(drop=True)
        self.assertLess((other["net_output_mwh"] - base["net_output_mwh"]).abs().max(), 1e-12)   # nobody else moved

    def test_what_stops_a_day(self):
        df = self.df
        for change, word in (
                (lambda d: pd.concat([d, d.iloc[[3]]]), "repeat a resource"),
                (lambda d: d.assign(**{"Resource Type": ["GEN"] + ["ESR"] * (len(d) - 1)}), "resource types"),
                (lambda d: d.assign(**{"Repeated Hour Flag": ["Y"] + ["N"] * (len(d) - 1)}), "repeated hour"),
                (lambda d: d.assign(**{"SCED Time Stamp": ["08/06/2026 00:00:29"] + list(d["SCED Time Stamp"])[1:]}), "the file's days"),
                (lambda d: d.assign(**{"SCED Time Stamp": ["not a time"] + list(d["SCED Time Stamp"])[1:]}), "cannot be read"),
                (lambda d: d[~pd.to_datetime(d["SCED Time Stamp"], format="%m/%d/%Y %H:%M:%S").dt.hour.isin([9, 10])], "a gap of"),
                (lambda d: d.iloc[0:0], "no rows")):
            with self.assertRaises(ValueError, msg=word) as e:
                sced.reduce_day(change(df.copy()), None, AUG5)
            self.assertIn(word, str(e.exception))

    def test_the_table_row(self):
        head = "# 60d_ESR_Data_in_SCED-04-OCT-26.csv in x.zip; https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1282310696; retrieved 2026-10-05T09:15:29Z"
        rows = sced.to_rows("2026-08-05", head, self.out, {"ADL_ESR1": "ADL_RN"})
        self.assertEqual(list(rows.columns), sced.COLS)
        r = rows[(rows["entity"] == "ercot:ADL_ESR1") & (rows["ts_utc"] == "2026-08-06T01:00:00Z")].iloc[0]
        self.assertEqual((r["variable"], r["value"], r["unit"], r["freq"], r["market"], r["node"]), ("net_output_mwh", "41.121847", "MWh", "PT1H", "ercot_rtm", "ADL_RN"))
        self.assertEqual((r["x_net_q1_mwh"], r["x_sced_runs"], r["x_hsl_mw"]), ("12.251828", "13", "60"))
        self.assertEqual(r["vintage"], "2026-10-04T00:00:00Z")                 # ERCOT published it 60 days after the day
        self.assertTrue(r["source_url"].endswith("doclookupId=1282310696"))
        self.assertEqual(rows[rows["entity"] == "ercot:ANCHOR_ESR1"]["node"].iloc[0], "")   # a resource the day-ahead file never names


class TheCeilings(unittest.TestCase):
    def test_a_zip_that_would_pass_12_gb_is_not_requested(self):
        asked = []

        def get(url, **kw):
            asked.append(url)
            raise AssertionError("no request may be made")
        doc = {"ConstructedName": "not_on_this_machine.zip", "DocID": "1", "ContentSize": "60000000", "PublishDate": "2026-10-04T05:08:09-05:00"}
        with self.assertRaises(sced.Ceiling):
            sced.get_zip(doc, AUG5, lambda m: None, False, {"bytes": sced.MAX_BYTES - 1000, "requests": 0}, get=get)
        self.assertEqual(asked, [])
        self.assertEqual((sced.MAX_BYTES, sced.MAX_ROWS), (12_000_000_000, 9_000_000))

    def test_the_operating_day_is_the_day_published_less_sixty(self):
        self.assertEqual(sced.operating_day({"PublishDate": "2026-10-04T05:08:09-05:00"}), AUG5)

    def test_neither_pull_is_on_a_schedule(self):
        # the prompt approved two pulls, not a standing one: nothing scheduled asks ERCOT for these reports
        for f in os.listdir(os.path.join(ROOT, ".github", "workflows")):
            text = src(".github", "workflows", f)
            self.assertNotIn("ercot_sced_esr", text, f)
            self.assertNotIn("ercot_rt_spp", text, f)
        for f in ("run_daily.sh", "run_monthly.sh", "scheduled.py"):
            text = src("warehouse", f)
            self.assertNotIn("ercot_sced_esr", text, f)
            self.assertNotIn("ercot_rt_spp", text, f)

    def test_both_ask_whether_ercot_is_paused_before_a_request(self):
        self.assertIn('ip.paused("ercot")', src("warehouse", "connectors", "ercot_sced_esr.py"))
        self.assertIn('ip.paused("ercot")', src("warehouse", "connectors", "ercot_rt_spp.py"))


class TheNodePrices(unittest.TestCase):
    def files(self):
        return sorted(f for f in os.listdir(FIX) if f.endswith("_csv.zip"))

    def test_one_of_ercots_own_files_is_one_interval(self):
        with open(os.path.join(FIX, self.files()[0]), "rb") as f:
            df, utc = spp.read_interval(f.read())
        # the file is stamped 28 September 00:00: the END of its interval. Its own columns say 27 September, hour 24, interval 4
        self.assertEqual(utc.strftime("%Y-%m-%dT%H:%M:%SZ"), "2026-09-28T04:45:00Z")      # 23:45 Central, the interval's start
        self.assertEqual((len(df), df["SettlementPointName"].nunique()), (1136, 1124))
        self.assertIn("HB_HUBAVG", set(df["SettlementPointName"]))
        self.assertEqual(set(df["DSTFlag"]), {"N"})

    def test_a_load_zone_is_printed_twice_and_the_table_keeps_one_price_for_a_name(self):
        with open(os.path.join(FIX, self.files()[0]), "rb") as f:
            df, _ = spp.read_interval(f.read())
        z = df[df["SettlementPointName"] == "LZ_AEN"]
        self.assertEqual(sorted(z["SettlementPointType"]), ["LZ", "LZEW"])
        pairs = df[df.duplicated(["SettlementPointName"], keep=False)].groupby("SettlementPointName")["SettlementPointPrice"].nunique()
        self.assertEqual((len(pairs), int((pairs > 1).sum())), (12, 4))                    # the two rows are not always one price
        out, _, _ = spp.table(set(), lambda m: None, zips=FIX)
        self.assertFalse(out.duplicated(["entity", "ts_utc"]).any())
        self.assertEqual(set(out["x_point_type"]) & spp.TWICE, set())
        want = z[z["SettlementPointType"] == "LZ"]["SettlementPointPrice"].iloc[0]
        self.assertEqual(out[(out["node"] == "LZ_AEN") & (out["ts_utc"] == "2026-09-28T04:45:00Z")]["value"].iloc[0], want)

    def test_the_table_keeps_the_storage_points_the_hubs_and_the_zones(self):
        with open(os.path.join(FIX, self.files()[0]), "rb") as f:
            df, _ = spp.read_interval(f.read())
        point = sorted(df[df["SettlementPointType"] == "RN"]["SettlementPointName"])[0]
        out, n, bad = spp.table({point}, lambda m: None, zips=FIX)
        self.assertEqual((n, bad), (3, []))
        self.assertEqual(list(out.columns), spp.COLS)
        self.assertEqual(sorted(out["ts_utc"].unique()), ["2026-09-28T04:45:00Z", "2026-09-28T05:00:00Z", "2026-09-28T05:15:00Z"])
        kinds = set(out["x_point_type"])
        self.assertTrue(kinds <= spp.KEEP_TYPES | {"RN"})
        self.assertEqual(set(out[out["x_point_type"] == "RN"]["node"]), {point})
        hub = out[(out["node"] == "HB_HUBAVG") & (out["ts_utc"] == "2026-09-28T04:45:00Z")].iloc[0]
        want = df[df["SettlementPointName"] == "HB_HUBAVG"]["SettlementPointPrice"].iloc[0]
        self.assertEqual((hub["value"], hub["variable"], hub["unit"], hub["freq"]), (want, "spp_rtm", "USD/MWh", "PT15M"))   # as ERCOT prints it

    def test_a_repeated_hour_is_not_written(self):
        with open(os.path.join(FIX, self.files()[0]), "rb") as f:
            z = zipfile.ZipFile(io.BytesIO(f.read()))
        name = z.namelist()[0]
        text = z.read(name).decode("utf-8").replace(",N\r\n", ",Y\r\n").replace(",N\n", ",Y\n")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as w:
            w.writestr(name, text)
        with self.assertRaises(ValueError) as e:
            spp.read_interval(buf.getvalue())
        self.assertIn("repeated hour", str(e.exception))

    def test_the_list_keeps_seven_days_and_the_connector_says_so(self):
        s = src("warehouse", "connectors", "ercot_rt_spp.py")
        self.assertIn("ERCOT's public list keeps seven days of it", s)
        self.assertIn("cannot be had from this list at any ceiling", s)


class TheMonthlyTable(unittest.TestCase):
    def setUp(self):
        out = sced.reduce_day(raw("2026-08-05"), None, AUG5)
        self.s = out.assign(day="2026-08-05", ts_utc=out["hour"])
        # the builder's own reader, on the real rows of the day-ahead table
        self.tmp = tempfile.mkdtemp()
        shutil.copy(os.path.join(FIX, "ercot_dam_esr_awards_sample.csv"), os.path.join(self.tmp, rt.DAM + ".csv"))
        self.d = rt.read_dam("2026-08-05T05:00:00Z", "2026-08-06T04:00:00Z", out_dir=self.tmp)
        hub = pd.read_csv(os.path.join(FIX, "hub_rtm_2026-08-05_sample.csv"), skiprows=1)
        self.hub = hub.set_index("ts_utc")["value"]
        dah = pd.read_csv(os.path.join(FIX, "hub_dam_2026-08-05_sample.csv"), skiprows=1)
        self.d["da_hub_price"] = self.d["ts_utc"].map(dah.set_index("ts_utc")["value"])

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_the_samples_are_a_whole_day(self):
        self.assertEqual((len(self.hub), len(self.d), len(self.s)), (96, 72, 72))

    def test_a_deviation_is_real_time_energy_less_a_quarter_of_the_award_at_each_intervals_price(self):
        m = rt.value_hours(self.s, self.d, self.hub)
        x = m[(m["resource"] == "ADL_ESR1") & (m["ts_utc"] == "2026-08-06T01:00:00Z")].iloc[0]
        self.assertEqual((x["award"], x["da_price"]), (4.1, 41.03))            # ERCOT's day-ahead award and the price at its node
        prices = [self.hub[f"2026-08-06T01:{q:02d}:00Z"] for q in (0, 15, 30, 45)]
        out = sum(x[q] * p for q, p in zip(sced.QUARTERS, prices))
        pos = sum(4.1 / 4 * p for p in prices)
        self.assertAlmostEqual(x["rt_output_hub_usd"], out, places=6)
        self.assertAlmostEqual(x["da_position_hub_usd"], pos, places=6)
        self.assertEqual(x["intervals_priced"], 4)
        self.assertAlmostEqual(x["da_energy_usd"], 4.1 * 41.03, places=9)

    def test_an_interval_with_no_price_is_not_valued_and_is_counted(self):
        m = rt.value_hours(self.s, self.d, self.hub.drop("2026-08-06T01:15:00Z"))
        x = m[(m["resource"] == "ADL_ESR1") & (m["ts_utc"] == "2026-08-06T01:00:00Z")].iloc[0]
        self.assertEqual(x["intervals_priced"], 3)
        full = rt.value_hours(self.s, self.d, self.hub)
        y = full[(full["resource"] == "ADL_ESR1") & (full["ts_utc"] == "2026-08-06T01:00:00Z")].iloc[0]
        self.assertAlmostEqual(y["rt_output_hub_usd"] - x["rt_output_hub_usd"], y["net_q2_mwh"] * self.hub["2026-08-06T01:15:00Z"], places=6)

    def test_the_month_adds_up_and_the_market_figure_is_the_floor_plus_the_deviation(self):
        m = rt.value_hours(self.s, self.d, self.hub)
        mw = self.d.groupby("resource")["da_hsl"].max().sum()
        v = rt.monthly(m, {"2026-08-05"}, {"2026-08": float(mw)})["2026-08"]
        self.assertEqual((v["days_held"], v["days_in_month"], v["resources"], v["resource_hours"]), (1, 31, 3, 72))
        self.assertEqual((v["intervals"], v["intervals_priced"]), (288, 288))
        self.assertEqual(v["rt_discharge_mwh"], round(float(self.s["discharge_mwh"].sum()), 3))
        self.assertEqual(v["da_sold_mwh"], 4.1)                                # one award in the sample: 4.1 MW for an hour
        self.assertEqual(v["rt_deviation_mwh"], round(v["rt_net_mwh"] - v["da_net_mwh"], 3))
        self.assertEqual(v["revenue_da_energy_usd"], round(4.1 * 41.03, 2))
        self.assertAlmostEqual(v["revenue_rt_deviation_hub_usd"], v["revenue_rt_output_hub_usd"] - v["revenue_da_position_hub_usd"], places=2)
        self.assertAlmostEqual(v["revenue_market_hub_usd"], v["revenue_da_usd"] + v["revenue_rt_deviation_hub_usd"], places=2)
        self.assertAlmostEqual(v["revenue_market_hub_usd_per_mw"], v["revenue_market_hub_usd"] / mw, places=3)
        for name in rt.SERVICES:
            self.assertAlmostEqual(v[f"as_imbalance_{name}_mwh"], v[f"as_rt_{name}_mwh"] - v[f"as_da_{name}_mwh"], places=3)

    def test_a_day_one_disclosure_lacks_is_not_a_matched_day(self):
        m = rt.value_hours(self.s, self.d, self.hub)
        self.assertEqual(rt.monthly(m, set(), {"2026-08": 1.0}), {})

    def test_every_hub_priced_variable_says_so_in_its_name(self):
        m = rt.value_hours(self.s, self.d, self.hub)
        v = rt.monthly(m, {"2026-08-05"}, {"2026-08": 100.0})["2026-08"]
        for k in v:
            if "rt_" in k and k.startswith("revenue_") or "market" in k or "position" in k:
                self.assertIn("_hub", k, k)
        self.assertEqual(rt.unit_of("revenue_market_hub_usd_per_mw"), "USD/MW")
        self.assertEqual(rt.unit_of("rt_discharge_mwh"), "MWh")
        self.assertEqual(rt.unit_of("da_node_minus_hub_sold"), "USD/MWh")


class ThePageAndTheHolds(unittest.TestCase):
    def test_the_page_stays_in_review_and_the_live_battery_page_is_not_this_sessions(self):
        rel = src("site", "lib", "release.ts")
        self.assertIn('"/cost-of-power/battery/awards": "review"', rel)
        self.assertIn('"/cost-of-power/battery": "live"', rel)
        page = src("site", "app", "cost-of-power", "battery", "awards", "RealTime.tsx")
        self.assertIn("data-rt-not", page)
        self.assertLess(page.index("data-rt-not"), page.index("data-rt-table"), "what it leaves out is stated first")
        self.assertIsNone(re.search(r">\s*\d+\.\d+\s*<", page), "no figure is written into the section: each is computed from the rows")

    def test_the_new_tables_are_held_out_of_a_visitors_counts(self):
        y = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        self.assertIn("ercot_sced_esr_hourly", y["catalogue_hold"])
        self.assertIn("ercot_rtm_node_prices", y["catalogue_hold"])
        self.assertIn("ercot_storage_rt_monthly", y["review_hold"])
        self.assertIn("ercot_storage_node_basis", y["review_hold"])
        for s in ("ercot:NP3-965-ER", "ercot:NP6-905-CD", "erw:ercot_storage_realtime"):
            self.assertIn(s, y["sources_hold"])

    def test_the_method_cites_the_protocol_sections(self):
        m = src("docs", "methods", "ercot_storage_realtime.md")
        for section in ("6.6.3.1", "6.7.2.1", "4.6.2.1", "4.6.4.1", "6.6.5.5"):
            self.assertIn(section, m)
        self.assertIn("RTRMPRESR", m)                                           # the price a battery's charging is settled at

    def test_no_em_dash_and_miso_is_still_paused(self):
        for parts in (("warehouse", "connectors", "ercot_sced_esr.py"), ("warehouse", "connectors", "ercot_rt_spp.py"),
                      ("warehouse", "derived", "ercot_storage_realtime.py"), ("docs", "methods", "ercot_storage_realtime.md"),
                      ("site", "app", "cost-of-power", "battery", "awards", "RealTime.tsx"), ("site", "lib", "storagerealtime.ts"), ("tests", "test_session120.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts[-1])
        self.assertIn("miso", src("warehouse", "metadata", "paused_sources.csv").lower())


if __name__ == "__main__":
    unittest.main()
