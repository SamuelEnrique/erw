"""Session 118: data integrity.

One rule for impossible values in three parts (an hour of demand or net generation, a zero in place of a missing
value, a day of interchange no tie can carry), on saved real rows of EIA's workbooks; the hold on the tables behind a
live page; California's hydro gap; the months the older pages leave out; and the register's three resolutions.
No network. tests/fixtures/session118/ holds real rows of the emissions connector's extracts, every column, unaltered.
"""
import json
import os
import re
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("warehouse/derived", "warehouse/connectors", "warehouse"):
    sys.path.insert(0, os.path.join(ROOT, *p.split("/")))
import carbon_left_out as clo  # noqa: E402
import data_faults as df  # noqa: E402
import eia930_emissions as em  # noqa: E402
import impossible_hours as ih  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session118")
# the median hour of each grid over its whole history (2018-07 to 2026-10-03), of the hours that pass the first three
# tests, measured on the extracts of 2026-10-04: what the range test compares an hour with in a real build
MEDIAN = {"ciso": {"demand_mwh": 24502.0, "net_generation_mwh": 18232.0}, "pjm": {"demand_mwh": 89838.0, "net_generation_mwh": 93183.0}}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def sample(ba):
    return em.read_extract(os.path.join(FIX, f"{ba}_hours_sample.csv"))


def not_used(ba, col, x=None):
    """The hour starts of a sample whose held value of `col` the rule does not use."""
    x = sample(ba) if x is None else x
    y = ih.screen_extract(x)
    raw = pd.to_numeric(x[col], errors="coerce")
    return list(x["ts_utc"][(raw.notna() & y[col].isna()).to_numpy()])


