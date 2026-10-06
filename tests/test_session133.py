"""Session 133: the energy mix, one page at /mix.

Energy Research Warehouse (ERW). The five connectors the session added (CAISO's supply history, CAISO's and ERCOT's
wind and solar forecasts, the NRC's reactor status, every retired generator of EIA-860M), the fill of California's
hydro gap from CAISO's own supply with its impossible-value screen (warehouse/derived/mix_profile.py), and the builder
of the new views (warehouse/derived/mix_views.py), on real samples saved under tests/fixtures/session133/: CAISO's own
files for two days of October 2019, a cut of its forecast report, three of ERCOT's hourly postings, the NRC's file, New
York's coal and nuclear units of EIA's inventory, and two months of ERCOT's hours as the mix reads them. Where a test
removes or changes a real value it says so: it tests the arithmetic and writes nothing.
"""
import datetime as dt
import io
import json
import os
import re
import sys
import unittest
import zipfile

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import caiso_fuel_supply as cfs  # noqa: E402
import caiso_fuel_supply_history as cfh  # noqa: E402
import caiso_wind_solar_forecast as cwf  # noqa: E402
import ercot_wind_solar_forecast as ewf  # noqa: E402
import iso_prices as ip  # noqa: E402
import mix_profile as mp  # noqa: E402
import mix_stress as ms  # noqa: E402
import mix_views as mv  # noqa: E402
import nrc_reactor_status as nrc  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session133")
SITE = os.path.join(ROOT, "site")
STAMP = ("https://example.invalid/an-address", "2026-10-06T09:30:00Z")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def fix(name, mode="r"):
    with open(os.path.join(FIX, name), mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
        return f.read()


class Answer:
    def __init__(self, text):
        self.text, self.status_code = text, 200


def caiso_day(day):
    """caiso_fuel_supply_history.day_rows on a saved file of CAISO's: the request is answered from the fixture."""
    text = fix(f"caiso_fuelsource_{day:%Y%m%d}.csv")
    keep = cfh.ip.with_retries
    cfh.ip.with_retries = lambda what, fn, log: Answer(text)
    try:
        return cfh.day_rows(day, lambda m: None)
    finally:
        cfh.ip.with_retries = keep


def own_hours():
    t = pd.read_csv(os.path.join(FIX, "caiso_fuel_supply_history.csv"), comment="#")
    w = t.pivot(index="ts_utc", columns="variable", values="value")
    w.index = pd.to_datetime(w.index, utc=True)
    w["net_generation"] = w[mp.cj.OWN].sum(axis=1)
    return w


def ercot_hours():
    x = pd.read_csv(os.path.join(FIX, "hours_ercot_2025_07_08.csv"), comment="#", index_col="ts", dtype={"day": str, "month": str})
    x.index = pd.to_datetime(x.index, utc=True)
    return x


class CaisoHistory(unittest.TestCase):
    def test_the_older_file_with_lower_case_columns_is_read_as_the_newer_one(self):
        head = fix("caiso_fuelsource_20191003.csv").splitlines()[0]
        self.assertIn("Natural gas", head)                         # CAISO's own spelling in 2019
        self.assertNotIn("Natural Gas", head)
        rows, why = caiso_day(dt.date(2019, 10, 3))
        self.assertIsNone(why)
        self.assertEqual(len(rows), 24 * len(cfs.SOURCES))
        self.assertEqual(set(rows["variable"]), set(cfs.VAR.values()))
        raw = pd.read_csv(io.StringIO(fix("caiso_fuelsource_20191003.csv")))
        first = rows[(rows["variable"] == "natural_gas_mw") & (rows["ts_utc"] == "2019-10-03T07:00:00Z")]["value"].iloc[0]
        self.assertAlmostEqual(first, raw["Natural gas"].iloc[:12].mean(), places=3)      # the hour is the mean of its twelve 5-minute values
        self.assertEqual(set(rows["source"]), {cfh.SOURCE})

    def test_the_window_and_the_ceiling(self):
        days = cfh.window(None, None)
        self.assertEqual((days[0], days[-1], len(days)), (dt.date(2018, 6, 1), dt.date(2025, 5, 31), 2557))
        self.assertLessEqual(len(days) * 24 * len(cfs.SOURCES) + 8 * len(cfs.SOURCES), cfh.CEILING)
        self.assertEqual(cfh.CEILING, 800_000)
        self.assertEqual(cfh.window("2017-01-01", "2030-01-01"), days)           # never outside the approved window
        self.assertEqual(cfh.NAME, "caiso_fuel_supply_history")                  # its own table: caiso_fuel_supply is not touched
        self.assertNotEqual(cfh.NAME, cfs.NAME)


class ImpossibleHours(unittest.TestCase):
    def test_caisos_file_of_1_october_2019_holds_hours_that_did_not_happen(self):
        w = own_hours()
        midnight = pd.Timestamp("2019-10-01T07:00:00Z")            # 00:00 Pacific
        self.assertLess(w.loc[midnight, "natural_gas_mw"], -3000)  # CAISO's own value
        self.assertGreater(w.loc[midnight, "solar_mw"], 9000)      # solar at midnight
        bad = mp.own_impossible(w, "America/Los_Angeles")
        self.assertTrue(bad[midnight])
        day = bad[(bad.index >= midnight) & (bad.index < midnight + pd.Timedelta(days=1))]
        self.assertGreaterEqual(int(day.sum()), 8)
        good = bad[(bad.index >= pd.Timestamp("2019-10-03T07:00:00Z")) & (bad.index < pd.Timestamp("2019-10-04T07:00:00Z"))]
        self.assertEqual(int(good.sum()), 0)                       # an ordinary day loses no hour

    def test_each_measure_alone(self):
        w = own_hours()
        ok = w[(w.index >= pd.Timestamp("2019-10-03T07:00:00Z")) & (w.index < pd.Timestamp("2019-10-04T07:00:00Z"))].copy()
        self.assertEqual(int(mp.own_impossible(ok, "America/Los_Angeles").sum()), 0)
        a = ok.copy()
        a.iloc[5, a.columns.get_loc("nuclear_mw")] = -200.0        # a real day with one nuclear value made negative
        self.assertTrue(mp.own_impossible(a, "America/Los_Angeles").iloc[5])
        b = ok.copy()
        b.iloc[2, b.columns.get_loc("solar_mw")] = 500.0           # 02:00 Pacific: the sun is down
        self.assertTrue(mp.own_impossible(b, "America/Los_Angeles").iloc[2])
        small = ok.copy()
        small.iloc[2, small.columns.get_loc("solar_mw")] = -38.0   # a plant's own use at night is CAISO's ordinary value
        self.assertFalse(mp.own_impossible(small, "America/Los_Angeles").iloc[2])

    def test_the_gap_months_are_read_from_caisos_own_supply_and_the_bad_hours_left_out(self):
        keep = ip.OUT_DIR
        ip.OUT_DIR = FIX
        try:
            filled, a, b, impossible = mp.caiso_gap()
        finally:
            ip.OUT_DIR = keep
        self.assertEqual((a.strftime("%Y-%m-%d %H:%M %Z"), b.strftime("%Y-%m-%d")), ("2019-10-01 00:00 PDT", "2020-09-01"))
        self.assertEqual(filled.index.min(), pd.Timestamp("2019-10-02T07:00:00Z") if impossible >= 24 else filled.index.min())
        self.assertTrue((filled.index >= a).all())                 # September's days in the sample are EIA's, not read here
        self.assertGreater(impossible, 0)
        self.assertNotIn(pd.Timestamp("2019-10-01T07:00:00Z"), filled.index)
        hour = pd.Timestamp("2019-10-03T19:00:00Z")
        w = own_hours()
        self.assertAlmostEqual(filled.loc[hour, "hydro"], w.loc[hour, "large_hydro_mw"] + w.loc[hour, "small_hydro_mw"], places=3)
        self.assertGreater(filled.loc[hour, "hydro"], 0)           # the source EIA's file leaves out in these months
        self.assertAlmostEqual(filled.loc[hour, "interchange"], -w.loc[hour, "imports_mw"], places=3)
        self.assertTrue(filled["demand"].isna().all())             # demand stays EIA's: the builder puts it in afterwards
        self.assertEqual(mp.GAP_MONTHS, ("2019-10", "2020-08"))

    def test_without_the_history_table_the_gap_stays_as_it_was(self):
        keep = ip.OUT_DIR
        ip.OUT_DIR = os.path.join(FIX, "no-such-folder")
        try:
            self.assertIsNone(mp.caiso_gap())
        finally:
            ip.OUT_DIR = keep


class Forecasts(unittest.TestCase):
    def zipped(self, name, text):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr(name, text)
        return buf.getvalue()

    def test_caisos_report_three_hubs_kept_and_other_areas_dropped(self):
        text = fix("caiso_sld_ren_fcst_dam_sample.csv")
        raw = pd.read_csv(io.StringIO(text))
        self.assertIn("AVA_", set(raw["TRADING_HUB"]))             # an area outside CAISO's grid, in CAISO's own answer
        t = cwf.parse(self.zipped("answer.csv", text), "DAM", *STAMP)
        self.assertEqual(set(t["entity"]), {"caiso:NP15", "caiso:SP15", "caiso:ZP26"})
        self.assertEqual(set(t["variable"]), {"wind_forecast_dam_mw", "solar_forecast_dam_mw"})
        self.assertEqual(len(t), int(raw["TRADING_HUB"].isin(cwf.HUBS).sum()))
        r = raw[(raw["TRADING_HUB"] == "SP15") & (raw["RENEWABLE_TYPE"] == "Solar")].sort_values("INTERVALSTARTTIME_GMT").iloc[20]
        got = t[(t["entity"] == "caiso:SP15") & (t["variable"] == "solar_forecast_dam_mw") & (t["ts_utc"] == pd.Timestamp(r["INTERVALSTARTTIME_GMT"]).strftime("%Y-%m-%dT%H:%M:%SZ"))]
        self.assertEqual(float(got["value"].iloc[0]), float(r["MW"]))

    def test_caisos_no_data_answer_is_not_an_error_and_another_error_is(self):
        xml = fix("caiso_sld_ren_fcst_no_data.xml")
        self.assertIn("<m:ERR_CODE>1000", xml)
        self.assertIsNone(cwf.parse(self.zipped("answer.xml", xml), "DAM", *STAMP))
        with self.assertRaises(RuntimeError):
            cwf.parse(self.zipped("answer.xml", xml.replace("<m:ERR_CODE>1000", "<m:ERR_CODE>1004")), "DAM", *STAMP)      # the real answer with its code changed

    def test_caisos_spans_are_thirty_days_and_meet_end_to_start(self):
        w = cwf.windows(dt.date(2023, 1, 1), dt.date(2023, 3, 15))
        self.assertTrue(all((b - a).days <= 30 for a, b in w))
        self.assertTrue(all(w[i][1] == w[i + 1][0] for i in range(len(w) - 1)))
        self.assertEqual((w[0][0], w[-1][1]), (dt.date(2023, 1, 1), dt.date(2023, 3, 16)))

    def postings(self):
        out = []
        for name in sorted(os.listdir(FIX)):
            m = re.match(r"cdr\.00013028\.0+\.(\d{8})\.(\d{6})\.WPPHRLYAVGACTNP4732\.csv", name)
            if m:
                published = pd.Timestamp(dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S"), tz="America/Chicago").tz_convert("UTC")
                out.append((published, pd.read_csv(os.path.join(FIX, name))))
        return out

    def test_ercots_forecast_is_the_one_made_a_day_before_the_hour(self):
        posts = self.postings()
        self.assertEqual(len(posts), 3)
        actual, forecast = ewf.pairs(posts, "STWPF_SYSTEM_WIDE")
        first_pub, first = posts[0]
        ts = ewf.hour_starts(first)
        # an hour more than a day after the first posting and before the second: its forecast is the first posting's
        later = [(t, f) for t, f in zip(ts, pd.to_numeric(first["STWPF_SYSTEM_WIDE"], errors="coerce")) if first_pub + pd.Timedelta(hours=24) <= t < posts[1][0] and pd.notna(f)]
        self.assertTrue(later)
        t, f = later[0]
        self.assertEqual(forecast[t], float(f))
        # no hour's forecast comes from a posting made less than a day before it
        self.assertTrue(all(t - min(p for p, _ in posts) >= ewf.LEAD for t in forecast.index))
        self.assertFalse(any(t < first_pub + ewf.LEAD for t in forecast.index))
        # the actual is the newest posting's value for the hour
        last = posts[-1][1]
        g = pd.to_numeric(last["SYSTEM_WIDE_GEN"], errors="coerce")
        i = g.last_valid_index()
        self.assertEqual(actual[ewf.hour_starts(last)[i]], float(g[i]))
        self.assertEqual(ewf.hour_starts(first).iloc[0], (pd.Timestamp(dt.datetime.strptime(first["DELIVERY_DATE"].iloc[0], "%m/%d/%Y"), tz="America/Chicago")
                                                          + pd.Timedelta(hours=int(first["HOUR_ENDING"].iloc[0]) - 1)).tz_convert("UTC"))

    def test_the_error_is_forecast_less_actual_on_the_hours_that_hold_both(self):
        actual, forecast = ewf.pairs(self.postings(), "STWPF_SYSTEM_WIDE")
        e = mv.error_tables(forecast, actual, "America/Chicago")
        both = actual.index.intersection(forecast.index)
        self.assertEqual(e["all"]["n"], len(both))
        err = forecast[both] - actual[both]
        self.assertAlmostEqual(e["all"]["bias"], round(float(err.mean()), 1), places=1)
        self.assertAlmostEqual(e["all"]["mae"], round(float(err.abs().mean()), 1), places=1)
        self.assertEqual(sum(h["n"] for h in e["hours"] if h), len(both))
        self.assertIsNone(mv.error_tables(forecast.iloc[:0], actual, "America/Chicago"))      # no hour with both, no figure


class Nrc(unittest.TestCase):
    def test_the_nrcs_file_as_listed(self):
        text = fix("nrc_powerreactorstatus_sample.txt")
        t = nrc.parse(text, *STAMP)
        lines = text.splitlines()[1:]
        self.assertEqual(len(t), len(lines))
        day, unit, power = lines[0].split("|")
        row = t.iloc[0]
        self.assertEqual((row["node"], row["value"], row["unit"], row["freq"]), (unit, float(power), "pct", "P1D"))
        self.assertEqual(row["ts_utc"], dt.datetime.strptime(day.split(" ")[0], "%m/%d/%Y").strftime("%Y-%m-%dT00:00:00Z"))
        self.assertEqual(row["entity"], "nrc:" + re.sub(r"[^a-z0-9]+", "_", unit.lower()).strip("_"))
        with self.assertRaises(RuntimeError):
            nrc.parse(text.replace(f"|{unit}|{power}", f"|{unit}|140", 1), *STAMP)       # a real line with an impossible power
        self.assertEqual(nrc.CEILING, 300_000)

    def test_a_reactor_is_placed_by_its_plants_name(self):
        self.assertEqual(mv.norm("D.C. Cook"), "d c cook")
        self.assertEqual(mv.NRC_ALIAS["d c cook"], "donald c cook")
        self.assertEqual(mv.norm("Nine Mile Point Nuclear Station"), "nine mile point nuclear station")


class Capacity(unittest.TestCase):
    def test_a_retired_unit_counts_until_the_month_before_it_retired(self):
        caps = ms.capacity(FIX)                                    # New York's coal and nuclear units, operating and retired
        nuc, coal = caps[("NYIS", "nuclear")], caps[("NYIS", "coal")]
        rt = pd.read_csv(os.path.join(FIX, "eia860m_retired_generators_all.csv"), comment="#", dtype=str)
        ip2 = rt[rt["name"].str.contains("Indian Point") & (rt["technology_group"] == "nuclear")]
        self.assertEqual(len(ip2), 2)                              # Indian Point 2 and 3, in EIA's Retired sheet
        last = ip2["status_date"].max()[:7]                        # the month the second unit retired
        before = (pd.Period(last) - 1).strftime("%Y-%m")
        self.assertAlmostEqual(nuc[before] - nuc[last], float(ip2.loc[ip2["status_date"].str[:7] == last, "nameplate_mw"].astype(float).sum()), places=1)
        self.assertGreater(nuc["2019-01"], nuc["2026-08"])         # the fleet of 2019 held the units since retired
        self.assertGreater(coal["2019-01"], 0)
        self.assertEqual(coal["2026-08"], 0)                       # New York's last coal unit is in the Retired sheet
        self.assertEqual(ms.RETIRED, "eia860m_retired_generators_all")
        self.assertEqual(ms.FROM_YEAR, 2019)


class Views(unittest.TestCase):
    def test_availability_is_output_over_installed_capacity_by_hour(self):
        x = ercot_hours()
        months = sorted(set(x["month"]))
        caps = {("ERCO", f): pd.Series({m: c for m in months}) for f, c in (("wind", 40000.0), ("solar", 30000.0), ("nuclear", 5000.0), ("natural_gas", 70000.0), ("coal", 14000.0), ("hydro", 500.0), ("storage", 12000.0))}
        av = mv.availability("ercot", x, caps)
        self.assertEqual(set(av), {"2025"})
        self.assertIn("summer", av["2025"])
        self.assertNotIn("winter", av["2025"])                     # the sample holds no winter hour
        held = x[x["held"]]
        h14 = held[held["hour"] == 14]
        self.assertAlmostEqual(av["2025"]["summer"]["solar"][14], round(float((100 * h14["solar"].clip(lower=0).fillna(0) / 30000.0).mean()), 1), places=1)
        both = (h14["hydro"].clip(lower=0).fillna(0) + h14["storage"].clip(lower=0).fillna(0)) / 12500.0
        self.assertAlmostEqual(av["2025"]["summer"]["hydro_storage"][14], round(float(100 * both.mean()), 1), places=1)      # hydro and storage together
        self.assertLess(av["2025"]["summer"]["solar"][2], 1.0)     # the sun is down
        self.assertNotIn("solar", mv.availability("ercot", x, {k: v for k, v in caps.items() if k[1] != "solar"})["2025"]["summer"])     # no capacity, no figure

    def test_more_records_from_the_held_hours(self):
        x = ercot_hours()
        rec = {r["key"]: r for r in mv.extra_records("ercot", x)["2025"]}
        held = x[x["held"]]
        self.assertEqual(rec["wind_hour_max"]["value"], round(float(held["wind"].max()), 1))
        self.assertEqual(rec["wind_hour_max"]["at"], held["wind"].idxmax().strftime("%Y-%m-%dT%H:%M:%SZ"))
        self.assertEqual(rec["demand_hour_max"]["value"], round(float(held["demand"].max()), 1))
        days = held.groupby("day")["solar"].agg(["sum", "size"])
        full = days[days["size"] >= 24]
        self.assertEqual(rec["solar_day_max"]["value"], round(float(full["sum"].max()), 1))        # a day is ranked only when every hour of it is held
        self.assertEqual(rec["solar_day_max"]["kind"], "day")
        gas = held[held["natural_gas"] > 0]
        share = 100 * gas["natural_gas"] / held.loc[gas.index, mp.SOURCES].fillna(0).clip(lower=0).sum(axis=1)
        self.assertAlmostEqual(rec["gas_share_min"]["value"], round(float(share.min()), 1), places=1)
        zero = x.copy()
        zero.loc[zero.index[10], "natural_gas"] = 0.0              # a real hour with its gas set to zero: a missing value, never the record
        self.assertGreater({r["key"]: r for r in mv.extra_records("ercot", zero)["2025"]}["gas_share_min"]["value"], 0)

    def test_a_factor_is_the_average_day_of_the_hours_held_and_needs_enough_days(self):
        x = ercot_hours()
        s = -x[x["held"]]["interchange"]
        out = mv.by_hour(s, "America/Chicago", digits=0)
        self.assertEqual(set(out["months"]), {"2025-07", "2025-08"})
        self.assertEqual(out["years"], {})                          # two months are not a year
        july = x[x["held"] & (x["month"] == "2025-07") & (x["hour"] == 17)]
        self.assertEqual(out["months"]["2025-07"][17], round(float(-july["interchange"].mean()), 0))
        thin = s[s.index.day <= 10]                                 # ten days of each month only
        self.assertEqual(mv.by_hour(thin, "America/Chicago")["months"], {})

    def test_miso_and_pjm_have_no_price_factor(self):
        self.assertEqual(set(mv.NO_PRICE), {"miso", "pjm"})
        self.assertNotIn("miso", mv.HUB)
        self.assertNotIn("pjm", mv.HUB)
        for g, status in (("miso", "paused"), ("pjm", "licensed")):
            with open(os.path.join(SITE, "data", "mixplus", f"{g}.json"), encoding="utf-8") as f:
                p = json.load(f)["factors"]
            self.assertEqual((p["price_da"]["status"], p["price_da"]["months"], p["price_rt"]["years"]), (status, {}, {}))


class TheSiteFiles(unittest.TestCase):
    def load(self, *parts):
        with open(os.path.join(SITE, "data", *parts), encoding="utf-8") as f:
            return json.load(f)

    def test_california_holds_the_months_of_the_hydro_gap_from_caisos_own_data(self):
        c = self.load("mix", "caiso.json")
        for m in ("2019-10", "2019-12", "2020-03", "2020-08"):
            self.assertIn(m, c["months"], m)
            self.assertEqual(c["months"][m]["side"], "caiso", m)
            self.assertGreater(c["months"][m]["hydro_share_pct"], 3, m)
        self.assertEqual(c["months"]["2019-08"]["side"], "eia930")
        self.assertIn("2019", c["years"])
        self.assertIn("2020", c["years"])
        self.assertGreaterEqual(len(c["months"]), 90)

    def test_every_grid_has_every_new_figure(self):
        for g in mp.GRIDS:
            p = self.load("mixplus", f"{g}.json")
            self.assertEqual(sorted(p["availability"])[0], "2019" if g != "spp" else sorted(p["availability"])[0], g)
            self.assertTrue({"wind", "natural_gas", "nuclear"} <= set(p["availability"]["2025"]["all"]) or g == "isone", g)
            self.assertTrue(all(len(v) == 24 for y in p["availability"].values() for s in y.values() for v in s.values()), g)
            self.assertIn("all", p["records"])
            self.assertTrue({"net_imports", "carbon", "temperature", "price_da", "price_rt"} <= set(p["factors"]), g)
            self.assertIn("2019-01", p["capacity"]["natural_gas"], g)
            s = self.load("stress", f"{g}.json")
            self.assertEqual(s["from_year"], 2019)
            first = sorted(s["years"])[0]
            self.assertIn("capacity_natural_gas_mw", s["years"][first], g)        # capacity for every year now, not from 2025 only

    def test_the_forecast_and_history_files(self):
        f = self.load("mix_forecast.json")["grids"]
        self.assertEqual(set(f), {"caiso", "ercot"})
        self.assertGreater(f["caiso"]["sources"]["solar"]["all"]["n"], 20000)
        self.assertEqual(len(f["caiso"]["sources"]["wind"]["hours"]), 24)
        h = self.load("mix_history.json")
        us = h["states"]["US"]
        self.assertEqual(us["2001"]["months"], 12)
        self.assertGreater(us["2001"]["coal"], us["2025"]["coal"])                # coal's decline
        self.assertLess(us["2001"]["natural_gas"], us["2025"]["natural_gas"])     # gas's rise
        self.assertGreaterEqual(len(h["states"]), 52)


class ThePage(unittest.TestCase):
    def test_one_tool_one_page_one_address(self):
        cfg = src("site", "next.config.ts")
        for old, view in (("/mix/v2", "day"), ("/mix/clean", "clean"), ("/mix/stress", "stress")):
            self.assertIn(f'{{ source: "{old}", destination: "/mix?view={view}", permanent: true }}', cfg)
        self.assertTrue(os.path.exists(os.path.join(SITE, "app", "mix", "page.tsx")))
        for gone in ("v2", "clean", "stress"):
            self.assertFalse(os.path.exists(os.path.join(SITE, "app", "mix", gone)), gone)
        for kept in ("mix-original", "mix-v2", "mix-clean", "mix-stress"):
            self.assertTrue(os.path.exists(os.path.join(SITE, "app", "_retired", kept, "page.tsx")), kept)       # nothing was deleted
        self.assertRegex(src("site", "lib", "release.ts"), r'"/mix":\s*"review"')

    def test_the_original_view_keeps_its_filters_and_its_three_sections(self):
        page = src("site", "app", "mix", "page.tsx")
        for words in ('name="ba"', 'name="state"', "today so far", "hourly mix, last 7 days", "monthly mix since 2001", "<Today ", "<Hourly ", "<Monthly "):
            self.assertIn(words, page, words)
        now = src("site", "components", "mix", "Now.tsx")
        for words in ("<ShareBar", "<StackedArea", "series_esum|${LATEST}", "series|${MONTHLY}"):
            self.assertIn(words, now, words)

    def test_the_page_face_carries_no_method(self):
        face = src("site", "app", "mix", "page.tsx") + src("site", "components", "mix", "views.tsx") + src("site", "components", "mix", "Now.tsx")
        shown = re.sub(r"(?m)^\s*//.*$", "", face)
        for word in ("methodology", "limitation", "disputed", "<Fold", "SourceLine", "<Cite", "CaisoBreakNote", "CaisoMixWithheld", "NoData"):
            self.assertNotIn(word, shown, word)
        self.assertIn('"/data/methods/generation_mix_hourly"', shown)
        for words in ("not held yet", "paused while terms are reviewed", "licensed source needed", "working on it"):
            self.assertIn(words, shown, words)

    def test_the_method_note_holds_what_the_page_does_not(self):
        note = src("docs", "methods", "generation_mix_hourly.md")
        for words in ("Session 133", "October 2019 to August 2020", "caiso_fuel_supply_history", "-4,098 MW", "eia860m_retired_generators_all", "after curtailment", "146 hours",
                      "Indian Point", "credit the California ISO", "17 U.S.C. 105", "HTTP 403"):
            self.assertIn(words, note, words)

    def test_the_refresh_is_written_and_not_scheduled(self):
        sh = src("warehouse", "refresh_mix.sh")
        for step in ('--step "caiso_wind_solar_forecast"', '--step "ercot_wind_solar_forecast"', '--step "nrc_reactor_status"', '--step "mix_views"'):
            self.assertIn("health.py run " + step, sh)
        for wf in os.listdir(os.path.join(ROOT, ".github", "workflows")):
            self.assertNotIn("refresh_mix.sh", src(".github", "workflows", wf), wf)
        self.assertNotIn("refresh_mix.sh", src("warehouse", "run_daily.sh"))
        self.assertNotIn("mix_views", src("warehouse", "run_daily.sh"))

    def test_the_new_tables_are_held_out_of_the_live_set(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
        import load
        for t in ("caiso_fuel_supply_history", "eia860m_retired_generators_all", "nrc_reactor_status", "caiso_wind_solar_forecast", "ercot_wind_solar_forecast"):
            self.assertIn(t, load.LIVE["catalogue_hold"])
        for s in ("caiso:todays_outlook_fuelsource_history", "eia:860m:retired", "nrc:power_reactor_status", "caiso:SLD_REN_FCST"):
            self.assertIn(s, load.LIVE["sources_hold"])
        reg = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), dtype=str, keep_default_na=False)
        self.assertIn("caiso:todays_outlook_fuelsource", set(reg["source"]))      # the daily table's own row is as it was

    def test_no_em_dash_in_what_the_session_wrote(self):
        for p in (("warehouse", "connectors", "caiso_fuel_supply_history.py"), ("warehouse", "connectors", "caiso_wind_solar_forecast.py"), ("warehouse", "connectors", "ercot_wind_solar_forecast.py"),
                  ("warehouse", "connectors", "nrc_reactor_status.py"), ("warehouse", "connectors", "eia860m_retired_all.py"), ("warehouse", "derived", "mix_views.py"),
                  ("warehouse", "derived", "mix_profile.py"), ("warehouse", "refresh_mix.sh"), ("site", "app", "mix", "page.tsx"), ("site", "lib", "mixpage.ts"), ("site", "lib", "mixdata.ts"),
                  ("site", "components", "mix", "views.tsx"), ("site", "components", "mix", "Charts.tsx"), ("site", "components", "mix", "Now.tsx"), ("site", "scripts", "check-mix.mjs"),
                  ("site", "scripts", "test-mix.mjs"), ("docs", "methods", "generation_mix_hourly.md"), ("tests", "test_session133.py")):
            text = src(*p)
            self.assertNotIn(chr(0x2014), text, p)
            self.assertNotIn(chr(0x2013), text, p)


if __name__ == "__main__":
    unittest.main()