class RuleAOnRealHours(unittest.TestCase):
    def test_pjm_19_october_2021_the_values_in_the_billions(self):
        x = sample("pjm")
        v = dict(zip(x["ts_utc"], pd.to_numeric(x["demand_mwh"])))
        self.assertEqual(v["2021-10-19T03:00:00Z"], 2147480000.0)          # as EIA's file gives it
        self.assertEqual(v["2021-10-19T02:00:00Z"], 1527760000.0)
        gone = not_used("pjm", "demand_mwh")
        for h in ("2021-10-19T02:00:00Z", "2021-10-19T03:00:00Z", "2021-10-19T04:00:00Z"):
            self.assertIn(h, gone)
        # the good hour on each side goes with them: its neighbours' median is theirs (the method note says so)
        self.assertIn("2021-10-19T01:00:00Z", gone)
        self.assertIn("2021-10-19T05:00:00Z", gone)
        self.assertIn("2020-07-13T22:00:00Z", gone)                         # 224,345 MW between hours near 125,000
        self.assertEqual(len(gone), 6)
        self.assertEqual(len(not_used("pjm", "net_generation_mwh")), 5)     # the same five hours of 19 October; July's is demand only

    def test_nothing_is_filled_or_moved(self):
        x = sample("pjm")
        y = ih.screen_extract(x)
        self.assertEqual(len(y), len(x))
        self.assertEqual(list(y["ts_utc"]), list(x["ts_utc"]))
        for c in ("demand_mwh", "net_generation_mwh"):
            raw = pd.to_numeric(x[c], errors="coerce")
            kept = y[c].notna().to_numpy()
            self.assertTrue((y[c][kept].to_numpy() == raw[kept].to_numpy()).all(), c)   # a used hour is the source's value
        self.assertTrue(x.drop(columns=["demand_mwh", "net_generation_mwh"]).equals(y.drop(columns=["demand_mwh", "net_generation_mwh"])))

    def test_a_zero_is_a_missing_value_new_york(self):
        x = sample("nyis")
        zeros = list(x["ts_utc"][pd.to_numeric(x["demand_mwh"]) == 0])
        self.assertEqual(zeros, [f"2026-02-09T23:00:00Z"] + [f"2026-02-10T0{h}:00:00Z" for h in range(5)])
        self.assertEqual(not_used("nyis", "demand_mwh"), zeros)
        self.assertEqual(not_used("nyis", "net_generation_mwh"), zeros)
        s = pd.Series(pd.to_numeric(x["demand_mwh"]).to_numpy(), index=pd.to_datetime(x["ts_utc"], utc=True))
        lo = ih.left_out(s)
        self.assertEqual(set(lo["reason"]), {"not above zero"})

    def test_spp_at_3_6_million_and_at_1_505(self):
        self.assertEqual(not_used("swpp", "demand_mwh"), ["2023-06-13T01:00:00Z", "2025-06-21T09:00:00Z"])
        self.assertEqual(not_used("swpp", "net_generation_mwh"), ["2023-06-13T01:00:00Z"])
        x = sample("swpp")
        v = dict(zip(x["ts_utc"], pd.to_numeric(x["demand_mwh"])))
        self.assertEqual((v["2023-06-13T01:00:00Z"], v["2025-06-21T09:00:00Z"]), (3621097.0, 1505.0))

    def test_a_real_collapse_is_kept_texas_in_winter_storm_uri(self):
        # ERCOT shed load on 15 February 2021: demand fell fast and for real. The rule uses every hour of those days
        self.assertEqual(not_used("erco", "demand_mwh"), [])
        self.assertEqual(not_used("erco", "net_generation_mwh"), [])

    def test_the_range_catches_a_run_the_hours_around_cannot(self):
        # California's net generation slides to 727 MW on 2023-11-10: each hour is close to the hours around it
        x = sample("ciso")
        x = x[(x["ts_utc"] >= "2023-11-08") & (x["ts_utc"] < "2023-11-13")]
        s = pd.Series(pd.to_numeric(x["net_generation_mwh"]).to_numpy(), index=pd.to_datetime(x["ts_utc"], utc=True))
        self.assertEqual(s["2023-11-10T10:00:00Z"], 727.0)
        local = ih.screen(s, rng=None)
        self.assertEqual(local["2023-11-10T10:00:00Z"], 727.0, "the test of the hours around passes it")
        med = MEDIAN["ciso"]["net_generation_mwh"]
        low = s[(s < ih.RANGE[0] * med) & local.notna()]
        self.assertEqual(len(low), 12)                                      # the twelve hours the whole history's median rejects
        both = ih.screen(s)                                                 # the sample's own median is close to the history's
        for ts in low.index:
            self.assertTrue(np.isnan(both[ts]), ts)
        lo = ih.left_out(s)
        self.assertEqual(lo.loc[pd.Timestamp("2023-11-10T10:00:00Z"), "reason"], "outside the grid's range")

    def test_the_range_is_wider_than_any_real_hour(self):
        # measured 2026-10-04 on every grid's history: the lowest hour of demand that passes the first three tests is
        # 0.465 of its grid's median, and the highest hour of anything 2.455 (California's net generation)
        self.assertLess(ih.RANGE[0], 0.465)
        self.assertGreater(ih.RANGE[1], 2.455)

    def test_the_hours_around_are_taken_by_the_clock_not_by_the_row(self):
        x = sample("pjm")
        cut = x[x["ts_utc"] != "2021-10-18T12:00:00Z"]                      # a file that skips an hour
        self.assertEqual(not_used("pjm", "demand_mwh", cut), not_used("pjm", "demand_mwh"))
        with self.assertRaises(ValueError):
            ih.screen_extract(pd.concat([x, x.iloc[[5]]]))

    def test_the_rule_as_it_stood_is_one_argument_away(self):
        s = pd.Series([100, 104, 108, 180, 112, 116, 0, 120, np.nan, 128.0], index=pd.date_range("2020-07-13", periods=10, freq="h"))
        v = s.where(s > 0)                                                  # session 97's own lines
        around = pd.concat([v.shift(k) for k in (-2, -1, 1, 2)], axis=1).median(axis=1)
        old = v.where(v.notna() & ~((v - around).abs() > 0.25 * around))
        pd.testing.assert_series_equal(ih.screen(s, rng=None), old)


class RuleCPairDays(unittest.TestCase):
    def frame(self):
        days = pd.date_range("2026-06-01", periods=60).strftime("%Y-%m-%d")
        a = pd.DataFrame({"entity": "eia930:SWPP-MISO", "day": days, "v": np.linspace(-9000, 9000, 60)})
        a.loc[50, "v"] = 2159056.0                                          # the day EIA reports, more than SPP's whole demand
        b = pd.DataFrame({"entity": "eia930:AAA-BBB", "day": days, "v": 100.0})
        # a pair that never moves has a deviation of zero, which counts as FLOOR (500 MWh): ten of them is 5,000 MWh
        b.loc[10, "v"] = 5050.0                                             # 4,950 MWh from the pair's median: used
        b.loc[11, "v"] = 5150.0                                             # 5,050 MWh from it: not used
        return pd.concat([a, b], ignore_index=True)

    def test_the_outlier_goes_and_the_floor_holds(self):
        it = self.frame()
        bad = ih.pair_days_far(it)
        self.assertEqual(list(it[bad]["v"]), [2159056.0, 5150.0])

    def test_the_three_builders_use_the_one_rule(self):
        import ai_power_regions as ap
        import ba_supply as bs
        it = self.frame()
        self.assertTrue((bs.screen(it) == ih.pair_days_far(it)).all())
        self.assertTrue((ap.screen(it) == ih.pair_days_far(it)).all())
        self.assertEqual((bs.MADS, bs.FLOOR), (ih.MADS, ih.FLOOR))
        self.assertEqual((ih.MADS, ih.FLOOR), (10, 500.0))
        self.assertIn("ba_supply.screen(it)", src("warehouse", "derived", "network_daily.py"))
        # the rule as the three builders had it, word for word
        g = it.groupby("entity")["v"]
        med = g.transform("median")
        mad = (it["v"] - med).abs().groupby(it["entity"]).transform("median")
        self.assertTrue((((it["v"] - med).abs() > 10 * np.maximum(mad, 500)) == ih.pair_days_far(it)).all())


class TheHold(unittest.TestCase):
    LIVE = ("carbon_intensity_hourly", "carbon_intensity_daily", "carbon_intensity_monthly", "cost_of_power_monthly", "cost_of_power_carbon",
            "ba_supply_monthly", "ai_power_regions")

    def setUp(self):
        self.was = os.environ.pop("ERW_SCREEN_TRIAL", None)

    def tearDown(self):
        os.environ.pop("ERW_SCREEN_TRIAL", None)
        if self.was is not None:
            os.environ["ERW_SCREEN_TRIAL"] = self.was

    def test_the_tables_behind_a_live_page_are_held(self):
        for t in self.LIVE:
            self.assertIn(t, ih.HELD)
            self.assertFalse(ih.applies(t), t)
        for t in ("generation_mix_hourly_profile", "eia930_demand_growth", "shoulder_hours_monthly", "flex_alert_effects"):
            self.assertTrue(ih.applies(t), t)

    def test_a_held_builder_writes_what_it_wrote(self):
        x = sample("pjm")
        for t in self.LIVE:
            self.assertIs(ih.screen_extract(x, t), x, t)                    # the extract as it came: no hour blanked

    def test_a_trial_build_applies_it(self):
        os.environ["ERW_SCREEN_TRIAL"] = "1"
        x = sample("pjm")
        y = ih.screen_extract(x, "cost_of_power_monthly")
        self.assertTrue(np.isnan(y["demand_mwh"][(x["ts_utc"] == "2021-10-19T03:00:00Z").to_numpy()].iloc[0]))

    def test_every_builder_that_reads_the_extract_calls_the_rule_by_its_table(self):
        self.assertIn("ih.screen_extract(em.read_extract(p)[[\"ts_utc\", \"demand_mwh\", \"net_generation_mwh\"]], TABLES[0], log=log)", src("warehouse", "derived", "carbon_intensity.py"))
        self.assertIn("x = ih.screen_extract(x, MONTHLY, log=log)", src("warehouse", "derived", "cost_of_power.py"))
        self.assertIn("ih.screen_extract(em.read_extract(ex)[[\"ts_utc\", \"demand_mwh\", \"net_generation_mwh\"]], NAME)", src("warehouse", "derived", "ba_supply.py"))
        self.assertIn('impossible_hours.screen_extract(x, "ai_power_regions")', src("warehouse", "derived", "ai_power_regions.py"))
        s = src("warehouse", "derived", "ai_power_regions.py")
        self.assertLess(s.index('impossible_hours.screen_extract(x, "ai_power_regions")'), s.index('x = x[in_window(x["ts_utc"])]'),
                        "the rule needs the whole history: it is applied before the window is cut")

    def test_the_flex_alert_table_uses_the_one_rule_in_place_of_its_own(self):
        s = src("warehouse", "derived", "flex_alert_scorecard.py")
        self.assertIn("bad = impossible_hours.screen(s).isna() & s.notna()", s)
        self.assertNotIn("bad = suspect(s)", s)

    def test_the_method_note_names_every_held_table(self):
        note = src("docs", "methods", "impossible_hours.md")
        for t in ih.HELD:
            self.assertIn(t, note)


class TheHydroGap(unittest.TestCase):
    def test_its_first_and_last_hour(self):
        hours = pd.Series(["2019-10-01T20:00:00Z", "2019-10-01T21:00:00Z", "2020-02-29T12:00:00Z", "2020-08-24T17:00:00Z", "2020-08-24T18:00:00Z"])
        self.assertEqual(list(ih.in_hydro_gap(hours)), [False, True, True, True, False])
        self.assertEqual(list(ih.in_hydro_gap(pd.to_datetime(hours, utc=True))), [False, True, True, True, False])
        self.assertEqual(len(pd.date_range(ih.CISO_NO_HYDRO[0], ih.CISO_NO_HYDRO[1], freq="h")), 7869)

    def test_the_carbon_builder_leaves_it_out_and_reads_the_late_hours_where_they_belong(self):
        s = src("warehouse", "derived", "carbon_intensity.py")
        self.assertIn("gap = ih.in_hydro_gap(j[\"ts_utc\"])", s)
        self.assertIn("j = j[~gap]", s)
        self.assertIn("cj.true_hours(", s)
        self.assertIn("if code == cj.BA and ih.applies(TABLES[0]):", s)


class TheMonthsThePagesLeaveOut(unittest.TestCase):
    def test_a_month_with_an_impossible_hour_is_listed_by_its_denominator(self):
        m = clo.months_with_impossible_hours(sample("pjm"))
        self.assertEqual(sorted(m["intensity_demand"]), ["2020-07", "2021-10"])
        self.assertEqual(sorted(m["intensity_generation"]), ["2021-10"])
        self.assertEqual(len(m["intensity_demand"]["2021-10"]), 5)
        self.assertEqual(m["intensity_demand"]["2020-07"][0]["value"], 224345.0)

    def test_only_months_the_table_holds_are_listed_and_california_gets_the_gap(self):
        import tempfile
        rows = [("eia930:PJM", "intensity_demand", "2021-10-01T00:00:00Z", "pjm"), ("eia930:PJM", "intensity_generation", "2021-10-01T00:00:00Z", "pjm"),
                ("eia930:PJM", "intensity_demand", "2021-09-01T00:00:00Z", "pjm"), ("eia930:CISO", "intensity_generation", "2020-01-01T00:00:00Z", "ciso"),
                ("eia930:CISO", "intensity_generation", "2023-10-01T00:00:00Z", "ciso")]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "carbon_intensity_monthly.csv")
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write("# a listing made for the test: which months a table holds\nentity,variable,ts_utc,ba\n")
                for r in rows:
                    f.write(",".join(r) + "\n")
            out = clo.build(p, {"pjm": sample("pjm"), "ciso": sample("ciso")})
        got = {(r["entity"], r["variable"], r["month"]) for r in out["months"]}
        self.assertEqual(got, {("eia930:PJM", "intensity_demand", "2021-10"), ("eia930:PJM", "intensity_generation", "2021-10"),
                               ("eia930:CISO", "intensity_generation", "2020-01")})   # July 2020 is not in the listing, so it is not listed
        self.assertEqual(out["hydro_gap"]["hours"], 7869)

    def test_the_sites_copy(self):
        f = json.loads(src("site", "data", "carbon_left_out.json"))
        keys = {(r["entity"], r["variable"], r["month"]) for r in f["months"]}
        self.assertIn(("eia930:PJM", "intensity_generation", "2021-10"), keys)      # 4.80 kg CO2/MWh in the held table
        self.assertIn(("eia930:SWPP", "intensity_generation", "2023-06"), keys)
        for month in ("2019-10", "2019-12", "2020-01", "2020-04", "2020-05", "2020-06", "2020-07"):
            self.assertIn(("eia930:CISO", "intensity_generation", month), keys)
        self.assertEqual(f["hydro_gap"]["first_hour"], ih.CISO_NO_HYDRO[0])
        self.assertEqual(sorted(f["held"]), ["carbon_intensity_daily", "carbon_intensity_hourly", "carbon_intensity_monthly"])
        for r in f["months"]:
            self.assertTrue(r["why"])

    def test_the_pages_leave_them_out_and_say_so(self):
        e = src("site", "app", "emissions", "page.tsx")
        self.assertIn("!carbonLeftOut(r.entity, r.variable, r.ts_utc)", e)
        self.assertIn("data-carbon-left-out", e)
        self.assertIn("/data/faults", e)
        g = src("site", "app", "grid", "[iso]", "page.tsx")
        self.assertIn("!carbonLeftOut(r.entity, r.variable, r.ts_utc)", g)
        self.assertIn("data-carbon-left-out", g)

    def test_the_older_pages_do_not_draw_eias_california_mix(self):
        self.assertIn('const withheld = ba.code === "ciso";', src("site", "app", "mix", "page.tsx"))
        self.assertEqual(src("site", "app", "mix", "page.tsx").count("withheld ? <CaisoMixWithheld"), 2)
        self.assertIn('if (r.ba.code === "ciso") return <CaisoMixWithheld', src("site", "app", "grid", "page.tsx"))
        self.assertIn('if (g.iso === "CAISO") return <CaisoMixWithheld />;', src("site", "app", "grid", "[iso]", "page.tsx"))
        c = src("site", "components", "CaisoMixWithheld.tsx")
        self.assertIn("eia930_ciso_generation_break", c)
        self.assertIsNone(re.search(r"\d{2,}\.\d", c), "the component states no figure of its own: it reads the register's evidence")

    def test_the_pages_stay_in_review(self):
        rel = src("site", "lib", "release.ts")
        for page in ("/emissions", "/mix", "/grid", "/grid/caiso"):
            self.assertIn(f'"{page}": "review"', rel, page)
        self.assertNotIn('"/data/faults": "live"', rel)
        self.assertNotIn('"/data/methods/impossible_hours": "live"', rel)


class TheRegister(unittest.TestCase):
    def setUp(self):
        self.faults = df.read_register()
        self.by = {f["id"]: f for f in self.faults}

    def test_every_entry_is_fixed_held_or_open_with_its_reason(self):
        for f in self.faults:
            self.assertIn(df.flat(f.get("resolution")), df.RESOLUTIONS, f["id"])
            self.assertGreater(len(df.flat(f.get("resolution_reason"))), 30, f["id"])
        self.assertEqual(df.RESOLUTIONS, ("fixed", "held_for_approval", "open"))

    def test_the_check_refuses_an_entry_without_one(self):
        tables = set(pd.read_csv(df.COVERAGE, dtype=str, keep_default_na=False)["table"])
        sources = set(pd.read_csv(df.SOURCES, dtype=str, keep_default_na=False)["source"])
        self.assertEqual(df.check(self.faults, tables, sources), [])
        bad = dict(self.faults[0], resolution="done")
        self.assertTrue(any("resolution" in b for b in df.check([bad], tables, sources)))
        bad = dict(self.faults[0])
        bad.pop("resolution_reason")
        self.assertTrue(any("resolution_reason" in b for b in df.check([bad], tables, sources)))

    def test_what_this_session_found_is_in_it(self):
        self.assertIn("eia930_unadjusted_values_in_the_billions", self.by)
        self.assertIn("eia930_net_generation_impossible_hours", self.by)
        ev = " ".join(self.by["eia930_unadjusted_values_in_the_billions"]["evidence"].split())
        self.assertIn("2,147,480,000", ev)
        self.assertIn("3,621,097", ev)
        gap = self.by["eia930_ciso_no_hydro"]
        self.assertEqual((gap["first"], gap["last"]), ("2019-10-01", "2020-08-24"))
        self.assertIn("7,869", " ".join(gap["evidence"].split()))

    def test_a_fault_behind_a_live_page_is_held_not_fixed(self):
        for fid in ("eia930_pjm_impossible_demand_hours", "eia930_nyiso_zero_demand_hours", "eia930_ciso_impossible_demand_hours",
                    "eia930_spp_impossible_demand_hours", "eia930_ciso_no_hydro", "eia930_unadjusted_values_in_the_billions"):
            self.assertEqual(self.by[fid]["resolution"], "held_for_approval", fid)

    def test_the_sites_copy_counts_them(self):
        f = json.loads(src("site", "data", "data_faults.json"))
        self.assertEqual(sum(f["by_resolution"].values()), f["faults"])
        self.assertEqual(f["faults"], len(self.faults))
        for r in f["rows"]:
            self.assertIn(r["resolution"], df.RESOLUTIONS)
            self.assertTrue(r["resolution_reason"])
        page = src("site", "app", "data", "faults", "page.tsx")
        self.assertIn("data-fault-resolution", page)
        self.assertIn("file.by_resolution", page)


class Standing(unittest.TestCase):
    def test_no_em_dash_in_what_this_session_wrote(self):
        for parts in (("warehouse", "derived", "impossible_hours.py"), ("warehouse", "derived", "carbon_left_out.py"), ("warehouse", "faults", "faults.yaml"),
                      ("docs", "methods", "impossible_hours.md"), ("site", "lib", "carbonLeftOut.ts"), ("site", "components", "CaisoMixWithheld.tsx"),
                      ("tests", "test_session118.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts[-1])

    def test_miso_is_still_paused(self):
        self.assertIn("miso", src("warehouse", "metadata", "paused_sources.csv").lower())


if __name__ == "__main__":
    unittest.main()
